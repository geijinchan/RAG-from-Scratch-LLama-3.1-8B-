"""
Tests for LLM Handler module using Groq Cloud API.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.llm_handler import LLMHandler
from config.settings import GROQ_MODEL


class TestGroqLLMHandler:
    """Test cases for Groq-based LLMHandler"""
    
    @pytest.fixture
    def llm_handler(self):
        """Create a mock GroqLLMHandler instance"""
        with patch('src.llm_handler.Groq') as mock_groq:
            mock_client = Mock()
            mock_groq.return_value = mock_client
            
            handler = LLMHandler(
                model_id=GROQ_MODEL,
                api_key="test_key_123"
            )
            handler.client = mock_client
            return handler
    
    def test_initialization(self, llm_handler):
        """Test LLMHandler initialization with Groq"""
        assert llm_handler.model_id == GROQ_MODEL
        assert llm_handler.api_key == "test_key_123"
        assert llm_handler.client is not None
    
    def test_initialization_without_api_key(self):
        """Test that initialization fails without API key"""
        with patch('src.llm_handler.Groq'):
            with pytest.raises(ValueError):
                LLMHandler(api_key="")
    
    def test_generate_text(self, llm_handler):
        """Test text generation via Groq API"""
        # Mock the API response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Generated answer text"))]
        llm_handler.client.chat.completions.create.return_value = mock_response
        
        prompt = "What are proteins?"
        result = llm_handler.generate(prompt)
        
        assert result == "Generated answer text"
        llm_handler.client.chat.completions.create.assert_called_once()
    
    def test_generate_with_custom_temperature(self, llm_handler):
        """Test generation with custom temperature"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response"))]
        llm_handler.client.chat.completions.create.return_value = mock_response
        
        result = llm_handler.generate("Query", temperature=0.3)
        
        # Verify API was called with correct temperature
        call_kwargs = llm_handler.client.chat.completions.create.call_args[1]
        assert call_kwargs['temperature'] == 0.3
    
    def test_generate_with_custom_max_tokens(self, llm_handler):
        """Test generation with custom max tokens"""
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Response"))]
        llm_handler.client.chat.completions.create.return_value = mock_response
        
        result = llm_handler.generate("Query", max_tokens=256)
        
        # Verify API was called with correct max_tokens
        call_kwargs = llm_handler.client.chat.completions.create.call_args[1]
        assert call_kwargs['max_tokens'] == 256
    
    def test_format_prompt_with_context(self, llm_handler):
        """Test prompt formatting with context"""
        query = "What are macronutrients?"
        context_items = [
            {
                "sentence_chunk": "Macronutrients are proteins, fats, and carbohydrates.",
                "page_number": 0,
                "similarity_score": 0.95
            },
            {
                "sentence_chunk": "They are essential for energy production.",
                "page_number": 1,
                "similarity_score": 0.87
            }
        ]
        
        prompt = llm_handler.format_prompt_with_context(query, context_items)
        
        assert prompt is not None
        assert "macronutrient" in prompt.lower()
        assert "Macronutrients are proteins" in prompt
        assert "essential for energy" in prompt
    
    def test_format_prompt_includes_context(self, llm_handler):
        """Test that formatted prompt includes context"""
        query = "Test question?"
        context = [
            {"sentence_chunk": "Context line 1"},
            {"sentence_chunk": "Context line 2"}
        ]
        
        prompt = llm_handler.format_prompt_with_context(query, context)
        
        assert "Context:" in prompt
        assert "Context line 1" in prompt
        assert "Context line 2" in prompt
    
    def test_get_model_info(self, llm_handler):
        """Test getting model information"""
        info = llm_handler.get_model_info()
        
        assert "model_id" in info
        assert "provider" in info
        assert info["provider"] == "Groq Cloud API"
        assert info["model_id"] == GROQ_MODEL
        assert info["inference_type"] == "API-based"
    
    def test_generate_streaming(self, llm_handler):
        """Test streaming text generation"""
        # Mock streaming response
        mock_chunk1 = Mock(choices=[Mock(delta=Mock(content="Hello "))])
        mock_chunk2 = Mock(choices=[Mock(delta=Mock(content="world"))])
        mock_chunk3 = Mock(choices=[Mock(delta=Mock(content="!"))])
        
        llm_handler.client.chat.completions.create.return_value = [
            mock_chunk1, mock_chunk2, mock_chunk3
        ]
        
        prompt = "Generate text"
        result = list(llm_handler.generate_streaming(prompt))
        
        assert result == ["Hello ", "world", "!"]
        
        # Verify stream=True was set in API call
        call_kwargs = llm_handler.client.chat.completions.create.call_args[1]
        assert call_kwargs['stream'] is True
    
    def test_generate_streaming_empty_delta(self, llm_handler):
        """Test streaming ignores empty delta content"""
        # Mock response with some empty deltas
        mock_chunk1 = Mock(choices=[Mock(delta=Mock(content="Text "))])
        mock_chunk2 = Mock(choices=[Mock(delta=Mock(content=None))])  # Empty
        mock_chunk3 = Mock(choices=[Mock(delta=Mock(content="here"))])
        
        llm_handler.client.chat.completions.create.return_value = [
            mock_chunk1, mock_chunk2, mock_chunk3
        ]
        
        result = list(llm_handler.generate_streaming("Generate"))
        
        # Only non-empty content should be returned
        assert "Text " in result
        assert "here" in result
        assert len(result) == 2


