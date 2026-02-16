# RAG Assistant - Production-Ready Retrieval-Augmented Generation

A **production-grade Retrieval-Augmented Generation (RAG)** system with local LLM deployment, Docker containerization, and Streamlit web interface. Built from scratch to understand RAG principles while maintaining enterprise-level architecture.

## 🚀 Features

### Core RAG Pipeline
- ✅ **PDF Processing**: Extract, chunk, and preprocess documents
- ✅ **Semantic Embeddings**: Generate embeddings with SentenceTransformers
- ✅ **Vector Retrieval**: Semantic search using dot-product similarity
- ✅ **LLM Integration**: Local Llama 3.1 8B with quantization support
- ✅ **Context Augmentation**: Smart prompt engineering with retrieved context
- ✅ **Stream Response**: Real-time token streaming for better UX

### Production Features
- 🐳 **Docker Containerization**: Complete Docker & docker-compose setup
- 🌐 **Streamlit Web UI**: Interactive chat interface
- ⚙️ **Configuration Management**: .env-based environment configuration
- 📝 **Structured Logging**: JSON and file-based logging
- 🛡️ **Error Handling**: Comprehensive error handling and validation
- 📊 **Statistics & Monitoring**: Pipeline statistics and health checks
- 🔐 **Security**: Support for Hugging Face token management
- 🚀 **GPU Optimization**: CUDA support with quantization options

### Architecture
```
RAG-Production/
├── app/                          # Streamlit application
│   ├── streamlit_app.py         # Main web interface
│   └── pages/                   # Multi-page support
├── config/                      # Configuration management
│   └── settings.py              # Environment-based settings
├── src/                         # Core RAG pipeline
│   ├── pdf_processor.py         # PDF extraction & chunking
│   ├── embedding_manager.py     # Embeddings generation
│   ├── retrieval.py             # Semantic search
│   ├── llm_handler.py           # LLM inference
│   └── rag_pipeline.py          # Orchestration
├── data/
│   ├── documents/               # Uploaded PDFs
│   ├── embeddings/              # Stored embeddings
│   └── cache/                   # Cache storage
├── logs/                        # Application logs
├── docker/
│   └── Dockerfile               # Container definition
├── docker-compose.yml           # Multi-container setup
└── requirements.txt             # Python dependencies
```

## 📋 Prerequisites

### Hardware
- **NVIDIA GPU** with 8GB+ VRAM (for Llama 3.1 8B)
- **CPU**: 4+ cores for embedding model
- **RAM**: 16GB+ recommended
- **Storage**: 50GB+ for models

### Software
- **Docker & Docker Compose** (for containerized deployment)
- **Python 3.10+** (for local development)
- **CUDA 11.8+** (for GPU support)
- **Hugging Face CLI** (for model downloads)

