#!/usr/bin/env python3
"""
Seed Passport Text Data

Seeds the database with sample passport text sections for reference water objects.
Uses actual passport data from hackathon documentation.

Usage:
    python seed_passport_texts.py
"""

import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.passport_text import PassportText
from models.water_object import WaterObject


# Passport data for Коскол
KOSKOL_PASSPORT = {
    "document_title": "Паспорт водного объекта: Озеро Коскол",
    "document_date": datetime(2023, 1, 15),
    "general_info": """Административная область: Улытауская область
Административный район: Улытауский район
Месторасположение водоема: 1,8 км З от села Коскол
Границы участка: центр N 49º31'21", E 67º03'11", север N 49º31'58", E 67º02'55", юг N 49º30'37" E 67º03'27", восток N 49º31'27", E 67º04'05", запад N 49º31'11", E 67º02'26"
""",
    "technical_params": """Длина, м: 2120
Ширина, м: 2500
Площадь, га: 221
Глубина максимальная, м: нет, высокая степень зарастаемости
Глубина средняя, м: -
Глубина минимальная, м: 0,5
""",
    "ecological_state": """Степень зарастания водоема:
- надводной растительностью: до 5 %, слабо
- подводной растительностью: до 10 %, слабо

Степень развития фитопланктона (цветение воды): сильно

Видовой состав фауны водоема:
- ихтиофауны: нет
- млекопитающих: нет
- беспозвоночных водных животных: Ceriodaphnia reticulate, Acanthocyclops lanquidoides
""",
    "recommendations": """Рыбопродуктивность водоема, кг/га:
- ихтиофауны: 50кг/га
- млекопитающих: нет
- беспозвоночных водных животных: 1,25г/м³

Рекомендуется мониторинг степени зарастания водоема и уровня цветения воды.
"""
}


# Passport data for Камыстыкол
KAMYSTYKOL_PASSPORT = {
    "document_title": "Паспорт водного объекта: Озеро Камыстыкол",
    "document_date": datetime(2023, 2, 20),
    "general_info": """Административная область: Улытауская область
Административный район: Улытауский район
Месторасположение водоема: 4,6 км Ю от села Коскол
Границы участка: центр N 49º34'09", E 67º04'25", север N 49º34'41", E 67º05'47", юг N 49º33'27" E 67º03'06", восток N 49º33'27", E 67º04'55", запад N 49º34'50", E 67º03'56"
""",
    "technical_params": """Длина, м: 4100
Ширина, м: 2200
Площадь, га: 658
Глубина максимальная, м: 3,5
Глубина средняя, м: 2,1
Глубина минимальная, м: 0,8

Тип водоема: озеро естественного происхождения
Питание водоема: атмосферные осадки, грунтовые воды
Уровенный режим: относительно стабильный с сезонными колебаниями до 0,5 м
Ледовый режим: замерзание в ноябре, вскрытие в апреле
""",
    "ecological_state": """Степень зарастания водоема:
- надводной растительностью: до 15 %, средне
- подводной растительностью: до 20 %, средне

Степень развития фитопланктона (цветение воды): средне

Видовой состав фауны водоема:
- ихтиофауны: карп, карась серебряный, плотва
- млекопитающих: ондатра
- беспозвоночных водных животных: Ceriodaphnia reticulata, Daphnia longispina, Acanthocyclops vernalis
""",
    "recommendations": """Рыбопродуктивность водоема, кг/га:
- ихтиофауны: 120 кг/га
- беспозвоночных водных животных: 2,5 г/м³

Рекомендуется:
1. Регулярный мониторинг качества воды
2. Контроль рыбных ресурсов
3. Поддержание экологического баланса водоема
"""
}


def get_water_object_by_name(db, name: str, region: str):
    """Find water object by name and region"""
    return db.query(WaterObject).filter(
        WaterObject.name == name,
        WaterObject.region == region
    ).first()


def seed_passport_for_object(db, object_id: int, passport_data: dict, object_name: str) -> bool:
    """
    Seed passport text for a water object.
    
    Args:
        db: Database session
        object_id: WaterObject ID
        passport_data: Dictionary with passport fields
        object_name: Name for logging
        
    Returns:
        True if seeded, False if already exists
    """
    # Check if passport already exists
    existing = db.query(PassportText).filter(
        PassportText.water_object_id == object_id
    ).first()
    
    if existing:
        print(f"  ⊘ Skipping {object_name} - passport already exists (ID: {existing.id})")
        return False
    
    # Build full_text from all sections
    full_text_parts = []
    if passport_data.get("general_info"):
        full_text_parts.append("=== ОБЩИЕ СВЕДЕНИЯ ===\n" + passport_data["general_info"])
    if passport_data.get("technical_params"):
        full_text_parts.append("=== ТЕХНИЧЕСКИЕ ПАРАМЕТРЫ ===\n" + passport_data["technical_params"])
    if passport_data.get("ecological_state"):
        full_text_parts.append("=== ЭКОЛОГИЧЕСКОЕ СОСТОЯНИЕ ===\n" + passport_data["ecological_state"])
    if passport_data.get("recommendations"):
        full_text_parts.append("=== РЕКОМЕНДАЦИИ ===\n" + passport_data["recommendations"])
    
    full_text = "\n\n".join(full_text_parts)
    
    # Create new passport
    passport = PassportText(
        water_object_id=object_id,
        document_title=passport_data.get("document_title"),
        document_date=passport_data.get("document_date"),
        full_text=full_text,
        general_info=passport_data.get("general_info"),
        technical_params=passport_data.get("technical_params"),
        ecological_state=passport_data.get("ecological_state"),
        recommendations=passport_data.get("recommendations")
    )
    
    db.add(passport)
    print(f"  ✓ Seeded passport for {object_name}")
    return True


def seed_passport_texts() -> int:
    """
    Seed passport text data for reference objects.
    
    Returns:
        Total number of passports seeded
    """
    print("=" * 70)
    print("Seeding Passport Text Data")
    print("=" * 70)
    
    db = SessionLocal()
    
    try:
        total_seeded = 0
        
        # Seed Коскол passport
        print("\n📄 Seeding passport for Коскол...")
        koskol = get_water_object_by_name(db, "Коскол", "Улытауская область")
        if not koskol:
            print("  ✗ Water object 'Коскол' not found. Run seed_reference_objects.py first.")
        else:
            if seed_passport_for_object(db, koskol.id, KOSKOL_PASSPORT, "Коскол"):
                total_seeded += 1
        
        # Seed Камыстыкол passport
        print("\n📄 Seeding passport for Камыстыкол...")
        kamystykol = get_water_object_by_name(db, "Камыстыкол", "Улытауская область")
        if not kamystykol:
            print("  ✗ Water object 'Камыстыкол' not found. Run seed_reference_objects.py first.")
        else:
            if seed_passport_for_object(db, kamystykol.id, KAMYSTYKOL_PASSPORT, "Камыстыкол"):
                total_seeded += 1
        
        # Commit all changes
        db.commit()
        
        print(f"\n{'=' * 70}")
        print(f"Total passports seeded: {total_seeded}")
        print(f"{'=' * 70}")
        
        return total_seeded
        
    except Exception as e:
        db.rollback()
        print(f"\n✗ Error seeding passport texts: {e}")
        import traceback
        traceback.print_exc()
        return 0
        
    finally:
        db.close()


def main():
    """CLI entry point"""
    try:
        count = seed_passport_texts()
        sys.exit(0 if count > 0 else 1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
