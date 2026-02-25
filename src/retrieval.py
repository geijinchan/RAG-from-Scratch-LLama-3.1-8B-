"""
Retrieval Module
Handles semantic search and context retrieval for RAG.
"""

import logging
from typing import List, Dict, Any, Tuple
import numpy as np
import torch
from sentence_transformers import util
from timeit import default_timer as timer
from config.settings import RETRIEVAL_TOP_K, EMBEDDING_MODEL
from src.embedding_manager import EmbeddingManager

logger = logging.getLogger(__name__)


class RetrieverConfig:
    """Configuration for retriever"""
    
    def __init__(
        self,
        top_k: int = RETRIEVAL_TOP_K,
        similarity_threshold: float = 0.0,
        prefer_longer_chunks: bool = False
    ):
        """
        Initialize retriever config.
        
        Args:
            top_k: Number of top results to return
            similarity_threshold: Minimum similarity score
            prefer_longer_chunks: Whether to prefer longer chunks
        """
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold
        self.prefer_longer_chunks = prefer_longer_chunks


class SemanticRetriever:
    """
    Semantic retriever using embeddings and similarity search.
    """
    
    def __init__(
        self,
        chunks_with_embeddings: List[Dict[str, Any]],
        embedding_manager: EmbeddingManager,
        config: RetrieverConfig = None
    ):
        """
        Initialize semantic retriever.
        
        Args:
            chunks_with_embeddings: List of chunks with embeddings
            embedding_manager: EmbeddingManager instance
            config: RetrieverConfig instance
        """
        self.chunks = chunks_with_embeddings
        self.embedding_manager = embedding_manager
        self.config = config or RetrieverConfig()
        
        logger.info(f"Initializing SemanticRetriever with {len(chunks_with_embeddings)} chunks")
        
        # Convert embeddings to tensor
        self.embeddings = self._prepare_embeddings()
    
    def _prepare_embeddings(self) -> torch.Tensor:
        """
        Prepare embeddings tensor from chunks.
        
        Returns:
            Embeddings tensor
        """
        embeddings_list = []
        for chunk in self.chunks:
            if "embedding" in chunk:
                embedding = chunk["embedding"]
                if isinstance(embedding, np.ndarray):
                    embedding = torch.tensor(embedding, dtype=torch.float32)
                embeddings_list.append(embedding)
        
        if not embeddings_list:
            logger.error("No embeddings found in chunks")
            raise ValueError("No embeddings found in chunks")
        
        embeddings = torch.stack(embeddings_list)
        
        # Move embeddings to the same device as the embedding model
        device = self.embedding_manager.device
        embeddings = embeddings.to(device)
        
        logger.info(f"Prepared embeddings tensor with shape: {embeddings.shape} on device: {device}")
        return embeddings
    
    def retrieve(
        self,
        query: str,
        top_k: int = None,
        return_scores: bool = True,
        print_time: bool = False
    ) -> Tuple[List[Dict[str, Any]], List[float]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: Query string
            top_k: Number of top results to return
            return_scores: Whether to return similarity scores
            print_time: Whether to print execution time
            
        Returns:
            Tuple of (retrieved chunks, scores)
        """
        if top_k is None:
            top_k = self.config.top_k
        
        try:
            # Embed query
            query_embedding = self.embedding_manager.generate_embeddings(
                query,
                convert_to_tensor=True,
                show_progress_bar=False
            )
            
            # Compute similarity scores
            start_time = timer()
            scores = util.dot_score(query_embedding, self.embeddings)[0]
            end_time = timer()
            
            if print_time:
                logger.info(f"Similarity calculation time: {end_time - start_time:.5f}s for {len(self.embeddings)} embeddings")
            
            # Get top-k results
            top_scores, indices = torch.topk(scores, k=min(top_k, len(self.chunks)))
            
            # Filter by threshold if set
            if self.config.similarity_threshold > 0:
                mask = top_scores >= self.config.similarity_threshold
                top_scores = top_scores[mask]
                indices = indices[mask]
            
            # Retrieve chunks
            retrieved_chunks = [self.chunks[idx] for idx in indices]
            
            logger.info(f"Retrieved {len(retrieved_chunks)} chunks for query: '{query}'")
            
            if return_scores:
                scores_list = [score.item() for score in top_scores]
                return retrieved_chunks, scores_list
            else:
                return retrieved_chunks, []
        
        except Exception as e:
            logger.error(f"Error retrieving chunks: {str(e)}")
            raise
    
    def retrieve_with_metadata(
        self,
        query: str,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chunks with metadata and scores.
        
        Args:
            query: Query string
            top_k: Number of top results
            
        Returns:
            List of retrieved chunks with scores and metadata
        """
        chunks, scores = self.retrieve(query, top_k=top_k, return_scores=True)
        
        # Add scores and metadata
        for chunk, score in zip(chunks, scores):
            chunk["similarity_score"] = score
        
        return chunks
    
    def update_chunks(self, new_chunks: List[Dict[str, Any]]):
        """
        Update chunks and rebuild embeddings tensor.
        
        Args:
            new_chunks: New chunks list
        """
        logger.info(f"Updating retriever with {len(new_chunks)} new chunks")
        self.chunks = new_chunks
        self.embeddings = self._prepare_embeddings()
    
    def add_chunks(self, new_chunks: List[Dict[str, Any]]):
        """
        Add chunks to existing ones.
        
        Args:
            new_chunks: Chunks to add
        """
        logger.info(f"Adding {len(new_chunks)} chunks to retriever")
        self.chunks.extend(new_chunks)
        self.embeddings = self._prepare_embeddings()
    
    def search_by_page(
        self,
        query: str,
        page_number: int,
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve chunks from specific page.
        
        Args:
            query: Query string
            page_number: Page number to search in
            top_k: Number of results
            
        Returns:
            Retrieved chunks from specified page
        """
        chunks, scores = self.retrieve(query, top_k=top_k*3 if top_k else None)
        
        page_chunks = [c for c in chunks if c.get("page_number") == page_number]
        
        return page_chunks[:top_k or self.config.top_k]
    
    def get_chunk_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about chunks.
        
        Returns:
            Statistics dictionary
        """
        if not self.chunks:
            return {}
        
        token_counts = [c.get("chunk_token_count", 0) for c in self.chunks]
        char_counts = [c.get("chunk_char_count", 0) for c in self.chunks]
        pages = set(c.get("page_number", 0) for c in self.chunks)
        
        return {
            "total_chunks": len(self.chunks),
            "unique_pages": len(pages),
            "avg_tokens_per_chunk": np.mean(token_counts) if token_counts else 0,
            "max_tokens_per_chunk": np.max(token_counts) if token_counts else 0,
            "min_tokens_per_chunk": np.min(token_counts) if token_counts else 0,
            "avg_chars_per_chunk": np.mean(char_counts) if char_counts else 0,
            "total_chars": sum(char_counts),
        }


# Utility function for backward compatibility
def retrieve_relevant_chunks(
    query: str,
    chunks: List[Dict[str, Any]],
    embedding_manager: EmbeddingManager,
    top_k: int = RETRIEVAL_TOP_K
) -> Tuple[List[Dict[str, Any]], List[float]]:
    """
    Standalone function to retrieve relevant chunks.
    
    Args:
        query: Query string
        chunks: List of chunks with embeddings
        embedding_manager: EmbeddingManager instance
        top_k: Number of top results
        
    Returns:
        Tuple of (retrieved chunks, scores)
    """
    retriever = SemanticRetriever(chunks, embedding_manager, RetrieverConfig(top_k=top_k))
    return retriever.retrieve(query, top_k=top_k)
