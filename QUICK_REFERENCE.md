# Quick Reference Guide - Groq RAG System

Fast lookup for common tasks and commands.

## 🚀 5-Minute Setup

```bash
# 1. Get API key (30 seconds)
# Visit: https://console.groq.com/keys

# 2. Create .env file (30 seconds)
echo "GROQ_API_KEY=gsk_your_key_here" > .env
echo "GROQ_MODEL=llama-3.3-70b-versatile" >> .env

# 3. Install dependencies (60 seconds)
pip install -r requirements.txt

# 4. Test it works (60 seconds)
python test_groq_rag.py

# 5. Run the app (instant)
streamlit run app/streamlit_app.py
# → Opens at http://localhost:8501
```

---

## 📋 Common Commands

### Testing
```bash
# Quick validation test
python test_groq_rag.py

# Full test suite
pytest tests/ -v

# Specific test file
pytest tests/test_llm_handler_groq.py -v

# Show print output during tests
pytest tests/ -s

# Stop on first failure
pytest tests/ -x
```

### Development
```bash
# Start app locally
streamlit run app/streamlit_app.py

# Check configuration
python -c "from config.settings import *; print(f'Model: {GROQ_MODEL}')"

# Test API connection
python -c "from src.llm_handler import LLMHandler; LLMHandler(api_key='test')" 2>&1 | head -5
```

### Docker
```bash
# Build image
docker build -t rag-groq .

# Run container
docker run --env-file .env -p 8501:8501 rag-groq

# Run with docker-compose
docker-compose up --build

# View logs
docker logs rag-groq

# Stop container
docker-compose down
```

### Deployment
```bash
# Heroku
git push heroku main

# AWS/Google Cloud/Azure
# See DEPLOYMENT_GUIDE.md for detailed instructions
```

---

## 🔧 Configuration Reference

### Required Settings (.env)
```bash
GROQ_API_KEY=gsk_xxxxxxxxxxxxx     # Your Groq API key
GROQ_MODEL=llama-3.3-70b-versatile # Which model to use
```

### Optional Settings
```bash
EMBEDDING_MODEL=all-mpnet-base-v2     # Embedding model
LLM_TEMPERATURE=0.7                    # 0.0=deterministic, 1.0=creative
LLM_MAX_NEW_TOKENS=2048                # Max response length
RETRIEVAL_TOP_K=5                      # How many chunks to retrieve
GROQ_API_TIMEOUT=60                    # API timeout in seconds
DEVICE=cpu                             # CPU or cuda (for embeddings only)
```

### Available Models
```
llama-3.3-70b-versatile    ← Recommended (balanced)
llama-3.1-70b-versatile    (long context, fine-grained)
llama-3.1-8b-instant       (fastest)
mixtral-8x7b-32768         (multimodal reasoning)
```

---

## 📚 File Structure

```
├── config/
│   └── settings.py          ← Configuration management
├── src/
│   ├── llm_handler.py       ← Groq API client (LLM)
│   ├── rag_pipeline.py      ← Main orchestration
│   ├── retrieval.py         ← Semantic search
│   ├── pdf_processor.py     ← PDF parsing
│   └── embedding_manager.py ← Text embeddings
├── app/
│   └── streamlit_app.py     ← Web interface
├── tests/
│   ├── test_llm_handler_groq.py    ← Groq tests
│   ├── test_rag_pipeline.py
│   ├── test_retrieval.py
│   └── ...
└── Documentation/
    ├── README.md            ← Project overview
    ├── GROQ_INTEGRATION.md  ← Groq details
    ├── TEST_GUIDE.md        ← Testing procedures
    ├── DEPLOYMENT_GUIDE.md  ← Deployment instructions
    └── MIGRATION_SUMMARY.md ← What changed
```

---

## 🐛 Troubleshooting

### "No module named 'groq'"
```bash
pip install groq>=0.4.0
# Or reinstall all:
pip install -r requirements.txt --force-reinstall
```

### "GROQ_API_KEY not found"
```bash
# Check .env exists
ls .env

# Add to .env if missing
echo "GROQ_API_KEY=gsk_xxxxx" >> .env

# Or set temporarily
export GROQ_API_KEY=gsk_xxxxx
```

### "API key invalid"
- Visit https://console.groq.com/keys
- Generate a new API key
- Update in `.env` file

### "Port 8501 already in use"
```bash
# Use different port
streamlit run app/streamlit_app.py --server.port=8502

# Or kill existing process
# On Windows: netstat -ano | findstr :8501
# On Mac/Linux: lsof -ti:8501 | xargs kill -9
```

### Tests failing with timeouts
```bash
# Increase timeout in .env
echo "GROQ_API_TIMEOUT=120" >> .env

# Or in config/settings.py
GROQ_API_TIMEOUT = 120
```

### Rate limit errors
- Check free tier: 5,000 requests/month
- Wait for limit reset
- Or upgrade Groq plan

---

## 📖 Documentation Map

| Need | Document | Section |
|------|----------|---------|
| Setup & overview | README.md | Quick Start |
| Groq specifics | GROQ_INTEGRATION.md | Full guide |
| How to test | TEST_GUIDE.md | Testing |
| How to deploy | DEPLOYMENT_GUIDE.md | Deployment |
| What changed | MIGRATION_SUMMARY.md | Overview |
| Quick help | This file | Quick Reference |

