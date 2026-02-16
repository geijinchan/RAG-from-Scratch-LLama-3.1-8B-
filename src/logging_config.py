"""
Logging configuration module.
Initializes structured logging for the application.
"""

import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from config.settings import LOGS_DIR, LOG_LEVEL, LOG_FORMAT

def setup_logging():
    """
    Configure logging for the application.
    Sets up file and console handlers with appropriate formatters.
    """
    
    # Create logs directory
    logs_dir = Path(LOGS_DIR)
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Log file path
    log_file = logs_dir / f"rag_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Formatter
    if LOG_FORMAT == "json":
        from pythonjsonlogger import jsonlogger
        formatter = jsonlogger.JsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s',
            timestamp=True
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, LOG_LEVEL))
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL))
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Suppress third-party loggers
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
    
    return root_logger

# Initialize logging on module import
logger = setup_logging()
