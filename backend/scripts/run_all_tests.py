#!/usr/bin/env python3
"""
Master Test Runner for Phase 11

Runs all validation tests for the GidroAtlas water management system.
"""

import subprocess
import sys


def run_test(test_name, command, description):
    """Run a single test and return result."""
    print(f"\n{'=' * 80}")
    print(f"Running: {test_name}")
    print(f"Description: {description}")
    print('=' * 80)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=False,
            text=True
        )
        
        success = result.returncode == 0
        return success, test_name
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return False, test_name


def main():
    """Run all Phase 11 tests."""
    print("=" * 80)
    print("GIDROATLAS - PHASE 11: TESTING & VALIDATION")
    print("=" * 80)
    
    tests = [
        {
            "name": "11.2 Priority Calculation Edge Cases",
            "command": "docker exec promtech-backend-1 python scripts/test_priority_calculation.py",
            "description": "Test priority formula with various conditions and ages"
        },
        {
            "name": "11.8 OpenAPI Documentation",
            "command": "curl -s http://localhost:8000/docs | grep -q 'GidroAtlas API'",
            "description": "Verify /docs endpoint is accessible"
        },
    ]
    
    results = []
    
    for test in tests:
        success, name = run_test(test["name"], test["command"], test["description"])
        results.append((name, success))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
    
    print(f"\n📊 Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed successfully!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
