"""
Test script for RAG water management queries.

This script tests the RAG endpoint with various water-related queries
to verify proper integration with the vector store and water metadata handling.
"""

import sys
import os
from pathlib import Path
import requests
import json
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Test queries for water management scenarios
TEST_SCENARIOS = [
    {
        "name": "High Priority Lakes",
        "query": "покажи озера с высоким приоритетом",
        "filters": {
            "priority_level": "high",
            "resource_type": "lake"
        }
    },
    {
        "name": "Regional Water Bodies",
        "query": "каково состояние водоемов в Алматинской области",
        "filters": {
            "region": "Алматинская область"
        }
    },
    {
        "name": "Priority Explanation",
        "query": "объясни приоритет обследования водных объектов",
        "filters": {}
    },
    {
        "name": "Technical Condition",
        "query": "водные объекты в критическом техническом состоянии",
        "filters": {}
    },
    {
        "name": "Passport Information",
        "query": "какая информация содержится в паспортах водоемов",
        "filters": {}
    },
    {
        "name": "Water Resources Overview",
        "query": "обзор водных ресурсов Казахстана",
        "filters": {}
    }
]


def test_rag_query(base_url: str, scenario: Dict[str, Any]):
    """Test a single RAG query scenario."""
    logger.info(f"\n{'=' * 80}")
    logger.info(f"🧪 TESTING: {scenario['name']}")
    logger.info(f"{'=' * 80}")
    logger.info(f"Query: {scenario['query']}")
    
    if scenario['filters']:
        logger.info(f"Filters: {json.dumps(scenario['filters'], ensure_ascii=False)}")
    
    try:
        # Build request payload
        payload = {
            "query": scenario['query'],
            **scenario['filters']
        }
        
        # Send request
        response = requests.post(
            f"{base_url}/api/rag/query",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            logger.info(f"\n✅ SUCCESS")
            logger.info(f"Response: {result['response'][:200]}...")
            logger.info(f"Confidence: {result['confidence']}")
            logger.info(f"Sources: {len(result.get('sources', []))}")
            
            # Display water-specific metadata
            if result.get('water_objects'):
                logger.info(f"\n💧 Water Objects Referenced:")
                for obj in result['water_objects']:
                    logger.info(f"  - {obj.get('name')} (ID: {obj.get('id')})")
                    logger.info(f"    Region: {obj.get('region')}, Type: {obj.get('resource_type')}")
                    logger.info(f"    Priority: {obj.get('priority_level')}")
            
            if result.get('regions'):
                logger.info(f"\n📍 Regions: {', '.join(result['regions'])}")
            
            if result.get('priority_levels'):
                logger.info(f"⚡ Priority Levels: {', '.join(result['priority_levels'])}")
            
            return True
        else:
            logger.error(f"❌ FAILED: HTTP {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_explain_priority(base_url: str, object_id: int):
    """Test the explain-priority convenience endpoint."""
    logger.info(f"\n{'=' * 80}")
    logger.info(f"🧪 TESTING: Explain Priority Endpoint")
    logger.info(f"{'=' * 80}")
    logger.info(f"Object ID: {object_id}")
    
    try:
        response = requests.post(
            f"{base_url}/api/rag/explain-priority/{object_id}",
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            logger.info(f"\n✅ SUCCESS")
            logger.info(f"Query: {result['query']}")
            logger.info(f"Response: {result['response'][:300]}...")
            logger.info(f"Confidence: {result['confidence']}")
            
            if result.get('water_objects'):
                logger.info(f"\n💧 Water Objects:")
                for obj in result['water_objects']:
                    logger.info(f"  - {obj.get('name')} (Priority: {obj.get('priority_level')})")
            
            return True
        else:
            logger.error(f"❌ FAILED: HTTP {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def check_system_status(base_url: str):
    """Check if RAG system is operational."""
    logger.info("🔍 Checking RAG system status...")
    
    try:
        response = requests.get(f"{base_url}/api/rag/status", timeout=10)
        
        if response.status_code == 200:
            status = response.json()
            logger.info(f"✅ System status: {status.get('status')}")
            logger.info(f"Supervisor agent: {status.get('supervisor_agent')}")
            logger.info(f"Available tools: {', '.join(status.get('available_tools', []))}")
            return True
        else:
            logger.error(f"❌ Status check failed: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Cannot connect to RAG system: {e}")
        return False


def main():
    """Run all RAG water management query tests."""
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    
    logger.info("=" * 80)
    logger.info("🚀 Starting RAG Water Management Query Tests")
    logger.info("=" * 80)
    logger.info(f"API Base URL: {base_url}")
    
    # Check system status
    if not check_system_status(base_url):
        logger.error("System not ready. Exiting.")
        return False
    
    logger.info("\n" + "=" * 80)
    logger.info("🧪 Running Query Scenarios")
    logger.info("=" * 80)
    
    # Run test scenarios
    passed = 0
    failed = 0
    
    for scenario in TEST_SCENARIOS:
        if test_rag_query(base_url, scenario):
            passed += 1
        else:
            failed += 1
        
        # Wait between tests
        import time
        time.sleep(2)
    
    # Test explain-priority endpoint with a sample object ID
    logger.info("\n" + "=" * 80)
    logger.info("🧪 Testing Convenience Endpoints")
    logger.info("=" * 80)
    
    if test_explain_priority(base_url, object_id=1):
        passed += 1
    else:
        failed += 1
    
    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("📊 TEST SUMMARY")
    logger.info("=" * 80)
    logger.info(f"✅ Passed: {passed}")
    logger.info(f"❌ Failed: {failed}")
    logger.info(f"Total: {passed + failed}")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
