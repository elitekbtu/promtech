import os
import logging
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
import sys
from pathlib import Path

# Add the backend directory to path
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from rag_agent.utils.vector_store import VectorStoreManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorSearchTool:
    """Vector search tool for the RAG system."""
    
    def __init__(self, 
                 vector_store_path: str = "rag_agent/data/vector_store",
                 embedding_model: str = "models/embedding-001",
                 google_api_key: Optional[str] = None):
        """
        Initialize the vector search tool.
        
        Args:
            vector_store_path: Path to the FAISS vector store
            embedding_model: Google embedding model to use
            google_api_key: Google API key
        """
        self.vector_store_path = vector_store_path
        self.embedding_model = embedding_model
        self.google_api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.google_api_key:
            raise ValueError(
                "GOOGLE_API_KEY environment variable is not set. "
                "Please set a valid Google API key to use vector search. "
                "Get your API key from: https://makersuite.google.com/app/apikey"
            )
        
        self.vector_store_manager = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the vector store manager."""
        try:
            self.vector_store_manager = VectorStoreManager(
                vector_store_path=self.vector_store_path,
                embedding_model=self.embedding_model
            )
            
            # Initialize embeddings
            if not self.vector_store_manager.initialize_embeddings(self.google_api_key):
                raise RuntimeError("Failed to initialize embeddings. Please check your GOOGLE_API_KEY.")
            
            # Try to load existing vector store
            if not self.vector_store_manager.load_vector_store():
                logger.warning("No existing vector store found. You may need to run the initialization script first.")
                logger.warning("Run: python backend/rag_agent/scripts/initialize_vector_db.py")
                
        except Exception as e:
            logger.error(f"Error initializing vector search tool: {e}")
            raise RuntimeError(f"Failed to initialize vector search: {e}")
    
    def search(self, query: str, k: int = 5, use_reranking: bool = True, 
               use_hyde: bool = True, use_hybrid: bool = True,
               similarity_threshold: float = 0.5) -> str:
        """
        Search for relevant documents using advanced RAG techniques:
        - HyDE (Hypothetical Document Embeddings) for query expansion
        - Hybrid Search (BM25 + Vector) for better recall
        - AI Reranking for improved precision
        
        Args:
            query: Search query
            k: Number of results to return
            use_reranking: Whether to use Gemini reranking for better accuracy
            use_hyde: Whether to use HyDE query expansion
            use_hybrid: Whether to use hybrid search (BM25 + Vector)
            similarity_threshold: Minimum similarity score (lower is better for FAISS distance)
            
        Returns:
            str: Formatted search results with quality indicators
        """
        if not self.vector_store_manager or not self.vector_store_manager.vector_store:
            raise RuntimeError(
                "Vector store not available. Please ensure the vector database is initialized. "
                "Run: python backend/rag_agent/scripts/initialize_vector_db.py"
            )
        
        try:
            # Use advanced RAG search with ALL best practices
            results = self.vector_store_manager.search_documents(
                query, 
                k=k, 
                use_reranking=use_reranking,
                use_hyde=use_hyde,
                use_hybrid=use_hybrid,
                use_multi_query=True,      # Multi-query retrieval (best practice)
                ensure_diversity=True,      # Source diversity (best practice)
                merge_context=True         # Context merging (best practice)
            )
            
            if not results:
                return f"❌ No relevant documents found for query: '{query}'\n\nTry:\n- Rephrasing your question\n- Using different keywords\n- Asking about available topics"
            
            # Улучшенная оценка качества результатов
            has_rerank = 'rerank_score' in results[0] if results else False
            
            if has_rerank:
                # Используем rerank_score как основной индикатор
                best_rerank = results[0].get('rerank_score', 0)
                best_combined = results[0].get('combined_score', 0)
                
                # Более умные пороги: если rerank >= 6 или combined >= 0.4, считаем хорошим
                if best_rerank >= 6 or best_combined >= 0.4:
                    quality_warning = ""
                elif best_rerank >= 4 or best_combined >= 0.3:
                    quality_warning = "💡 Results found, but may need refinement. Try being more specific.\n\n"
                else:
                    quality_warning = "⚠️ Results have limited relevance. Try rephrasing or using different keywords.\n\n"
            else:
                # Используем similarity score (distance: меньше = лучше)
                best_score = results[0].get('similarity_score', 1.0)
                # Для distance: < 0.5 = отлично, < 0.7 = хорошо, < 1.0 = нормально
                if best_score < 0.5:
                    quality_warning = ""
                elif best_score < 0.7:
                    quality_warning = "💡 Results found, but may need refinement.\n\n"
                else:
                    quality_warning = "⚠️ Results may have limited relevance. Consider rephrasing.\n\n"
            
            # Format results with enhanced metadata
            formatted_results = [quality_warning] if quality_warning else []
            
            for i, result in enumerate(results, 1):
                # Используем enhanced_content если есть (с parent context)
                content = result.get('enhanced_content') or result['content']
                metadata = result['metadata']
                sim_score = result['similarity_score']
                
                # Extract source information
                source = metadata.get('source', 'Unknown')
                filename = metadata.get('filename', metadata.get('source_file', 'Unknown'))
                document_type = metadata.get('document_type', 'text')
                is_pdf = document_type == 'pdf'
                
                # Water management specific metadata
                object_id = metadata.get('object_id')
                object_name = metadata.get('object_name')
                region = metadata.get('region')
                resource_type = metadata.get('resource_type')
                priority_level = metadata.get('priority_level')
                section_type = metadata.get('section_type')
                content_type = metadata.get('content_type')
                
                # Check for merged chunks (contextual compression)
                merged_count = result.get('merged_chunks', 0)
                has_parent_context = 'parent_context' in result
                
                # Clean filename
                if isinstance(source, str) and '/' in source:
                    filename = source.split('/')[-1]
                
                # Улучшенные индикаторы качества с более реалистичными порогами
                if has_rerank:
                    # Используем rerank_score как основной индикатор
                    combined_score = result.get('combined_score', 0)
                    rerank_score = result.get('rerank_score', 0)
                    
                    # Более реалистичные пороги: rerank >= 7 = отлично, >= 5 = хорошо, >= 3 = нормально
                    if rerank_score >= 7.5 or (combined_score > 0.65 and rerank_score >= 6):
                        confidence_emoji = "🟢"
                        confidence_level = "Excellent"
                    elif rerank_score >= 5.5 or (combined_score > 0.45 and rerank_score >= 4):
                        confidence_emoji = "🟡"
                        confidence_level = "Good"
                    elif rerank_score >= 3.5 or combined_score > 0.3:
                        confidence_emoji = "🟠"
                        confidence_level = "Fair"
                    else:
                        confidence_emoji = "🔴"
                        confidence_level = "Low"
                    
                    score_display = f"Relevance: {rerank_score:.1f}/10, Combined: {combined_score:.2f}"
                else:
                    # Используем similarity score (FAISS distance: меньше = лучше)
                    # Более реалистичные пороги для distance
                    if sim_score < 0.3:
                        confidence_emoji = "🟢"
                        confidence_level = "Excellent"
                    elif sim_score < 0.5:
                        confidence_emoji = "🟡"
                        confidence_level = "Good"
                    elif sim_score < 0.8:
                        confidence_emoji = "🟠"
                        confidence_level = "Fair"
                    else:
                        confidence_emoji = "🔴"
                        confidence_level = "Low"
                    
                    # Показываем similarity как процент (инвертируем distance)
                    similarity_percent = max(0, min(100, (1 - min(sim_score, 1.0)) * 100))
                    score_display = f"Similarity: {similarity_percent:.0f}% (distance: {sim_score:.3f})"
                
                # Document type indicator with water management awareness
                if document_type == 'water_object':
                    doc_type_indicator = "💧 Водный объект"
                elif document_type == 'passport_text':
                    doc_type_indicator = "📋 Паспорт объекта"
                elif is_pdf:
                    doc_type_indicator = "📄 PDF"
                else:
                    doc_type_indicator = "📝 Text"
                
                # Build result entry
                result_lines = [
                    f"{confidence_emoji} **Result {i}** ({confidence_level}) {doc_type_indicator}",
                ]
                
                # Add water management specific metadata
                if object_name:
                    result_lines.append(f"🏷️  Объект: {object_name}")
                if region:
                    result_lines.append(f"📍 Регион: {region}")
                if resource_type:
                    resource_types = {
                        "lake": "Озеро",
                        "canal": "Канал",
                        "reservoir": "Водохранилище"
                    }
                    type_name = resource_types.get(resource_type, resource_type.title())
                    result_lines.append(f"🌊 Тип: {type_name}")
                if priority_level and priority_level != "N/A":
                    priority_emojis = {
                        "high": "🔴 ВЫСОКИЙ",
                        "medium": "🟡 СРЕДНИЙ",
                        "low": "🟢 НИЗКИЙ"
                    }
                    priority_display = priority_emojis.get(priority_level.lower(), priority_level.upper())
                    result_lines.append(f"⚡ Приоритет: {priority_display}")
                if section_type and section_type != "full_text":
                    section_names = {
                        "general_info": "Общая информация",
                        "technical_params": "Технические параметры",
                        "ecological_state": "Экологическое состояние",
                        "recommendations": "Рекомендации"
                    }
                    section_name = section_names.get(section_type, section_type.replace('_', ' ').title())
                    result_lines.append(f"📑 Раздел: {section_name}")
                if object_id:
                    result_lines.append(f"🔗 ID объекта: {object_id}")
                
                # Source file info (if not water management data)
                if not object_name:
                    result_lines.append(f"📁 Source: {filename}")
                
                # Add context indicators
                if merged_count > 1:
                    result_lines.append(f"🔗 Merged {merged_count} related chunks for comprehensive context")
                if has_parent_context:
                    result_lines.append(f"📚 Includes parent document context")
                
                # Add score and content
                content_length = 800 if merged_count > 1 or has_parent_context else 500
                content_preview = content[:content_length] if len(content) > content_length else content
                
                result_lines.extend([
                    f"📊 {score_display}",
                    f"📖 Content:\n{content_preview}{'...' if len(content) > content_length else ''}",
                    f"{'─' * 80}"
                ])
                
                formatted_results.append("\n".join(result_lines) + "\n")
            
            result_text = "\n".join(formatted_results)
            
            # Add helpful footer with statistics
            rerank_status = " (with AI reranking)" if has_rerank else ""
            unique_sources = len(set(r.get('metadata', {}).get('source_file', '') for r in results))
            merged_count = sum(1 for r in results if r.get('merged_chunks', 0) > 1)
            
            footer = f"\n✅ Found {len(results)} relevant result(s) from {unique_sources} document(s){rerank_status}."
            if merged_count > 0:
                footer += f"\n🔗 {merged_count} result(s) include merged context from multiple chunks."
            
            result_text += footer + "\n"
            
            return result_text
            
        except Exception as e:
            logger.error(f"Error performing vector search: {e}")
            return f"❌ Error searching documents: {str(e)}"
    
    def get_store_info(self) -> Dict[str, Any]:
        """Get information about the vector store."""
        if not self.vector_store_manager:
            return {"status": "not_initialized"}
        
        return self.vector_store_manager.get_vector_store_info()


# Global vector search tool instance
_vector_search_tool_instance = None


def get_vector_search_tool() -> VectorSearchTool:
    """Get the global vector search tool instance."""
    global _vector_search_tool_instance
    if _vector_search_tool_instance is None:
        _vector_search_tool_instance = VectorSearchTool()
    return _vector_search_tool_instance


@tool
def vector_search_tool(query: str) -> str:
    """
    Search through local knowledge base using vector similarity.
    
    This tool searches through company documents, policies, and procedures
    to find relevant information based on semantic similarity.
    
    Args:
        query: The search query to find relevant documents
        
    Returns:
        str: Formatted search results with sources and similarity scores
    """
    tool_instance = get_vector_search_tool()
    return tool_instance.search(query)


@tool
def vector_search_with_metadata(query: str, k: int = 3) -> Dict[str, Any]:
    """
    Search through local knowledge base and return detailed metadata.
    
    Args:
        query: The search query to find relevant documents
        k: Number of results to return
        
    Returns:
        Dict: Detailed search results with metadata
    """
    tool_instance = get_vector_search_tool()
    
    if not tool_instance.vector_store_manager or not tool_instance.vector_store_manager.vector_store:
        return {
            "error": "Vector store not available",
            "results": [],
            "total_results": 0
        }
    
    try:
        results = tool_instance.vector_store_manager.search_documents(query, k=k)
        
        return {
            "query": query,
            "results": results,
            "total_results": len(results),
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error in vector search with metadata: {e}")
        return {
            "error": str(e),
            "results": [],
            "total_results": 0
        }


def get_vector_store_status() -> Dict[str, Any]:
    """
    Get the current status of the vector store.
    
    Returns:
        Dict: Status information about the vector store
    """
    try:
        tool_instance = get_vector_search_tool()
        info = tool_instance.get_store_info()
        
        if info.get("status") == "not_initialized":
            return {
                "status": "error",
                "message": "Vector store is not initialized. Please run the initialization script first.",
                "available": False
            }
        
        if info.get("status") == "error":
            return {
                "status": "error",
                "message": info.get('error', 'Unknown error'),
                "available": False
            }
        
        return {
            "status": "ready",
            "message": "Vector store is ready",
            "available": True,
            "details": {
                "index_type": info.get('index_type', 'unknown'),
                "embedding_dimension": info.get('embedding_dimension', 'unknown'),
                "total_vectors": info.get('total_vectors', 'unknown')
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "available": False
        }


def initialize_vector_store(documents_path: str = "rag_agent/documents",
                           vector_store_path: str = "rag_agent/data/vector_store",
                           google_api_key: Optional[str] = None) -> bool:
    """
    Initialize the vector store from documents.
    
    Args:
        documents_path: Path to documents directory
        vector_store_path: Path to store the FAISS index
        google_api_key: Google API key
        
    Returns:
        bool: True if successful, False otherwise
    """
    from rag_agent.utils.vector_store import create_vector_store_from_documents
    
    try:
        success = create_vector_store_from_documents(
            documents_path=documents_path,
            vector_store_path=vector_store_path,
            google_api_key=google_api_key
        )
        
        if success:
            # Reinitialize the tool instance to use the new vector store
            global _vector_search_tool_instance
            _vector_search_tool_instance = VectorSearchTool(
                vector_store_path=vector_store_path,
                google_api_key=google_api_key
            )
            logger.info("Vector store initialized successfully")
        else:
            logger.error("Failed to initialize vector store")
        
        return success
        
    except Exception as e:
        logger.error(f"Error initializing vector store: {e}")
        return False


# Export the main search function for easy access
def search_documents(query: str, k: int = 3) -> str:
    """
    Convenience function to search documents.
    
    Args:
        query: Search query
        k: Number of results
        
    Returns:
        str: Search results
    """
    return vector_search_tool.invoke({"query": query})


if __name__ == "__main__":
    # Example usage and testing
    print("Testing vector search tool...")
    
    # Check if vector store exists
    status = get_vector_store_status()
    print(f"Vector store status: {status}")
    
    # If not initialized, initialize it
    if "not initialized" in status.lower():
        print("Initializing vector store...")
        success = initialize_vector_store()
        if success:
            print("Vector store initialized successfully!")
        else:
            print("Failed to initialize vector store")
            exit(1)
    
    # Test search with generic query
    test_query = "company policies"
    print(f"\nSearching for: '{test_query}'")
    results = vector_search_tool.invoke({"query": test_query})
    print(f"Results:\n{results}")
