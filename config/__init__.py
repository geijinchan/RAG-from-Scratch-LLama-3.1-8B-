"""
Configuration Module

Centralized configuration management for the RAG system.

Features:
    - Environment-based configuration
    - GPU/CPU device detection and management
    - Model and API configuration
    - Logging setup
    - Path management
    - Validation and health checks

Usage:
    from config import settings
    
    # Access configuration
    device = settings.DEVICE
    embeddings_dir = settings.EMBEDDINGS_DIR
    
    # Check GPU availability
    gpu_info = settings.Config.get_gpu_info()
    
    # Validate configuration
    settings.Config.validate_config()
"""

from config.settings import (
    # Paths
    BASE_DIR,
    DATA_DIR,
    EMBEDDINGS_DIR,
    DOCUMENTS_DIR,
    LOGS_DIR,
    CACHE_DIR,
    
    # GPU/Device Configuration
    USE_GPU,
    DEVICE,
    GPU_DEVICE_ID,
    CUDA_VISIBLE_DEVICES,
    
    # Models
    EMBEDDING_MODEL,
    GROQ_MODEL,
    
    # API
    GROQ_API_KEY,
    HUGGINGFACE_TOKEN,
    
    # LLM Parameters
    LLM_TEMPERATURE,
    LLM_MAX_NEW_TOKENS,
    RETRIEVAL_TOP_K,
    
    # Application
    DEBUG,
    ENVIRONMENT,
    LOG_LEVEL,
    
    # Config class
    Config,
)

__version__ = "1.0.0"

__all__ = [
    'BASE_DIR',
    'DATA_DIR',
    'EMBEDDINGS_DIR',
    'DOCUMENTS_DIR',
    'LOGS_DIR',
    'CACHE_DIR',
    'USE_GPU',
    'DEVICE',
    'GPU_DEVICE_ID',
    'CUDA_VISIBLE_DEVICES',
    'EMBEDDING_MODEL',
    'GROQ_MODEL',
    'GROQ_API_KEY',
    'HUGGINGFACE_TOKEN',
    'LLM_TEMPERATURE',
    'LLM_MAX_NEW_TOKENS',
    'RETRIEVAL_TOP_K',
    'DEBUG',
    'ENVIRONMENT',
    'LOG_LEVEL',
    'Config',
]
