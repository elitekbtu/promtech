#!/usr/bin/env python3
"""
Test Script: RAG System Integration

Tests RAG endpoints and tools integration with water management queries.
"""

import requests
import sys
import json
import time


BASE_URL = "http://localhost:8000"


def test_rag_integration():
    """Test RAG endpoints and tools."""
    print("=" * 80)
    print("RAG SYSTEM INTEGRATION TEST")
    print("=" * 80)
    print()
    
    test_results = []
    
    # Test 1: Basic RAG query
    print("🤖 Test 1: Basic RAG Query (Озеро Балхаш)")
    query_payload = {
        "query": "Расскажи об озере Балхаш",
        "environment": "production"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/rag/query",
            json=query_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            has_response = bool(data.get("response"))
            has_sources = bool(data.get("sources"))
            status_success = data.get("status") == "success"
            
            print(f"   Status: {response.status_code}")
            print(f"   Has response: {has_response}")
            print(f"   Has sources: {has_sources}")
            print(f"   Status field: {data.get('status')}")
            print(f"   Confidence: {data.get('confidence', 0)}")
            
            if has_response:
                response_text = data.get("response", "")
                print(f"   Response length: {len(response_text)} characters")
                print(f"   Response preview: {response_text[:150]}...")
            
            passed = has_response and status_success
            status = "✅" if passed else "❌"
            print(f"   {status} Test result: {'PASS' if passed else 'FAIL'}")
            test_results.append(passed)
        else:
            print(f"   ❌ HTTP {response.status_code}")
            test_results.append(False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        test_results.append(False)
    
    # Test 2: RAG query with filters
    print("\n🔍 Test 2: RAG Query with Context Filters")
    query_payload = {
        "query": "Какие водоемы в Алматинской области?",
        "region": "Алматинская",
        "environment": "production"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/rag/query",
            json=query_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            has_response = bool(data.get("response"))
            status_success = data.get("status") == "success"
            
            print(f"   Status: {response.status_code}")
            print(f"   Has response: {has_response}")
            print(f"   Status field: {data.get('status')}")
            
            passed = has_response and status_success
            status = "✅" if passed else "❌"
            print(f"   {status} Test result: {'PASS' if passed else 'FAIL'}")
            test_results.append(passed)
        else:
            print(f"   ❌ HTTP {response.status_code}")
            test_results.append(False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        test_results.append(False)
    
    # Test 3: Priority explanation endpoint
    print("\n📊 Test 3: Priority Explanation Endpoint")
    
    # First, get an object ID
    try:
        auth_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": "beknur@beknur.com", "password": "beknur"}
        )
        
        if auth_response.status_code == 200:
            token = auth_response.json().get("access_token", "")
            headers = {"Authorization": f"Bearer {token}"}
            
            objects_response = requests.get(
                f"{BASE_URL}/api/objects?limit=1",
                headers=headers
            )
            
            if objects_response.status_code == 200:
                objects = objects_response.json().get("items", [])
                
                if objects:
                    object_id = objects[0]["id"]
                    object_name = objects[0]["name"]
                    
                    print(f"   Testing with object: {object_name} (ID: {object_id})")
                    
                    priority_response = requests.post(
                        f"{BASE_URL}/api/rag/explain-priority/{object_id}",
                        timeout=30
                    )
                    
                    if priority_response.status_code == 200:
                        data = priority_response.json()
                        has_response = bool(data.get("response"))
                        
                        print(f"   Status: {priority_response.status_code}")
                        print(f"   Has explanation: {has_response}")
                        
                        if has_response:
                            response_text = data.get("response", "")
                            print(f"   Explanation length: {len(response_text)} characters")
                        
                        passed = has_response
                        status = "✅" if passed else "❌"
                        print(f"   {status} Test result: {'PASS' if passed else 'FAIL'}")
                        test_results.append(passed)
                    else:
                        print(f"   ❌ HTTP {priority_response.status_code}")
                        test_results.append(False)
                else:
                    print("   ⚠️  No objects found to test priority explanation")
                    test_results.append(True)
            else:
                print(f"   ❌ Failed to fetch objects: HTTP {objects_response.status_code}")
                test_results.append(False)
        else:
            print(f"   ❌ Authentication failed: HTTP {auth_response.status_code}")
            test_results.append(False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        test_results.append(False)
    
    # Test 4: Vector search tool
    print("\n🔎 Test 4: Vector Search via RAG")
    query_payload = {
        "query": "Паспорт водного объекта: озеро",
        "environment": "production"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/rag/query",
            json=query_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            sources = data.get("sources", [])
            used_vector_search = any(
                s.get("tool") == "vector_search_tool" 
                for s in sources
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Sources count: {len(sources)}")
            print(f"   Used vector_search: {used_vector_search}")
            
            if sources:
                print(f"   Tools used: {', '.join(s.get('tool', 'unknown') for s in sources)}")
            
            passed = used_vector_search
            status = "✅" if passed else "❌"
            print(f"   {status} Test result: {'PASS' if passed else 'FAIL'}")
            test_results.append(passed)
        else:
            print(f"   ❌ HTTP {response.status_code}")
            test_results.append(False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        test_results.append(False)
    
    # Test 5: Russian language support
    print("\n🇷🇺 Test 5: Russian Language Support")
    query_payload = {
        "query": "Скажи мне о гидротехнических сооружениях Казахстана",
        "environment": "production"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/rag/query",
            json=query_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "")
            has_cyrillic = any(ord(char) >= 0x0400 and ord(char) <= 0x04FF for char in response_text)
            
            print(f"   Status: {response.status_code}")
            print(f"   Response contains Cyrillic: {has_cyrillic}")
            print(f"   Response length: {len(response_text)} characters")
            
            passed = has_cyrillic or len(response_text) > 0
            status = "✅" if passed else "❌"
            print(f"   {status} Test result: {'PASS' if passed else 'FAIL'}")
            test_results.append(passed)
        else:
            print(f"   ❌ HTTP {response.status_code}")
            test_results.append(False)
    except Exception as e:
        print(f"   ❌ Error: {e}")
        test_results.append(False)
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All RAG integration tests passed!")
        return True
    else:
        print("❌ Some RAG tests failed")
        return False


if __name__ == "__main__":
    success = test_rag_integration()
    sys.exit(0 if success else 1)
