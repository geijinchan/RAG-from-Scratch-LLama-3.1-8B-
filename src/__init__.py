"""
RAG System Core Modules

Enterprise-level Retrieval-Augmented Generation (RAG) system with:
- GPU-accelerated semantic embedding (SentenceTransformers)
- Semantic similarity-based retrieval
- Groq Cloud API integration for LLM inference
- PDF document processing and chunking
- Production-grade logging and error handling

Key Components:
    - RAGPipeline: Main orchestrator
    - PDFProcessor: Document extraction and chunking
    - EmbeddingManager: Vector generation with GPU support
    - SemanticRetriever: Similarity-based search
    - LLMHandler: Groq API client
"""

__version__ = "1.0.0"
__author__ = "RAG Development Team"
__license__ = "MIT"

# Core imports
from src.rag_pipeline import RAGPipeline
from src.pdf_processor import PDFProcessor
from src.embedding_manager import EmbeddingManager
from src.retrieval import SemanticRetriever
from src.llm_handler import LLMHandler

# Public API
__all__ = [
    'RAGPipeline',
    'PDFProcessor',
    'EmbeddingManager',
    'SemanticRetriever',
    'LLMHandler',
    '__version__',
    '__author__',
    '__license__',
]