### API Tokens
- **Hugging Face Token**: [Get access to Llama 3.1 8B](https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone repository
git clone <repo-url>
cd RAG-Production

# 2. Create .env file
cp .env.example .env

# 3. Add your Hugging Face token to .env
# HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxx

# 4. Build and run with Docker Compose
docker-compose up --build

# 5. Access the app
# Open http://localhost:8501 in your browser
```

### Option 2: Local Development

```bash
# 1. Clone and setup
git clone <repo-url>
cd RAG-Production
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env and add your tokens and preferences

# 4. Download spaCy model (one-time)
python -m spacy download en_core_web_sm

# 5. Run Streamlit
streamlit run app/streamlit_app.py
```

## 🎯 Usage

### Web Interface (Streamlit)

1. **Upload PDF**
   - Click "Upload PDF Document" in sidebar
   - Select your PDF file
   - System automatically processes and embeds

2. **Query**
   - Enter your question in the input field
   - Click "Ask"
   - View answer with retrieved context

3. **Customize**
   - Adjust temperature, max tokens, top-k in sidebar
   - View pipeline statistics
   - Clear chat history as needed

### Python API

```python
from src.rag_pipeline import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline(load_llm=True)

# Process PDF
chunks = pipeline.process_pdf("document.pdf")
embedded_chunks = pipeline.embed_chunks(chunks)
pipeline.setup_retriever(embedded_chunks)

# Query
answer = pipeline.ask(
    query="What are macronutrients?",
    top_k=5,
    temperature=0.7,
    max_new_tokens=512
)

# Or with context
answer, context = pipeline.ask("Your question", return_context=True)
for chunk in context:
    print(f"Score: {chunk['similarity_score']:.4f}")
    print(f"Text: {chunk['sentence_chunk']}")
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# API Keys
HUGGINGFACE_TOKEN=hf_xxxxx

# Models
EMBEDDING_MODEL=all-mpnet-base-v2
LLM_MODEL_ID=meta-llama/Meta-Llama-3.1-8B-Instruct
DEVICE=cuda

# Generation
LLM_TEMPERATURE=0.7
LLM_MAX_NEW_TOKENS=512
RETRIEVAL_TOP_K=5

# Processing
MIN_CHUNK_TOKENS=30
SENTENCE_CHUNK_SIZE=10

# Paths
DATA_DIR=./data
LOGS_DIR=./logs

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# App
ENVIRONMENT=production
DEBUG=false
```

## 🐳 Docker Deployment

### Build Custom Image

```bash
docker build -f docker/Dockerfile -t rag-assistant:latest .
```

### Run Container

```bash
docker run -p 8501:8501 \
  -e HUGGINGFACE_TOKEN="your_token" \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --gpus all \
  rag-assistant:latest
```

### Using Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f rag-app

# Stop services
docker-compose down
```

## 📊 API Reference

### RAGPipeline

```python
# Process and retrieve
pipeline.pipeline(pdf_path, query=None, save_embeddings=True)

# Retrieve context chunks
context = pipeline.retrieve(query, top_k=5)

# Generate answer
answer = pipeline.generate(query, context_chunks, temperature=0.7)

# Full RAG in one call
answer, context = pipeline.ask(query, top_k=5, return_context=True)

# Pipeline statistics
stats = pipeline.get_statistics()
```

### PDFProcessor

```python
processor = PDFProcessor()
chunks = processor.process_pdf("file.pdf")
```

### EmbeddingManager

```python
manager = EmbeddingManager()
embeddings = manager.generate_embeddings(["text1", "text2"])
manager.save_embeddings(chunks, "embeddings.pkl")
loaded = manager.load_embeddings("embeddings.pkl")
```

### SemanticRetriever

```python
retriever = SemanticRetriever(chunks, embedding_manager)
results, scores = retriever.retrieve(query, top_k=5)
```

### LLMHandler

```python
llm = LLMHandler()
answer = llm.generate(prompt, temperature=0.7, max_new_tokens=512)

# Streaming
for token in llm.generate_streaming(prompt):
    print(token, end='')
```

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src

# Specific test
pytest tests/test_pdf_processor.py -v
```

## 🔍 Monitoring and Logging

### Log Files
- Located in `./logs/`
- Format: `streamlit_YYYYMMDD_HHMMSS.log`
- Configurable via `LOG_LEVEL` and `LOG_FORMAT`

### Health Check
```bash
# Docker health status
docker ps --format "{{.Names}} {{.Status}}"

# Manual check
curl http://localhost:8501/_stcore/health
```

## 🚀 Performance Optimization

### For Limited VRAM (< 8GB)
```bash
# Enable 8-bit quantization
USE_8BIT_QUANTIZATION=true

# Or 4-bit
USE_4BIT_QUANTIZATION=true

# Reduce batch size
EMBEDDING_BATCH_SIZE=16
```

### For Multiple Concurrent Users
- Use larger batch sizes for embeddings
- Deploy multiple container instances
- Use load balancer (nginx, HAProxy)

## 🛠️ Troubleshooting

### CUDA Out of Memory
1. Enable quantization in `.env`
2. Reduce `LLM_MAX_NEW_TOKENS`
3. Reduce `RETRIEVAL_TOP_K`

### Slow Embedding Generation
1. Increase `EMBEDDING_BATCH_SIZE`
2. Use GPU (ensure CUDA is available)

### Model Download Issues
```bash
# Manually download models
huggingface-cli login
huggingface-cli download sentence-transformers/all-mpnet-base-v2
huggingface-cli download meta-llama/Meta-Llama-3.1-8B-Instruct
```

## 📚 Educational Resources

- [RAG Paper](https://arxiv.org/abs/2005.11401)
- [Retrieval Augmented Generation Guide](https://js.langchain.com/docs/modules/data_connection/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)
- [LangChain Documentation](https://python.langchain.com/)

## 🔄 Update & Maintenance

```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Clean Docker resources
docker-compose down -v
docker system prune

# Rebuild containers
docker-compose down
docker-compose up --build
```

## 📝 License

This project is licensed under the MIT License - see [LICENSE.txt](LICENSE.txt)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📧 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check [Troubleshooting](#-troubleshooting) section
- Review logs in `./logs/`

## 🙏 Acknowledgments

- Hugging Face for Transformers and model hosting
- Meta for Llama 3.1 8B model
- Sentence Transformers team
- Streamlit for the web framework
