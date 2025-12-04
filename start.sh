#!/bin/bash

# Quick start script for Real Estate AI Platform
# This script initializes and starts all services

set -e

echo "🚀 Starting Real Estate AI Platform..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your API keys if needed."
fi

# Start services
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Initialize database
echo "🗄️  Initializing database..."
docker-compose exec -T backend python init_db.py || echo "⚠️  Database might already be initialized"

# Check if we should seed data
read -p "🌱 Seed database with mock data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌱 Seeding database with mock data..."
    docker-compose exec -T backend python seed_db.py
fi

echo ""
echo "✅ All services are running!"
echo ""
echo "📍 Access points:"
echo "   Frontend:      http://localhost:3000"
echo "   Gradio UI:     http://localhost:7860"
echo "   API Docs:      http://localhost:8000/docs"
echo "   MinIO Console: http://localhost:9001 (minio/minio123)"
echo ""
echo "📊 View logs: docker-compose logs -f"
echo "🛑 Stop all: docker-compose down"
echo ""

