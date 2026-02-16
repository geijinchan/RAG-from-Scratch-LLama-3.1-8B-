"""
QUICKSTART GUIDE - Running RAG Assistant

This file provides quick instructions for getting the RAG Assistant up and running.
"""

## Quick Start Options

### Option 1: Docker (Easiest - Recommended)

1. Prerequisites:
   - Docker and Docker Compose installed
   - Hugging Face account and API token

2. Setup:
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env and add your Hugging Face token
   # HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxx
   ```

3. Run:
   ```bash
   # On Windows
   ./start.bat
   
   # On Linux/Mac
   bash start.sh
   
   # Or manually
   docker-compose up --build
   ```

4. Access:
   - Open http://localhost:8501 in your browser

### Option 2: Local Python Environment

1. Prerequisites:
   - Python 3.10+
   - NVIDIA GPU (highly recommended)
   - CUDA 11.8+ (if using GPU)

2. Setup:
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate it
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Download spaCy model
   python -m spacy download en_core_web_sm
   ```

3. Configure:
   ```bash
   # Copy and edit environment file
   cp .env.example .env
   
   # Edit .env with your settings
   ```

4. Run:
   ```bash
   streamlit run app/streamlit_app.py
   ```

5. Access:
   - Open http://localhost:8501 in your browser

## Usage

1. **Upload a PDF**
   - Click "Upload PDF Document" in the left sidebar
   - Select your PDF file
   - Wait for processing (first run takes a few minutes to download models)

2. **Ask Questions**
   - Type your question in the input field
   - Click "Ask"
   - View the answer and retrieved context

3. **Adjust Settings**
   - Temperature: Controls creativity (0.0 = deterministic, 1.0 = creative)
   - Max Tokens: How long answers should be
   - Top-K: How many context chunks to retrieve

## Key Environment Variables

```
HUGGINGFACE_TOKEN=        # Your Hugging Face API token (REQUIRED)
DEVICE=cuda              # cuda or cpu
LLM_TEMPERATURE=0.7      # Generation creativity
RETRIEVAL_TOP_K=5        # Number of context chunks
```

## Common Issues & Solutions

### Issue: CUDA Out of Memory
Solution:
1. Enable quantization in .env: `USE_8BIT_QUANTIZATION=true`
2. Reduce `LLM_MAX_NEW_TOKENS` to 256
3. Reduce `RETRIEVAL_TOP_K` to 3

### Issue: Models won't download
Solution:
```bash
# Login to Hugging Face first
huggingface-cli login

# Then try again
```

### Issue: Docker won't start
Solution:
1. Make sure Docker daemon is running
2. Check available disk space (models need ~50GB)
3. Ensure .env file exists with valid token

## Architecture Overview

```
User Interface (Streamlit)
        ↓
    RAG Pipeline
        ↓
    ┌───┴────┬───────┬─────────┐
    ↓        ↓       ↓         ↓
 PDF Proc  Embedding Retrieval  LLM
   (Text)   (Vectors)  (Search) (Generation)
    ↓        ↓       ↓         ↓
  Chunks  SentenceT SemanticR Llama 3.1
          Embedders Retriever  8B
```

## Next Steps

1. Try different PDF documents
2. Experiment with temperature settings
3. Check logs in `./logs/` folder
4. Review API documentation in PRODUCTION_README.md
5. Build custom integrations using the Python API

## Getting Help

- Check logs: `./logs/`
- Review errors in Streamlit sidebar
- Check PRODUCTION_README.md for detailed documentation
- Review docker-compose logs: `docker-compose logs -f`

## Performance Tips

- Use GPU for best performance
- Batch process multiple questions
- Cache embeddings (done automatically)
- Use smaller PDFs for faster processing (< 100 pages)

Enjoy your RAG Assistant! 🚀
