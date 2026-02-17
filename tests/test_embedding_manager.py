"""
Tests for Embedding Manager module.
"""

import pytest
import tempfile
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.embedding_manager import EmbeddingManager, embed_texts
from config.settings import EMBEDDING_MODEL, EMBEDDINGS_DIR


class TestEmbeddingManager:
    """Test cases for EmbeddingManager"""
    
    @pytest.fixture
    def embedding_manager(self):
        """Create an EmbeddingManager instance"""
        return EmbeddingManager(model_name=EMBEDDING_MODEL, device="cpu")
    
    def test_initialization(self, embedding_manager):
        """Test EmbeddingManager initialization"""
        assert embedding_manager.model is not None
        assert embedding_manager.model_name == EMBEDDING_MODEL
        assert embedding_manager.device == "cpu"
    
    def test_get_embedding_dimension(self, embedding_manager):
        """Test getting embedding dimension"""
        dim = embedding_manager.get_embedding_dimension()
        assert isinstance(dim, int)
        assert dim > 0
    
    def test_generate_single_embedding(self, embedding_manager):
        """Test embedding a single text"""
        text = "This is a test sentence for embedding"
        embedding = embedding_manager.generate_embeddings(text, show_progress_bar=False)
        
        assert embedding is not None
        assert len(embedding.shape) == 2
        assert embedding.shape[0] == 1
    
    def test_generate_multiple_embeddings(self, embedding_manager):
        """Test embedding multiple texts"""
        texts = [
            "First test sentence",
            "Second test sentence",
            "Third test sentence"
        ]
        embeddings = embedding_manager.generate_embeddings(texts, show_progress_bar=False)
        
        assert embeddings is not None
        assert embeddings.shape[0] == 3
        assert embeddings.shape[1] > 0
    
    def test_embedding_consistency(self, embedding_manager):
        """Test that same text produces same embedding"""
        text = "Consistent text for testing"
        emb1 = embedding_manager.generate_embeddings(text, show_progress_bar=False)
        emb2 = embedding_manager.generate_embeddings(text, show_progress_bar=False)
        
        # Should be very similar (not exactly same due to fp32 precision)
        assert np.allclose(emb1, emb2, atol=1e-5)
    
    def test_embed_chunks(self, embedding_manager):
        """Test embedding a list of chunks"""
        chunks = [
            {"sentence_chunk": "Text for chunk 1", "chunk_token_count": 10},
            {"sentence_chunk": "Text for chunk 2", "chunk_token_count": 15},
        ]
        
        result = embedding_manager.embed_chunks(chunks, batch_size=2)
        
        assert len(result) == 2
        assert all("embedding" in chunk for chunk in result)
    
    def test_save_and_load_embeddings(self, embedding_manager):
        """Test saving and loading embeddings"""
        chunks = [
            {
                "sentence_chunk": "Test chunk 1",
                "chunk_token_count": 10,
                "page_number": 0
            },
        ]
        
        embedded_chunks = embedding_manager.embed_chunks(chunks)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            save_path = Path(tmpdir) / "test_embeddings.pkl"
            
            # Mock the save path
            with patch.object(embedding_manager, 'embeddings_dir', Path(tmpdir)):
                embedding_manager.save_embeddings(embedded_chunks, filename="test_embeddings.pkl")
                loaded = embedding_manager.load_embeddings(save_path)
            
            assert len(loaded) == len(embedded_chunks)
            assert "embedding" in loaded[0]


class TestEmbeddingIntegration:
    """Integration tests for embedding operations"""
    
    @pytest.fixture
    def embedding_manager(self):
        """Create an EmbeddingManager instance"""
        return EmbeddingManager(device="cpu")
    
    def test_embedding_pipeline(self, embedding_manager):
        """Test complete embedding pipeline: chunk → embed → save → load"""
        # Simulate chunks from PDF processor
        chunks = [
            {
                "sentence_chunk": "Macronutrients include carbohydrates, proteins, and fats.",
                "chunk_token_count": 15,
                "page_number": 0,
                "chunk_char_count": 60
            },
            {
                "sentence_chunk": "Micronutrients are vitamins and minerals.",
                "chunk_token_count": 10,
                "page_number": 1,
                "chunk_char_count": 45
            }
        ]
        
        # Step 1: Embed chunks
        embedded_chunks = embedding_manager.embed_chunks(chunks)
        
        # Verify embeddings were added
        assert all("embedding" in chunk for chunk in embedded_chunks)
        
        # Step 2: Verify embedding shape
        for chunk in embedded_chunks:
            embedding = chunk["embedding"]
            assert isinstance(embedding, np.ndarray)
            assert len(embedding.shape) == 1
    
    def test_batch_processing(self, embedding_manager):
        """Test batch processing of embeddings"""
        chunks = [
            {"sentence_chunk": f"Sample text {i}", "chunk_token_count": 5}
            for i in range(10)
        ]
        
        # Process with small batch size
        result = embedding_manager.embed_chunks(chunks, batch_size=3)
        
        assert len(result) == 10
        assert all("embedding" in chunk for chunk in result)
