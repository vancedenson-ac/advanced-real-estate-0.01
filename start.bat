@echo off
REM Quick start script for Real Estate AI Platform (Windows)
REM This script initializes and starts all services

echo 🚀 Starting Real Estate AI Platform...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker first.
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo 📝 Creating .env file from .env.example...
    copy .env.example .env >nul
    echo ✅ Created .env file. Please edit it with your API keys if needed.
)

REM Start services
echo 🐳 Starting Docker containers...
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Initialize database
echo 🗄️  Initializing database...
docker-compose exec -T backend python init_db.py
if errorlevel 1 (
    echo ⚠️  Database might already be initialized
)

REM Check if we should seed data
set /p SEED_DATA="🌱 Seed database with mock data? (y/n): "
if /i "%SEED_DATA%"=="y" (
    echo 🌱 Seeding database with mock data...
    docker-compose exec -T backend python seed_db.py
)

echo.
echo ✅ All services are running!
echo.
echo 📍 Access points:
echo    Frontend:      http://localhost:3000
echo    Gradio UI:     http://localhost:7860
echo    API Docs:      http://localhost:8000/docs
echo    MinIO Console: http://localhost:9001 (minio/minio123)
echo.
echo 📊 View logs: docker-compose logs -f
echo 🛑 Stop all: docker-compose down
echo.

pause

