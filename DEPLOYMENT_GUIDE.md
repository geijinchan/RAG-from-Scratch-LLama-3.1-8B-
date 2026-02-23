# Deployment Guide for Groq-Integrated RAG System

Complete guide for deploying the RAG system with Groq Cloud API integration.

## Table of Contents
1. [Local Deployment](#local-deployment)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Monitoring & Logging](#monitoring--logging)
6. [Troubleshooting](#troubleshooting)

---

## Local Deployment

### Prerequisites
- Python 3.10+
- pip or conda
- Groq API key from https://console.groq.com

### Step 1: Clone and Setup

```bash
# Navigate to project directory
cd "RAG From Scratch/git"

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 2: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify Groq is installed
pip list | grep groq
```

**Expected packages:**
- groq>=0.4.0 (Groq API client)
- streamlit (Web UI)
- sentence-transformers (Embeddings)
- pymupdf (PDF processing)
- numpy, pandas (Data processing)
- pytest (Testing)

### Step 3: Configure Environment

Create `.env` file with your settings:

```bash
# Get your API key from https://console.groq.com/keys
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx

# Model to use
GROQ_MODEL=llama-3.3-70b-versatile

# Embedding model
EMBEDDING_MODEL=all-mpnet-base-v2

# Optional: Adjust these for performance tuning
LLM_TEMPERATURE=0.7
LLM_MAX_NEW_TOKENS=2048
RETRIEVAL_TOP_K=5
```

**Validate configuration:**

```bash
python -c "from config.settings import GROQ_MODEL, GROQ_API_KEY; print(f'Model: {GROQ_MODEL}'); print(f'API Key set: {bool(GROQ_API_KEY)}')"
```

### Step 4: Test Installation

```bash
# Run quick test
python test_groq_rag.py

# Run full test suite
pytest tests/ -v
```

**Expected output:**
```
✅ Groq LLM Handler tests passed!
✅ RAG Pipeline tests passed!
✅ Error handling tests passed!
✅ Configuration loading passed!
🎉 ALL TESTS PASSED! 🎉
```

### Step 5: Run Streamlit App

```bash
# Start the Streamlit application
streamlit run app/streamlit_app.py
```

**Application will open at:** http://localhost:8501

**Features:**
- Upload PDF documents
- Ask questions about documents
- See retrieved context and answers
- Real-time streaming responses

---

## Docker Deployment

### Prerequisites
- Docker installed
- docker-compose (optional but recommended)

### Using Docker Compose (Recommended)

**1. Create `.env` file:**

```bash
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=all-mpnet-base-v2
```

**2. Deploy with Docker Compose:**

```bash
# Build and start the container
docker-compose up --build

# In another terminal, check logs
docker-compose logs -f

# Stop the service
docker-compose down
```

**3. Access the application:**

```
http://localhost:8501
```

### Using Docker Directly

**1. Build image:**

```bash
docker build -t rag-groq:latest .
```

**2. Run container:**

```bash
docker run \
  --env-file .env \
  -p 8501:8501 \
  --name rag-groq \
  rag-groq:latest
```

**3. Access application:**

```
http://localhost:8501
```

**4. Stop container:**

```bash
docker stop rag-groq
docker rm rag-groq
```

### Advanced Docker Options

**Run with volume mounting (for persistence):**

```bash
docker run \
  --env-file .env \
  -p 8501:8501 \
  -v $(pwd)/uploads:/app/uploads \
  -v $(pwd)/data:/app/data \
  rag-groq:latest
```

**Run with GPU support (if needed):**

```bash
docker run \
  --gpus all \
  --env-file .env \
  -p 8501:8501 \
  rag-groq:latest
```

**Run in background (daemon mode):**

```bash
docker run \
  -d \
  --env-file .env \
  -p 8501:8501 \
  --restart unless-stopped \
  --name rag-groq \
  rag-groq:latest

# View logs
docker logs -f rag-groq
```

---

## Cloud Deployment

### Heroku Deployment

**1. Add Procfile:**

Create `Procfile`:

```
web: streamlit run --server.port=$PORT --server.address=0.0.0.0 app/streamlit_app.py
```

**2. Add Runtime:**

Create `runtime.txt`:

```
python-3.10.13
```

**3. Deploy:**

```bash
# Login to Heroku
heroku login

# Create app
heroku create rag-groq-app

# Set environment variables
heroku config:set GROQ_API_KEY=gsk_xxxxx
heroku config:set GROQ_MODEL=llama-3.3-70b-versatile

# Deploy
git push heroku main

# Open in browser
heroku open
```

### AWS EC2 Deployment

**1. Launch EC2 instance:**

```bash
# Ubuntu 22.04 LTS recommended
# Instance type: t3.medium or larger
# Storage: 20GB
```

**2. SSH into instance:**

```bash
ssh -i your-key.pem ubuntu@your-instance.amazonaws.com
```

**3. Setup on instance:**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and tools
sudo apt install -y python3.10 python3-pip python3-venv git

# Clone repository
git clone <your-repo-url>
cd "RAG From Scratch/git"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
GROQ_API_KEY=gsk_xxxxx
GROQ_MODEL=llama-3.3-70b-versatile
EOF

# Run app
streamlit run app/streamlit_app.py --server.address=0.0.0.0 --server.port=8501
```

**4. Access application:**

```
http://your-instance-public-ip:8501
```

**5. Run in background with PM2:**

```bash
# Install PM2
npm install -g pm2

# Start app
pm2 start "streamlit run app/streamlit_app.py --server.address=0.0.0.0 --server.port=8501" --name rag-groq

# View logs
pm2 logs rag-groq

# Auto-restart on reboot
pm2 startup
pm2 save
```

### Google Cloud Run Deployment

**1. Create Dockerfile (already exists):**

```bash
# Verify Dockerfile exists
ls -la Dockerfile
```

**2. Build and push image:**

```bash
# Authenticate with Google Cloud
gcloud auth configure-docker

# Build image
docker build -t gcr.io/YOUR_PROJECT_ID/rag-groq:latest .

# Push to Google Container Registry
docker push gcr.io/YOUR_PROJECT_ID/rag-groq:latest
```

**3. Deploy to Cloud Run:**

```bash
gcloud run deploy rag-groq \
  --image gcr.io/YOUR_PROJECT_ID/rag-groq:latest \
  --platform managed \
  --region us-central1 \
  --memory 512Mi \
  --timeout 3600 \
  --set-env-vars GROQ_API_KEY=gsk_xxxxx,GROQ_MODEL=llama-3.3-70b-versatile \
  --allow-unauthenticated
```

**4. Access deployed app:**

```
https://rag-groq-xxxx.run.app
```

### Azure Container Instances

**1. Create Azure Container Registry:**

```bash
az acr create --resource-group myRG --name myRegistry --sku Basic
```

**2. Build and push:**

```bash
az acr build --registry myRegistry --image rag-groq:latest .
```

**3. Deploy:**

```bash
az container create \
  --resource-group myRG \
  --name rag-groq \
  --image myRegistry.azurecr.io/rag-groq:latest \
  --cpu 2 --memory 4 \
  --registry-login-server myRegistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --environment-variables GROQ_API_KEY=gsk_xxxxx GROQ_MODEL=llama-3.3-70b-versatile \
  --ports 8501 \
  --dns-name-label rag-groq
```

---

## Environment Configuration

### Production Settings

For production, update `.env`:

```bash
# API Configuration
GROQ_API_KEY=your_production_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Embeddings
EMBEDDING_MODEL=all-mpnet-base-v2

# LLM Settings
LLM_TEMPERATURE=0.5          # Lower = more deterministic
LLM_MAX_NEW_TOKENS=1024      # Shorter responses, faster

# Retrieval
RETRIEVAL_TOP_K=3            # Fewer chunks, faster retrieval
RETRIEVAL_SIMILARITY_THRESHOLD=0.3

# Timeout
GROQ_API_TIMEOUT=30          # 30 seconds

# Device (embeddings only - LLM uses API)
DEVICE=cpu                   # Or 'cuda' if GPU available
```

### Performance Tuning

**For faster responses:**

```bash
LLM_TEMPERATURE=0.3          # More consistent
LLM_MAX_NEW_TOKENS=256       # Shorter outputs
RETRIEVAL_TOP_K=2            # Fewer chunks
```

**For better quality:**

```bash
LLM_TEMPERATURE=0.8          # More varied
LLM_MAX_NEW_TOKENS=2048      # Longer outputs
RETRIEVAL_TOP_K=5            # More context
```

**For reliability:**

```bash
GROQ_API_TIMEOUT=60          # Longer timeout
EMBEDDING_MODEL=all-MiniLM-L6-v2  # Smaller, faster
```

### Model Selection

**Available Groq models:**

```bash
# Balanced (recommended)
GROQ_MODEL=llama-3.3-70b-versatile

# Faster, less capable
GROQ_MODEL=llama-3.1-8b-instant

# More capable, slower
GROQ_MODEL=llama-3.1-70b-versatile

# Alternative mixed expert
GROQ_MODEL=mixtral-8x7b-32768
```

---

## Monitoring & Logging

### Application Logs

**Streamlit logs:**

```bash
# View Streamlit logs
streamlit logs

# Or check container logs
docker logs rag-groq
```

**Application logging:**

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
```

### Performance Monitoring

**Check API usage:**

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.groq.com/usage
```

**Monitor response times:**

```python
import time
from src.llm_handler import LLMHandler

handler = LLMHandler()

start = time.time()
response = handler.generate("Test prompt")
elapsed = time.time() - start

print(f"Response time: {elapsed:.2f}s")
```

### Health Checks

**Create health check endpoint:**

```python
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "groq_model": GROQ_MODEL,
        "timestamp": datetime.now()
    }
```

**Test health:**

```bash
curl http://localhost:8501/health
```

---

## Troubleshooting Deployment

### Common Issues

#### 1. **Module not found errors**

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check installation
python -c "import groq; print(groq.__version__)"
```

#### 2. **API key not found**

```bash
# Verify .env file exists
ls -la .env

# Check environment variable
echo $GROQ_API_KEY

# Set if missing
export GROQ_API_KEY=gsk_xxxxx
```

#### 3. **Port already in use**

```bash
# Kill process on port 8501
lsof -ti:8501 | xargs kill -9

# Or use different port
streamlit run app/streamlit_app.py --server.port=8502
```

#### 4. **Connection timeouts**

```bash
# Increase timeout
export GROQ_API_TIMEOUT=60

# Check internet connection
curl -I https://api.groq.com
```

#### 5. **Docker build fails**

```bash
# Clean build
docker build --no-cache -t rag-groq:latest .

# Check Dockerfile
cat Dockerfile

# View build logs
docker buildx build --progress=plain -t rag-groq:latest .
```

#### 6. **Memory issues**

```bash
# Check memory usage
docker stats rag-groq

# Increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory

# Or reduce batch size in code
RETRIEVAL_TOP_K=2
```

### Debugging

**Enable verbose logging:**

```bash
# Streamlit debug mode
streamlit run app/streamlit_app.py --logger.level=debug

# Python debug mode
python -u test_groq_rag.py
```

**Check configuration:**

```python
from config.settings import *

print(f"Model: {GROQ_MODEL}")
print(f"API Key: {'***' if GROQ_API_KEY else 'Not set'}")
print(f"Temperature: {LLM_TEMPERATURE}")
print(f"Max Tokens: {LLM_MAX_NEW_TOKENS}")
```

---

## Rollback Procedure

If deployment fails:

```bash
# Docker rollback
docker run \
  -p 8501:8501 \
  --env-file .env \
  rag-groq:previous-version

# Git rollback
git revert HEAD
git push

# Redeploy previous version
```

---

## Upgrade Procedure

To upgrade to new version:

```bash
# Pull latest changes
git pull origin main

# Rebuild Docker image
docker build --no-cache -t rag-groq:latest .

# Restart container
docker-compose restart

# Or redeploy to cloud
gcloud run deploy rag-groq --image gcr.io/...
```

---

## Performance Checklist

- [ ] All dependencies installed
- [ ] `.env` file configured with API key
- [ ] Tests passing locally
- [ ] Streamlit app runs without errors
- [ ] API calls work (test with `test_groq_rag.py`)
- [ ] Response time acceptable (<10s)
- [ ] Memory usage reasonable (~400MB)
- [ ] Error handling works
- [ ] Logs are being recorded
- [ ] Docker image builds without errors
- [ ] Container starts successfully
- [ ] Health checks pass
- [ ] Load testing complete

---

## Getting Help

**Documentation:**
- [GROQ_INTEGRATION.md](GROQ_INTEGRATION.md) - Groq integration details
- [TEST_GUIDE.md](TEST_GUIDE.md) - Testing procedures
- [README.md](README.md) - Project overview

**Resources:**
- [Groq API Docs](https://console.groq.com/docs)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Docker Docs](https://docs.docker.com/)

**Support:**
- GitHub Issues
- Groq Discord Community
- Stack Overflow

---

Happy deploying! 🚀
