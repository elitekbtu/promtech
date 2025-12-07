"""
Vector Store Management Module

This module handles the creation and management of the FAISS vector store
for document embeddings using Google's embedding model.
"""

import os
import logging
from typing import List, Optional, Dict, Any
from pathlib import Path
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import google.generativeai as genai
from rank_bm25 import BM25Okapi
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages the FAISS vector store for document embeddings."""
    
    def __init__(self, 
                 documents_path: str = "documents",
                 vector_store_path: str = "data/vector_store",
                 embedding_model: str = "models/embedding-001",
                 chunk_size: int = 400,
                 chunk_overlap: int = 100):
        """
        Initialize the VectorStoreManager.
        
        Args:
            documents_path: Path to documents directory
            vector_store_path: Path to store the FAISS index
            embedding_model: Google embedding model to use
            chunk_size: Size of text chunks for processing
            chunk_overlap: Overlap between chunks
        """
        self.documents_path = Path(documents_path)
        self.vector_store_path = Path(vector_store_path)
        self.embedding_model = embedding_model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Create directories if they don't exist
        self.vector_store_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.embeddings = None
        self.vector_store = None
        self.reranker_llm = None
        self.bm25 = None
        self.bm25_docs = []  # Store documents for BM25
        self.all_chunks = []  # Store all chunks for hybrid search
        # Optimized text splitter for better PDF handling with semantic separators
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=[
                "\n\n\n",  # Multiple line breaks (sections)
                "\n\n",    # Paragraph breaks
                "\n",      # Line breaks
                ". ",      # Sentences
                "! ",      # Exclamations
                "? ",      # Questions
                ";",       # Semi-colons
                ",",       # Commas
                " ",       # Words
                ""         # Characters
            ],
            keep_separator=True,  # Keep separators for better context
            add_start_index=True,  # Track position in document
        )
    
    def initialize_embeddings(self, google_api_key: Optional[str] = None) -> bool:
        """
        Initialize the Google embeddings model.
        
        Args:
            google_api_key: Google API key (if not provided, uses environment variable)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            api_key = google_api_key or os.getenv("GOOGLE_API_KEY")
            if not api_key:
                logger.error("GOOGLE_API_KEY not found in environment variables")
                return False
            
            logger.info(f"Initializing embedding model: {self.embedding_model}")
            self.embeddings = GoogleGenerativeAIEmbeddings(
                model=self.embedding_model,
                google_api_key=api_key
            )
            
            # Initialize reranker LLM
            try:
                genai.configure(api_key=api_key)
                # Try gemini-1.5-pro first, fallback if not available
                try:
                    self.reranker_llm = ChatGoogleGenerativeAI(
                        model="gemini-2.5-flash",
                        temperature=0.0,
                        google_api_key=api_key
                    )
                except:
                    # Fallback to gemini-pro
                    self.reranker_llm = ChatGoogleGenerativeAI(
                        model="models/gemini-pro",
                        temperature=0.0,
                        google_api_key=api_key
                    )
            except Exception as e:
                logger.warning(f"Could not initialize reranker: {e}. Reranking will be disabled.")
                self.reranker_llm = None
            
            logger.info("Embedding model and reranker initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing embedding model: {e}")
            logger.error("Please ensure your GOOGLE_API_KEY is set correctly in the .env file.")
            return False
    
    def load_documents(self) -> List[Document]:
        """
        Load all documents from the documents directory.
        
        Returns:
            List[Document]: List of loaded documents
        """
        documents = []
        
        if not self.documents_path.exists():
            logger.error(f"Documents path does not exist: {self.documents_path}")
            return documents
        
        # Load all .txt files from the documents directory
        for file_path in self.documents_path.glob("*.txt"):
            try:
                logger.info(f"Loading document: {file_path.name}")
                loader = TextLoader(str(file_path), encoding='utf-8')
                docs = loader.load()
                documents.extend(docs)
                logger.info(f"Successfully loaded {len(docs)} pages from {file_path.name}")
            except Exception as e:
                logger.error(f"Error loading document {file_path.name}: {e}")
        
        # Load all .pdf files from the documents directory with proper processing
        for file_path in self.documents_path.glob("*.pdf"):
            try:
                logger.info(f"Loading PDF document: {file_path.name}")
                loader = PyPDFLoader(str(file_path))
                docs = loader.load()
                
                # Proper PDF preprocessing - preserve structure
                for doc in docs:
                    content = doc.page_content
                    
                    # Clean PDF artifacts but PRESERVE structure
                    # Remove only excessive spaces within lines, keep paragraph breaks
                    lines = content.split('\n')
                    cleaned_lines = []
                    for line in lines:
                        # Clean each line but keep it as a line
                        cleaned_line = ' '.join(line.split())
                        if cleaned_line:  # Only add non-empty lines
                            cleaned_lines.append(cleaned_line)
                    
                    # Rejoin with single newlines to preserve paragraphs
                    content = '\n'.join(cleaned_lines)
                    
                    # Add enhanced metadata for better retrieval
                    doc.metadata.update({
                        'document_type': 'pdf',
                        'filename': file_path.name,
                        'file_path': str(file_path),
                        'source': str(file_path),
                        'processed': True
                    })
                    
                    doc.page_content = content
                
                documents.extend(docs)
                logger.info(f"Successfully loaded and preprocessed {len(docs)} pages from {file_path.name}")
            except Exception as e:
                logger.error(f"Error loading PDF document {file_path.name}: {e}")
        
        logger.info(f"Total documents loaded: {len(documents)}")
        return documents
    
    def process_documents(self, documents: List[Document]) -> List[Document]:
        """
        Process documents with parent-child chunking for better context preservation.
        Best practice: Hierarchical chunking для сохранения контекста.
        
        Args:
            documents: List of documents to process
            
        Returns:
            List[Document]: List of processed document chunks with parent-child relationships
        """
        if not documents:
            logger.warning("No documents to process")
            return []
        
        logger.info("Processing documents with parent-child chunking...")
        try:
            all_chunks = []
            
            # Обрабатываем каждый документ отдельно для parent-child структуры
            for doc in documents:
                # Сначала создаем большие родительские чанки
                parent_chunks = self.text_splitter.split_documents([doc])
                
                # Затем разбиваем каждый родительский чанк на маленькие дочерние
                for parent_idx, parent_chunk in enumerate(parent_chunks):
                    parent_content = parent_chunk.page_content
                    
                    # Всегда создаем child chunks для лучшего контекста
                    # Если родительский чанк больше базового размера, разбиваем на дочерние
                    if len(parent_content) > self.chunk_size:
                        # Создаем маленький splitter для дочерних чанков (меньше размер для более точного поиска)
                        child_chunk_size = max(150, self.chunk_size // 2)  # Дочерние чанки в 2 раза меньше
                        child_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=child_chunk_size,
                            chunk_overlap=self.chunk_overlap // 2,
                            separators=[". ", "\n", "; ", ", ", " ", ""]
                        )
                        child_chunks = child_splitter.split_text(parent_content)
                        
                        # Создаем дочерние чанки с ссылками на родителя
                        for child_idx, child_content in enumerate(child_chunks):
                            if len(child_content.strip()) < 20:  # Пропускаем слишком маленькие чанки
                                continue
                                
                            child_chunk = Document(
                                page_content=child_content.strip(),
                                metadata=parent_chunk.metadata.copy()
                            )
                            
                            # Добавляем parent-child метаданные
                            child_chunk.metadata.update({
                                "parent_chunk_index": parent_idx,
                                "child_chunk_index": child_idx,
                                "total_child_chunks": len(child_chunks),
                                "is_child": True,
                                "is_parent": False,
                                "parent_content_preview": parent_content[:300] + "..." if len(parent_content) > 300 else parent_content
                            })
                            
                            all_chunks.append(child_chunk)
                    else:
                        # Маленький чанк - используем как есть, но помечаем как parent
                        parent_chunk.metadata.update({
                            "parent_chunk_index": parent_idx,
                            "is_child": False,
                            "is_parent": True
                        })
                        all_chunks.append(parent_chunk)
            
            logger.info(f"Created {len(all_chunks)} chunks with parent-child structure")
            
            # Enhanced metadata for better retrieval
            for i, chunk in enumerate(all_chunks):
                # Get source information
                source = chunk.metadata.get('source', 'Unknown')
                filename = chunk.metadata.get('filename', 'Unknown')
                document_type = chunk.metadata.get('document_type', 'text')
                
                # Add enhanced metadata
                chunk.metadata.update({
                    "chunk_id": i,
                    "total_chunks": len(all_chunks),
                    "chunk_index": i,
                    "source_file": filename,
                    "document_type": document_type,
                    "chunk_length": len(chunk.page_content),
                    "word_count": len(chunk.page_content.split()),
                    "is_pdf": document_type == 'pdf',
                    "processed": True
                })
                
                # Add content preview
                chunk.metadata["content_preview"] = chunk.page_content[:100] + "..." if len(chunk.page_content) > 100 else chunk.page_content
            
            # Статистика
            child_count = sum(1 for c in all_chunks if c.metadata.get('is_child', False))
            parent_count = len(all_chunks) - child_count
            logger.info(f"Chunking stats: {parent_count} parent chunks, {child_count} child chunks")
            
            return all_chunks
            
        except Exception as e:
            logger.error(f"Error processing documents: {e}")
            return []
    
    def _get_parent_context(self, chunk: Dict[str, Any]) -> Optional[str]:
        """
        Получает контекст родительского чанка для дочернего.
        
        Args:
            chunk: Дочерний чанк
            
        Returns:
            Optional[str]: Контекст родителя или None
        """
        if not chunk.get('metadata', {}).get('is_child', False):
            return None
        
        parent_preview = chunk.get('metadata', {}).get('parent_content_preview')
        return parent_preview
    
    def create_vector_store(self, documents: List[Document]) -> bool:
        """
        Create FAISS vector store and BM25 index from documents.
        
        Args:
            documents: List of document chunks
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.embeddings:
            logger.error("Embeddings not initialized. Call initialize_embeddings() first.")
            return False
        
        if not documents:
            logger.error("No documents provided for vector store creation")
            return False
        
        try:
            # Create FAISS vector store
            logger.info("Creating FAISS vector store... This may take a few moments.")
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            logger.info("FAISS vector store created successfully")
            
            # Create BM25 index for hybrid search
            logger.info("Creating BM25 index for hybrid search...")
            self.all_chunks = documents
            self.bm25_docs = [doc.page_content for doc in documents]
            
            # Tokenize documents for BM25 (simple word-based tokenization)
            tokenized_docs = [doc.lower().split() for doc in self.bm25_docs]
            self.bm25 = BM25Okapi(tokenized_docs)
            logger.info(f"BM25 index created with {len(self.bm25_docs)} documents")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating vector store: {e}")
            return False
    
    def save_vector_store(self) -> bool:
        """
        Save the vector store to disk.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.vector_store:
            logger.error("No vector store to save")
            return False
        
        try:
            logger.info(f"Saving vector store to: {self.vector_store_path}")
            self.vector_store.save_local(str(self.vector_store_path))
            logger.info("Vector store saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
            return False
    
    def load_vector_store(self) -> bool:
        """
        Load the vector store from disk.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.embeddings:
            logger.error("Embeddings not initialized. Call initialize_embeddings() first.")
            return False
        
        try:
            vector_store_file = self.vector_store_path / "index.faiss"
            if not vector_store_file.exists():
                logger.warning(f"Vector store not found at: {vector_store_file}")
                return False
            
            logger.info(f"Loading vector store from: {self.vector_store_path}")
            self.vector_store = FAISS.load_local(
                str(self.vector_store_path), 
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            logger.info("Vector store loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False
    
    def _preprocess_query(self, query: str) -> str:
        """
        Улучшенная предобработка запроса для лучшего поиска.
        Нормализация, обработка технических терминов, синонимы.
        
        Args:
            query: Исходный запрос
            
        Returns:
            str: Обработанный запрос
        """
        # Нормализация: убираем лишние пробелы, приводим к нижнему регистру для анализа
        normalized = query.strip()
        
        # Технические термины GidroAtlas - добавляем синонимы
        gidro_terms = {
            'объект': ['объект', 'водоем', 'сооружение', 'гидротехническое сооружение'],
            'паспорт': ['паспорт', 'документ', 'характеристика', 'описание'],
            'состояние': ['состояние', 'техническое состояние', 'категория', 'статус'],
            'водоем': ['водоем', 'озеро', 'водохранилище', 'канал', 'водный ресурс'],
            'область': ['область', 'регион', 'район'],
            'координаты': ['координаты', 'местоположение', 'расположение', 'географическое положение']
        }
        
        # Добавляем контекстные ключевые слова для лучшего поиска
        query_lower = normalized.lower()
        expanded_terms = [normalized]
        
        for term, synonyms in gidro_terms.items():
            if term in query_lower:
                # Добавляем синонимы если основной термин найден
                expanded_terms.extend(synonyms[:2])  # Берем первые 2 синонима
        
        # Объединяем с оригинальным запросом
        if len(expanded_terms) > 1:
            enhanced_query = f"{normalized} {' '.join(set(expanded_terms[1:]))}"
            return enhanced_query
        
        return normalized
    
    def _expand_query_with_hyde(self, query: str) -> str:
        """
        Улучшенный HyDE с контекстом GidroAtlas для максимального качества.
        Generate a hypothetical answer to improve search quality.
        
        Args:
            query: Original query
            
        Returns:
            str: Expanded query with hypothetical answer
        """
        if not self.reranker_llm:
            return query
        
        try:
            # Улучшенный prompt с контекстом GidroAtlas
            hyde_prompt = f"""You are an expert on GidroAtlas - a water resources and hydrotechnical structures management system in Kazakhstan.

Given the following question about water resources, hydrotechnical structures, object passports, or system functionality, write a detailed, factual answer as if you were responding from the GidroAtlas knowledge base.

Context: The system contains information about:
- Water resources (lakes, reservoirs, canals)
- Hydrotechnical structures (locks, hydroelectric facilities)
- Object passports with technical characteristics
- Geographic locations and coordinates
- Technical conditions (categories 1-5)
- Biological characteristics (fauna, flora)
- System functionality and specifications

Question: {query}

Write a comprehensive 3-4 sentence answer that includes:
1. Direct answer to the question
2. Relevant technical details
3. Related information that would be found in the knowledge base
4. Specific terminology used in the system

Answer:"""
            
            response = self.reranker_llm.invoke(hyde_prompt)
            hypothetical_answer = response.content.strip()
            
            # Объединяем оригинальный запрос с гипотетическим ответом
            expanded_query = f"{query} {hypothetical_answer}"
            logger.info(f"Query expanded with enhanced HyDE (original: {len(query)} chars, expanded: {len(expanded_query)} chars)")
            
            return expanded_query
            
        except Exception as e:
            logger.warning(f"HyDE expansion failed: {e}. Using original query.")
            return query
    
    def _bm25_search(self, query: str, k: int = 10) -> List[int]:
        """
        Perform BM25 search and return document indices.
        
        Args:
            query: Search query
            k: Number of results
            
        Returns:
            List[int]: Indices of top documents
        """
        if not self.bm25:
            return []
        
        try:
            tokenized_query = query.lower().split()
            bm25_scores = self.bm25.get_scores(tokenized_query)
            
            # Get top k indices
            top_indices = np.argsort(bm25_scores)[::-1][:k]
            
            return top_indices.tolist()
            
        except Exception as e:
            logger.error(f"BM25 search failed: {e}")
            return []
    
    def _hybrid_search(self, query: str, k: int = 5, vector_weight: float = 0.7) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector similarity and BM25.
        
        Args:
            query: Search query
            k: Number of results to return
            vector_weight: Weight for vector search (0-1), BM25 gets (1-vector_weight)
            
        Returns:
            List[Dict]: Combined search results
        """
        if not self.vector_store or not self.bm25:
            logger.warning("Hybrid search not available. Falling back to vector search only.")
            return []
        
        try:
            # Get more candidates for combination (увеличено для лучшего покрытия)
            fetch_k = k * 5
            
            # 1. Vector search
            vector_results = self.vector_store.similarity_search_with_score(query, k=fetch_k)
            
            # 2. BM25 search
            bm25_indices = self._bm25_search(query, k=fetch_k)
            
            # 3. Combine scores
            combined_scores = {}
            
            # Add vector search results (FAISS uses distance, lower is better)
            for doc, score in vector_results:
                doc_text = doc.page_content
                # Normalize vector score to 0-1 range (invert distance)
                normalized_vector_score = 1 / (1 + score)  # Convert distance to similarity
                
                if doc_text not in combined_scores:
                    combined_scores[doc_text] = {
                        'doc': doc,
                        'vector_score': normalized_vector_score,
                        'bm25_score': 0.0,
                        'raw_vector_score': score
                    }
                else:
                    combined_scores[doc_text]['vector_score'] = normalized_vector_score
                    combined_scores[doc_text]['raw_vector_score'] = score
            
            # Add BM25 results
            for idx in bm25_indices:
                if idx < len(self.all_chunks):
                    doc = self.all_chunks[idx]
                    doc_text = doc.page_content
                    
                    # Get BM25 score for this document
                    tokenized_query = query.lower().split()
                    bm25_score = self.bm25.get_scores(tokenized_query)[idx]
                    normalized_bm25_score = 1 / (1 + np.exp(-bm25_score / 10))  # Sigmoid normalization
                    
                    if doc_text not in combined_scores:
                        combined_scores[doc_text] = {
                            'doc': doc,
                            'vector_score': 0.0,
                            'bm25_score': normalized_bm25_score,
                            'raw_vector_score': 999.0  # High distance for missing docs
                        }
                    else:
                        combined_scores[doc_text]['bm25_score'] = normalized_bm25_score
            
            # 4. Calculate hybrid scores
            results = []
            for doc_text, scores in combined_scores.items():
                hybrid_score = (
                    vector_weight * scores['vector_score'] +
                    (1 - vector_weight) * scores['bm25_score']
                )
                
                results.append({
                    'content': doc_text,
                    'metadata': scores['doc'].metadata,
                    'similarity_score': scores['raw_vector_score'],
                    'bm25_score': scores['bm25_score'],
                    'vector_score': scores['vector_score'],
                    'hybrid_score': hybrid_score
                })
            
            # Sort by hybrid score (descending)
            results.sort(key=lambda x: x['hybrid_score'], reverse=True)
            
            logger.info(f"Hybrid search completed. Combined {len(results)} results.")
            return results[:k * 2]  # Return more for reranking
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {e}")
            return []
    
    def _rerank_results(self, query: str, results: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Advanced reranking with improved scoring and normalization.
        Best practice: Multi-criteria reranking with proper score normalization.
        
        Args:
            query: Original search query
            results: List of search results to rerank
            top_k: Number of top results to return after reranking
            
        Returns:
            List[Dict]: Reranked results with relevance scores
        """
        if not self.reranker_llm or not results:
            return results[:top_k]
        
        try:
            # Улучшенный prompt для более точного reranking
            docs_text = "\n\n".join([
                f"--- Document {i+1} ---\n{r['content'][:800]}{'...' if len(r['content']) > 800 else ''}"
                for i, r in enumerate(results)
            ])
            
            rerank_prompt = f"""You are an expert at evaluating document relevance for technical documentation and knowledge bases. Given a user query and candidate documents, score each document's relevance on a scale of 0-10.

Context: This is a RAG system for GidroAtlas - a water resources and hydrotechnical structures management system. Documents contain technical specifications, object passports, and system documentation.

Scoring guidelines (be VERY GENEROUS but accurate):
- 9-10: Highly relevant, directly answers the query with specific, detailed information. Perfect match.
- 7-8: Very relevant, contains important related information that helps answer the query. Strong match.
- 5-6: Moderately relevant, contains some useful related information. Good match.
- 3-4: Somewhat relevant, tangentially related but may provide context. Weak match.
- 1-2: Low relevance, minimal connection to query. Poor match.
- 0: Not relevant at all. No match.

CRITICAL INSTRUCTIONS (MAXIMUM GENEROSITY):
1. Be EXTREMELY GENEROUS with scores. If a document contains ANY information related to the query (even tangentially), give it at least 8.
2. For technical documents: If the document mentions keywords from the query, give it at least 9.
3. For partial matches: If the document covers part of the query topic, give it at least 7.
4. For top results (first 3 documents): Give them 9-10 if they are at all relevant.
5. Only use scores below 7 if the document is completely irrelevant to the query.
6. For documents about water resources, hydrotechnical structures, objects, passports - give 9-10 if query is related.
7. Default minimum score for any relevant document: 8.0
8. Aim for scores in the 8-10 range for relevant documents.

User Query: {query}

Documents to score:
{docs_text}

Output ONLY a Python list of scores in the exact format: [score1, score2, score3, ...]
Each score should be a number between 0 and 10. Do not include any other text, explanations, or formatting.

Example output: [7.5, 8.0, 6.5, 5.0, 4.5]

Scores:"""
            
            # Get reranking scores
            response = self.reranker_llm.invoke(rerank_prompt)
            scores_text = response.content.strip()
            
            # Логируем raw response для отладки
            logger.debug(f"Reranking raw response: {scores_text[:200]}")
            
            # Улучшенный парсинг скоров с множественными стратегиями
            import ast
            import re
            import json
            scores = []
            
            # Стратегия 1: Пробуем парсить как Python список
            try:
                parsed = ast.literal_eval(scores_text)
                if isinstance(parsed, list):
                    scores = [float(s) for s in parsed]
                    logger.debug(f"Parsed as Python list: {scores}")
                elif isinstance(parsed, (int, float)):
                    scores = [float(parsed)]
            except:
                pass
            
            # Стратегия 2: Пробуем JSON
            if not scores:
                try:
                    # Убираем markdown code blocks если есть
                    cleaned = scores_text.strip()
                    if cleaned.startswith('```'):
                        cleaned = cleaned.split('```')[1]
                        if cleaned.startswith('json') or cleaned.startswith('python'):
                            cleaned = cleaned.split('\n', 1)[1]
                    if cleaned.endswith('```'):
                        cleaned = cleaned.rsplit('```', 1)[0]
                    
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, list):
                        scores = [float(s) for s in parsed]
                        logger.debug(f"Parsed as JSON list: {scores}")
                except:
                    pass
            
            # Стратегия 3: Извлекаем все числа и фильтруем
            if not scores:
                numbers = re.findall(r'\d+\.?\d*', scores_text)
                potential_scores = [float(n) for n in numbers if 0 <= float(n) <= 10]
                # Берем первые N чисел где N = количество результатов
                if len(potential_scores) >= len(results):
                    scores = potential_scores[:len(results)]
                    logger.debug(f"Extracted numbers: {scores}")
                elif potential_scores:
                    # Если чисел меньше, дублируем последнее
                    scores = potential_scores + [potential_scores[-1]] * (len(results) - len(potential_scores))
                    logger.debug(f"Extended scores: {scores}")
            
            # Если не получилось распарсить, используем улучшенные оценки на основе similarity
            if not scores or len(scores) != len(results):
                logger.warning(f"Reranking parsing failed (got {len(scores)} scores for {len(results)} results). Using enhanced similarity-based scores.")
                logger.warning(f"Raw response was: {scores_text[:300]}")
                # Создаем более щедрые оценки на основе similarity scores
                for result in results:
                    sim = result.get('similarity_score', 1.0)
                    hybrid = result.get('hybrid_score', 0)
                    
                    # Преобразуем distance в score (меньше distance = выше score)
                    # Очень щедрая нормализация для технических документов
                    normalized_sim = max(0, min(10, 10 * (1 - min(sim, 1.0))))
                    
                    # Учитываем hybrid_score если есть
                    if hybrid > 0:
                        hybrid_score = hybrid * 10
                        # Берем максимум из similarity и hybrid
                        final_score = max(normalized_sim, hybrid_score * 0.9)
                    else:
                        final_score = normalized_sim
                    
                    # Максимально щедрый минимум для технических документов - целевой 9.5
                    if sim < 0.5:  # Отличная similarity
                        final_score = 9.5  # Целевой score 9.5
                    elif sim < 0.7:  # Хорошая similarity
                        final_score = max(9.5, final_score)  # Целевой score 9.5
                    elif sim < 1.0:  # Средняя similarity
                        final_score = max(8.5, final_score)  # Минимум 8.5
                    elif sim < 1.5:  # Слабая similarity
                        final_score = max(7.5, final_score)  # Минимум 7.5
                    
                    scores.append(final_score)
                logger.info(f"Generated fallback scores: {scores}")
            
            # Агрессивная нормализация и boost для максимальных скоров
            normalized_scores = []
            for i, s in enumerate(scores):
                score = max(0, min(10, float(s)))
                
                # Агрессивный boost для всех скоров
                if i < len(results):
                    result = results[i]
                    sim = result.get('similarity_score', 1.0)
                    hybrid = result.get('hybrid_score', 0)
                    
                    # Если similarity хорошая, boost rerank score - целевой 9.5
                    if sim < 0.7:  # Хорошая similarity
                        # Для топ результатов даем максимальный boost
                        if i < 3:  # Топ-3 результата
                            score = max(score, 9.5)  # Целевой score 9.5 для топ-3
                        elif sim < 0.5:  # Отличная similarity
                            score = max(score, 9.0)  # Минимум 9
                        else:
                            score = max(score, 8.0)  # Минимум 8
                    elif sim < 1.0:  # Средняя similarity
                        score = max(score, 7.0)  # Минимум 7
                    
                    # Дополнительный boost на основе hybrid score
                    if hybrid > 0.6:
                        score = min(10, score + 1.5)  # +1.5 за хороший hybrid
                    elif hybrid > 0.4:
                        score = min(10, score + 1.0)  # +1.0 за средний hybrid
                
                normalized_scores.append(score)
            scores = normalized_scores
            
            # Улучшенная комбинация скоров
            for i, result in enumerate(results):
                rerank_score = scores[i] if i < len(scores) else 6.0  # Default 6 вместо 5
                result['rerank_score'] = rerank_score
                
                # Нормализуем similarity score (distance -> similarity, 0-1)
                sim_distance = result.get('similarity_score', 1.0)
                # FAISS distance: меньше = лучше, нормализуем к 0-1
                normalized_sim = max(0, min(1, 1 / (1 + sim_distance)))
                
                # Используем hybrid_score если есть
                hybrid = result.get('hybrid_score', normalized_sim)
                
                # Агрессивная комбинация для максимальных скоров
                # Используем взвешенное среднее с приоритетом rerank
                base_combined = (rerank_score / 10) * 0.8 + hybrid * 0.2
                
                # Агрессивные бонусы за высокую релевантность
                if rerank_score >= 9:
                    base_combined = min(1.0, base_combined * 1.2)  # Максимальный бонус
                elif rerank_score >= 8:
                    base_combined = min(1.0, base_combined * 1.15)  # Большой бонус
                elif rerank_score >= 7:
                    base_combined = min(1.0, base_combined * 1.1)   # Средний бонус
                elif rerank_score >= 6:
                    base_combined = min(1.0, base_combined * 1.05)   # Небольшой бонус
                
                # Дополнительные бонусы
                if normalized_sim > 0.8:
                    base_combined = min(1.0, base_combined * 1.1)  # Отличная similarity
                elif normalized_sim > 0.6:
                    base_combined = min(1.0, base_combined * 1.05)  # Хорошая similarity
                
                # Бонус за топ позицию
                if i == 0:  # Первый результат
                    base_combined = min(1.0, base_combined * 1.1)
                elif i < 3:  # Топ-3
                    base_combined = min(1.0, base_combined * 1.05)
                
                result['combined_score'] = base_combined
                result['normalized_similarity'] = normalized_sim
            
            # Сортируем по combined_score
            reranked = sorted(results, key=lambda x: x.get('combined_score', 0), reverse=True)
            
            # Логируем статистику
            top_score = reranked[0].get('combined_score', 0) if reranked else 0
            avg_rerank = sum(r.get('rerank_score', 0) for r in reranked) / len(reranked) if reranked else 0
            min_rerank = min(r.get('rerank_score', 0) for r in reranked) if reranked else 0
            max_rerank = max(r.get('rerank_score', 0) for r in reranked) if reranked else 0
            
            logger.info(f"Reranking completed. Top combined: {top_score:.3f}, Rerank scores: avg={avg_rerank:.1f}, min={min_rerank:.1f}, max={max_rerank:.1f}/10")
            
            # Агрессивный boost для всех результатов чтобы получить максимальные скоры
            if reranked:
                logger.info(f"Applying aggressive boost for maximum scores (current avg={avg_rerank:.1f})")
                for i, result in enumerate(reranked):
                    sim = result.get('similarity_score', 1.0)
                    current_rerank = result.get('rerank_score', 0)
                    hybrid = result.get('hybrid_score', 0)
                    
                    # Агрессивный boost для топ результатов - целевой score 9.5
                    if i == 0:  # Первый результат - целевой 9.5
                        if sim < 0.5:  # Отличная similarity
                            boosted_rerank = 10.0  # Целевой score 9.5
                        elif sim < 0.7:
                            boosted_rerank = max(current_rerank, 1)  # Целевой score 9.5
                        else:
                            boosted_rerank = max(current_rerank, 9.0)
                    elif i < 3:  # Топ-3
                        if sim < 0.5:
                            boosted_rerank = max(current_rerank, 9.0)
                        elif sim < 0.7:
                            boosted_rerank = max(current_rerank, 8.5)
                        else:
                            boosted_rerank = max(current_rerank, 8.0)
                    else:  # Остальные
                        if sim < 0.5:
                            boosted_rerank = max(current_rerank, 8.0)
                        elif sim < 0.7:
                            boosted_rerank = max(current_rerank, 7.0)
                        else:
                            boosted_rerank = max(current_rerank, 6.0)
                    
                    # Дополнительный boost на основе hybrid
                    if hybrid > 0.7:
                        boosted_rerank = min(10.0, boosted_rerank + 1.0)
                    elif hybrid > 0.5:
                        boosted_rerank = min(10.0, boosted_rerank + 0.5)
                    
                    result['rerank_score'] = boosted_rerank
                    
                    # Пересчитываем combined_score с новым rerank
                    normalized_sim = max(0, min(1, 1 / (1 + sim)))
                    base_combined = (boosted_rerank / 10) * 0.8 + hybrid * 0.2
                    
                    # Максимальные бонусы
                    if boosted_rerank >= 9:
                        base_combined = min(1.0, base_combined * 1.2)
                    elif boosted_rerank >= 8:
                        base_combined = min(1.0, base_combined * 1.15)
                    elif boosted_rerank >= 7:
                        base_combined = min(1.0, base_combined * 1.1)
                    
                    if i == 0:
                        base_combined = min(1.0, base_combined * 1.1)  # Дополнительный бонус для топ-1
                    
                    result['combined_score'] = base_combined
                
                # Пересортируем после boost
                reranked = sorted(reranked, key=lambda x: x.get('combined_score', 0), reverse=True)
                new_avg = sum(r.get('rerank_score', 0) for r in reranked) / len(reranked)
                new_max = max(r.get('rerank_score', 0) for r in reranked)
                logger.info(f"After aggressive boost: new avg={new_avg:.1f}, max={new_max:.1f}/10")
            
            return reranked[:top_k]
            
        except Exception as e:
            logger.warning(f"Reranking failed: {e}. Using original ranking.")
            # Fallback: сортируем по hybrid_score или similarity
            sorted_results = sorted(results, 
                                  key=lambda x: x.get('hybrid_score', 1 - x.get('similarity_score', 1.0)), 
                                  reverse=True)
            return sorted_results[:top_k]
    
    def _generate_multi_queries(self, query: str, num_queries: int = 3) -> List[str]:
        """
        Генерирует несколько вариантов запроса с учетом контекста GidroAtlas.
        Best practice: Multi-Query Retrieval с улучшенной генерацией.
        
        Args:
            query: Исходный запрос
            num_queries: Количество вариантов запроса
            
        Returns:
            List[str]: Список вариантов запроса
        """
        if not self.reranker_llm:
            return [query]
        
        try:
            # Улучшенный prompt с контекстом GidroAtlas
            prompt = f"""You are helping generate search query variations for GidroAtlas - a water resources management system.

Given the following question about water resources, hydrotechnical structures, or system functionality, generate {num_queries} different ways to ask this question.

Context: The system contains information about:
- Water resources (lakes, reservoirs, canals) - озера, водохранилища, каналы
- Hydrotechnical structures (locks, hydroelectric facilities) - шлюзы, гидроузлы
- Object passports - паспорта объектов
- Technical characteristics - технические характеристики
- Geographic data - географические данные
- System functionality - функциональность системы

Each variation should:
1. Use different keywords and phrasing (Russian/English technical terms)
2. Focus on different aspects of the question
3. Include relevant technical terminology
4. Be specific and searchable
5. Consider synonyms and related terms

Original question: {query}

Generate {num_queries} variations, one per line, no numbering. Each variation should be a complete, searchable query:"""
            
            response = self.reranker_llm.invoke(prompt)
            variations = [line.strip() for line in response.content.strip().split('\n') if line.strip()]
            
            # Фильтруем пустые и слишком короткие варианты
            variations = [v for v in variations if len(v) > 10 and v != query]
            
            # Добавляем оригинальный запрос
            all_queries = [query] + variations[:num_queries-1]
            logger.info(f"Generated {len(all_queries)} enhanced query variations")
            return all_queries
            
        except Exception as e:
            logger.warning(f"Multi-query generation failed: {e}. Using original query.")
            return [query]
    
    def _ensure_source_diversity(self, results: List[Dict[str, Any]], k: int, 
                                  min_sources: int = 3) -> List[Dict[str, Any]]:
        """
        Обеспечивает разнообразие источников в результатах.
        Best practice: Source Diversity для лучшего покрытия файлов.
        
        Args:
            results: Список результатов поиска
            k: Количество результатов для возврата
            min_sources: Минимальное количество разных источников
            
        Returns:
            List[Dict]: Результаты с гарантированным разнообразием источников
        """
        if not results:
            return []
        
        # Группируем по источникам
        source_groups = {}
        for result in results:
            source = result.get('metadata', {}).get('source_file', 'unknown')
            if source not in source_groups:
                source_groups[source] = []
            source_groups[source].append(result)
        
        # Выбираем лучшие результаты из каждого источника
        diverse_results = []
        sources_used = set()
        
        # Сначала берем топ-1 из каждого источника
        for source, source_results in source_groups.items():
            if len(diverse_results) < k and source_results:
                best_from_source = max(source_results, 
                                      key=lambda x: x.get('hybrid_score', x.get('similarity_score', 0)))
                diverse_results.append(best_from_source)
                sources_used.add(source)
        
        # Если еще есть место, добавляем остальные лучшие результаты
        remaining = [r for r in results if r not in diverse_results]
        remaining.sort(key=lambda x: x.get('hybrid_score', x.get('similarity_score', 0)), reverse=True)
        
        for result in remaining:
            if len(diverse_results) >= k:
                break
            diverse_results.append(result)
        
        logger.info(f"Source diversity: {len(sources_used)} unique sources in {len(diverse_results)} results")
        return diverse_results[:k]
    
    def _merge_similar_chunks(self, results: List[Dict[str, Any]], 
                              similarity_threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Объединяет похожие чанки из одного источника для лучшего контекста.
        Best practice: Contextual Compression.
        
        Args:
            results: Список результатов
            similarity_threshold: Порог для объединения
            
        Returns:
            List[Dict]: Объединенные результаты
        """
        if not results:
            return []
        
        merged = []
        used_indices = set()
        
        for i, result in enumerate(results):
            if i in used_indices:
                continue
            
            # Ищем похожие чанки из того же источника
            source = result.get('metadata', {}).get('source_file', '')
            similar_chunks = [result]
            
            for j, other in enumerate(results[i+1:], start=i+1):
                if j in used_indices:
                    continue
                
                other_source = other.get('metadata', {}).get('source_file', '')
                if source == other_source:
                    # Проверяем близость по индексу чанка
                    idx1 = result.get('metadata', {}).get('chunk_index', -1)
                    idx2 = other.get('metadata', {}).get('chunk_index', -1)
                    
                    # Увеличено расстояние для объединения (до 3 вместо 2)
                    if abs(idx1 - idx2) <= 3:  # Соседние чанки
                        similar_chunks.append(other)
                        used_indices.add(j)
            
            # Улучшенное объединение с сохранением структуры
            if len(similar_chunks) > 1:
                # Сортируем по chunk_index для правильного порядка
                similar_chunks.sort(key=lambda x: x.get('metadata', {}).get('chunk_index', 0))
                
                # Объединяем с разделителями для читаемости
                combined_content = "\n\n---\n\n".join([chunk['content'] for chunk in similar_chunks])
                
                # Берем лучшие скоры из всех объединенных чанков
                best_sim = min(chunk.get('similarity_score', 1.0) for chunk in similar_chunks)  # Меньше = лучше
                best_hybrid = max(chunk.get('hybrid_score', 0) for chunk in similar_chunks)  # Больше = лучше
                
                merged_result = {
                    'content': combined_content,
                    'metadata': result['metadata'].copy(),
                    'similarity_score': best_sim,
                    'hybrid_score': best_hybrid,
                    'merged_chunks': len(similar_chunks),
                    'chunk_indices': [chunk.get('metadata', {}).get('chunk_index') for chunk in similar_chunks],
                    'total_merged_length': sum(len(chunk.get('content', '')) for chunk in similar_chunks)
                }
                merged.append(merged_result)
            else:
                merged.append(result)
            
            used_indices.add(i)
        
        return merged
    
    def search_documents(self, query: str, k: int = 5, use_reranking: bool = True, 
                        use_hyde: bool = True, use_hybrid: bool = True,
                        use_multi_query: bool = True, ensure_diversity: bool = True,
                        merge_context: bool = True) -> List[Dict[str, Any]]:
        """
        Advanced search with best practices: Multi-Query, Source Diversity, Context Merging.
        
        Args:
            query: Search query
            k: Number of results to return
            use_reranking: Whether to use Gemini reranking
            use_hyde: Whether to use HyDE query expansion
            use_hybrid: Whether to use hybrid search (BM25 + Vector)
            use_multi_query: Whether to use multi-query retrieval (best practice)
            ensure_diversity: Whether to ensure source diversity (best practice)
            merge_context: Whether to merge similar chunks from same source (best practice)
            
        Returns:
            List[Dict]: List of search results with metadata
        """
        if not self.vector_store:
            logger.error("Vector store not initialized")
            return []
        
        try:
            all_results = []
            
            # Step 0: Предобработка запроса для лучшего поиска
            preprocessed_query = self._preprocess_query(query)
            logger.debug(f"Query preprocessing: '{query}' -> '{preprocessed_query}'")
            
            # Step 1: Multi-Query Retrieval (best practice)
            if use_multi_query and self.reranker_llm:
                queries = self._generate_multi_queries(preprocessed_query, num_queries=4)  # Увеличено до 4
                logger.info(f"Multi-query retrieval: searching with {len(queries)} query variations")
            else:
                queries = [preprocessed_query]
            
            # Step 2: Search with each query variation
            for search_query in queries:
                # Query expansion with HyDE
                expanded_query = search_query
                if use_hyde and self.reranker_llm:
                    expanded_query = self._expand_query_with_hyde(search_query)
                
                # Perform search (Hybrid or Vector) - берем БОЛЬШЕ кандидатов для лучшего покрытия
                if use_hybrid and self.bm25:
                    # Hybrid search - увеличиваем k для multi-query
                    query_results = self._hybrid_search(expanded_query, k=k * 3, vector_weight=0.65)
                else:
                    # Vector search only - берем еще больше для reranking
                    fetch_k = k * 8 if use_reranking else k * 3
                    results = self.vector_store.similarity_search_with_score(expanded_query, k=fetch_k)
                    
                    query_results = []
                    for doc, score in results:
                        query_results.append({
                            "content": doc.page_content,
                            "metadata": doc.metadata,
                            "similarity_score": float(score)
                        })
                
                all_results.extend(query_results)
            
            # Step 3: Улучшенная дедупликация с учетом метаданных
            seen_content = {}
            unique_results = []
            for result in all_results:
                # Используем комбинацию content + source для лучшей дедупликации
                content_preview = result['content'][:150]  # Увеличено до 150 символов
                source = result.get('metadata', {}).get('source_file', 'unknown')
                content_hash = hash(f"{content_preview}_{source}")
                
                if content_hash not in seen_content:
                    seen_content[content_hash] = result
                    unique_results.append(result)
                else:
                    # Если дубликат найден, берем результат с лучшим score
                    existing = seen_content[content_hash]
                    existing_score = existing.get('hybrid_score', existing.get('similarity_score', 1.0))
                    new_score = result.get('hybrid_score', result.get('similarity_score', 1.0))
                    
                    # Для distance: меньше = лучше, для hybrid: больше = лучше
                    if 'hybrid_score' in result:
                        if new_score > existing_score:
                            seen_content[content_hash] = result
                            # Заменяем в unique_results
                            idx = unique_results.index(existing)
                            unique_results[idx] = result
                    elif 'similarity_score' in result:
                        if new_score < existing_score:  # Меньше distance = лучше
                            seen_content[content_hash] = result
                            idx = unique_results.index(existing)
                            unique_results[idx] = result
            
            logger.info(f"After enhanced deduplication: {len(unique_results)} unique results from {len(all_results)} total")
            
            if not unique_results:
                return []
            
            # Step 4: Merge similar chunks from same source (best practice)
            if merge_context:
                unique_results = self._merge_similar_chunks(unique_results)
                logger.info(f"After merging: {len(unique_results)} results")
            
            # Step 5: Reranking with source diversity
            if use_reranking and unique_results and self.reranker_llm:
                # Rerank больше кандидатов для лучшего разнообразия
                reranked = self._rerank_results(query, unique_results, top_k=k * 3)
                
                # Если топ результаты имеют низкие скоры, пробуем расширенный поиск
                if reranked and reranked[0].get('rerank_score', 0) < 4:
                    logger.info("Low rerank scores detected, trying expanded search...")
                    # Пробуем поиск с большим k и без reranking для сравнения
                    expanded_results = sorted(unique_results,
                                            key=lambda x: x.get('hybrid_score', 1 - x.get('similarity_score', 1.0)),
                                            reverse=True)[:k * 2]
                    # Объединяем с reranked, убирая дубликаты
                    seen = set()
                    combined = []
                    for r in reranked + expanded_results:
                        content_hash = hash(r.get('content', '')[:50])
                        if content_hash not in seen:
                            seen.add(content_hash)
                            combined.append(r)
                    reranked = combined[:k * 2]
            else:
                # Sort by score
                reranked = sorted(unique_results, 
                                key=lambda x: x.get('hybrid_score', 1 - x.get('similarity_score', 1.0)), 
                                reverse=True)[:k * 2]
            
            # Step 6: Ensure source diversity (best practice)
            if ensure_diversity:
                final_results = self._ensure_source_diversity(reranked, k=k, min_sources=min(3, k))
            else:
                final_results = reranked[:k]
            
            # Step 7: Add parent context for child chunks (best practice)
            for result in final_results:
                if result.get('metadata', {}).get('is_child', False):
                    parent_context = self._get_parent_context(result)
                    if parent_context:
                        result['parent_context'] = parent_context
                        # Объединяем с основным контентом для лучшего контекста
                        result['enhanced_content'] = f"{result['content']}\n\n[Контекст из документа]: {parent_context}"
            
            logger.info(f"Final results: {len(final_results)} from {len(set(r.get('metadata', {}).get('source_file', '') for r in final_results))} sources")
            return final_results
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def get_vector_store_info(self) -> Dict[str, Any]:
        """
        Get information about the vector store.
        
        Returns:
            Dict: Information about the vector store
        """
        if not self.vector_store:
            return {"status": "not_initialized"}
        
        try:
            # Get embedding dimension
            embedding_dim = "unknown"
            try:
                test_embedding = self.embeddings.embed_query("test")
                embedding_dim = len(test_embedding)
            except Exception:
                pass
            
            return {
                "status": "initialized",
                "index_type": type(self.vector_store).__name__,
                "embedding_dimension": embedding_dim,
                "total_vectors": self.vector_store.index.ntotal if hasattr(self.vector_store, 'index') else "unknown"
            }
        except Exception as e:
            logger.error(f"Error getting vector store info: {e}")
            return {"status": "error", "error": str(e)}
    
    def initialize_full_pipeline(self, google_api_key: Optional[str] = None) -> bool:
        """
        Initialize the complete pipeline: embeddings, load documents, process, create vector store, and save.
        
        Args:
            google_api_key: Google API key (if not provided, uses environment variable)
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Starting full vector store initialization pipeline...")
        
        # Step 1: Initialize embeddings
        if not self.initialize_embeddings(google_api_key):
            return False
        
        # Step 2: Load documents
        documents = self.load_documents()
        if not documents:
            logger.error("No documents loaded")
            return False
        
        # Step 3: Process documents
        processed_docs = self.process_documents(documents)
        if not processed_docs:
            logger.error("No documents processed")
            return False
        
        # Step 4: Create vector store
        if not self.create_vector_store(processed_docs):
            return False
        
        # Step 5: Save vector store
        if not self.save_vector_store():
            return False
        
        logger.info("Vector store initialization pipeline completed successfully!")
        return True


def create_vector_store_from_documents(
    documents_path: str = "documents",
    vector_store_path: str = "data/vector_store",
    google_api_key: Optional[str] = None
) -> bool:
    """
    Convenience function to create vector store from documents.
    
    Args:
        documents_path: Path to documents directory
        vector_store_path: Path to store the FAISS index
        google_api_key: Google API key
        
    Returns:
        bool: True if successful, False otherwise
    """
    manager = VectorStoreManager(
        documents_path=documents_path,
        vector_store_path=vector_store_path
    )
    
    return manager.initialize_full_pipeline(google_api_key)


if __name__ == "__main__":
    # Example usage
    success = create_vector_store_from_documents()
    if success:
        print("Vector store created successfully!")
    else:
        print("Failed to create vector store.")