class TestGroqPromptFormatting:
    """Test cases for prompt formatting with Groq"""
    
    @pytest.fixture
    def llm_handler(self):
        """Create mock LLMHandler"""
        with patch('src.llm_handler.Groq'):
            handler = LLMHandler(api_key="test_key")
            return handler
    
    def test_context_inclusion_in_prompt(self, llm_handler):
        """Test that context is properly included in prompt"""
        query = "Tell me about vitamins"
        context = [
            {"sentence_chunk": "Vitamins are organic compounds."},
            {"sentence_chunk": "They are essential micronutrients."}
        ]
        
        prompt = llm_handler.format_prompt_with_context(query, context)
        
        assert "vitamins" in prompt.lower()
        assert "organic compounds" in prompt
        assert "micronutrients" in prompt
    
    def test_query_in_prompt(self, llm_handler):
        """Test that query is included in formatted prompt"""
        query = "What is protein?"
        context = [
            {"sentence_chunk": "Protein is a macronutrient."}
        ]
        
        prompt = llm_handler.format_prompt_with_context(query, context)
        
        assert "What is protein?" in prompt
        assert "Protein is a macronutrient" in prompt
    
    def test_multiple_context_items(self, llm_handler):
        """Test formatting with multiple context items"""
        query = "Question"
        context = [
            {"sentence_chunk": f"Item {i}"} for i in range(5)
        ]
        
        prompt = llm_handler.format_prompt_with_context(query, context)
        
        # All context items should be in prompt
        for i in range(5):
            assert f"Item {i}" in prompt


class TestGroqErrorHandling:
    """Test error handling in Groq LLMHandler"""
    
    @pytest.fixture
    def llm_handler(self):
        """Create mock LLMHandler"""
        with patch('src.llm_handler.Groq'):
            handler = LLMHandler(api_key="test_key")
            return handler
    
    def test_generate_api_error(self, llm_handler):
        """Test handling of API errors during generation"""
        llm_handler.client.chat.completions.create.side_effect = Exception("API Error")
        
        with pytest.raises(RuntimeError):
            llm_handler.generate("Test prompt")
    
    def test_streaming_api_error(self, llm_handler):
        """Test handling of API errors during streaming"""
        llm_handler.client.chat.completions.create.side_effect = Exception("API Error")
        
        with pytest.raises(RuntimeError):
            list(llm_handler.generate_streaming("Test prompt"))


class TestGroqIntegration:
    """Integration tests for Groq operations"""
    
    @pytest.fixture
    def mock_groq_handler(self):
        """Create a mock Groq handler for testing"""
        with patch('src.llm_handler.Groq') as mock_groq:
            mock_client = Mock()
            mock_groq.return_value = mock_client
            
            handler = LLMHandler(
                model_id="llama-3.3-70b-versatile",
                api_key="test_key"
            )
            handler.client = mock_client
            return handler
    
    def test_end_to_end_rag_flow(self, mock_groq_handler):
        """Test complete RAG flow with Groq"""
        # Step 1: Format prompt
        context = [
            {"sentence_chunk": "Python is a programming language"}
        ]
        query = "What is Python?"
        
        formatted_prompt = mock_groq_handler.format_prompt_with_context(query, context)
        assert "Python is a programming language" in formatted_prompt
        
        # Step 2: Generate response
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="Python is a popular programming language..."))
        ]
        mock_groq_handler.client.chat.completions.create.return_value = mock_response
        
        response = mock_groq_handler.generate(formatted_prompt)
        assert "Python" in response
    
    def test_model_info_structure(self, mock_groq_handler):
        """Test that model info has correct structure"""
        info = mock_groq_handler.get_model_info()
        
        required_keys = ["model_id", "provider", "type", "temperature", "max_tokens"]
        for key in required_keys:
            assert key in info
        
        assert "Groq" in info["provider"]
        assert "API" in info["type"]
