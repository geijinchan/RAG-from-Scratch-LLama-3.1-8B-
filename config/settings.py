"""
Application settings and configuration management.
Loads configuration from environment variables with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import logging

# Load .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", BASE_DIR / "data"))
EMBEDDINGS_DIR = Path(os.getenv("EMBEDDINGS_DIR", DATA_DIR / "embeddings"))
DOCUMENTS_DIR = Path(os.getenv("DOCUMENTS_DIR", DATA_DIR / "documents"))
LOGS_DIR = Path(os.getenv("LOGS_DIR", BASE_DIR / "logs"))
CACHE_DIR = Path(os.getenv("CACHE_DIR", DATA_DIR / "cache"))

# Create directories if they don't exist
for directory in [DATA_DIR, EMBEDDINGS_DIR, DOCUMENTS_DIR, LOGS_DIR, CACHE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Configuration
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")

# Model Configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-mpnet-base-v2")
LLM_MODEL_ID = os.getenv("LLM_MODEL_ID", "meta-llama/Meta-Llama-3.1-8B-Instruct")
DEVICE = os.getenv("DEVICE", "cuda")

# LLM Parameters
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_NEW_TOKENS: int = int(os.getenv("LLM_MAX_NEW_TOKENS", "512"))
RETRIEVAL_TOP_K: int = int(os.getenv("RETRIEVAL_TOP_K", "5"))

# PDF Processing
MIN_CHUNK_TOKENS: int = int(os.getenv("MIN_CHUNK_TOKENS", "30"))
SENTENCE_CHUNK_SIZE: int = int(os.getenv("SENTENCE_CHUNK_SIZE", "10"))

# Streamlit Configuration
STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
STREAMLIT_SERVER_HEADLESS: bool = os.getenv("STREAMLIT_SERVER_HEADLESS", "true").lower() == "true"
STREAMLIT_MAX_UPLOAD_SIZE: int = int(os.getenv("STREAMLIT_SERVER_MAXUPLOADSIZE", "200"))

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")

# Application Configuration
DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

# Quantization Configuration (for memory optimization)
USE_8BIT_QUANTIZATION: bool = True
USE_4BIT_QUANTIZATION: bool = False  # Use 8-bit instead for better compatibility
QUANTIZATION_COMPUTE_DTYPE = "float16"

# Model Cache
CACHE_EMBEDDING_MODEL: bool = True
CACHE_LLM_MODEL: bool = True

# File size limits
MAX_PDF_SIZE_MB: int = 50
MAX_PDF_SIZE_BYTES: int = MAX_PDF_SIZE_MB * 1024 * 1024

# Batch Processing
EMBEDDING_BATCH_SIZE: int = 32
GENERATION_BATCH_SIZE: int = 1

# Timeouts (in seconds)
EMBEDDING_TIMEOUT: int = 300
LLM_TIMEOUT: int = 600

class Config:
    """Configuration class for accessing settings"""
    
    @staticmethod
    def get_embedding_dir() -> Path:
        """Get embeddings directory"""
        return EMBEDDINGS_DIR
    
    @staticmethod
    def get_documents_dir() -> Path:
        """Get documents directory"""
        return DOCUMENTS_DIR
    
    @staticmethod
    def get_logs_dir() -> Path:
        """Get logs directory"""
        return LOGS_DIR
    
    @staticmethod
    def get_cache_dir() -> Path:
        """Get cache directory"""
        return CACHE_DIR
    
    @staticmethod
    def validate_config() -> bool:
        """Validate critical configuration"""
        required_vars = ["EMBEDDING_MODEL", "LLM_MODEL_ID"]
        for var in required_vars:
            if not globals().get(var):
                logging.warning(f"Missing configuration: {var}")
        return True

# Validate on import
Config.validate_config()
