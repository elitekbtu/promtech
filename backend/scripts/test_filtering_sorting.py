#!/usr/bin/env python3
"""
Test Script: Filtering, Sorting, and Pagination

Tests various combinations of filtering, sorting, and pagination
on the /api/objects endpoint.
"""

import requests
import sys
import json


BASE_URL = "http://localhost:8000"


def test_filtering_sorting_pagination():
    """Test filtering, sorting, and pagination."""
    print("=" * 80)
    print("FILTERING, SORTING, AND PAGINATION TEST")
    print("=" * 80)
    print()
    
    # Get auth token
    auth_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": "beknur@beknur.com", "password": "beknur"}
    )
    
    if auth_response.status_code != 200:
        print("❌ Failed to authenticate")
        return False
    
    token = auth_response.json().get("access_token", "")
    headers = {"Authorization": f"Bearer {token}"}
    
    test_results = []
    
    # Test 1: Basic pagination
    print("📄 Test 1: Basic Pagination")
    test_cases = [
        {"limit": 5, "offset": 0, "desc": "First page (5 items)"},
        {"limit": 5, "offset": 5, "desc": "Second page (5 items)"},
        {"limit": 10, "offset": 0, "desc": "First page (10 items)"},
    ]
    
    for test in test_cases:
        response = requests.get(
            f"{BASE_URL}/api/objects",
            params={"limit": test["limit"], "offset": test["offset"]},
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            items_count = len(data.get("items", []))
            expected_items = min(test["limit"], data.get("total", 0) - test["offset"])
            passed = items_count <= test["limit"]
            
            status = "✅" if passed else "❌"
            print(f"  {status} {test['desc']}: Got {items_count} items (limit={test['limit']}, offset={test['offset']})")
            test_results.append(passed)
        else:
            print(f"  ❌ {test['desc']}: HTTP {response.status_code}")
            test_results.append(False)
    
    # Test 2: Filtering by region
    print("\n🗺️  Test 2: Filtering by Region")
    regions_response = requests.get(f"{BASE_URL}/api/objects?limit=100", headers=headers)
    if regions_response.status_code == 200:
        all_objects = regions_response.json().get("items", [])
        unique_regions = list(set(obj["region"] for obj in all_objects if obj.get("region")))
        
        if unique_regions:
            test_region = unique_regions[0]
            filtered_response = requests.get(
                f"{BASE_URL}/api/objects",
                params={"region": test_region},
                headers=headers
            )
            
            if filtered_response.status_code == 200:
                filtered_items = filtered_response.json().get("items", [])
                all_match = all(item["region"] == test_region for item in filtered_items)
                
                status = "✅" if all_match else "❌"
                print(f"  {status} Filter by region '{test_region}': {len(filtered_items)} items, all match: {all_match}")
                test_results.append(all_match)
            else:
                print(f"  ❌ Filter by region failed: HTTP {filtered_response.status_code}")
                test_results.append(False)
        else:
            print("  ⚠️  No regions found to test filtering")
            test_results.append(True)
    else:
        print(f"  ❌ Failed to fetch objects: HTTP {regions_response.status_code}")
        test_results.append(False)
    
    # Test 3: Filtering by resource type
    print("\n🏞️  Test 3: Filtering by Resource Type")
    resource_types = ["озеро", "канал", "водохранилище"]
    
    for resource_type in resource_types:
        response = requests.get(
            f"{BASE_URL}/api/objects",
            params={"resource_type": resource_type},
            headers=headers
        )
        
        if response.status_code == 200:
            items = response.json().get("items", [])
            if items:
                all_match = all(item["resource_type"] == resource_type for item in items)
                status = "✅" if all_match else "❌"
                print(f"  {status} Filter by resource_type '{resource_type}': {len(items)} items, all match: {all_match}")
                test_results.append(all_match)
            else:
                print(f"  ℹ️  No objects with resource_type '{resource_type}'")
                test_results.append(True)
        else:
            print(f"  ❌ Filter failed: HTTP {response.status_code}")
            test_results.append(False)
    
    # Test 4: Sorting
    print("\n📊 Test 4: Sorting")
    sort_tests = [
        {"sort_by": "name", "order": "asc", "desc": "Sort by name (ascending)"},
        {"sort_by": "priority", "order": "desc", "desc": "Sort by priority (descending)"},
        {"sort_by": "passport_date", "order": "desc", "desc": "Sort by passport_date (descending)"},
    ]
    
    for test in sort_tests:
        response = requests.get(
            f"{BASE_URL}/api/objects",
            params={"sort_by": test["sort_by"], "order": test["order"], "limit": 10},
            headers=headers
        )
        
        if response.status_code == 200:
            items = response.json().get("items", [])
            
            if len(items) >= 2:
                # Check if sorted correctly
                values = [item.get(test["sort_by"]) for item in items if item.get(test["sort_by"]) is not None]
                
                if test["order"] == "asc":
                    is_sorted = all(values[i] <= values[i+1] for i in range(len(values)-1))
                else:
                    is_sorted = all(values[i] >= values[i+1] for i in range(len(values)-1))
                
                status = "✅" if is_sorted else "❌"
                print(f"  {status} {test['desc']}: {len(items)} items, correctly sorted: {is_sorted}")
                test_results.append(is_sorted)
            else:
                print(f"  ⚠️  {test['desc']}: Not enough items to verify sorting")
                test_results.append(True)
        else:
            print(f"  ❌ {test['desc']}: HTTP {response.status_code}")
            test_results.append(False)
    
    # Test 5: Combined filtering and sorting
    print("\n🔧 Test 5: Combined Filtering and Sorting")
    response = requests.get(
        f"{BASE_URL}/api/objects",
        params={
            "resource_type": "озеро",
            "sort_by": "priority",
            "order": "desc",
            "limit": 5
        },
        headers=headers
    )
    
    if response.status_code == 200:
        items = response.json().get("items", [])
        type_match = all(item["resource_type"] == "озеро" for item in items)
        
        if len(items) >= 2:
            priorities = [item["priority"] for item in items]
            sorted_correctly = all(priorities[i] >= priorities[i+1] for i in range(len(priorities)-1))
        else:
            sorted_correctly = True
        
        passed = type_match and sorted_correctly
        status = "✅" if passed else "❌"
        print(f"  {status} Filter озеро + Sort by priority desc: {len(items)} items, type match: {type_match}, sorted: {sorted_correctly}")
        test_results.append(passed)
    else:
        print(f"  ❌ Combined test failed: HTTP {response.status_code}")
        test_results.append(False)
    
    # Test 6: Pagination with filtering
    print("\n📑 Test 6: Pagination with Filtering")
    response = requests.get(
        f"{BASE_URL}/api/objects",
        params={
            "resource_type": "озеро",
            "limit": 3,
            "offset": 0
        },
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        items = data.get("items", [])
        total = data.get("total", 0)
        has_more = data.get("has_more", False)
        
        type_match = all(item["resource_type"] == "озеро" for item in items)
        pagination_correct = len(items) <= 3 and (has_more == (total > 3))
        
        passed = type_match and pagination_correct
        status = "✅" if passed else "❌"
        print(f"  {status} Filter озеро with pagination: {len(items)}/{total} items, has_more: {has_more}, correct: {passed}")
        test_results.append(passed)
    else:
        print(f"  ❌ Pagination with filtering failed: HTTP {response.status_code}")
        test_results.append(False)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All filtering/sorting/pagination tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False


if __name__ == "__main__":
    success = test_filtering_sorting_pagination()
    sys.exit(0 if success else 1)