---

## 🧠 Code Examples

### Basic RAG Usage
```python
from src.rag_pipeline import RAGPipeline
from config.settings import GROQ_MODEL

# Initialize
rag = RAGPipeline(groq_model=GROQ_MODEL, load_llm=True)

# Process PDF
chunks = rag.process_pdf("document.pdf")
embedded = rag.embed_chunks(chunks)
rag.setup_retriever(embedded)

# Ask question
answer, context = rag.ask("What is this about?")
print(answer)
```

### Direct LLM Usage
```python
from src.llm_handler import LLMHandler
from config.settings import GROQ_MODEL, GROQ_API_KEY

handler = LLMHandler(
    model_id=GROQ_MODEL,
    api_key=GROQ_API_KEY
)

# Generate text
response = handler.generate("Explain AI in one sentence")
print(response)

# Stream response
for chunk in handler.generate_streaming("Tell me about Python"):
    print(chunk, end='', flush=True)
```

### Custom Temperature/Tokens
```python
from src.llm_handler import LLMHandler

handler = LLMHandler(
    model_id="llama-3.1-8b-instant",
    api_key="gsk_xxxxx",
    temperature=0.3,  # More deterministic
    max_tokens=512    # Shorter responses
)

response = handler.generate("Your prompt")
```

---

## 📊 Performance Expectations

### First Time Setup
- Get API key: 1 min
- Configure: 1 min
- Install dependencies: 1 min
- Run tests: 2 min
- **Total: ~5 minutes**

### Typical Query
- Upload PDF: 30-60 seconds
- Ask question: 3-5 seconds
- Get response: Streamed in real-time
- **Total: <10 seconds**

### System Resources
- Memory: ~400 MB
- CPU: ~20% usage
- Network: Minimal (just API calls)
- GPU: Not needed

---

## ✅ Validation Checklist

New to the system? Run through this:

- [ ] Created `.env` with GROQ_API_KEY
- [ ] Installed dependencies: `pip install -r requirements.txt`
- [ ] Ran test script: `python test_groq_rag.py`
- [ ] All tests passed: `pytest tests/ -v`
- [ ] App starts: `streamlit run app/streamlit_app.py`
- [ ] Can upload PDFs
- [ ] Can ask questions
- [ ] Get responses back

If any step fails, check [Troubleshooting](#-troubleshooting) above.

---

## 🔗 Important Links

**Get Started:**
- Groq API Key: https://console.groq.com/keys
- Groq Docs: https://console.groq.com/docs
- Groq Playground: https://console.groq.com/playground

**Project Documentation:**
- Main README: [README.md](README.md)
- Groq Integration: [GROQ_INTEGRATION.md](GROQ_INTEGRATION.md)
- Testing Guide: [TEST_GUIDE.md](TEST_GUIDE.md)
- Deployment: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

**External Resources:**
- Python: https://python.org/
- Streamlit: https://streamlit.io/
- Docker: https://docker.com/
- GitHub: https://github.com/

---

## 💡 Pro Tips

### For Performance
- Use `llama-3.1-8b-instant` for speed (lose some quality)
- Set `RETRIEVAL_TOP_K=2` to retrieve fewer chunks
- Use `LLM_TEMPERATURE=0.3` for consistent results

### For Quality
- Use `llama-3.3-70b-versatile` for better answers
- Set `RETRIEVAL_TOP_K=5` for more context
- Use `LLM_TEMPERATURE=0.7` for creativity

### For Development
- Use `pytest tests/ -s` to see print statements
- Use `pytest tests/test_file.py -v` to test specific file
- Enable logging: `logging.basicConfig(level=logging.DEBUG)`

### For Production
- Monitor API usage at https://console.groq.com/usage
- Use `GROQ_API_TIMEOUT=120` for reliability
- Set up error logging and alerting
- Document your API key (use environment variables)

---

## 🚀 Next Steps

**Just Starting?**
1. Follow [5-Minute Setup](#-5-minute-setup) above
2. Read [README.md](README.md) for overview
3. Run `python test_groq_rag.py` to validate

**Ready to Deploy?**
1. Review [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
2. Choose deployment platform (local, Docker, cloud)
3. Follow platform-specific instructions

**Want to Learn More?**
1. Read [GROQ_INTEGRATION.md](GROQ_INTEGRATION.md) for technical details
2. Review [TEST_GUIDE.md](TEST_GUIDE.md) for testing approaches
3. Check [MIGRATION_SUMMARY.md](MIGRATION_SUMMARY.md) for what changed

---

## 📞 Getting Help

**Problem Type** | **Where to Look**
---|---
Setup issues | GROQ_INTEGRATION.md → Setup
Testing problems | TEST_GUIDE.md → Troubleshooting
Deployment errors | DEPLOYMENT_GUIDE.md → Troubleshooting
General questions | README.md or search docs
Groq API issues | https://console.groq.com/docs

---

**Last Updated:** February 20, 2026
**Status:** ✅ Production Ready
**Version:** 2.0 - Groq Cloud API Edition

*For complete information, see the documentation files in this directory.*
