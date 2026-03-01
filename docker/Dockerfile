# ============================================================
# GPU IMAGE — MAX COMPATIBILITY BUILD
# ============================================================
FROM nvidia/cuda:12.1.1-runtime-ubuntu22.04 AS gpu

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# ---------- system ----------
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-venv python3-pip \
    git curl build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1

WORKDIR /app

# ---------- python deps ----------
COPY requirements.txt .

RUN python3 -m pip install --upgrade pip setuptools wheel

# install base deps (NO torch inside requirements)
RUN python3 -m pip install --no-cache-dir -r requirements.txt

# 🔥 GPU torch — VERIFIED MATCH
RUN python3 -m pip install --no-cache-dir \
    torch==2.5.1+cu121 \
    torchvision==0.20.1+cu121 \
    torchaudio==2.5.1+cu121 \
    --index-url https://download.pytorch.org/whl/cu121

# ---------- spacy ----------
RUN python3 -m spacy download en_core_web_sm

# ---------- copy project ----------
COPY app/ ./app/
COPY src/ ./src/
COPY config/ ./config/
COPY data/ ./data/
COPY logs/ ./logs/

RUN mkdir -p data/documents data/embeddings data/cache logs

EXPOSE 8501

CMD ["streamlit", "run", "app/streamlit_app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]