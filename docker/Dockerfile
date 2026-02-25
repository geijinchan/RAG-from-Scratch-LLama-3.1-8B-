# Multi-stage Dockerfile for RAG Application - GPU & CPU Compatible
# Usage:
#   GPU:  docker build --build-arg USE_GPU=true -t rag-app .
#   CPU:  docker build --build-arg USE_GPU=false -t rag-app .

ARG USE_GPU=true
ARG CUDA_VERSION=12.2.2

# ============================================================================
# GPU BASE IMAGE (CUDA 12.2)
# ============================================================================
FROM nvidia/cuda:${CUDA_VERSION}-runtime-ubuntu22.04 as gpu-builder

ENV PYTHON_VERSION=3.11 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    CUDA_HOME=/usr/local/cuda \
    PATH=/usr/local/cuda/bin:${PATH} \
    LD_LIBRARY_PATH=/usr/local/cuda/lib64:${LD_LIBRARY_PATH}

RUN apt-get update && apt-get install -y \
    python${PYTHON_VERSION} python${PYTHON_VERSION}-venv \
    python${PYTHON_VERSION}-dev python3-pip \
    git wget curl build-essential libssl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python${PYTHON_VERSION} 1 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python${PYTHON_VERSION} 1

# ============================================================================
# CPU BASE IMAGE (PYTHON 3.11 SLIM)
# ============================================================================
FROM python:3.11-slim-ubuntu as cpu-builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y \
    build-essential libssl-dev libffi-dev \
    git wget curl \
    && rm -rf /var/lib/apt/lists/*

# ============================================================================
# BUILDER STAGE - Install Dependencies
# ============================================================================
FROM ${USE_GPU:+gpu_builder}${USE_GPU:0} as final-base

WORKDIR /app

# Set DEVICE based on USE_GPU
ENV DEVICE=${USE_GPU:+cuda}${USE_GPU:0:+cpu} \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# Copy requirements
COPY requirements.txt .

# Install dependencies with CUDA support if GPU
RUN if [ "$(python -c 'import torch; print(torch.__version__)')" = "" ] || [ "$DEVICE" = "cuda" ]; then \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu122; \
    else \
    pip install --no-cache-dir -r requirements.txt; \
    fi

# Download spaCy model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY app/ ./app/
COPY src/ ./src/
COPY config/ ./config/
COPY data/ ./data/
COPY logs/ ./logs/

# Create necessary directories with proper permissions
RUN mkdir -p data/documents data/embeddings data/cache logs && \
    chmod -R 777 data/ logs/

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit app
CMD ["streamlit", "run", "app/streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--logger.level=info"]
