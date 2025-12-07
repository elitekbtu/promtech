#!/usr/bin/env python3
"""
Vector Database Initialization Script

This script initializes the FAISS vector database from documents and water management data
using Google embeddings. Run this script to create the vector store before using the RAG system.
"""

import os
import sys
import logging
from pathlib import Path

# Add the backend directory to the path so we can import our modules
current_dir = Path(__file__).parent
rag_agent_dir = current_dir.parent
backend_dir = rag_agent_dir.parent
sys.path.insert(0, str(backend_dir))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Initialize vector database with documents and water management data."""
    print("=" * 80)
    print("🚀 Initializing Vector Database")
    print("=" * 80)
    
    # Check for Google API key
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        print("❌ Error: GOOGLE_API_KEY not set")
        print("Set it with: export GOOGLE_API_KEY='your-key-here'")
        return False
    
    print("✅ Google API key found")
    
    # Set up paths
    documents_path = current_dir.parent / "documents"
    vector_store_path = current_dir.parent / "data" / "vector_store"
    
    print(f"📁 Documents path: {documents_path}")
    print(f"📁 Vector store path: {vector_store_path}")
    
    try:
        from rag_agent.utils.vector_store import VectorStoreManager
        from database import SessionLocal
        
        # Initialize vector store manager
        manager = VectorStoreManager(
            documents_path=str(documents_path),
            vector_store_path=str(vector_store_path),
            chunk_size=500,
            chunk_overlap=100
        )
        
        # Initialize embeddings
        print("\n🔄 Initializing Google embeddings...")
        if not manager.initialize_embeddings():
            print("❌ Failed to initialize embeddings")
            return False
        
        # Load existing documents from files
        if documents_path.exists():
            doc_files = list(documents_path.glob("*.txt")) + list(documents_path.glob("*.pdf"))
            if doc_files:
                print(f"\n📄 Found {len(doc_files)} document files:")
                for doc_file in doc_files:
                    print(f"   - {doc_file.name}")
                
                print("\n🔄 Processing documents...")
                documents = manager.load_documents()
                if documents:
                    processed_docs = manager.process_documents(documents)
                    if processed_docs:
                        manager.create_vector_store(processed_docs)
                        print("✅ Document files indexed successfully")
        
        # Index water management data from database
        print("\n" + "=" * 80)
        print("🌊 Indexing Water Management Data from Database")
        print("=" * 80)
        
        db = SessionLocal()
        try:
            if manager.index_water_management_data(db):
                print("\n" + "=" * 80)
                print("✅ SUCCESS: Vector database initialized!")
                print("=" * 80)
                print("\nVector store contains:")
                print("  • Documents from files (.txt, .pdf)")
                print("  • Water objects (озера, каналы, водохранилища)")
                print("  • Passport documents (паспорта объектов)")
                print("  • Technical conditions (техническое состояние)")
                print("  • Priority calculations (приоритеты обследования)")
                print("  • Regional water data (региональные данные)")
                
                # Test search
                print("\n🧪 Testing search...")
                try:
                    from rag_agent.tools.vector_search import vector_search_tool
                    result = vector_search_tool.invoke({"query": "водные объекты с высоким приоритетом", "k": 2})
                    print(f"✅ Search is working! Found results.")
                except Exception as e:
                    print(f"⚠️  Search test failed: {e}")
                
                return True
            else:
                print("❌ Failed to index water management data")
                return False
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error during initialization: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Done!")
    else:
        print("\n💥 Failed!")
        sys.exit(1)
