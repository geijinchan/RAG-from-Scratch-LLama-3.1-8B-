"""
RAG Pipeline Module
Orchestrates the complete RAG workflow.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path
from src.pdf_processor import PDFProcessor
from src.embedding_manager import EmbeddingManager
from src.retrieval import SemanticRetriever, RetrieverConfig
from src.llm_handler import LLMHandler
from config.settings import (
    EMBEDDING_MODEL,
    LLM_MODEL_ID,
    DEVICE,
    RETRIEVAL_TOP_K,
    EMBEDDINGS_DIR,
    LLM_TEMPERATURE,
    LLM_MAX_NEW_TOKENS
)

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Complete RAG (Retrieval-Augmented Generation) pipeline.
    Orchestrates PDF processing, embedding, retrieval, and generation.
    """
    
    def __init__(
        self,
        embedding_model: str = EMBEDDING_MODEL,
        llm_model: str = LLM_MODEL_ID,
        device: str = DEVICE,
        load_llm: bool = True
    ):
        """
        Initialize RAG pipeline.
        
        Args:
            embedding_model: Embedding model name
            llm_model: LLM model ID
            device: Device to use
            load_llm: Whether to load LLM immediately
        """
        logger.info("Initializing RAG Pipeline")
        
        self.device = device
        self.pdf_processor = PDFProcessor() # Initialize PDF processor
        self.embedding_manager = EmbeddingManager(
            model_name=embedding_model,
            device=device
        )
        
        self.llm_handler: Optional[LLMHandler] = None
        if load_llm:
            logger.info("Loading LLM...")
            self.llm_handler = LLMHandler(
                model_id=llm_model,
                device=device
            )
        
        self.retriever: Optional[SemanticRetriever] = None
        self.chunks: List[Dict[str, Any]] = []
        
        logger.info("RAG Pipeline initialized successfully")
    
    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        Process PDF document.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            List of processed chunks
        """
        logger.info(f"Processing PDF: {pdf_path}")
        
        try:
            chunks = self.pdf_processor.process_pdf(pdf_path)
            logger.info(f"Processed {len(chunks)} chunks from PDF")
            return chunks
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise
    
    def embed_chunks(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate embeddings for chunks.
        
        Args:
            chunks: List of chunks to embed
            
        Returns:
            Chunks with embeddings
        """
        logger.info(f"Embedding {len(chunks)} chunks")
        
        try:
            embedded_chunks = self.embedding_manager.embed_chunks(chunks)
            logger.info(f"Successfully embedded {len(embedded_chunks)} chunks")
            return embedded_chunks
        except Exception as e:
            logger.error(f"Error embedding chunks: {str(e)}")
            raise
    
    def setup_retriever(self, chunks: List[Dict[str, Any]], top_k: int = RETRIEVAL_TOP_K):
        """
        Setup semantic retriever with chunks.
        
        Args:
            chunks: List of chunks with embeddings
            top_k: Number of top results to retrieve
        """
        logger.info(f"Setting up retriever with {len(chunks)} chunks")
        
        try:
            config = RetrieverConfig(top_k=top_k)
            self.retriever = SemanticRetriever(
                chunks_with_embeddings=chunks,
                embedding_manager=self.embedding_manager,
                config=config
            )
            self.chunks = chunks
            logger.info("Retriever setup complete")
        except Exception as e:
            logger.error(f"Error setting up retriever: {str(e)}")
            raise
    
    def load_llm(self, model_id: str = LLM_MODEL_ID):
        """
        Load language model.
        
        Args:
            model_id: Model ID to load
        """
        logger.info(f"Loading LLM: {model_id}")
        
        try:
            self.llm_handler = LLMHandler(
                model_id=model_id,
                device=self.device
            )
            logger.info("LLM loaded successfully")
        except Exception as e:
            logger.error(f"Error loading LLM: {str(e)}")
            raise
    
    def retrieve(
        self,
        query: str,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for query.
        
        Args:
            query: Query string
            top_k: Number of results to return
            
        Returns:
            Retrieved chunks
        """
        if self.retriever is None:
            raise RuntimeError("Retriever not initialized. Call setup_retriever first.")
        
        try:
            logger.info(f"Retrieving chunks for query: '{query}'")
            chunks = self.retriever.retrieve_with_metadata(query, top_k=top_k)
            logger.info(f"Retrieved {len(chunks)} chunks")
            return chunks
        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            raise
    
    def generate(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        temperature: float = LLM_TEMPERATURE,
        max_new_tokens: int = LLM_MAX_NEW_TOKENS
    ) -> str:
        """
        Generate answer based on query and context.
        
        Args:
            query: Query string
            context_chunks: Retrieved context chunks
            temperature: Generation temperature
            max_new_tokens: Maximum tokens to generate
            
        Returns:
            Generated answer
        """
        if self.llm_handler is None:
            raise RuntimeError("LLM not loaded. Call load_llm first.")
        
        try:
            logger.info(f"Generating answer for query: '{query}'")
            
            # Format prompt with context
            prompt = self.llm_handler.format_prompt_with_context(query, context_chunks)
            
            # Generate
            answer = self.llm_handler.generate(
                prompt=prompt,
                temperature=temperature,
                max_new_tokens=max_new_tokens
            )
            
            logger.info("Answer generated successfully")
            return answer
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise
    
    def generate_streaming(
        self,
        query: str,
        context_chunks: List[Dict[str, Any]],
        temperature: float = LLM_TEMPERATURE,
        max_new_tokens: int = LLM_MAX_NEW_TOKENS
    ):
        """
        Generate answer with streaming output.
        
        Args:
            query: Query string
            context_chunks: Retrieved context chunks
            temperature: Generation temperature
            max_new_tokens: Maximum tokens to generate
            
        Yields:
            Generated tokens
        """
        if self.llm_handler is None:
            raise RuntimeError("LLM not loaded. Call load_llm first.")
        
        try:
            logger.info(f"Streaming generation for query: '{query}'")
            
            # Format prompt with context
            prompt = self.llm_handler.format_prompt_with_context(query, context_chunks)
            
            # Generate with streaming
            for token in self.llm_handler.generate_streaming(
                prompt=prompt,
                temperature=temperature,
                max_new_tokens=max_new_tokens
            ):
                yield token
            
        except Exception as e:
            logger.error(f"Error in streaming generation: {str(e)}")
            raise
    
    def ask(
        self,
        query: str,
        top_k: int = RETRIEVAL_TOP_K,
        temperature: float = LLM_TEMPERATURE,
        max_new_tokens: int = LLM_MAX_NEW_TOKENS,
        return_context: bool = False
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Complete RAG pipeline in one call.
        
        Args:
            query: User query
            top_k: Number of context chunks to retrieve
            temperature: Generation temperature
            max_new_tokens: Maximum tokens to generate
            return_context: Whether to return retrieved context
            
        Returns:
            Tuple of (answer, context_chunks) or just answer
        """
        # Retrieve
        context_chunks = self.retrieve(query, top_k=top_k)
        
        # Generate
        answer = self.generate(
            query=query,
            context_chunks=context_chunks,
            temperature=temperature,
            max_new_tokens=max_new_tokens
        )
        
        if return_context:
            return answer, context_chunks
        return answer
    
    def pipeline(
        self,
        pdf_path: str,
        query: str = None,
        save_embeddings: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Complete pipeline: PDF processing, embedding, retrieval, and generation.
        
        Args:
            pdf_path: Path to PDF
            query: Optional query to run immediately
            save_embeddings: Whether to save embeddings to disk
            **kwargs: Additional arguments for ask()
            
        Returns:
            Pipeline results
        """
        try:
            logger.info("Starting complete RAG pipeline")
            
            # Process PDF
            chunks = self.process_pdf(pdf_path)
            
            # Embed
            embedded_chunks = self.embed_chunks(chunks)
            
            # Save embeddings if requested
            if save_embeddings:
                self.embedding_manager.save_embeddings(embedded_chunks)
            
            # Setup retriever
            self.setup_retriever(embedded_chunks)
            
            results = {
                "status": "success",
                "chunks_processed": len(embedded_chunks),
                "pdf_path": pdf_path
            }
            
            # If query provided, run full RAG
            if query:
                logger.info(f"Running query: '{query}'")
                answer, context = self.ask(query, return_context=True, **kwargs)
                results["query"] = query
                results["answer"] = answer
                results["context_chunks"] = context
            
            logger.info("Pipeline execution complete")
            return results
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get pipeline statistics.
        
        Returns:
            Statistics dictionary
        """
        stats = {
            "embedding_model": self.embedding_manager.model_name,
            "llm_loaded": self.llm_handler is not None,
            "retriever_initialized": self.retriever is not None,
        }
        
        if self.retriever:
            stats.update(self.retriever.get_chunk_statistics())
        
        if self.llm_handler:
            stats.update(self.llm_handler.get_model_info())
        
        return stats
