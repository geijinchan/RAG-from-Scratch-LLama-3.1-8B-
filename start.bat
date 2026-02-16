@echo off
REM Startup script for RAG application on Windows

echo.
echo ====================================
echo RAG Assistant Startup Script
echo ====================================
echo.

REM Check if .env file exists
if not exist .env (
    echo Warning: .env file not found!
    echo Creating .env from .env.example...
    copy .env.example .env
    echo.
    echo Please edit .env with your configuration (especially HUGGINGFACE_TOKEN)
    pause
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

echo OK: Docker is running
echo.

REM Build and start containers
echo Building Docker containers...
docker-compose down
docker-compose up --build

echo.
echo RAG Assistant is running!
echo Access the app at: http://localhost:8501
pause
