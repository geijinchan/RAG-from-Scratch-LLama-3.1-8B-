"""
Test Suite Module

Comprehensive test coverage for the RAG system.

Test Categories:
    - test_pdf_processor: PDF extraction and chunking
    - test_embedding_manager: Vector generation
    - test_retrieval: Semantic search
    - test_rag_pipeline: End-to-end RAG pipeline
    - test_llm_handler: Groq API integration
    - test_llm_handler_groq: Production Groq tests

Running Tests:
    pytest tests/
    pytest tests/test_rag_pipeline.py -v
    pytest tests/ --cov=src --cov-report=html
"""

__version__ = "1.0.0"

__all__ = []
