#!/usr/bin/env python3
"""
Seed Reference Water Objects

Seeds the database with reference water objects from hackathon documentation:
- Барыкколь (Barakkol)
- Коскол (Koskol) 
- Камыстыкол (Kamystykol)

These are test objects with known passport data for development and testing.

Usage:
    python seed_reference_objects.py
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.water_object import WaterObject, ResourceType, WaterType, FaunaType, PriorityLevel


# Reference objects from hackathon documentation
REFERENCE_OBJECTS = [
    {
        "name": "Коскол",
        "region": "Улытауская область",
        "resource_type": ResourceType.lake,
        "water_type": WaterType.non_fresh,
        "fauna": FaunaType.non_fish_bearing,
        "passport_date": datetime(2023, 1, 15),
        "technical_condition": 3,
        "latitude": 49.522778,  # N 49°31'21"
        "longitude": 67.053056,  # E 67°03'11"
        "pdf_url": None,
        "priority": 0,
        "priority_level": PriorityLevel.low
    },
    {
        "name": "Камыстыкол",
        "region": "Улытауская область",
        "resource_type": ResourceType.lake,
        "water_type": WaterType.non_fresh,
        "fauna": FaunaType.fish_bearing,
        "passport_date": datetime(2023, 2, 20),
        "technical_condition": 4,
        "latitude": 49.569167,  # N 49°34'09"
        "longitude": 67.073611,  # E 67°04'25"
        "pdf_url": None,
        "priority": 0,
        "priority_level": PriorityLevel.low
    },
    {
        "name": "Бухтарминский судоходный шлюз",
        "region": "Западно-Казахстанская область",
        "resource_type": ResourceType.other,
        "water_type": None,
        "fauna": None,
        "passport_date": datetime(2022, 5, 1),
        "technical_condition": 3,
        "latitude": 42.783333,  # 42°47' с. ш.
        "longitude": 71.550000,  # 71°33' в. д.
        "pdf_url": None,
        "priority": 0,
        "priority_level": PriorityLevel.low
    },
    {
        "name": "Шульбинский судоходный шлюз",
        "region": "Северо-Казахстанская область",
        "resource_type": ResourceType.other,
        "water_type": None,
        "fauna": None,
        "passport_date": datetime(2022, 8, 3),
        "technical_condition": 5,
        "latitude": 50.533333,  # 50°32' с. ш.
        "longitude": 57.383333,  # 57°23' в. д.
        "pdf_url": None,
        "priority": 0,
        "priority_level": PriorityLevel.low
    },
    {
        "name": "Чаглинский гидроузел",
        "region": "Восточно-Казахстанская область",
        "resource_type": ResourceType.other,
        "water_type": None,
        "fauna": None,
        "passport_date": datetime(2020, 8, 3),
        "technical_condition": 1,
        "latitude": 54.750000,  # 54°45' с. ш.
        "longitude": 69.200000,  # 69°12' в. д.
        "pdf_url": None,
        "priority": 0,
        "priority_level": PriorityLevel.low
    }
]


def seed_reference_objects() -> int:
    """
    Seed reference water objects into database.
    
    Returns:
        Number of objects seeded
    """
    print("=" * 70)
    print("Seeding Reference Water Objects")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        seeded = 0
        
        for obj_data in REFERENCE_OBJECTS:
            # Check if object already exists
            existing = db.query(WaterObject).filter(
                WaterObject.name == obj_data["name"],
                WaterObject.region == obj_data["region"]
            ).first()
            
            if existing:
                print(f"⊘ Skipping {obj_data['name']} - already exists (ID: {existing.id})")
                continue
            
            # Create new object
            water_obj = WaterObject(**obj_data)
            water_obj.update_priority()
            
            db.add(water_obj)
            db.commit()
            db.refresh(water_obj)
            
            print(f"✓ Seeded {water_obj.name} (ID: {water_obj.id}, Priority: {water_obj.priority}, Level: {water_obj.priority_level.value})")
            seeded += 1
        
        print(f"\n{'=' * 70}")
        print(f"Seeded {seeded} reference objects")
        print(f"{'=' * 70}")
        
        return seeded
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Error seeding objects: {e}")
        import traceback
        traceback.print_exc()
        return 0
        
    finally:
        db.close()


def main():
    """CLI entry point"""
    try:
        count = seed_reference_objects()
        sys.exit(0 if count > 0 else 1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
