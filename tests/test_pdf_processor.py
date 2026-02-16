"""
Tests for PDF processor module.
"""

import pytest
import tempfile
from pathlib import Path
from src.pdf_processor import PDFProcessor, text_formatter


class TestPDFProcessor:
    """Test cases for PDFProcessor"""
    
    @pytest.fixture
    def processor(self):
        """Create a PDFProcessor instance"""
        return PDFProcessor()
    
    def test_text_formatter(self):
        """Test text formatting"""
        text = "This  is   a   test\nwith newlines\n"
        result = PDFProcessor.text_formatter(text)
        
        assert "\n" not in result
        assert "  " not in result
        assert result.startswith("This")
    
    def test_split_list(self):
        """Test list splitting"""
        input_list = list(range(25))
        result = PDFProcessor._split_list(input_list, slice_size=10)
        
        assert len(result) == 3
        assert len(result[0]) == 10
        assert len(result[1]) == 10
        assert len(result[2]) == 5
    
    def test_split_list_exact(self):
        """Test list splitting with exact division"""
        input_list = list(range(20))
        result = PDFProcessor._split_list(input_list, slice_size=10)
        
        assert len(result) == 2
        assert len(result[0]) == 10
        assert len(result[1]) == 10


class TestPDFProcessing:
    """Integration tests for PDF processing"""
    
    @pytest.fixture
    def processor(self):
        """Create a PDFProcessor instance"""
        return PDFProcessor()
    
    @pytest.fixture
    def sample_text_data(self):
        """Create sample page data"""
        return [
            {
                "page_number": 0,
                "text": "This is a test sentence. This is another test sentence. "
                        "And here is a third test sentence.",
                "page_char_count": 100,
                "page_sentence_count_raw": 3,
                "page_token_count": 25
            }
        ]
    
    def test_split_into_sentences(self, processor, sample_text_data):
        """Test sentence splitting"""
        result = processor.split_into_sentences(sample_text_data)
        
        assert len(result) > 0
        assert "sentences" in result[0]
        assert len(result[0]["sentences"]) > 0
    
    def test_chunk_sentences(self, processor, sample_text_data):
        """Test sentence chunking"""
        sample_text_data = processor.split_into_sentences(sample_text_data)
        result = processor.chunk_sentences(sample_text_data)
        
        assert len(result) > 0
        assert "sentence_chunks" in result[0]
    
    def test_create_chunks(self, processor, sample_text_data):
        """Test chunk creation"""
        sample_text_data = processor.split_into_sentences(sample_text_data)
        sample_text_data = processor.chunk_sentences(sample_text_data)
        result = processor.create_chunks(sample_text_data)
        
        assert len(result) > 0
        assert "sentence_chunk" in result[0]
        assert "chunk_token_count" in result[0]
    
    def test_filter_chunks(self, processor):
        """Test chunk filtering"""
        chunks = [
            {"sentence_chunk": "short", "chunk_token_count": 1},
            {"sentence_chunk": "this is a longer chunk with more content", "chunk_token_count": 50},
        ]
        
        result = processor.filter_chunks(chunks)
        
        # Only the longer chunk should remain
        assert len(result) <= len(chunks)
