"""
Tests for Retrieval module.
"""

import pytest
import numpy as np
# import torch
from unittest.mock import Mock, patch, MagicMock
from src.retrieval import SemanticRetriever, RetrieverConfig, retrieve_relevant_chunks
from src.embedding_manager import EmbeddingManager
from config.settings import RETRIEVAL_TOP_K, DEVICE


class TestRetrieverConfig:
    """Test cases for RetrieverConfig"""
    
    def test_default_config(self):
        """Test default retriever configuration"""
        config = RetrieverConfig()
        
        assert config.top_k == RETRIEVAL_TOP_K
        assert config.similarity_threshold == 0.0
        assert config.prefer_longer_chunks == False
    
    def test_custom_config(self):
        """Test custom retriever configuration"""
        config = RetrieverConfig(
            top_k=10,
            similarity_threshold=0.5,
            prefer_longer_chunks=True
        )
        
        assert config.top_k == 10
        assert config.similarity_threshold == 0.5
        assert config.prefer_longer_chunks == True


class TestSemanticRetriever:
    """Test cases for SemanticRetriever"""
    
    @pytest.fixture
    def embedding_manager(self):
        """Create an EmbeddingManager instance"""
        return EmbeddingManager(device="cpu")
    
    @pytest.fixture
    def sample_chunks_with_embeddings(self, embedding_manager):
        """Create sample chunks with embeddings"""
        chunks = [
            {
                "sentence_chunk": "Macronutrients are proteins, fats, and carbohydrates.",
                "chunk_token_count": 15,
                "page_number": 0,
                "chunk_char_count": 50
            },
            {
                "sentence_chunk": "Micronutrients include vitamins and minerals.",
                "chunk_token_count": 12,
                "page_number": 1,
                "chunk_char_count": 45
            },
            {
                "sentence_chunk": "Water is essential for all biological functions.",
                "chunk_token_count": 10,
                "page_number": 2,
                "chunk_char_count": 45
            },
            {
                "sentence_chunk": "Protein is important for muscle growth.",
                "chunk_token_count": 9,
                "page_number": 3,
                "chunk_char_count": 40
            },
            {
                "sentence_chunk": "Calcium is crucial for bone health.",
                "chunk_token_count": 8,
                "page_number": 4,
                "chunk_char_count": 35
            }
        ]
        
        # Generate embeddings
        texts = [chunk["sentence_chunk"] for chunk in chunks]
        embeddings = embedding_manager.generate_embeddings(texts, show_progress_bar=False)
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding.cpu().numpy()
        
        return chunks
    
    @pytest.fixture
    def retriever(self, embedding_manager, sample_chunks_with_embeddings):
        """Create a SemanticRetriever instance"""
        config = RetrieverConfig(top_k=3)
        return SemanticRetriever(
            chunks_with_embeddings=sample_chunks_with_embeddings,
            embedding_manager=embedding_manager,
            config=config
        )
    
    def test_retriever_initialization(self, retriever, sample_chunks_with_embeddings):
        """Test retriever initialization"""
        assert retriever.chunks is not None
        assert len(retriever.chunks) == len(sample_chunks_with_embeddings)
        assert retriever.embeddings is not None
    
    def test_retrieve_single_query(self, retriever):
        """Test retrieving chunks for a single query"""
        query = "What are macronutrients?"
        chunks, scores = retriever.retrieve(query, top_k=3, return_scores=True)
        
        assert len(chunks) <= 3
        assert len(scores) == len(chunks)
        assert all(isinstance(score, float) for score in scores)
        assert all(score >= 0 for score in scores)
    
    def test_retrieve_with_metadata(self, retriever):
        """Test retrieving with metadata"""
        query = "protein"
        results = retriever.retrieve_with_metadata(query, top_k=2)
        
        assert len(results) <= 2
        assert all("similarity_score" in result for result in results)
    
    def test_retrieve_by_page(self, retriever):
        """Test retrieving chunks from specific page"""
        query = "nutrition"
        page_results = retriever.search_by_page(query, page_number=0, top_k=2)
        
        # All results should be from page 0
        assert all(result.get("page_number") == 0 for result in page_results)
    
    def test_get_chunk_statistics(self, retriever):
        """Test getting chunk statistics"""
        stats = retriever.get_chunk_statistics()
        
        assert "total_chunks" in stats
        assert "unique_pages" in stats
        assert "avg_tokens_per_chunk" in stats
        assert stats["total_chunks"] == 5
    
    def test_update_chunks(self, retriever, embedding_manager):
        """Test updating chunks"""
        new_chunks = [
            {
                "sentence_chunk": "New chunk text",
                "chunk_token_count": 5,
                "embedding": embedding_manager.generate_embeddings(
                    "New chunk text", show_progress_bar=False
                ).cpu().numpy()
            }
        ]
        
        retriever.update_chunks(new_chunks)
        
        assert len(retriever.chunks) == 1
        assert retriever.chunks[0]["sentence_chunk"] == "New chunk text"
    
    def test_add_chunks(self, retriever, embedding_manager):
        """Test adding chunks"""
        initial_count = len(retriever.chunks)
        
        new_chunks = [
            {
                "sentence_chunk": "Additional chunk",
                "chunk_token_count": 5,
                "embedding": embedding_manager.generate_embeddings(
                    "Additional chunk", show_progress_bar=False
                ).cpu().numpy()
            }
        ]
        
        retriever.add_chunks(new_chunks)
        
        assert len(retriever.chunks) == initial_count + 1


