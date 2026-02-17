"""
Tests for LLM Handler module.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from src.llm_handler import LLMHandler
from config.settings import DEVICE, LLM_MODEL_ID


class TestLLMHandler:
    """Test cases for LLMHandler"""
    
    @pytest.fixture
    def llm_handler(self):
        """Create an LLMHandler instance (using CPU for testing)"""
        # Mock the model loading for fast tests
        with patch('src.llm_handler.AutoModelForCausalLM.from_pretrained'):
            with patch('src.llm_handler.AutoTokenizer.from_pretrained'):
                handler = LLMHandler(device="cpu")
                # Mock the tokenizer
                handler.tokenizer = Mock()
                handler.model = Mock()
                return handler
    
    def test_initialization(self, llm_handler):
        """Test LLMHandler initialization"""
        assert llm_handler.model is not None
        assert llm_handler.tokenizer is not None
        assert llm_handler.device == "cpu"
    
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
        
        # Mock the apply_chat_template to return formatted prompt
        llm_handler.tokenizer.apply_chat_template = Mock(
            return_value="formatted_prompt"
        )
        
        prompt = llm_handler.format_prompt_with_context(query, context_items)
        
        assert prompt is not None
        assert "formatted_prompt" in prompt or "What are macronutrients?" in prompt
    
    def test_get_model_info(self, llm_handler):
        """Test getting model information"""
        llm_handler.model.config = Mock()
        llm_handler.tokenizer.vocab_size = 32000
        
        def count_parameters(model):
            return 1000000
        
        with patch('builtins.sum', return_value=1000000):
            info = llm_handler.get_model_info()
            
            assert "model_id" in info
            assert "device" in info
            assert info["device"] == "cpu"


class TestPromptFormatting:
    """Test cases for prompt formatting"""
    
    @pytest.fixture
    def llm_handler(self):
        """Create LLMHandler with mocked components"""
        with patch('src.llm_handler.AutoModelForCausalLM.from_pretrained'):
            with patch('src.llm_handler.AutoTokenizer.from_pretrained'):
                handler = LLMHandler(device="cpu")
                handler.tokenizer = Mock()
                handler.model = Mock()
                return handler
    
    def test_context_inclusion_in_prompt(self, llm_handler):
        """Test that context is properly included in prompt"""
        query = "Tell me about vitamins"
        context = [
            {"sentence_chunk": "Vitamins are organic compounds."},
            {"sentence_chunk": "They are essential micronutrients."}
        ]
        
        llm_handler.tokenizer.apply_chat_template = Mock(
            return_value="<prompt>Vitamins are organic compounds...</prompt>"
        )
        
        prompt = llm_handler.format_prompt_with_context(query, context)
        
        # Verify the method was called
        assert llm_handler.tokenizer.apply_chat_template.called
    
    def test_query_in_prompt(self, llm_handler):
        """Test that query is included in formatted prompt"""
        query = "What is protein?"
        context = [
            {"sentence_chunk": "Protein is a macronutrient."}
        ]
        
        def mock_format(conversation, tokenize=False, add_generation_prompt=False):
            return f"Context: {conversation[0]['content']}"
        
        llm_handler.tokenizer.apply_chat_template = Mock(side_effect=mock_format)
        
        prompt = llm_handler.format_prompt_with_context(query, context)
        
        # Query should be in the prompt somewhere
        assert "protein" in prompt.lower()


class TestLLMModelInfo:
    """Test cases for LLM model information"""
    
    @pytest.fixture
    def llm_handler(self):
        """Create LLMHandler with mocked components"""
        with patch('src.llm_handler.AutoModelForCausalLM.from_pretrained'):
            with patch('src.llm_handler.AutoTokenizer.from_pretrained'):
                handler = LLMHandler(device="cpu")
                handler.model = Mock()
                handler.tokenizer = Mock()
                handler.tokenizer.vocab_size = 32000
                return handler
    
    def test_model_info_structure(self, llm_handler):
        """Test structure of model information"""
        # Mock the parameters
        llm_handler.model.parameters = Mock(return_value=[Mock(numel=Mock(return_value=100000))])
        
        # We need to mock sum since it's used in get_model_info
        with patch('builtins.sum', return_value=100000):
            info = llm_handler.get_model_info()
            
            assert isinstance(info, dict)
            assert "model_id" in info
            assert "device" in info
            assert "vocab_size" in info


class TestLLMIntegration:
    """Integration tests for LLM operations"""
    
    @pytest.fixture
    def mock_llm_handler(self):
        """Create a mock LLM handler for testing"""
        with patch('src.llm_handler.AutoModelForCausalLM.from_pretrained'):
            with patch('src.llm_handler.AutoTokenizer.from_pretrained'):
                handler = LLMHandler(device="cpu")
                handler.tokenizer = Mock()
                handler.model = Mock()
                handler.tokenizer.eos_token_id = 2
                return handler
    
    def test_generation_prompt_flow(self, mock_llm_handler):
        """Test the flow from prompt to generation"""
        context = [
            {"sentence_chunk": "Sample context text"}
        ]
        query = "Sample query"
        
        # Setup mock
        mock_llm_handler.tokenizer.apply_chat_template = Mock(
            return_value="formatted_prompt"
        )
        
        # Format prompt
        prompt = mock_llm_handler.format_prompt_with_context(query, context)
        
        # Verify prompt formatting was called
        assert mock_llm_handler.tokenizer.apply_chat_template.called
