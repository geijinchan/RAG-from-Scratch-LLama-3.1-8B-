#!/bin/bash
# Docker GPU Deployment Quick Reference
# Fast commands for deploying the RAG system with GPU support

# ============================================================================
# SETUP & CONFIGURATION
# ============================================================================

# 1. Verify GPU is available on your system
echo "=== Checking GPU Availability ==="
nvidia-smi
echo ""
# Look for your GPU name and CUDA version

# 2. Install NVIDIA Container Runtime (Linux only)
echo "=== Installing NVIDIA Container Runtime ==="
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-container-runtime
sudo systemctl restart docker
echo "✓ NVIDIA Container Runtime installed"
echo ""

# 3. Verify Docker GPU support
echo "=== Verifying Docker GPU Support ==="
docker run --rm --runtime=nvidia nvidia/cuda:12.2.2-base nvidia-smi
echo "✓ Docker GPU support verified"
echo ""

# ============================================================================
# BUILD & DEPLOYMENT COMMANDS
# ============================================================================

# 4. Build with GPU support
echo "=== Building Docker Image with GPU Support ==="
docker-compose -f docker-compose.yml build

# 5. Start application with GPU
echo "=== Starting RAG App (GPU Mode) ==="
docker-compose up -d

# 6. Check if container is running
echo "=== Checking Container Status ==="
docker ps | grep rag-assistant

# 7. View logs
echo "=== Application Logs ==="
docker logs -f rag-assistant-production

# ============================================================================
# MONITORING & VERIFICATION
# ============================================================================

# 8. Monitor GPU usage in real-time
echo "=== GPU Usage (Real-time) ==="
watch -n 1 'docker exec rag-assistant-production nvidia-smi'
# Press Ctrl+C to exit

# 9. Check container resource usage
echo "=== Container Resource Usage ==="
docker stats rag-assistant-production

# 10. Verify GPU availability inside container
echo "=== GPU Status Inside Container ==="
docker exec rag-assistant-production python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU Name: {torch.cuda.get_device_name()}')"

# ============================================================================
# COMMON OPERATIONS
# ============================================================================

# View configuration
echo "=== View Final Docker Compose Configuration ==="
docker-compose config

# Rebuild from scratch
echo "=== Rebuild from Scratch ==="
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Stop application
echo "=== Stop Application ==="
docker-compose down

# Clean up unused images and containers
echo "=== Cleanup ==="
docker system prune -f  # Remove unused containers and images
docker volume prune -f  # Remove unused volumes

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

# Check NVIDIA driver version
nvidia-smi --query-gpu=driver_version --format=csv,noheader

# Check CUDA version
Docker exec rag-assistant-production nvidia-smi | grep "CUDA"

# Check GPU memory allocation
docker exec rag-assistant-production python -c "import torch; print(f'GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB')"

# Test GPU stress
docker exec rag-assistant-production python -m pip install gpu-monitor
docker exec rag-assistant-production python -c "import torch; x = torch.randn(5000, 5000, device='cuda'); y = x @ x; print('GPU Test Passed')"

# ============================================================================
# SWITCHING TO CPU (if GPU fails)
# ============================================================================

echo "=== Switch to CPU Mode ==="
export USE_GPU=false
export DEVICE=cpu
docker-compose build
docker-compose up -d

# ============================================================================
# ACCESSING THE APPLICATION
# ============================================================================

echo "=== Access Application ==="
echo "Open browser: http://localhost:8501"
echo "Upload a PDF and start querying!"

# ============================================================================
# PRODUCTION DEPLOYMENT
# ============================================================================

# Multi-GPU deployment
export CUDA_VISIBLE_DEVICES=0,1,2,3  # Use GPUs 0, 1, 2, 3
docker-compose up -d

# Scale instances (with load balancer)
docker-compose up -d --scale rag-app=3

# Deploy to Kubernetes
kubectl apply -f kubernetes/deployment.yaml
kubectl get deployments rag-app
kubectl logs -f deployment/rag-app

# ============================================================================
# PERFORMANCE TUNING
# ============================================================================

# Increase GPU memory utilization (in .env)
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:256

# Enable GPU float32 optimization
CUDA_LAUNCH_BLOCKING=0  # Default (faster)
CUDA_LAUNCH_BLOCKING=1  # For debugging

# Monitor GPU memory
docker exec rag-assistant-production nvidia-smi -l 1 --query-gpu=memory.used --format=csv

# ============================================================================
# BACKUP & MAINTENANCE
# ============================================================================

# Backup embeddings
docker exec rag-assistant-production tar -czf /app/data/embeddings-backup.tar.gz /app/data/embeddings/

# Copy backup to host
docker cp rag-assistant-production:/app/data/embeddings-backup.tar.gz ./

# Restart container cleanly
docker-compose restart

# Update without downtime (blue-green deployment)
docker-compose up -d --no-deps --build rag-app

# ============================================================================
# DETAILED COMMANDS REFERENCE
# ============================================================================

# View environment variables in container
docker-compose exec rag-assistant-production env | grep CUDA

# Check disk usage
docker exec rag-assistant-production du -sh /app/data/*

# View Streamlit logs
docker exec rag-assistant-production tail -f /app/logs/*.log

# Connect to container shell
docker exec -it rag-assistant-production /bin/bash

# Run Python command in container
docker exec rag-assistant-production python -c "YOUR_PYTHON_CODE"

# ============================================================================
# QUICK REFERENCE TABLE
# ============================================================================

cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════╗
║                    DOCKER GPU DEPLOYMENT SUMMARY                      ║
╠════════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  BUILD                                                                 ║
║  $ docker-compose build                                               ║
║                                                                        ║
║  START (GPU)                                                           ║
║  $ docker-compose up -d                                               ║
║                                                                        ║
║  START (CPU)                                                           ║
║  $ USE_GPU=false docker-compose up -d                                 ║
║                                                                        ║
║  VIEW LOGS                                                             ║
║  $ docker logs -f rag-assistant-production                            ║
║                                                                        ║
║  MONITOR GPU                                                           ║
║  $ docker stats rag-assistant-production                              ║
║  $ watch -n 1 'docker exec rag-assistant-production nvidia-smi'       ║
║                                                                        ║
║  STOP                                                                  ║
║  $ docker-compose down                                                ║
║                                                                        ║
║  CLEANUP                                                               ║
║  $ docker system prune -f                                             ║
║                                                                        ║
║  ACCESS                                                                ║
║  → http://localhost:8501                                              ║
║                                                                        ║
╚════════════════════════════════════════════════════════════════════════╝

EOF
