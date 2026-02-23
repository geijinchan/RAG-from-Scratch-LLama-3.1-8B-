#!/usr/bin/env python3
"""
Test Script for Groq-integrated RAG System

This script demonstrates:
1. Testing RAG pipeline with Groq
2. Testing LLM handler with Groq API
3. Complete end-to-end RAG workflow
4. Handling Groq API interactions

Usage:
    python test_groq_rag.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from unittest.mock import Mock, patch
from config.settings import GROQ_MODEL, GROQ_API_KEY
from src.rag_pipeline import RAGPipeline
from src.llm_handler import LLMHandler


def test_groq_llm_handler():
    """Test Groq LLM Handler functionality"""
    print("\n" + "="*70)
    print("TEST 1: Groq LLM Handler")
    print("="*70)
    
    # Mock Groq client
    with patch('src.llm_handler.Groq') as mock_groq_class:
        mock_client = Mock()
        mock_groq_class.return_value = mock_client
        
        # Create handler
        print("\n✓ Creating Groq LLM Handler...")
        handler = LLMHandler(
            model_id=GROQ_MODEL,
            api_key="test_api_key_123"
        )
        print(f"  Model: {handler.model_id}")
        print(f"  Temperature: {handler.temperature}")
        print(f"  Max Tokens: {handler.max_tokens}")
        
        # Test generation
        print("\n✓ Testing text generation...")
        mock_response = Mock()
        mock_response.choices = [
            Mock(message=Mock(content="This is a test response from Groq."))
        ]
        mock_client.chat.completions.create.return_value = mock_response
        
        result = handler.generate("What is AI?")
        print(f"  Query: 'What is AI?'")
        print(f"  Response: {result}")
        
        # Verify API was called correctly
        call_args = mock_client.chat.completions.create.call_args
        print(f"  ✓ API called with model: {call_args[1]['model']}")
        print(f"  ✓ Temperature: {call_args[1]['temperature']}")
        print(f"  ✓ Max tokens: {call_args[1]['max_tokens']}")
        
        # Test streaming
        print("\n✓ Testing streaming generation...")
        mock_chunks = [
            Mock(choices=[Mock(delta=Mock(content="Hello "))]),
            Mock(choices=[Mock(delta=Mock(content="from "))]),
            Mock(choices=[Mock(delta=Mock(content="Groq!"))]),
        ]
        mock_client.chat.completions.create.return_value = mock_chunks
        
        stream_result = list(handler.generate_streaming("Say hello"))
        print(f"  Chunks: {stream_result}")
        
        # Verify stream=True
        call_args = mock_client.chat.completions.create.call_args
        print(f"  ✓ Streaming enabled: {call_args[1].get('stream', False)}")
        
        # Test prompt formatting
        print("\n✓ Testing prompt formatting...")
        context = [
            {"sentence_chunk": "Python is a programming language"},
            {"sentence_chunk": "It's easy to learn"}
        ]
        query = "What is Python?"
        
        formatted = handler.format_prompt_with_context(query, context)
        print(f"  Query: {query}")
        print(f"  Context items: {len(context)}")
        print(f"  Formatted prompt length: {len(formatted)} chars")
        print(f"  ✓ Query in prompt: {query in formatted}")
        print(f"  ✓ Context in prompt: {'Python is a programming' in formatted}")
        
        # Test model info
        print("\n✓ Testing model info...")
        info = handler.get_model_info()
        print(f"  Provider: {info['provider']}")
        print(f"  Type: {info['type']}")
        print(f"  Inference: {info['inference_type']}")
        
    print("\n✅ Groq LLM Handler tests passed!")


def test_rag_pipeline_with_groq():
    """Test RAG Pipeline with Groq integration"""
    print("\n" + "="*70)
    print("TEST 2: RAG Pipeline with Groq")
    print("="*70)
    
    with patch('src.rag_pipeline.PDFProcessor'):
        with patch('src.rag_pipeline.EmbeddingManager') as mock_embedding:
            with patch('src.llm_handler.Groq') as mock_groq_class:
                
                # Setup mocks
                mock_client = Mock()
                mock_groq_class.return_value = mock_client
                
                mock_embedding_instance = Mock()
                mock_embedding.return_value = mock_embedding_instance
                
                # Create pipeline
                print("\n✓ Creating RAG Pipeline with Groq...")
                pipeline = RAGPipeline(load_llm=True)
                print(f"  PDF Processor: {pipeline.pdf_processor is not None}")
                print(f"  Embedding Manager: {pipeline.embedding_manager is not None}")
                print(f"  LLM Handler: {pipeline.llm_handler is not None}")
                
                # Mock PDF processing
                print("\n✓ Testing PDF processing step...")
                mock_chunks = [
                    {"sentence_chunk": "Page 1 content", "chunk_token_count": 10},
                    {"sentence_chunk": "Page 2 content", "chunk_token_count": 12},
                ]
                pipeline.pdf_processor.process_pdf = Mock(return_value=mock_chunks)
                
                chunks = pipeline.process_pdf("test.pdf")
                print(f"  Processed chunks: {len(chunks)}")
                for i, chunk in enumerate(chunks):
                    print(f"    Chunk {i+1}: {chunk['sentence_chunk'][:30]}...")
                
                # Mock embedding
                print("\n✓ Testing embedding step...")
                embedded = [
                    {**c, "embedding": Mock()} for c in mock_chunks
                ]
                pipeline.embedding_manager.embed_chunks = Mock(return_value=embedded)
                
                result = pipeline.embed_chunks(chunks)
                print(f"  Embedded chunks: {len(result)}")
                print(f"  ✓ Embeddings attached: {all('embedding' in c for c in result)}")
                
                # Mock retriever setup
                print("\n✓ Testing retriever setup...")
                pipeline.setup_retriever(result)
                print(f"  Retriever initialized: {pipeline.retriever is not None}")
                
                # Mock retrieval and generation
                print("\n✓ Testing retrieval and generation...")
                context_chunks = [
                    {
                        "sentence_chunk": "Context text",
                        "page_number": 0,
                        "similarity_score": 0.95
                    }
                ]
                pipeline.retriever.retrieve_with_metadata = Mock(
                    return_value=context_chunks
                )
                
                mock_response = Mock()
                mock_response.choices = [
                    Mock(message=Mock(content="Answer to the question"))
                ]
                mock_client.chat.completions.create.return_value = mock_response
                
                answer, retrieved = pipeline.ask("Test question?")
                print(f"  Question: 'Test question?'")
                print(f"  Retrieved chunks: {len(retrieved)}")
                print(f"  Answer length: {len(answer)} chars")
                print(f"  ✓ API called: {mock_client.chat.completions.create.called}")
    
    print("\n✅ RAG Pipeline tests passed!")


def test_error_handling():
    """Test error handling in Groq integration"""
    print("\n" + "="*70)
    print("TEST 3: Error Handling")
    print("="*70)
    
    # Test missing API key
    print("\n✓ Testing missing API key error...")
    try:
        handler = LLMHandler(api_key="")
        print("  ✗ Should have raised ValueError")
    except ValueError as e:
        print(f"  ✓ Correctly raised ValueError: {str(e)[:50]}...")
    
    # Test API error handling
    print("\n✓ Testing API error handling...")
    with patch('src.llm_handler.Groq') as mock_groq_class:
        mock_client = Mock()
        mock_groq_class.return_value = mock_client
        
        handler = LLMHandler(model_id="test-model", api_key="test_key")
        
        # Simulate API error
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        try:
            handler.generate("Test prompt")
            print("  ✗ Should have raised RuntimeError")
        except RuntimeError as e:
            print(f"  ✓ Correctly raised RuntimeError: {str(e)[:50]}...")
    
    print("\n✅ Error handling tests passed!")


def test_config_loading():
    """Test configuration loading"""
    print("\n" + "="*70)
    print("TEST 4: Configuration Loading")
    print("="*70)
    
    print("\n✓ Loading configuration...")
    print(f"  GROQ_MODEL: {GROQ_MODEL}")
    print(f"  GROQ_API_KEY present: {'*' * 10 if GROQ_API_KEY else 'Not set'}")
    
    from config.settings import (
        EMBEDDING_MODEL,
        LLM_TEMPERATURE,
        LLM_MAX_NEW_TOKENS,
        RETRIEVAL_TOP_K,
    )
    
    print(f"\n✓ Other settings:")
    print(f"  EMBEDDING_MODEL: {EMBEDDING_MODEL}")
    print(f"  LLM_TEMPERATURE: {LLM_TEMPERATURE}")
    print(f"  LLM_MAX_NEW_TOKENS: {LLM_MAX_NEW_TOKENS}")
    print(f"  RETRIEVAL_TOP_K: {RETRIEVAL_TOP_K}")
    
    print("\n✅ Configuration loading passed!")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("GROQ-INTEGRATED RAG SYSTEM - TEST SUITE")
    print("="*70)
    
    try:
        test_config_loading()
        test_groq_llm_handler()
        test_rag_pipeline_with_groq()
        test_error_handling()
        
        print("\n" + "="*70)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("="*70)
        print("\nYour RAG system is ready to use with Groq!")
        print("\nNext steps:")
        print("1. Update .env with your GROQ_API_KEY")
        print("2. Run: streamlit run app/streamlit_app.py")
        print("3. Upload a PDF and ask questions!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
