#!/usr/bin/env python3
"""
OSM Water Bodies Import Script

Imports water bodies from OpenStreetMap for Kazakhstan using the Overpass API.
Queries for lakes, canals, reservoirs, and rivers with names.

Usage:
    python import_osm_water.py [--limit N] [--dry-run]
"""

import sys
import os
import requests
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models.water_object import WaterObject, ResourceType, WaterType, FaunaType


# Kazakhstan bounding box (approximate)
KAZAKHSTAN_BBOX = {
    "south": 40.5,
    "north": 55.5,
    "west": 46.5,
    "east": 87.5
}


def build_overpass_query(bbox: Dict[str, float], timeout: int = 180) -> str:
    """
    Build Overpass API query for water bodies in Kazakhstan.
    
    Queries for:
    - natural=water with water=lake
    - natural=water with water=reservoir
    - natural=water with water=canal
    - waterway=river (linear features)
    - waterway=riverbank (area features)
    
    Args:
        bbox: Dictionary with south, north, west, east coordinates
        timeout: Query timeout in seconds
        
    Returns:
        Overpass QL query string
    """
    bbox_str = f"{bbox['south']},{bbox['west']},{bbox['north']},{bbox['east']}"
    
    query = f"""
[out:json][timeout:{timeout}];
(
  // Lakes
  nwr["natural"="water"]["water"="lake"]["name"]({bbox_str});
  
  // Reservoirs
  nwr["natural"="water"]["water"="reservoir"]["name"]({bbox_str});
  
  // Canals
  nwr["natural"="water"]["water"="canal"]["name"]({bbox_str});
  
  // Rivers (areas)
  nwr["natural"="water"]["water"="river"]["name"]({bbox_str});
  nwr["waterway"="riverbank"]["name"]({bbox_str});
  
  // Rivers (linear - ways only, converted to areas in processing)
  way["waterway"="river"]["name"]({bbox_str});
);
out center;
"""
    return query


def query_overpass_api(query: str, max_retries: int = 3) -> Optional[Dict[str, Any]]:
    """
    Execute Overpass API query with retry logic.
    
    Args:
        query: Overpass QL query string
        max_retries: Maximum number of retry attempts
        
    Returns:
        JSON response from API or None on failure
    """
    url = "https://overpass-api.de/api/interpreter"
    
    for attempt in range(max_retries):
        try:
            print(f"Querying Overpass API (attempt {attempt + 1}/{max_retries})...")
            response = requests.post(url, data={"data": query}, timeout=300)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 30  # Exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Giving up.")
                return None


def map_osm_resource_type(osm_tags: Dict[str, str]) -> ResourceType:
    """
    Map OSM tags to ResourceType enum.
    
    Args:
        osm_tags: Dictionary of OSM tags
        
    Returns:
        ResourceType enum value
    """
    water_type = osm_tags.get("water", "")
    waterway_type = osm_tags.get("waterway", "")
    
    # Map water=* tags
    if water_type == "lake":
        return ResourceType.lake
    elif water_type == "reservoir":
        return ResourceType.reservoir
    elif water_type == "canal":
        return ResourceType.canal
    elif water_type == "river":
        return ResourceType.river
    
    # Map waterway=* tags
    if waterway_type == "river" or waterway_type == "riverbank":
        return ResourceType.river
    elif waterway_type == "canal":
        return ResourceType.canal
    
    return ResourceType.other


def get_region_from_coordinates(lat: float, lon: float) -> str:
    """
    Approximate region from coordinates.
    For now returns "Unknown" - can be enhanced with reverse geocoding.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Region name
    """
    # TODO: Implement reverse geocoding or use admin_level tags from OSM
    # For now, return placeholder that will be updated manually or via separate process
    return "Неизвестная область"


