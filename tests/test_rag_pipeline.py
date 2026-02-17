"""
Tests for RAG Pipeline module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from src.rag_pipeline import RAGPipeline
from config.settings import EMBEDDING_MODEL, LLM_MODEL_ID, DEVICE


class TestRAGPipelineInitialization:
    """Test cases for RAG Pipeline initialization"""
    
    def test_pipeline_initialization_without_llm(self):
        """Test pipeline initialization without loading LLM"""
        with patch('src.rag_pipeline.PDFProcessor'):
            with patch('src.rag_pipeline.EmbeddingManager'):
                pipeline = RAGPipeline(load_llm=False)
                
                assert pipeline.pdf_processor is not None
                assert pipeline.embedding_manager is not None
                assert pipeline.llm_handler is None
                assert pipeline.retriever is None
    
    def test_pipeline_initialization_with_llm(self):
        """Test pipeline initialization with LLM loading"""
        with patch('src.rag_pipeline.PDFProcessor'):
            with patch('src.rag_pipeline.EmbeddingManager'):
                with patch('src.rag_pipeline.LLMHandler'):
                    pipeline = RAGPipeline(load_llm=True)
                    
                    assert pipeline.llm_handler is not None


class TestRAGPipelineComponents:
    """Test individual pipeline components"""
    
    @pytest.fixture
    def pipeline(self):
        """Create a mock RAG pipeline"""
        with patch('src.rag_pipeline.PDFProcessor'):
            with patch('src.rag_pipeline.EmbeddingManager'):
                return RAGPipeline(load_llm=False)
    
    def test_process_pdf(self, pipeline):
        """Test PDF processing step"""
        mock_chunks = [
            {"sentence_chunk": "Test chunk", "chunk_token_count": 10}
        ]
        
        pipeline.pdf_processor.process_pdf = Mock(return_value=mock_chunks)
        
        result = pipeline.process_pdf("test.pdf")
        
        assert len(result) == 1
        assert result[0]["sentence_chunk"] == "Test chunk"
        pipeline.pdf_processor.process_pdf.assert_called_once_with("test.pdf")
    
    def test_embed_chunks(self, pipeline):
        """Test chunk embedding step"""
        chunks = [
            {"sentence_chunk": "Text 1", "chunk_token_count": 10},
            {"sentence_chunk": "Text 2", "chunk_token_count": 12}
        ]
        
        embedded_chunks = [
            {**chunk, "embedding": MagicMock()}
            for chunk in chunks
        ]
        
        pipeline.embedding_manager.embed_chunks = Mock(return_value=embedded_chunks)
        
        result = pipeline.embed_chunks(chunks)
        
        assert len(result) == 2
        assert all("embedding" in chunk for chunk in result)
    
    def test_setup_retriever(self, pipeline):
        """Test retriever setup"""
        chunks = [
            {
                "sentence_chunk": "Text",
                "chunk_token_count": 10,
                "embedding": MagicMock()
            }
        ]
        
        pipeline.setup_retriever(chunks, top_k=5)
        
        assert pipeline.retriever is not None


class TestRAGPipelineWorkflow:
    """Test RAG pipeline workflows"""
    
    @pytest.fixture
    def mock_pipeline(self):
        """Create a mock pipeline for workflow testing"""
        with patch('src.rag_pipeline.PDFProcessor'):
            with patch('src.rag_pipeline.EmbeddingManager'):
                with patch('src.rag_pipeline.LLMHandler'):
                    pipeline = RAGPipeline(load_llm=True)
                    return pipeline
    
    def test_retrieve_step(self, mock_pipeline):
        """Test retrieval step in pipeline"""
        mock_chunks = [
            {"sentence_chunk": "Context", "page_number": 0, "similarity_score": 0.95}
        ]
        
        mock_pipeline.retriever = Mock()
        mock_pipeline.retriever.retrieve_with_metadata = Mock(return_value=mock_chunks)
        
        result = mock_pipeline.retrieve("query", top_k=5)
        
        assert len(result) == 1
        assert result[0]["sentence_chunk"] == "Context"
    
    def test_generate_step(self, mock_pipeline):
        """Test generation step in pipeline"""
        context_chunks = [
            {"sentence_chunk": "Context text"}
        ]
        
        mock_pipeline.llm_handler = Mock()
        mock_pipeline.llm_handler.format_prompt_with_context = Mock(
            return_value="formatted_prompt"
        )
        mock_pipeline.llm_handler.generate = Mock(
            return_value="Generated answer"
        )
        
        result = mock_pipeline.generate("query", context_chunks)
        
        assert result == "Generated answer"
        mock_pipeline.llm_handler.generate.assert_called_once()
    
    def test_ask_simple(self, mock_pipeline):
        """Test simple ask without context return"""
        mock_pipeline.retrieve = Mock(
            return_value=[{"sentence_chunk": "Context"}]
        )
        mock_pipeline.generate = Mock(return_value="Answer")
        
        result = mock_pipeline.ask("query", return_context=False)
        
        assert result == "Answer"
    
    def test_ask_with_context(self, mock_pipeline):
        """Test ask with context return"""
        context = [{"sentence_chunk": "Context"}]
        
        mock_pipeline.retrieve = Mock(return_value=context)
        mock_pipeline.generate = Mock(return_value="Answer")
        
        answer, returned_context = mock_pipeline.ask("query", return_context=True)
        
        assert answer == "Answer"
        assert returned_context == context


class TestRAGPipelineIntegration:
    """Integration tests for RAG pipeline"""
    
    @pytest.fixture
    def mock_full_pipeline(self):
        """Create a fully mocked pipeline for integration testing"""
        with patch('src.rag_pipeline.PDFProcessor'):
            with patch('src.rag_pipeline.EmbeddingManager'):
                with patch('src.rag_pipeline.LLMHandler'):
                    return RAGPipeline(load_llm=True)
    
    def test_complete_pipeline_workflow(self, mock_full_pipeline):
        """Test complete pipeline from PDF to answer"""
        # Mock all components
        pdf_chunks = [{"sentence_chunk": "Test", "chunk_token_count": 10}]
        embedded_chunks = [{"sentence_chunk": "Test", "embedding": MagicMock()}]
        context_chunks = [{"sentence_chunk": "Test", "similarity_score": 0.95}]
        
        mock_full_pipeline.process_pdf = Mock(return_value=pdf_chunks)
        mock_full_pipeline.embed_chunks = Mock(return_value=embedded_chunks)
        mock_full_pipeline.setup_retriever = Mock()
        mock_full_pipeline.retrieve = Mock(return_value=context_chunks)
        mock_full_pipeline.generate = Mock(return_value="Generated Answer")
        
        # Execute pipeline
        result = mock_full_pipeline.ask("What is in the document?", return_context=True)
        
        assert result[0] == "Generated Answer"  # answer
        assert len(result[1]) > 0  # context
    
    def test_pipeline_statistics(self, mock_full_pipeline):
        """Test getting pipeline statistics"""
        mock_full_pipeline.retriever = Mock()
        mock_full_pipeline.retriever.get_chunk_statistics = Mock(
            return_value={"total_chunks": 100}
        )
        mock_full_pipeline.llm_handler = Mock()
        mock_full_pipeline.llm_handler.get_model_info = Mock(
            return_value={"model_id": "test-model"}
        )
        
        stats = mock_full_pipeline.get_statistics()
        
        assert "total_chunks" in stats
        assert "model_id" in stats


class TestRAGPipelineErrorHandling:
    """Test error handling in RAG pipeline"""
    
    @pytest.fixture
    def pipeline(self):
        """Create RAG pipeline"""
        with patch('src.rag_pipeline.PDFProcessor'):
            with patch('src.rag_pipeline.EmbeddingManager'):
                return RAGPipeline(load_llm=False)
    
    def test_retrieve_without_retriever(self, pipeline):
        """Test that retrieve raises error without initialized retriever"""
        with pytest.raises(RuntimeError):
            pipeline.retrieve("query")
    
    def test_generate_without_llm(self, pipeline):
        """Test that generate raises error without initialized LLM"""
        with pytest.raises(RuntimeError):
            pipeline.generate("query", [])
