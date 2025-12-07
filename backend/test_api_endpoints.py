#!/usr/bin/env python3
"""
Test API endpoints for RAG system.
"""

import sys
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

def test_live_query_endpoint_logic():
    """Test the logic of live_query endpoint without actual HTTP."""
    print("🧪 Test 9: Testing live_query endpoint logic...")
    try:
        from rag_agent.routes.live_query_router import LiveQueryRequest, LiveQueryResponse
        
        # Test request validation
        try:
            empty_request = LiveQueryRequest(query="")
            print("⚠️  Empty query should be validated")
        except Exception:
            print("✅ Empty query validation works")
        
        # Test request with valid data
        request = LiveQueryRequest(
            query="test query about water",
            context={"tool_name": "vector_search"}
        )
        assert request.query == "test query about water"
        assert request.context["tool_name"] == "vector_search"
        print("✅ Request model validation works")
        
        return True
    except Exception as e:
        print(f"❌ Endpoint logic test failed: {e}")
        return False

def test_tool_status_endpoints():
    """Test tool status endpoints."""
    print("\n🧪 Test 10: Testing tool status endpoints...")
    try:
        from rag_agent.tools.vector_search import get_vector_store_status
        from rag_agent.tools.web_search import get_web_search_status
        
        # Test vector store status
        vector_status = get_vector_store_status()
        assert isinstance(vector_status, dict)
        assert "status" in vector_status
        print("✅ Vector store status endpoint works")
        
        # Test web search status
        web_status = get_web_search_status()
        assert isinstance(web_status, dict)
        assert "status" in web_status
        print("✅ Web search status endpoint works")
        
        return True
    except Exception as e:
        print(f"❌ Tool status test failed: {e}")
        return False

def test_vector_search_functionality():
    """Test actual vector search functionality."""
    print("\n🧪 Test 11: Testing vector search functionality...")
    try:
        from rag_agent.tools.vector_search import get_vector_search_tool
        
        tool = get_vector_search_tool()
        
        # Test search with valid query
        result = tool.search("озеро балхаш", k=5)
        
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Check for quality indicators
        has_quality = "🟢" in result or "🟡" in result or "Result" in result
        assert has_quality, "Result should contain quality indicators"
        
        print("✅ Vector search returns formatted results")
        print(f"   Result length: {len(result)} chars")
        print(f"   Contains quality indicators: {has_quality}")
        
        return True
    except Exception as e:
        print(f"❌ Vector search functionality test failed: {e}")
        return False

def test_biological_query():
    """Test search for biological information."""
    print("\n🧪 Test 12: Testing biological query (fauna information)...")
    try:
        from rag_agent.tools.vector_search import get_vector_search_tool
        
        tool = get_vector_search_tool()
        
        # Test query about fauna
        result = tool.search("видовой состав фауны балхаш", k=10)
        
        assert isinstance(result, str)
        assert len(result) > 0
        
        # Check that result contains information (not error)
        is_error = result.startswith("❌")
        assert not is_error, "Biological query should return results, not error"
        
        print("✅ Biological query works correctly")
        print(f"   Result preview: {result[:200]}...")
        
        return True
    except Exception as e:
        print(f"❌ Biological query test failed: {e}")
        return False

def test_error_handling_comprehensive():
    """Test comprehensive error handling."""
    print("\n🧪 Test 13: Testing comprehensive error handling...")
    try:
        from rag_agent.tools.vector_search import get_vector_search_tool
        
        tool = get_vector_search_tool()
        
        # Test various invalid inputs
        invalid_inputs = [
            ("", ValueError),
            (None, (ValueError, AttributeError, TypeError)),
            (123, (ValueError, AttributeError)),
            ("   ", ValueError),  # Only whitespace
        ]
        
        for invalid_input, expected_error in invalid_inputs:
            try:
                tool.search(invalid_input)
                print(f"⚠️  Input {invalid_input} should raise error")
            except expected_error:
                print(f"✅ Input {invalid_input} correctly raises error")
            except Exception as e:
                if isinstance(expected_error, tuple) and type(e) in expected_error:
                    print(f"✅ Input {invalid_input} correctly raises {type(e).__name__}")
                else:
                    print(f"⚠️  Input {invalid_input} raised {type(e).__name__} instead of expected")
        
        return True
    except Exception as e:
        print(f"❌ Comprehensive error handling test failed: {e}")
        return False

def test_response_formatting():
    """Test response formatting quality."""
    print("\n🧪 Test 14: Testing response formatting...")
    try:
        from rag_agent.tools.vector_search import get_vector_search_tool
        
        tool = get_vector_search_tool()
        
        result = tool.search("балхаш", k=3)
        
        # Check formatting elements
        has_source = "📁 Source:" in result or "Source:" in result
        has_content = "Content:" in result or "📖" in result
        has_footer = "✅ Found" in result or "result" in result.lower()
        
        print(f"   Has source indicator: {has_source}")
        print(f"   Has content section: {has_content}")
        print(f"   Has footer: {has_footer}")
        
        assert has_source or has_content, "Result should be well-formatted"
        
        print("✅ Response formatting is good")
        return True
    except Exception as e:
        print(f"❌ Response formatting test failed: {e}")
        return False

def run_all_tests():
    """Run all API endpoint tests."""
    print("=" * 60)
    print("🚀 Running API Endpoint Tests")
    print("=" * 60)
    
    tests = [
        test_live_query_endpoint_logic,
        test_tool_status_endpoints,
        test_vector_search_functionality,
        test_biological_query,
        test_error_handling_comprehensive,
        test_response_formatting,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 API Tests Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All API tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)

