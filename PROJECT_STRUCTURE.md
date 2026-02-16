"""
Project structure and component documentation.
"""

# RAG Assistant - Project Structure

## Directory Hierarchy

```
RAG-Production/
│
├── app/                              # Streamlit Web Application
│   ├── __init__.py
│   ├── streamlit_app.py             # Main application entry point
│   └── pages/                       # Multi-page Streamlit apps
│       ├── __init__.py
│       └── (future pages...)
│
├── src/                             # Core RAG Pipeline Modules
│   ├── __init__.py
│   ├── pdf_processor.py            # PDF extraction, chunking
│   ├── embedding_manager.py        # Embeddings generation/storage
│   ├── retrieval.py                # Semantic search
│   ├── llm_handler.py              # LLM inference
│   ├── rag_pipeline.py             # Orchestration
│   ├── logging_config.py           # Logging setup
│   └── utils.py                    # Utility functions
│
├── config/                          # Configuration Management
│   ├── __init__.py
│   └── settings.py                 # Environment-based settings
│
├── data/                            # Data Storage
│   ├── documents/                  # Uploaded PDF files
│   ├── embeddings/                 # Stored embeddings
│   └── cache/                      # Temporary cache
│
├── logs/                            # Application Logs
│   └── (log files generated at runtime)
│
├── docker/                          # Docker Configuration
│   └── Dockerfile                  # Container definition
│
├── tests/                           # Unit & Integration Tests
│   ├── __init__.py
│   ├── test_pdf_processor.py
│   ├── test_embedding_manager.py
│   ├── test_retrieval.py
│   ├── test_llm_handler.py
│   └── test_rag_pipeline.py
│
├── .env                             # Environment variables (local)
├── .env.example                    # Environment template
├── .dockerignore                   # Docker ignore rules
├── .gitignore                      # Git ignore rules
├── docker-compose.yml              # Multi-container orchestration
├── requirements.txt                # Python dependencies
├── start.sh                        # Startup script (Linux/Mac)
├── start.bat                       # Startup script (Windows)
├── README.md                       # Original project README
├── PRODUCTION_README.md            # Detailed documentation
├── QUICKSTART.md                   # Quick start guide
└── PROJECT_STRUCTURE.md            # This file
```

## Component Details

### app/streamlit_app.py
- Main web interface
- PDF upload handling
- Chat interface
- Settings management
- Statistics display

### src/pdf_processor.py
- PDFProcessor class
- PDF text extraction (PyMuPDF)
- Text preprocessing and cleaning
- Sentence tokenization (spaCy)
- Text chunking and filtering
- Full pipeline orchestration

### src/embedding_manager.py
- EmbeddingManager class
- Model loading and caching
- Batch embedding generation
- Embeddings persistence (save/load)
- Metadata management

### src/retrieval.py
- SemanticRetriever class
- RetrieverConfig configuration
- Similarity-based search
- Results scoring and ranking
- Chunk statistics

### src/llm_handler.py
- LLMHandler class
- Model loading with quantization
- Text generation
- Streaming generation
- Prompt formatting
- Model information

### src/rag_pipeline.py
- RAGPipeline class
- Main orchestration
- Pipeline workflows
- Error handling
- Statistics aggregation

### config/settings.py
- Environment variable management
- Path configuration
- Model parameters
- Logging configuration
- Validation

## Data Flow

```
PDF Upload
    ↓
[PDFProcessor]
    ├── Extract text (PyMuPDF)
    ├── Format & clean
    ├── Split to sentences (spaCy)
    ├── Chunk sentences
    └── Filter by size
    ↓
[EmbeddingManager]
    ├── Load embedding model
    ├── Generate embeddings
    └── Save embeddings
    ↓
User Query
    ↓
[SemanticRetriever]
    ├── Embed query
    ├── Compute similarity
    └── Return top-K chunks
    ↓
[LLMHandler]
    ├── Format prompt with context
    ├── Load LLM model
    ├── Generate response
    └── Return answer
    ↓
Display to User
```

## Configuration Hierarchy

1. Default values in code
2. .env.example template
3. .env local configuration
4. Environment variable overrides
5. Docker environment variables

## API endpoints (Streamlit)

- `/` - Main chat interface
- Sidebar - Document upload and settings
- Chat history - Interactive conversation

## Database/Storage

- **Embeddings**: Pickle files in `data/embeddings/`
- **Documents**: Raw PDFs in `data/documents/`
- **Cache**: Temporary files in `data/cache/`
- **Logs**: JSON logs in `logs/`

## Error Handling

- File validation
- Model loading errors
- GPU memory errors
- API failures
- Type validation

## Security Features

- Hugging Face token management
- Environment-based secrets
- No hardcoded credentials
- PDF size validation
- Input sanitization

## Performance Characteristics

- PDF processing: ~10-30 sec per 100 pages
- Embedding generation: ~2-5 sec per 100 chunks
- Query retrieval: <100ms
- Answer generation: 5-30 sec depending on length

## Logging Strategy

- File and console handlers
- JSON structured logging
- Module-level loggers
- Timestamp tracking
- Error traces

## Testing Coverage Areas

- PDF processing
- Embedding generation
- Retrieval accuracy
- LLM integration
- End-to-end pipeline

## Dependencies Overview

Key external dependencies:
- transformers: LLM models
- sentence-transformers: Embeddings
- PyMuPDF: PDF processing
- spaCy: NLP preprocessing
- torch: Deep learning
- streamlit: Web framework
- python-dotenv: Environment management

## Future Enhancement Points

- Vector database integration (Pinecone, Milvus)
- Multiple LLM support
- Batch processing
- API authentication
- User management
- Performance analytics
- Advanced retrieval (re-ranking)
- Multi-document search
- Export functionality