def parse_osm_element(element: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse OSM element into WaterObject format.
    
    Args:
        element: OSM element from Overpass API response
        
    Returns:
        Dictionary with WaterObject fields or None if invalid
    """
    tags = element.get("tags", {})
    
    # Skip elements without name
    name = tags.get("name", "").strip()
    if not name:
        return None
    
    # Get coordinates
    lat = None
    lon = None
    
    if element["type"] == "node":
        lat = element.get("lat")
        lon = element.get("lon")
    elif "center" in element:
        lat = element["center"].get("lat")
        lon = element["center"].get("lon")
    
    if lat is None or lon is None:
        return None
    
    # Map resource type
    resource_type = map_osm_resource_type(tags)
    
    # Get region (placeholder for now)
    region = get_region_from_coordinates(lat, lon)
    
    # Determine water type (default to fresh for Kazakhstan lakes)
    # Can be refined based on known salt lakes
    water_type = WaterType.fresh
    salt_tag = tags.get("salt", "").lower()
    if salt_tag in ["yes", "true", "1"]:
        water_type = WaterType.non_fresh
    
    # Check for known salt lakes by name
    salt_lake_keywords = ["соленое", "солёное", "туз", "кумкуль"]
    if any(keyword in name.lower() for keyword in salt_lake_keywords):
        water_type = WaterType.non_fresh
    
    return {
        "name": name,
        "region": region,
        "resource_type": resource_type,
        "water_type": water_type,
        "fauna": None,  # Unknown from OSM
        "passport_date": None,
        "technical_condition": 3,  # Default middle value
        "latitude": lat,
        "longitude": lon,
        "pdf_url": None,
        "priority": 0,
        "priority_level": "low"
    }


def bulk_insert_water_objects(db: Session, objects: List[Dict[str, Any]], batch_size: int = 100) -> int:
    """
    Bulk insert water objects into database.
    
    Args:
        db: Database session
        objects: List of water object dictionaries
        batch_size: Number of objects to insert per transaction
        
    Returns:
        Number of objects inserted
    """
    inserted = 0
    
    for i in range(0, len(objects), batch_size):
        batch = objects[i:i + batch_size]
        
        try:
            # Create WaterObject instances
            water_objects = []
            for obj_data in batch:
                water_obj = WaterObject(**obj_data)
                water_obj.update_priority()
                water_objects.append(water_obj)
            
            # Bulk insert
            db.bulk_save_objects(water_objects)
            db.commit()
            
            inserted += len(batch)
            print(f"Inserted batch {i // batch_size + 1}: {len(batch)} objects (total: {inserted})")
            
        except Exception as e:
            db.rollback()
            print(f"Error inserting batch {i // batch_size + 1}: {e}")
            continue
    
    return inserted


def import_osm_water(limit: Optional[int] = None, dry_run: bool = False) -> int:
    """
    Main import function.
    
    Args:
        limit: Maximum number of objects to import (for testing)
        dry_run: If True, parse data but don't insert into database
        
    Returns:
        Number of objects imported
    """
    print("=" * 70)
    print("OSM Water Bodies Import for Kazakhstan")
    print("=" * 70)
    
    # Build and execute query
    query = build_overpass_query(KAZAKHSTAN_BBOX)
    print(f"\nBounding box: {KAZAKHSTAN_BBOX}")
    print(f"Limit: {limit if limit else 'None (import all)'}")
    print(f"Dry run: {dry_run}")
    print()
    
    data = query_overpass_api(query)
    if not data:
        print("Failed to fetch data from Overpass API")
        return 0
    
    elements = data.get("elements", [])
    print(f"\nFetched {len(elements)} elements from OSM")
    
    # Parse elements
    print("\nParsing OSM elements...")
    water_objects = []
    
    for element in elements:
        parsed = parse_osm_element(element)
        if parsed:
            water_objects.append(parsed)
            
            if limit and len(water_objects) >= limit:
                break
    
    print(f"Parsed {len(water_objects)} valid water objects")
    
    if not water_objects:
        print("No valid water objects found")
        return 0
    
    # Show sample
    print("\nSample objects:")
    for obj in water_objects[:3]:
        print(f"  - {obj['name']} ({obj['resource_type'].value}) at {obj['latitude']:.4f}, {obj['longitude']:.4f}")
    
    if dry_run:
        print("\nDry run mode - skipping database insertion")
        return len(water_objects)
    
    # Insert into database
    print(f"\nInserting {len(water_objects)} objects into database...")
    db = SessionLocal()
    try:
        inserted = bulk_insert_water_objects(db, water_objects)
        print(f"\n✓ Successfully imported {inserted} water objects")
        return inserted
    finally:
        db.close()


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Import water bodies from OpenStreetMap")
    parser.add_argument("--limit", type=int, help="Maximum number of objects to import")
    parser.add_argument("--dry-run", action="store_true", help="Parse data but don't insert into database")
    
    args = parser.parse_args()
    
    try:
        count = import_osm_water(limit=args.limit, dry_run=args.dry_run)
        print(f"\nImport complete: {count} objects")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