class TestRetrievalIntegration:
    """Integration tests for retrieval operations"""
    
    @pytest.fixture
    def setup_retrieval(self):
        """Setup for retrieval integration tests"""
        embedding_manager = EmbeddingManager(device="cpu")
        
        chunks = [
            {
                "sentence_chunk": "Machine learning is a subset of artificial intelligence.",
                "chunk_token_count": 15,
                "page_number": 0,
            },
            {
                "sentence_chunk": "Deep learning uses neural networks with multiple layers.",
                "chunk_token_count": 15,
                "page_number": 1,
            },
            {
                "sentence_chunk": "Natural language processing helps computers understand text.",
                "chunk_token_count": 15,
                "page_number": 2,
            }
        ]
        
        # Embed chunks
        texts = [c["sentence_chunk"] for c in chunks]
        embeddings = embedding_manager.generate_embeddings(texts, show_progress_bar=False)
        
        for chunk, embedding in zip(chunks, embeddings):
            chunk["embedding"] = embedding.cpu().numpy()
        
        config = RetrieverConfig(top_k=2)
        retriever = SemanticRetriever(chunks, embedding_manager, config)
        
        return embedding_manager, retriever, chunks
    
    def test_end_to_end_retrieval(self, setup_retrieval):
        """Test complete retrieval pipeline"""
        embedding_manager, retriever, chunks = setup_retrieval
        
        # Query related to machine learning
        query = "artificial intelligence and learning"
        results = retriever.retrieve_with_metadata(query, top_k=2)
        
        # Should retrieve at least one result
        assert len(results) > 0
        
        # Results should have similarity scores
        assert all("similarity_score" in r for r in results)
        
        # Top result should be relevant
        assert "learning" in results[0]["sentence_chunk"].lower() or \
               "intelligence" in results[0]["sentence_chunk"].lower()
    
    def test_similarity_ranking(self, setup_retrieval):
        """Test that similarity scores are properly ranked"""
        embedding_manager, retriever, chunks = setup_retrieval
        
        query = "neural networks"
        results = retriever.retrieve_with_metadata(query, top_k=3)
        
        if len(results) > 1:
            # Scores should be in descending order
            scores = [r.get("similarity_score", 0) for r in results]
            assert scores == sorted(scores, reverse=True)
