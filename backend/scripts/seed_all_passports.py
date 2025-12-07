#!/usr/bin/env python3
"""
Seed All Passport PDFs

Extracts text from all PDF files in uploads/passports/ directory and seeds them
into the database. Creates water objects from passport metadata and links passport texts.

Usage:
    python scripts/seed_all_passports.py [--dry-run]
"""

import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pypdf import PdfReader
from database import SessionLocal
from models.water_object import WaterObject, ResourceType, WaterType, FaunaType, PriorityLevel
from models.passport_text import PassportText


# Passport directory path
PASSPORT_DIR = Path(__file__).parent.parent / "uploads" / "passports"


def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extract text content from PDF file.
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        Extracted text content
    """
    try:
        reader = PdfReader(pdf_path)
        text_parts = []
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                text_parts.append(text)
        
        return "\n\n".join(text_parts)
    except Exception as e:
        print(f"  ✗ Error extracting text from {pdf_path.name}: {e}")
        return ""


def parse_passport_metadata(text: str, filename: str) -> Optional[Dict[str, Any]]:
    """
    Parse passport text to extract water object metadata.
    
    Args:
        text: Extracted passport text
        filename: PDF filename
        
    Returns:
        Dictionary with water object fields or None
    """
    metadata = {}
    
    # Extract object name (various patterns)
    name_patterns = [
        r"Наименование[:\s]+([^\n]+)",
        r"Название[:\s]+([^\n]+)",
        r"наименование водоема[:\s]+([^\n]+)",
        r"Паспорт[:\s]+([^\n]+)",
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            metadata["name"] = match.group(1).strip()
            break
    
    if not metadata.get("name"):
        # Use filename as fallback
        metadata["name"] = f"Водный объект {filename[:8]}"
    
    # Extract region/oblast
    region_patterns = [
        r"Облость[:\s]+([^\n]+)",
        r"Область[:\s]+([^\n]+)",
        r"Административная область[:\s]+([^\n]+)",
        r"область[:\s]+([А-Яа-яёЁ\s-]+область)",
    ]
    
    for pattern in region_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            region = match.group(1).strip()
            # Clean up common formatting
            region = re.sub(r'_+', ' ', region)
            region = re.sub(r'\s+', ' ', region)
            metadata["region"] = region
            break
    
    if not metadata.get("region"):
        metadata["region"] = "Неизвестная область"
    
    # Extract resource type
    resource_type_map = {
        "озеро": ResourceType.lake,
        "река": ResourceType.river,
        "канал": ResourceType.canal,
        "водохранилище": ResourceType.reservoir,
        "гидроузел": ResourceType.other,
        "шлюз": ResourceType.other,
    }
    
    type_pattern = r"Тип водного ресурса[:\s]+([^\n]+)"
    match = re.search(type_pattern, text, re.IGNORECASE)
    if match:
        type_text = match.group(1).strip().lower()
        for keyword, rtype in resource_type_map.items():
            if keyword in type_text:
                metadata["resource_type"] = rtype
                break
    
    if not metadata.get("resource_type"):
        metadata["resource_type"] = ResourceType.lake  # Default
    
    # Extract water type
    water_type_pattern = r"Тип воды[:\s]+([^\n]+)"
    match = re.search(water_type_pattern, text, re.IGNORECASE)
    if match:
        water_text = match.group(1).strip().lower()
        if "непресная" in water_text or "соленая" in water_text:
            metadata["water_type"] = WaterType.non_fresh
        elif "пресная" in water_text:
            metadata["water_type"] = WaterType.fresh
        elif "нет" not in water_text:
            metadata["water_type"] = WaterType.fresh  # Default to fresh
    
    # Extract fauna
    fauna_pattern = r"Наличие фауны[:\s]+([^\n]+)"
    match = re.search(fauna_pattern, text, re.IGNORECASE)
    if match:
        fauna_text = match.group(1).strip().lower()
        if "да" in fauna_text or "есть" in fauna_text:
            metadata["fauna"] = FaunaType.fish_bearing
        elif "нет" in fauna_text:
            metadata["fauna"] = FaunaType.non_fish_bearing
    
    # Extract passport date
    date_patterns = [
        r"Дата паспорта[:\s]+(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})",
        r"дата[:\s]+(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})",
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            date_str = match.group(1)
            # Parse various date formats
            for fmt in ["%d.%m.%Y", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%y"]:
                try:
                    metadata["passport_date"] = datetime.strptime(date_str, fmt)
                    break
                except:
                    continue
            break
    
    # Extract technical condition
    condition_pattern = r"Техническое состояние[:\s]+\(?(\d)[)\s]?"
    match = re.search(condition_pattern, text, re.IGNORECASE)
    if match:
        condition = int(match.group(1))
        if 1 <= condition <= 5:
            metadata["technical_condition"] = condition
    
    if not metadata.get("technical_condition"):
        metadata["technical_condition"] = 3  # Default
    
    # Extract coordinates
    coord_patterns = [
        r"Координаты[:\s]+([^\n]+)",
        r"координат[ыа][:\s]+([^\n]+)",
        r"N\s*(\d+)º(\d+)[′'].*E\s*(\d+)º(\d+)[′']",
        r"центр[:\s]+N\s*(\d+)º(\d+)[′'].*E\s*(\d+)º(\d+)[′']",
    ]
    
    for pattern in coord_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if len(match.groups()) == 4:  # Degrees and minutes format
                lat_deg, lat_min, lon_deg, lon_min = match.groups()
                metadata["latitude"] = float(lat_deg) + float(lat_min) / 60
                metadata["longitude"] = float(lon_deg) + float(lon_min) / 60
                break
            else:
                # Try to parse from text
                coord_text = match.group(1)
                # Look for N/S and E/W coordinates
                lat_match = re.search(r"N\s*(\d+)º(\d+)", coord_text)
                lon_match = re.search(r"E\s*(\d+)º(\d+)", coord_text)
                if lat_match and lon_match:
                    lat_deg, lat_min = lat_match.groups()
                    lon_deg, lon_min = lon_match.groups()
                    metadata["latitude"] = float(lat_deg) + float(lat_min) / 60
                    metadata["longitude"] = float(lon_deg) + float(lon_min) / 60
                    break
    
    return metadata if metadata.get("name") else None


def extract_passport_sections(text: str) -> Dict[str, str]:
    """
    Extract structured sections from passport text.
    
    Args:
        text: Full passport text
        
    Returns:
        Dictionary with section names and content
    """
    sections = {}
    
    # Section patterns
    section_patterns = {
        "general_info": [
            r"1\.\s*Географическое расположение(.*?)(?=\d\.|$)",
            r"Административная область(.*?)(?=\d\.\s*[А-Я]|$)",
        ],
        "technical_params": [
            r"2\.\s*Физическая характеристика(.*?)(?=\d\.|$)",
            r"Длина[,\s]+м(.*?)(?=\d\.\s*[А-Я]|$)",
        ],
        "ecological_state": [
            r"3\.\s*Биологическая характеристика(.*?)(?=\d\.|$)",
            r"Степень зарастания(.*?)(?=\d\.\s*[А-Я]|$)",
        ],
        "recommendations": [
            r"Рекомендации(.*?)(?=\d\.\s*[А-Я]|$)",
            r"Рыбопродуктивность(.*?)$",
        ],
    }
    
    for section_name, patterns in section_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                content = match.group(1).strip()
                # Clean up multiple spaces and underscores
                content = re.sub(r'_+', ' ', content)
                content = re.sub(r'\s+', ' ', content)
                sections[section_name] = content
                break
    
    return sections


def seed_passport_from_pdf(db, pdf_path: Path, dry_run: bool = False) -> bool:
    """
    Extract and seed passport data from single PDF file.
    
    Args:
        db: Database session
        pdf_path: Path to PDF file
        dry_run: If True, parse but don't insert
        
    Returns:
        True if successfully seeded, False otherwise
    """
    print(f"\n📄 Processing {pdf_path.name}...")
    
    # Extract text
    text = extract_text_from_pdf(pdf_path)
    if not text or len(text) < 100:
        print(f"  ✗ Insufficient text extracted ({len(text)} chars)")
        return False
    
    print(f"  ✓ Extracted {len(text)} characters")
    
    # Parse metadata
    metadata = parse_passport_metadata(text, pdf_path.name)
    if not metadata:
        print(f"  ✗ Failed to parse metadata")
        return False
    
    print(f"  ✓ Parsed metadata: {metadata['name']} ({metadata['region']})")
    
    if dry_run:
        print(f"  ⊙ Dry run - skipping database insertion")
        return True
    
    # Check if water object already exists
    existing_obj = db.query(WaterObject).filter(
        WaterObject.name == metadata["name"],
        WaterObject.region == metadata["region"]
    ).first()
    
    if existing_obj:
        water_obj = existing_obj
        print(f"  ⊙ Water object already exists (ID: {water_obj.id})")
    else:
        # Create water object
        water_obj = WaterObject(
            name=metadata["name"],
            region=metadata["region"],
            resource_type=metadata["resource_type"],
            water_type=metadata.get("water_type"),
            fauna=metadata.get("fauna"),
            passport_date=metadata.get("passport_date"),
            technical_condition=metadata["technical_condition"],
            latitude=metadata.get("latitude"),
            longitude=metadata.get("longitude"),
            pdf_url=f"/passports/{pdf_path.name}",
            priority=0,
            priority_level=PriorityLevel.low
        )
        water_obj.update_priority()
        
        db.add(water_obj)
        db.flush()  # Get ID without committing
        print(f"  ✓ Created water object (ID: {water_obj.id}, Priority: {water_obj.priority})")
    
    # Check if passport text already exists
    existing_passport = db.query(PassportText).filter(
        PassportText.water_object_id == water_obj.id
    ).first()
    
    if existing_passport:
        print(f"  ⊙ Passport text already exists (ID: {existing_passport.id})")
        return True
    
    # Extract sections
    sections = extract_passport_sections(text)
    
    # Create passport text
    passport = PassportText(
        water_object_id=water_obj.id,
        document_title=f"Паспорт: {metadata['name']}",
        document_date=metadata.get("passport_date"),
        full_text=text,
        general_info=sections.get("general_info"),
        technical_params=sections.get("technical_params"),
        ecological_state=sections.get("ecological_state"),
        recommendations=sections.get("recommendations")
    )
    
    db.add(passport)
    print(f"  ✓ Created passport text")
    
    return True


def seed_all_passports(dry_run: bool = False) -> Dict[str, int]:
    """
    Seed all passport PDFs from uploads/passports directory.
    
    Args:
        dry_run: If True, parse but don't insert into database
        
    Returns:
        Dictionary with statistics
    """
    print("=" * 70)
    print("Seeding All Passport PDFs")
    print("=" * 70)
    print(f"Directory: {PASSPORT_DIR}")
    print(f"Dry run: {dry_run}")
    
    if not PASSPORT_DIR.exists():
        print(f"\n✗ Directory not found: {PASSPORT_DIR}")
        return {"total": 0, "processed": 0, "failed": 0}
    
    # Get all PDF files
    pdf_files = list(PASSPORT_DIR.glob("*.pdf"))
    print(f"\nFound {len(pdf_files)} PDF files")
    
    if not pdf_files:
        print("✗ No PDF files found")
        return {"total": 0, "processed": 0, "failed": 0}
    
    stats = {
        "total": len(pdf_files),
        "processed": 0,
        "failed": 0,
    }
    
    db = SessionLocal()
    
    try:
        for pdf_path in pdf_files:
            try:
                if seed_passport_from_pdf(db, pdf_path, dry_run):
                    stats["processed"] += 1
                    if not dry_run:
                        db.commit()  # Commit after each successful PDF
                else:
                    stats["failed"] += 1
            except Exception as e:
                print(f"  ✗ Error processing {pdf_path.name}: {e}")
                stats["failed"] += 1
                db.rollback()
                continue
        
        print(f"\n{'=' * 70}")
        print(f"Processing Complete")
        print(f"{'=' * 70}")
        print(f"Total PDFs: {stats['total']}")
        print(f"Successfully processed: {stats['processed']}")
        print(f"Failed: {stats['failed']}")
        print(f"{'=' * 70}")
        
        return stats
        
    finally:
        db.close()


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed all passport PDFs from uploads directory")
    parser.add_argument("--dry-run", action="store_true", help="Parse PDFs but don't insert into database")
    
    args = parser.parse_args()
    
    try:
        stats = seed_all_passports(dry_run=args.dry_run)
        success_rate = (stats["processed"] / stats["total"] * 100) if stats["total"] > 0 else 0
        print(f"\nSuccess rate: {success_rate:.1f}%")
        
        if not args.dry_run:
            print("\n⚠️  Don't forget to rebuild the vector store:")
            print("   python rag_agent/scripts/rebuild_vector_store.py")
        
        sys.exit(0 if stats["failed"] == 0 else 1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
