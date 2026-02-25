# Testing Guide for Groq-Integrated RAG System

This guide explains how to test the RAG system with Groq Cloud API integration.

## Table of Contents
1. [Quick Start](#quick-start)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [End-to-End Testing](#end-to-end-testing)
5. [Manual Testing](#manual-testing)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Run All Tests
```bash
# Install dependencies first
pip install -r requirements.txt

# Run the complete test suite
pytest tests/ -v

# Or run just Groq tests
pytest tests/test_llm_handler_groq.py -v
```

### Run Example Test Script
```bash
# Run the handy test script with mocked Groq
python test_groq_rag.py
```

This will:
- ✅ Test Groq LLM Handler initialization
- ✅ Test text generation with mocking
- ✅ Test streaming responses
- ✅ Test RAG pipeline integration
- ✅ Test error handling
- ✅ Test configuration loading

---

## Unit Testing

### 1. Test Groq LLM Handler

Tests the core Groq API integration:

```bash
pytest tests/test_llm_handler_groq.py::TestGroqLLMHandler -v
```

**What it tests:**
- Handler initialization with API key
- Text generation with Groq API
- Custom temperature and max_tokens parameters
- API error handling
- Model info retrieval

**Example test output:**
```
test_initialization PASSED
test_generate_text PASSED
test_generate_with_custom_temperature PASSED
test_generate_with_custom_max_tokens PASSED
test_streaming_generation PASSED
```

### 2. Test Prompt Formatting

Tests how prompts are formatted with context:

```bash
pytest tests/test_llm_handler_groq.py::TestGroqPromptFormatting -v
```

**What it tests:**
- Context inclusion in prompts
- Query inclusion in prompts
- Multiple context items handling
- Prompt structure validation

### 3. Test Error Handling

Tests API error scenarios:

```bash
pytest tests/test_llm_handler_groq.py::TestGroqErrorHandling -v
```

**What it tests:**
- API error propagation
- Streaming error handling
- Invalid API key errors
- Timeout handling

---

## Integration Testing

### Test RAG Pipeline with Groq

Tests the complete RAG pipeline:

```bash
pytest tests/test_rag_pipeline.py -v
```

**What it tests:**
- Pipeline initialization with Groq
- PDF processing integration
- Embedding generation
- Retrieval with context
- Generation with Groq

### Test Retrieval System

Tests semantic retrieval (independent of LLM):

```bash
pytest tests/test_retrieval.py -v
```

**What it tests:**
- Chunk retrieval
- Similarity scoring
- Top-K filtering
- Metadata preservation

### Test PDF Processing

Tests document processing:

```bash
pytest tests/test_pdf_processor.py -v
```

**What it tests:**
- PDF parsing
- Text extraction
- Chunk creation
- Token counting

### Test Embeddings

Tests embedding generation:

```bash
pytest tests/test_embedding_manager.py -v
```

**What it tests:**
- Embedding generation
- Batch processing
- Dimension consistency
- Similarity calculation

---

## End-to-End Testing

### Complete System Flow

Run the test script to test the complete workflow:

```bash
python test_groq_rag.py
```

**This tests:**
1. Configuration loading
2. LLM handler initialization
3. Generation and streaming
4. RAG pipeline setup
5. Error handling
6. Model info retrieval

### Example Output
```
======================================================================
GROQ-INTEGRATED RAG SYSTEM - TEST SUITE
======================================================================

======================================================================
TEST 1: Groq LLM Handler
======================================================================

✓ Creating Groq LLM Handler...
  Model: llama-3.3-70b-versatile
  Temperature: 0.7
  Max Tokens: 2048

✓ Testing text generation...
  Query: 'What is AI?'
  Response: This is a test response from Groq.
  ✓ API called with model: llama-3.3-70b-versatile
  ✓ Temperature: 0.7
  ✓ Max tokens: 2048

✓ Testing streaming generation...
  Chunks: ['Hello ', 'from ', 'Groq!']

✅ Groq LLM Handler tests passed!
```

---

## Manual Testing

### 1. Test Groq Connection

Test if Groq API is accessible:

```python
from groq import Groq
import os

api_key = os.getenv('GROQ_API_KEY')
client = Groq(api_key=api_key)

# List available models
models = client.models.list()
print("Available models:")
for model in models.data:
    print(f"  - {model.id}")
```

### 2. Test With Real API

**WARNING: Uses real API quota!**

Create a test file `test_real_groq.py`:

```python
from src.llm_handler import LLMHandler
from config.settings import GROQ_MODEL, GROQ_API_KEY

# Create handler
handler = LLMHandler(
    model_id=GROQ_MODEL,
    api_key=GROQ_API_KEY
)

# Test generation
print("Testing real Groq API...")
response = handler.generate("What is RAG (Retrieval Augmented Generation)?")
print(f"Response: {response}")

# Test streaming
print("\nTesting streaming...")
for chunk in handler.generate_streaming("Tell me about Python in one sentence."):
    print(chunk, end='', flush=True)
print()
```

Run it:
```bash
python test_real_groq.py
```

### 3. Test Streamlit App

Test the full UI:

```bash
streamlit run app/streamlit_app.py
```

**Manual steps:**
1. Upload a PDF document
2. Wait for processing to complete
3. Ask a question about the document
4. Verify the answer uses retrieved context

---

## Testing Different Groq Models

Test with different models to compare performance:

```python
from src.llm_handler import LLMHandler
from config.settings import GROQ_API_KEY

models = [
    "llama-3.3-70b-versatile",
    "llama-3.1-70b-versatile",
    "llama-3.1-8b-instant",
    "mixtral-8x7b-32768"
]

prompt = "What is artificial intelligence in one sentence?"

for model_name in models:
    try:
        handler = LLMHandler(
            model_id=model_name,
            api_key=GROQ_API_KEY
        )
        print(f"\n{model_name}:")
        response = handler.generate(prompt, temperature=0.3)
        print(f"  {response[:100]}...")
    except Exception as e:
        print(f"  Error: {e}")
```

---

## Performance Testing

### Measure Response Time

```python
import time
from src.llm_handler import LLMHandler
from config.settings import GROQ_MODEL, GROQ_API_KEY

handler = LLMHandler(
    model_id=GROQ_MODEL,
    api_key=GROQ_API_KEY
)

start = time.time()
response = handler.generate("Explain quantum computing in detail.")
elapsed = time.time() - start

print(f"Response time: {elapsed:.2f} seconds")
print(f"Response length: {len(response)} characters")
print(f"Tokens per second: {len(response.split()) / elapsed:.1f}")
```

### Test Streaming Performance

```python
import time
from src.llm_handler import LLMHandler
from config.settings import GROQ_MODEL, GROQ_API_KEY

handler = LLMHandler(
    model_id=GROQ_MODEL,
    api_key=GROQ_API_KEY
)

start = time.time()
chunks = list(handler.generate_streaming("Write a 200-word essay on AI."))
elapsed = time.time() - start

print(f"Streaming time: {elapsed:.2f} seconds")
print(f"Total chunks: {len(chunks)}")
print(f"Chunks per second: {len(chunks) / elapsed:.1f}")
```

---

## Troubleshooting Tests

### Common Issues

#### 1. **ImportError: No module named 'groq'**
```bash
# Install Groq SDK
pip install groq>=0.4.0

# Or reinstall all requirements
pip install -r requirements.txt
```

#### 2. **ValueError: GROQ_API_KEY not found**
```bash
# Set API key in .env
echo "GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx" >> .env

# Or set environment variable
export GROQ_API_KEY="gsk_xxxxxxxxxxxxxxxx"
```

#### 3. **Tests Fail with "API Key invalid"**
- Check if API key is correct in `.env`
- Verify key has appropriate permissions on Groq dashboard
- Try with a fresh API key from https://console.groq.com

#### 4. **Timeout Errors**
```bash
# Increase timeout in config/settings.py
# Change GROQ_API_TIMEOUT from 60 to 120

# Or set environment variable
export GROQ_API_TIMEOUT=120
```

#### 5. **Rate Limit Errors**
- Check Groq free tier limits (5000 requests/month)
- Upgrade plan if needed
- Implement request batching in your code

### Debug Mode

Run tests with verbose output:

```bash
# Very verbose output
pytest tests/ -vv

# Show print statements
pytest tests/ -s

# Stop on first failure
pytest tests/ -x

# Run specific test
pytest tests/test_llm_handler_groq.py::TestGroqLLMHandler::test_generate_text -v
```

### Enable Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Get logger
logger = logging.getLogger('src.llm_handler')

# Now test will show detailed logs
from src.llm_handler import LLMHandler
```

---

## Testing Checklist

- [ ] All dependencies installed: `pip list | grep groq`
- [ ] API key configured: `.env` has `GROQ_API_KEY`
- [ ] Model name set: `.env` has `GROQ_MODEL`
- [ ] Unit tests pass: `pytest tests/test_llm_handler_groq.py -v`
- [ ] Integration tests pass: `pytest tests/test_rag_pipeline.py -v`
- [ ] All tests pass: `pytest tests/ -v`
- [ ] Test script runs: `python test_groq_rag.py`
- [ ] Configuration loads: Tests report correct model and timeout
- [ ] Error handling works: Tests validate error propagation
- [ ] Streamlit app starts: `streamlit run app/streamlit_app.py`

---

## CI/CD Testing

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      env:
        GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        GROQ_MODEL: llama-3.3-70b-versatile
      run: |
        pytest tests/ -v
```

### Docker Testing

```bash
# Build image
docker build -t rag-groq .

# Run tests in container
docker run --env-file .env rag-groq pytest tests/ -v

# Run test script in container
docker run --env-file .env rag-groq python test_groq_rag.py
```

---

## Performance Benchmarks

Expected performance with Groq:

| Metric | Value |
|--------|-------|
| First response time | 2-10 seconds |
| Streaming latency | <100ms first chunk |
| Generation speed | 50-100 tokens/sec |
| Memory usage | ~400MB |
| API latency | <500ms |
| Cost | Free tier: 5000 requests/month |

---

## Next Steps

1. **Run the integrated test:** `python test_groq_rag.py`
2. **Run pytest:** `pytest tests/ -v`
3. **Deploy Streamlit:** `streamlit run app/streamlit_app.py`
4. **Monitor performance:** Use test scripts to benchmark
5. **Scale up:** Ready for production use

---

## Support

For issues:
1. Check [Tests Output](#testing-checklist)
2. Review [Troubleshooting](#troubleshooting-tests)
3. See [GROQ_INTEGRATION.md](GROQ_INTEGRATION.md) for setup help
4. Check [Groq API Docs](https://console.groq.com/docs)

Happy testing! 🚀
