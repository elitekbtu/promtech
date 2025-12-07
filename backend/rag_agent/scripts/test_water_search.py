"""
Test script for water management semantic search.

This script tests various water-related queries to verify that the vector store
properly indexes and retrieves water management data.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rag_agent.tools.vector_search import VectorSearchTool
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Test queries in Russian and English
TEST_QUERIES = [
    # Basic water object queries
    ("озера с высоким приоритетом", "Lakes with high priority"),
    ("водоемы в Алматинской области", "Water bodies in Almaty region"),
    ("каналы с непресной водой", "Canals with non-fresh water"),
    ("водохранилища с фауной", "Reservoirs with fauna"),
    
    # Technical condition queries
    ("объекты с критическим техническим состоянием", "Objects with critical technical condition"),
    ("водные объекты в плохом состоянии", "Water objects in poor condition"),
    ("техническое состояние озер", "Technical condition of lakes"),
    
    # Priority and inspection queries
    ("приоритет обследования водных объектов", "Inspection priority of water objects"),
    ("почему высокий приоритет", "Why high priority"),
    ("расчет приоритета", "Priority calculation"),
    ("объекты требующие срочного обследования", "Objects requiring urgent inspection"),
    
    # Passport queries
    ("паспорт озера Балхаш", "Lake Balkhash passport"),
    ("информация о паспортах водоемов", "Information about water body passports"),
    ("устаревшие паспорта", "Outdated passports"),
    ("биологическая характеристика водоема", "Biological characteristics of water body"),
    
    # Regional queries
    ("водные ресурсы Казахстана", "Water resources of Kazakhstan"),
    ("гидротехнические сооружения", "Hydrotechnical structures"),
    ("состояние водных объектов по регионам", "Condition of water objects by region"),
    
    # Complex queries
    ("озера с фауной и высоким приоритетом в Алматинской области", 
     "Lakes with fauna and high priority in Almaty region"),
    ("водохранилища с устаревшими паспортами старше 5 лет", 
     "Reservoirs with outdated passports older than 5 years"),
]


def run_test_query(tool: VectorSearchTool, query_ru: str, query_en: str):
    """Run a single test query and display results."""
    print("\n" + "=" * 100)
    print(f"🔍 QUERY (RU): {query_ru}")
    print(f"🔍 QUERY (EN): {query_en}")
    print("=" * 100)
    
    try:
        # Test with Russian query
        results = tool.search(query_ru, k=3, use_reranking=True)
        print(results)
        
    except Exception as e:
        logger.error(f"Error running query '{query_ru}': {e}")
        import traceback
        traceback.print_exc()


def test_metadata_filtering():
    """Test that metadata is properly utilized in search results."""
    print("\n" + "=" * 100)
    print("🧪 TESTING METADATA FILTERING AND DISPLAY")
    print("=" * 100)
    
    tool = VectorSearchTool()
    
    # Test query that should return water objects
    query = "водные объекты с высоким приоритетом"
    print(f"\nQuery: {query}")
    print("-" * 100)
    
    results = tool.search(query, k=5, use_reranking=True)
    
    # Check if results contain water management metadata
    if "Объект:" in results:
        print("✅ Water object metadata displayed correctly")
    else:
        print("⚠️  Water object metadata not found in results")
    
    if "Приоритет:" in results:
        print("✅ Priority information displayed correctly")
    else:
        print("⚠️  Priority information not found in results")
    
    if "Регион:" in results:
        print("✅ Region information displayed correctly")
    else:
        print("⚠️  Region information not found in results")
    
    print("\nFull results:")
    print(results)


def main():
    """Main test function."""
    logger.info("=" * 100)
    logger.info("🚀 Starting Water Management Semantic Search Tests")
    logger.info("=" * 100)
    
    try:
        # Initialize vector search tool
        logger.info("\n📦 Initializing vector search tool...")
        tool = VectorSearchTool()
        logger.info("✅ Vector search tool initialized successfully")
        
        # Check vector store info
        info = tool.get_store_info()
        logger.info(f"\n📊 Vector Store Info:")
        logger.info(f"   Status: {info.get('status', 'Unknown')}")
        if 'total_documents' in info:
            logger.info(f"   Total documents: {info['total_documents']}")
        
        # Test metadata filtering first
        test_metadata_filtering()
        
        # Run all test queries
        logger.info("\n" + "=" * 100)
        logger.info("🧪 RUNNING TEST QUERIES")
        logger.info("=" * 100)
        
        for query_ru, query_en in TEST_QUERIES:
            run_test_query(tool, query_ru, query_en)
            input("\n⏸️  Press Enter to continue to next query...")
        
        logger.info("\n" + "=" * 100)
        logger.info("✅ ALL TESTS COMPLETED")
        logger.info("=" * 100)
        
    except Exception as e:
        logger.error(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
