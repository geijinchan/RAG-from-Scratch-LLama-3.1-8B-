#!/bin/bash
# Startup script for RAG application

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}RAG Assistant Startup Script${NC}"
echo "=================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found!${NC}"
    echo -e "Creating .env from .env.example..."
    cp .env.example .env
    echo -e "${RED}Please edit .env with your configuration (especially HUGGINGFACE_TOKEN)${NC}"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker is running${NC}"

# Build and start containers
echo -e "${YELLOW}Building Docker containers...${NC}"
docker-compose down
docker-compose up --build

echo -e "${GREEN}RAG Assistant is running!${NC}"
echo "Access the app at: http://localhost:8501"
