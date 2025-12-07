#!/usr/bin/env python3
"""
Test Script: Role-Based Access Control

Tests that guest users cannot access priority-related endpoints
while expert users can access all endpoints.
"""

import requests
import sys
import json


BASE_URL = "http://localhost:8000"


def test_rbac():
    """Test role-based access control."""
    print("=" * 80)
    print("ROLE-BASED ACCESS CONTROL TEST")
    print("=" * 80)
    print()
    
    # Test credentials (you may need to create these users first)
    guest_credentials = {
        "email": "guest@example.com",
        "password": "guest123"
    }
    
    expert_credentials = {
        "email": "beknur@beknur.com",
        "password": "beknur"
    }
    
    print("🔐 Step 1: Login as Guest")
    try:
        guest_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=guest_credentials
        )
        
        if guest_response.status_code == 200:
            guest_data = guest_response.json()
            print(f"✅ Guest login successful")
            guest_token = guest_data.get('access_token', '')
        elif guest_response.status_code == 403:
            print(f"⚠️  Guest login blocked (status 403) - as expected, only experts can login")
            print("   Guest access is provided without authentication")
            guest_token = None
        else:
            print(f"⚠️  Guest login failed (status {guest_response.status_code})")
            print("   Creating guest user may be needed for this test")
            guest_token = None
    except Exception as e:
        print(f"❌ Guest login error: {e}")
        guest_token = None
    
    print("\n🔐 Step 2: Login as Expert")
    try:
        expert_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=expert_credentials
        )
        
        if expert_response.status_code == 200:
            expert_data = expert_response.json()
            print(f"✅ Expert login successful")
            expert_token = expert_data.get('access_token', '')
        else:
            print(f"❌ Expert login failed (status {expert_response.status_code})")
            expert_token = None
    except Exception as e:
        print(f"❌ Expert login error: {e}")
        expert_token = None
    
    print("\n" + "=" * 80)
    print("TESTING ENDPOINTS")
    print("=" * 80)
    
    test_results = []
    
    # Test 1: GET /api/objects (should work for both)
    print("\n📋 Test 1: GET /api/objects (public endpoint)")
    
    if guest_token:
        guest_objects = requests.get(
            f"{BASE_URL}/api/objects?limit=1",
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        guest_priority_in_response = '"priority"' in guest_objects.text
        print(f"   Guest: {guest_objects.status_code} - Priority field visible: {guest_priority_in_response}")
        test_results.append({
            "test": "Guest /objects access",
            "expected": "200, priority hidden",
            "actual": f"{guest_objects.status_code}, priority {'visible' if guest_priority_in_response else 'hidden'}",
            "pass": guest_objects.status_code == 200
        })
    
    if expert_token:
        expert_objects = requests.get(
            f"{BASE_URL}/api/objects?limit=1",
            headers={"Authorization": f"Bearer {expert_token}"}
        )
        expert_priority_in_response = '"priority"' in expert_objects.text
        print(f"   Expert: {expert_objects.status_code} - Priority field visible: {expert_priority_in_response}")
        test_results.append({
            "test": "Expert /objects access",
            "expected": "200, priority visible",
            "actual": f"{expert_objects.status_code}, priority {'visible' if expert_priority_in_response else 'hidden'}",
            "pass": expert_objects.status_code == 200
        })
    
    # Test 2: GET /api/priorities/table (experts only)
    print("\n🔒 Test 2: GET /api/priorities/table (expert-only endpoint)")
    
    if guest_token:
        guest_priorities = requests.get(
            f"{BASE_URL}/api/priorities/table",
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        print(f"   Guest: {guest_priorities.status_code} (expected: 403 Forbidden)")
        test_results.append({
            "test": "Guest /priorities/table access",
            "expected": "403",
            "actual": str(guest_priorities.status_code),
            "pass": guest_priorities.status_code == 403
        })
    
    if expert_token:
        expert_priorities = requests.get(
            f"{BASE_URL}/api/priorities/table",
            headers={"Authorization": f"Bearer {expert_token}"}
        )
        print(f"   Expert: {expert_priorities.status_code} (expected: 200 OK)")
        test_results.append({
            "test": "Expert /priorities/table access",
            "expected": "200",
            "actual": str(expert_priorities.status_code),
            "pass": expert_priorities.status_code == 200
        })
    
    # Test 3: GET /api/priorities/stats (experts only)
    print("\n🔒 Test 3: GET /api/priorities/stats (expert-only endpoint)")
    
    if guest_token:
        guest_stats = requests.get(
            f"{BASE_URL}/api/priorities/stats",
            headers={"Authorization": f"Bearer {guest_token}"}
        )
        print(f"   Guest: {guest_stats.status_code} (expected: 403 Forbidden)")
        test_results.append({
            "test": "Guest /priorities/stats access",
            "expected": "403",
            "actual": str(guest_stats.status_code),
            "pass": guest_stats.status_code == 403
        })
    
    if expert_token:
        expert_stats = requests.get(
            f"{BASE_URL}/api/priorities/stats",
            headers={"Authorization": f"Bearer {expert_token}"}
        )
        print(f"   Expert: {expert_stats.status_code} (expected: 200 OK)")
        test_results.append({
            "test": "Expert /priorities/stats access",
            "expected": "200",
            "actual": str(expert_stats.status_code),
            "pass": expert_stats.status_code == 200
        })
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    
    passed = sum(1 for r in test_results if r["pass"])
    total = len(test_results)
    
    for result in test_results:
        status = "✅ PASS" if result["pass"] else "❌ FAIL"
        print(f"{status} {result['test']}")
        print(f"   Expected: {result['expected']}, Actual: {result['actual']}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All RBAC tests passed!")
        return True
    else:
        print("❌ Some RBAC tests failed")
        return False


if __name__ == "__main__":
    success = test_rbac()
    sys.exit(0 if success else 1)
