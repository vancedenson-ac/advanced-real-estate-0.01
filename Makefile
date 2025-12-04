.PHONY: help start stop restart logs test test-cov test-watch clean seed migrate dev-backend dev-frontend build up down

# Default target
help:
	@echo "Real Estate AI Platform - Quick Commands"
	@echo ""
	@echo "🚀 Service Management:"
	@echo "  make start       - Start all services and initialize database"
	@echo "  make stop        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make up          - Start services (docker-compose up -d)"
	@echo "  make down        - Stop services (docker-compose down)"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test        - Run all tests"
	@echo "  make test-cov    - Run tests with coverage report"
	@echo "  make test-watch  - Run tests in watch mode (requires pytest-watch)"
	@echo ""
	@echo "🌱 Data Management:"
	@echo "  make seed        - Seed database with mock data"
	@echo "  make migrate     - Initialize database schema"
	@echo ""
	@echo "💻 Development:"
	@echo "  make dev-backend - Start backend in development mode (hot reload)"
	@echo "  make dev-frontend- Start frontend in development mode (hot reload)"
	@echo ""
	@echo "🔧 Build & Cleanup:"
	@echo "  make build       - Build all Docker images"
	@echo "  make clean       - Clean up containers and volumes"
	@echo ""
	@echo "📚 Documentation:"
	@echo "  See README.md for main documentation"
	@echo "  See README-tests.md for testing documentation"
	@echo "  See QUICKSTART.md for quick start guide"

# Quick start
start:
	@echo "🚀 Starting Real Estate AI Platform..."
	@if [ ! -f .env ]; then \
		cp .env.example .env && echo "📝 Created .env file"; \
	fi
	@docker-compose up -d
	@echo "⏳ Waiting for services..."
	@sleep 10
	@docker-compose exec -T backend python init_db.py || echo "⚠️  Database might already be initialized"
	@echo ""
	@echo "✅ Services started!"
	@echo "📍 Frontend: http://localhost:3000"
	@echo "📍 API Docs: http://localhost:8000/docs"
	@echo "📍 Gradio: http://localhost:7860"

# Stop services
stop:
	@echo "🛑 Stopping services..."
	@docker-compose down

# Restart services
restart: stop start

# View logs
logs:
	@docker-compose logs -f

# Run tests
test:
	@echo "🧪 Running tests..."
	@cd backend && pytest -v tests/

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	@cd backend && pytest --cov=app --cov-report=html --cov-report=term --verbose tests/
	@echo ""
	@echo "📊 Coverage report: backend/htmlcov/index.html"

# Run tests in watch mode
test-watch:
	@echo "🧪 Running tests in watch mode..."
	@cd backend && pytest-watch tests/

# Seed database
seed:
	@echo "🌱 Seeding database with mock data..."
	@docker-compose exec -T backend python seed_db.py || \
		(cd backend && python seed_db.py)

# Initialize database
migrate:
	@echo "🗄️  Initializing database..."
	@docker-compose exec -T backend python init_db.py

# Development - Backend
dev-backend:
	@echo "💻 Starting backend in development mode..."
	@cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Development - Frontend
dev-frontend:
	@echo "💻 Starting frontend in development mode..."
	@cd frontend/react-app && npm start

# Build images
build:
	@echo "🔨 Building Docker images..."
	@docker-compose build

# Clean up
clean:
	@echo "🧹 Cleaning up..."
	@docker-compose down -v
	@echo "✅ Cleaned up containers and volumes"

# Docker compose shortcuts
up:
	@docker-compose up -d

down:
	@docker-compose down

# Batch test and start
all: start test-cov
	@echo ""
	@echo "✅ Started services and ran all tests!"

