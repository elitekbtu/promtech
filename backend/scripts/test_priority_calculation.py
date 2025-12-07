#!/usr/bin/env python3
"""
Test Script: Priority Calculation Edge Cases

Tests the priority calculation formula with various edge cases:
- Priority = (6 - technical_condition) * 3 + passport_age_years
- Priority Level: high (>=10), medium (6-9), low (<=5)
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.water_object import WaterObject, ResourceType, WaterType, FaunaType, PriorityLevel


def test_priority_calculation():
    """Test priority calculation with edge cases."""
    print("=" * 80)
    print("PRIORITY CALCULATION EDGE CASES TEST")
    print("=" * 80)
    print("\nFormula: priority = (6 - technical_condition) * 3 + passport_age_years")
    print("Priority Levels: high (>=10), medium (6-9), low (<=5)\n")
    
    db = SessionLocal()
    
    test_cases = [
        {
            "name": "Тест 1: Минимальный приоритет",
            "technical_condition": 5,  # Best condition
            "passport_date": datetime.now() - timedelta(days=365*2),  # 2 years old
            "expected_priority": 5,  # (6-5)*3 + 2 = 5
            "expected_level": PriorityLevel.low
        },
        {
            "name": "Тест 2: Максимальный приоритет (старый объект, плохое состояние)",
            "technical_condition": 1,  # Worst condition
            "passport_date": datetime(1950, 1, 1),  # ~75 years old
            "expected_priority": None,  # (6-1)*3 + 75 = 90
            "expected_level": PriorityLevel.high
        },
        {
            "name": "Тест 3: Граница high/medium (приоритет 10)",
            "technical_condition": 3,
            "passport_date": datetime.now() - timedelta(days=365*1),  # 1 year old
            "expected_priority": 10,  # (6-3)*3 + 1 = 10
            "expected_level": PriorityLevel.high
        },
        {
            "name": "Тест 4: Граница medium/low (приоритет 6)",
            "technical_condition": 4,
            "passport_date": datetime.now(),  # Fresh passport
            "expected_priority": 6,  # (6-4)*3 + 0 = 6
            "expected_level": PriorityLevel.medium
        },
        {
            "name": "Тест 5: Граница medium/low (приоритет 5)",
            "technical_condition": 5,
            "passport_date": datetime.now() - timedelta(days=365*2),  # 2 years old
            "expected_priority": 5,  # (6-5)*3 + 2 = 5
            "expected_level": PriorityLevel.low
        },
        {
            "name": "Тест 6: Очень старый паспорт, среднее состояние",
            "technical_condition": 3,
            "passport_date": datetime(1960, 1, 1),  # ~65 years old
            "expected_priority": None,  # (6-3)*3 + 65 = 74
            "expected_level": PriorityLevel.high
        },
        {
            "name": "Тест 7: Новый паспорт, плохое состояние",
            "technical_condition": 2,
            "passport_date": datetime.now() - timedelta(days=180),  # 0 years
            "expected_priority": 12,  # (6-2)*3 + 0 = 12
            "expected_level": PriorityLevel.high
        },
        {
            "name": "Тест 8: Идеальное состояние, свежий паспорт",
            "technical_condition": 5,
            "passport_date": datetime.now() - timedelta(days=30),  # 0 years
            "expected_priority": 3,  # (6-5)*3 + 0 = 3
            "expected_level": PriorityLevel.low
        },
    ]
    
    try:
        print(f"{'Тест':<50} {'Расчет':<25} {'Ожид.':<7} {'Факт.':<7} {'Уровень':<10} {'Статус'}")
        print("-" * 120)
        
        passed = 0
        failed = 0
        
        for i, test in enumerate(test_cases, 1):
            # Create test object
            obj = WaterObject(
                name=f"Тестовый объект {i}",
                region="Тестовая область",
                resource_type=ResourceType.lake,
                water_type=WaterType.fresh,
                technical_condition=test["technical_condition"],
                passport_date=test["passport_date"],
                latitude=45.0,
                longitude=75.0
            )
            
            # Calculate priority
            obj.update_priority()
            
            # Calculate expected
            age_years = (datetime.now() - test["passport_date"]).days // 365
            calculated = (6 - test["technical_condition"]) * 3 + age_years
            
            # Verify
            if test["expected_priority"]:
                priority_match = obj.priority == test["expected_priority"]
            else:
                priority_match = True  # Skip exact match for very old objects
            
            level_match = obj.priority_level == test["expected_level"]
            
            status = "✅ PASS" if (priority_match and level_match) else "❌ FAIL"
            
            if priority_match and level_match:
                passed += 1
            else:
                failed += 1
            
            calc_str = f"(6-{test['technical_condition']})*3+{age_years}"
            print(f"{test['name']:<50} {calc_str:<25} {calculated:<7} {obj.priority:<7} {obj.priority_level.value:<10} {status}")
        
        print("-" * 120)
        print(f"\n📊 Результаты: {passed} пройдено, {failed} провалено")
        
        if failed == 0:
            print("✅ Все тесты пройдены успешно!")
            return True
        else:
            print("❌ Некоторые тесты провалились")
            return False
            
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = test_priority_calculation()
    sys.exit(0 if success else 1)
