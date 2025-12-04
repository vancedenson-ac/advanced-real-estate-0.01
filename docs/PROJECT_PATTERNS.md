# Project Patterns & Architecture Reference Guide

This document describes the comprehensive patterns, structure, and best practices used in this AI application stack. Use this as a reference when creating new projects or working with AI assistants to maintain consistency.

## Table of Contents

1. [Project Structure](#project-structure)
2. [Technology Stack](#technology-stack)
3. [Docker & Containerization](#docker--containerization)
4. [Database Patterns](#database-patterns)
5. [Backend API Patterns](#backend-api-patterns)
6. [Frontend Patterns](#frontend-patterns)
7. [Background Jobs](#background-jobs)
8. [Documentation Patterns](#documentation-patterns)
9. [Build & Deployment](#build--deployment)
10. [Code Organization](#code-organization)
11. [Testing Patterns](#testing-patterns)
12. [Development Workflow](#development-workflow)

---

## Project Structure

### Root Directory Layout

```
project-root/
├── backend/                    # FastAPI backend application
│   ├── app/                    # Application code
│   │   ├── __init__.py
│   │   ├── main.py             # FastAPI app entrypoint
│   │   ├── database.py         # SQLAlchemy models & session
│   │   ├── init_db.py          # Database initialization script
│   │   ├── workers.py           # Celery configuration
│   │   ├── model_stub.py       # ML model interface (stub)
│   │   ├── routes/             # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── health.py       # Health check endpoint
│   │   │   ├── upload.py       # Upload endpoints
│   │   │   ├── query.py        # Query/search endpoints
│   │   │   ├── chat.py         # Chat/RAG endpoints
│   │   │   └── tasks.py        # Task status endpoints
│   │   ├── services/           # Business logic services
│   │   │   ├── __init__.py
│   │   │   ├── crud.py         # Database CRUD operations
│   │   │   ├── embeddings.py   # Embedding generation
│   │   │   ├── s3_utils.py     # Object storage utilities
│   │   │   └── [other services]
│   │   ├── schemas/            # Pydantic models
│   │   │   ├── __init__.py
│   │   │   └── prediction.py
│   │   ├── fixtures/           # Mock data generators
│   │   │   ├── __init__.py
│   │   │   ├── mock_data.py
│   │   │   └── seed_data.py
│   │   └── workers/            # Celery workers (optional)
│   │       ├── __init__.py
│   │       └── celery.py       # Celery task definitions
│   ├── tests/                 # Test suite
│   │   ├── __init__.py
│   │   ├── conftest.py         # Pytest configuration
│   │   ├── test_api.py
│   │   ├── test_integration.py
│   │   └── README.md
│   ├── Dockerfile
│   ├── requirements.txt        # Production dependencies
│   ├── requirements-test.txt  # Test dependencies
│   ├── pytest.ini             # Pytest configuration
│   └── seed_db.py             # Database seeding script
│
├── frontend/
│   ├── react-app/              # React production frontend
│   │   ├── src/
│   │   │   ├── components/    # React components
│   │   │   ├── pages/         # Page components
│   │   │   ├── api.js         # API client
│   │   │   ├── App.js
│   │   │   └── index.js
│   │   ├── public/
│   │   ├── Dockerfile
│   │   ├── nginx.conf
│   │   ├── package.json
│   │   └── tailwind.config.js
│   │
│   └── gradio-interface/       # Gradio testing interface
│       ├── app.py              # Gradio app
│       ├── Dockerfile
│       └── requirements.txt
│
├── data/                       # Local data (gitignored)
│   ├── postgres/              # PostgreSQL data
│   ├── minio/                 # MinIO object storage
│   └── uploads/               # Temporary uploads
│
├── docker-compose.yml          # Service orchestration
├── Makefile                    # Build automation
├── start.sh                    # Linux/macOS startup script
├── start.bat                   # Windows startup script
├── run_tests.sh                # Linux/macOS test runner
├── run_tests.bat               # Windows test runner
├── .gitignore
├── .env.example                # Environment template
│
├── README.md                   # Main documentation
├── README-backend.md           # Backend documentation
├── README-frontend.md          # Frontend documentation
├── README-middleware.md        # Middleware documentation
├── README-tests.md             # Testing documentation
├── QUICKSTART.md               # Quick start guide
├── ARCHITECTURE.md             # Architecture documentation
├── SEED_DATA.md                # Seed data guide
└── TROUBLESHOOTING.md          # Troubleshooting guide
```

### Key Principles

1. **Separation of Concerns**: Clear boundaries between frontend, backend, and infrastructure
2. **Dual Frontend Pattern**: Gradio for rapid testing/development, React for production UI
3. **Containerization**: Every service runs in Docker containers
4. **Comprehensive Documentation**: Multiple focused README files
5. **Automation**: Makefile and startup scripts for common tasks

---

## Technology Stack

### Core Technologies

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend API** | FastAPI 0.104+ | REST API framework |
| **Database** | PostgreSQL 14+ | Primary database |
| **Vector Search** | pgvector extension | Semantic similarity search |
| **ORM** | SQLAlchemy 2.0+ | Database ORM |
| **Object Storage** | MinIO (S3-compatible) | Image/file storage |
| **Message Broker** | Redis 7+ | Celery task queue |
| **Background Jobs** | Celery 5.3+ | Async task processing |
| **Production Frontend** | React 18+ | Production user interface |
| **Testing Frontend** | Gradio 4.7+ | Rapid API testing interface |
| **Deployment** | Docker + Docker Compose | Container orchestration |

### Python Stack

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pgvector==0.2.4
boto3==1.29.7
celery==5.3.4
redis==5.0.1
pydantic==2.5.0
python-multipart==0.0.6
numpy==1.26.2
Pillow==10.1.0
python-dotenv==1.0.0
```

### Frontend Stack

**React Production:**
- React 18+
- Tailwind CSS
- Axios/Fetch for API calls
- React Router (if needed)

**Gradio Testing:**
- Gradio 4.7+
- Requests library for API calls

---

## Docker & Containerization

### Docker Compose Structure

```yaml
services:
  backend:
    build: ./backend
    container_name: project-backend
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
      - minio
    volumes:
      - ./data/uploads:/data/uploads
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/dbname
      - MINIO_ENDPOINT=minio:9000
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0

  worker:
    build: ./backend
    command: celery -A app.workers.celery worker --loglevel=INFO
    container_name: project-worker
    depends_on:
      - backend
      - redis
      - db
      - minio
    volumes:
      - ./data/uploads:/data/uploads
    environment:
      # Same as backend

  frontend:
    build: ./frontend/react-app
    container_name: project-frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  gradio:
    build: ./frontend/gradio-interface
    container_name: project-gradio
    ports:
      - "7860:7860"
    depends_on:
      - backend
    environment:
      - API_BASE_URL=http://backend:8000/api

  db:
    image: ankane/pgvector:latest
    container_name: project-db
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: dbname
    ports:
      - "5432:5432"
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: project-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  minio:
    image: minio/minio:latest
    container_name: project-minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minio
      MINIO_ROOT_PASSWORD: minio123
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - ./data/minio:/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
```

### Backend Dockerfile Pattern

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Expose port
EXPOSE 8000

# Default command (can be overridden in docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile Pattern (React)

```dockerfile
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Gradio Dockerfile Pattern

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 7860

CMD ["python", "app.py"]
```

---

## Database Patterns

### PostgreSQL + pgvector Setup

**Database Initialization (`app/database.py`):**

```python
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
import os
from datetime import datetime

Base = declarative_base()

# Example model with vector embedding
class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    s3_path = Column(String, nullable=False)
    embedding = Column(Vector(768), nullable=True)  # Image embedding
    text_embedding = Column(Vector(1536), nullable=True)  # Text embedding
    meta = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/dbname"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Dependency for FastAPI database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables and pgvector extension."""
    from sqlalchemy import text
    
    try:
        # Create pgvector extension
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
```

### Database Initialization Script (`app/init_db.py`)

```python
"""Initialize database tables and pgvector extension."""
from app.database import init_db

if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
```

### Vector Search Pattern

```python
from sqlalchemy import text
import numpy as np

def search_by_embedding(query_embedding: np.ndarray, k: int = 10, db: Session = Depends(get_db)):
    """Search images using vector similarity."""
    # Convert embedding to string format for pgvector
    embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"
    
    results = db.execute(
        text(f"""
            SELECT id, filename, s3_path,
                   embedding <=> :embedding::vector as distance
            FROM images
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> :embedding::vector
            LIMIT :k
        """),
        {"embedding": embedding_str, "k": k}
    ).fetchall()
    
    return results
```

---

## Backend API Patterns

### FastAPI Application Structure (`app/main.py`)

```python
"""FastAPI main entrypoint."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import upload, query, chat, health, tasks
from .database import init_db

app = FastAPI(
    title="Project Name API",
    description="API description",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(tasks.router, prefix="/api", tags=["tasks"])

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Project Name API",
        "version": "0.1.0",
        "docs": "/docs"
    }
```

### Route Handler Pattern (`app/routes/upload.py`)

```python
"""Upload endpoints."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from ..database import get_db, Image
from ..services.crud import create_image
from ..workers.celery import process_image_task

router = APIRouter()

class UploadResponse(BaseModel):
    status: str
    image_id: int
    task_id: Optional[str] = None

@router.post("/upload/", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    listing_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Upload image synchronously."""
    # Validate file
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read file
    contents = await file.read()
    
    # Create image record
    image = create_image(
        db=db,
        image_data=contents,
        filename=file.filename,
        listing_id=listing_id
    )
    
    return UploadResponse(
        status="success",
        image_id=image.id
    )

@router.post("/upload/async", response_model=UploadResponse)
async def upload_image_async(
    file: UploadFile = File(...),
    listing_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Upload image asynchronously."""
    # Save to S3 first
    s3_path = upload_to_s3(file)
    
    # Queue processing task
    task = process_image_task.delay(
        s3_path=s3_path,
        filename=file.filename,
        listing_id=listing_id
    )
    
    return UploadResponse(
        status="queued",
        image_id=0,
        task_id=task.id
    )
```

### Service Pattern (`app/services/crud.py`)

```python
"""CRUD operations for database."""
from sqlalchemy.orm import Session
from typing import Optional
from ..database import Image
from ..services.s3_utils import upload_fileobj
from ..services.embeddings import generate_image_embedding
from io import BytesIO

def create_image(
    db: Session,
    image_data: bytes,
    filename: str,
    listing_id: Optional[int] = None,
    meta: Optional[dict] = None
) -> Image:
    """Create an image record and upload to S3."""
    # Generate embeddings
    image_embedding = generate_image_embedding(image_data)
    text_embedding = generate_text_embedding(f"image {filename}")
    
    # Upload to S3
    image_file = BytesIO(image_data)
    s3_key = f"images/{listing_id or 'unassigned'}/{filename}"
    s3_path = upload_fileobj(image_file, s3_key, content_type="image/jpeg")
    
    # Create database record
    image = Image(
        listing_id=listing_id,
        filename=filename,
        s3_path=s3_path,
        embedding=image_embedding.tolist(),
        text_embedding=text_embedding.tolist(),
        meta=meta or {}
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    
    return image
```

---

## Frontend Patterns

### Gradio Testing Interface (`frontend/gradio-interface/app.py`)

```python
"""Gradio UI for API testing."""
import gradio as gr
import requests
import json
from typing import Optional

API_BASE_URL = "http://backend:8000/api"

def upload_image(file, listing_id: Optional[int] = None, async_mode: bool = False):
    """Upload image and get predictions."""
    if file is None:
        return "Please upload an image file"
    
    try:
        with open(file.name, 'rb') as f:
            files = {'file': f}
            data = {}
            if listing_id:
                data['listing_id'] = listing_id
            
            endpoint = f"{API_BASE_URL}/upload/async" if async_mode else f"{API_BASE_URL}/upload/"
            response = requests.post(endpoint, files=files, data=data)
            response.raise_for_status()
            
            result = response.json()
            return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"

def query_images(query_text: str, k: int = 6):
    """Query similar images."""
    if not query_text:
        return "Please enter a query"
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/query/",
            json={
                "query": query_text,
                "k": k
            }
        )
        response.raise_for_status()
        
        result = response.json()
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Error: {str(e)}"

# Create Gradio interface
with gr.Blocks(title="API Testing Interface") as demo:
    gr.Markdown("# API Testing Interface")
    
    with gr.Tabs():
        with gr.Tab("Upload Image"):
            with gr.Row():
                with gr.Column():
                    upload_file = gr.File(label="Upload Image", type="filepath")
                    upload_listing_id = gr.Number(label="Listing ID (optional)", value=None)
                    upload_async = gr.Checkbox(label="Async Mode", value=False)
                    upload_btn = gr.Button("Upload", variant="primary")
                
                with gr.Column():
                    upload_output = gr.Textbox(label="Result", lines=20)
            
            upload_btn.click(
                fn=upload_image,
                inputs=[upload_file, upload_listing_id, upload_async],
                outputs=upload_output
            )
        
        with gr.Tab("Query Images"):
            with gr.Row():
                with gr.Column():
                    query_text = gr.Textbox(label="Query Text", placeholder="Enter query...")
                    query_k = gr.Slider(label="Top K", minimum=1, maximum=20, value=6, step=1)
                    query_btn = gr.Button("Query", variant="primary")
                
                with gr.Column():
                    query_output = gr.Textbox(label="Results", lines=20)
            
            query_btn.click(
                fn=query_images,
                inputs=[query_text, query_k],
                outputs=query_output
            )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
```

### React Production Frontend Pattern (`frontend/react-app/src/api.js`)

```javascript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

export const uploadImage = async (file, listingId = null) => {
  const formData = new FormData();
  formData.append('file', file);
  if (listingId) {
    formData.append('listing_id', listingId);
  }

  const response = await fetch(`${API_BASE_URL}/upload/`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Upload failed');
  }

  return response.json();
};

export const queryImages = async (query, k = 6) => {
  const response = await fetch(`${API_BASE_URL}/query/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, k }),
  });

  if (!response.ok) {
    throw new Error('Query failed');
  }

  return response.json();
};
```

---

## Background Jobs

### Celery Configuration (`app/workers.py`)

```python
"""Celery worker configuration."""
from celery import Celery
import os

CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery = Celery(
    "project_workers",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
```

### Celery Task Pattern (`app/workers/celery.py`)

```python
"""Celery tasks."""
from ..workers import celery
from ..database import SessionLocal, Image
from ..services.labeling import ImageLabeler
from ..services.s3_utils import download_file
from ..services.crud import create_image_label

@celery.task(name="process_image_s3")
def process_image_s3(s3_path: str, filename: str, listing_id: int = None):
    """
    Process image from S3: download, run inference, persist to database.
    """
    db = SessionLocal()
    try:
        # Download from S3
        image_data = download_file(s3_path)
        
        # Run model inference
        labeler = ImageLabeler()
        predictions = labeler.label_image(image_data)
        
        # Get image record
        image = db.query(Image).filter(Image.s3_path == s3_path).first()
        if not image:
            return {"status": "error", "error": "Image not found"}
        
        # Create label record
        create_image_label(
            db=db,
            image_id=image.id,
            predictions=predictions,
            model_version="v1.0"
        )
        
        return {
            "status": "success",
            "image_id": image.id,
            "predictions": predictions
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
    finally:
        db.close()
```

---

## Documentation Patterns

### Main README Structure (`README.md`)

```markdown
# Project Name

Brief description of the project.

## Mission

What the project aims to achieve.

## Purpose

What the project is for and who it serves.

## High-Level Architecture

[Architecture diagram or description]

## Component Overview

### Frontend
Description and link to frontend README.

### Backend
Description and link to backend README.

### Middleware
Description and link to middleware README.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- (Optional) API keys

### One-Command Start

**Linux/macOS:**
```bash
chmod +x start.sh && ./start.sh
```

**Windows:**
```cmd
start.bat
```

**Using Make:**
```bash
make start
```

## Key Features

- Feature 1
- Feature 2
- Feature 3

## Technology Stack

- **Frontend**: React, Gradio
- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL + pgvector
- **Cache/Broker**: Redis
- **Storage**: MinIO (S3-compatible)
- **Background Jobs**: Celery
- **Deployment**: Docker, Docker Compose

## Documentation

- **[Quick Start Guide](QUICKSTART.md)**
- **[Architecture Guide](ARCHITECTURE.md)**
- [Backend Documentation](README-backend.md)
- [Frontend Documentation](README-frontend.md)
- [Testing Documentation](README-tests.md)

## Quick Commands (Makefile)

[Document common Makefile commands]

## License

MIT
```

### Specialized README Files

1. **README-backend.md**: API documentation, database schema, services
2. **README-frontend.md**: Frontend components, usage, customization
3. **README-middleware.md**: Infrastructure setup, configuration
4. **README-tests.md**: Testing patterns, running tests, coverage
5. **QUICKSTART.md**: Step-by-step getting started guide
6. **ARCHITECTURE.md**: Detailed architecture documentation
7. **SEED_DATA.md**: How to seed database with test data
8. **TROUBLESHOOTING.md**: Common issues and solutions

---

## Build & Deployment

### Makefile Pattern (`Makefile`)

```makefile
.PHONY: help start stop restart logs test test-cov clean seed migrate build up down

# Default target
help:
	@echo "Project Name - Quick Commands"
	@echo ""
	@echo "🚀 Service Management:"
	@echo "  make start       - Start all services and initialize database"
	@echo "  make stop        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - View logs from all services"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test        - Run all tests"
	@echo "  make test-cov    - Run tests with coverage report"
	@echo ""
	@echo "🌱 Data Management:"
	@echo "  make seed        - Seed database with mock data"
	@echo "  make migrate     - Initialize database schema"
	@echo ""
	@echo "🔧 Build & Cleanup:"
	@echo "  make build       - Build all Docker images"
	@echo "  make clean       - Clean up containers and volumes"

# Quick start
start:
	@echo "🚀 Starting Project..."
	@if [ ! -f .env ]; then \
		cp .env.example .env && echo "📝 Created .env file"; \
	fi
	@docker-compose up -d
	@echo "⏳ Waiting for services..."
	@sleep 10
	@docker-compose exec -T backend python app/init_db.py || echo "⚠️  Database might already be initialized"
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

# Seed database
seed:
	@echo "🌱 Seeding database with mock data..."
	@docker-compose exec -T backend python seed_db.py

# Initialize database
migrate:
	@echo "🗄️  Initializing database..."
	@docker-compose exec -T backend python app/init_db.py

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
```

### Startup Script Pattern (`start.sh`)

```bash
#!/bin/bash

# Project Name - Start Script

echo "🚀 Starting Project..."
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it and try again."
    exit 1
fi

# Start services
echo "📦 Starting Docker containers..."
docker-compose up -d

# Wait for services to be ready
echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Initialize database
echo ""
echo "🗄️  Initializing database..."
docker-compose exec -T backend python app/init_db.py || echo "⚠️  Database might already be initialized"

echo ""
echo "✅ Services started!"
echo ""
echo "📍 Access points:"
echo "   - Frontend: http://localhost:3000"
echo "   - API Documentation: http://localhost:8000/docs"
echo "   - Gradio Interface: http://localhost:7860"
echo ""
echo "💡 View logs: docker-compose logs -f"
echo "💡 Stop services: docker-compose down"
```

### Windows Startup Script Pattern (`start.bat`)

```batch
@echo off
REM Project Name - Start Script (Windows)

echo 🚀 Starting Project...
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ docker-compose is not installed. Please install it and try again.
    exit /b 1
)

REM Start services
echo 📦 Starting Docker containers...
docker-compose up -d

REM Wait for services to be ready
echo.
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Initialize database
echo.
echo 🗄️  Initializing database...
docker-compose exec -T backend python app/init_db.py
if %errorlevel% neq 0 (
    echo ⚠️  Database might already be initialized
)

echo.
echo ✅ Services started!
echo.
echo 📍 Access points:
echo    - Frontend: http://localhost:3000
echo    - API Documentation: http://localhost:8000/docs
echo    - Gradio Interface: http://localhost:7860
echo.
echo 💡 View logs: docker-compose logs -f
echo 💡 Stop services: docker-compose down
```

---

## Code Organization

### Import Organization

```python
# Standard library imports
import os
from datetime import datetime
from typing import Optional, List

# Third-party imports
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Local application imports
from .database import get_db, Image
from .services.crud import create_image
from .workers.celery import process_image_task
```

### Service Layer Pattern

- **Services** (`app/services/`): Business logic, reusable functions
- **Routes** (`app/routes/`): API endpoints, request/response handling
- **Database** (`app/database.py`): Models and session management
- **Workers** (`app/workers/`): Background task definitions
- **Schemas** (`app/schemas/`): Pydantic models for validation

### Error Handling Pattern

```python
from fastapi import HTTPException

@router.post("/endpoint")
async def endpoint(data: RequestModel, db: Session = Depends(get_db)):
    try:
        # Business logic
        result = process_data(data)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
```

---

## Testing Patterns

### Test Structure (`backend/tests/`)

```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures
├── test_api.py          # API endpoint tests
├── test_integration.py  # Integration tests
├── test_services.py     # Service layer tests
└── README.md            # Testing documentation
```

### Pytest Configuration (`pytest.ini`)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow tests
```

### Test Fixtures Pattern (`tests/conftest.py`)

```python
"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Test database
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/test_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    """Create a test database session."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session):
    """Create a test client."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

### Test Example (`tests/test_api.py`)

```python
"""API endpoint tests."""
import pytest
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    """Test health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_upload_image(client: TestClient):
    """Test image upload endpoint."""
    with open("tests/fixtures/test_image.jpg", "rb") as f:
        response = client.post(
            "/api/upload/",
            files={"file": ("test.jpg", f, "image/jpeg")}
        )
    assert response.status_code == 200
    assert "image_id" in response.json()
```

---

## Development Workflow

### Environment Variables

Create `.env.example`:

```bash
DATABASE_URL=postgresql://postgres:postgres@db:5432/dbname
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minio
MINIO_SECRET_KEY=minio123
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
OPENAI_API_KEY=your_key_here
```

### Development Commands

```bash
# Start development
make start

# View logs
make logs
# or
docker-compose logs -f backend

# Run tests
make test

# Run tests with coverage
make test-cov

# Rebuild after code changes
docker-compose up -d --build backend

# Access database
docker-compose exec db psql -U postgres -d dbname

# Access backend shell
docker-compose exec backend bash

# Stop everything
make stop

# Clean up everything
make clean
```

### Git Ignore Pattern (`.gitignore`)

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/

# IDEs
.vscode/
.idea/
*.swp
*.swo

# Environment variables
.env
.env.local

# Data directories
data/
*.db
*.sqlite

# Logs
*.log
logs/

# Testing
.pytest_cache/
.coverage
htmlcov/

# OS
.DS_Store
Thumbs.db
```

---

## Production Readiness Patterns

### Database Migrations (Alembic)

**Critical for Production**: Use Alembic for schema versioning instead of `create_all()`.

**Setup:**
```bash
pip install alembic
alembic init alembic
```

**Configuration (`alembic/env.py`):**
```python
from app.database import Base
target_metadata = Base.metadata
```

**Migration Pattern:**
```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

**In Docker Compose:**
```yaml
backend:
  command: sh -c "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"
```

### Structured Logging Pattern

**Production Logging (`app/config/logging.py`):**
```python
import logging
import json
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

def setup_logging(level=logging.INFO):
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)
    
    # Suppress noisy loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
```

**Usage in Code:**
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Processing image", extra={"image_id": image_id, "user_id": user_id})
logger.error("Upload failed", exc_info=True)
```

### Database Connection Pooling

**Production Database Configuration:**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,              # Number of connections to maintain
    max_overflow=10,           # Max connections beyond pool_size
    pool_pre_ping=True,        # Verify connections before using
    pool_recycle=3600,         # Recycle connections after 1 hour
    echo=False                 # Set to True for SQL debugging
)
```

### Global Exception Handler

**FastAPI Exception Handling (`app/main.py`):**
```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}", extra={
        "path": request.url.path,
        "method": request.method
    })
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}", extra={
        "path": request.url.path,
        "method": request.method
    })
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True, extra={
        "path": request.url.path,
        "method": request.method
    })
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

### Health Check Pattern (Enhanced)

**Production Health Check (`app/routes/health.py`):**
```python
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from ..database import get_db, engine
import redis
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy"}

@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check - verifies database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return {"status": "not ready", "database": "disconnected", "error": str(e)}, 503

@router.get("/health/live")
async def liveness_check():
    """Liveness check - service is running."""
    return {"status": "alive"}
```

### API Versioning Pattern

**Versioned Routes (`app/main.py`):**
```python
from .routes import v1

app.include_router(v1.router, prefix="/api/v1", tags=["v1"])
# Future: app.include_router(v2.router, prefix="/api/v2", tags=["v2"])
```

**Versioned Router (`app/routes/v1/__init__.py`):**
```python
from fastapi import APIRouter
from .upload import router as upload_router
from .query import router as query_router

router = APIRouter()
router.include_router(upload_router, prefix="/upload", tags=["upload"])
router.include_router(query_router, prefix="/query", tags=["query"])
```

### Graceful Shutdown Pattern

**Docker Compose with Graceful Shutdown:**
```yaml
backend:
  stop_grace_period: 30s
  command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --graceful-timeout 30
```

**Application Shutdown Handler:**
```python
import signal
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown
    logger.info("Shutting down gracefully...")
    # Close database connections
    engine.dispose()
    # Wait for ongoing requests
    await asyncio.sleep(1)

app = FastAPI(lifespan=lifespan)
```

### Rate Limiting Pattern (Future)

**Using `slowapi` (Flask-style for FastAPI):**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@router.post("/upload/")
@limiter.limit("10/minute")
async def upload_image(request: Request, ...):
    ...
```

### Secrets Management Pattern

**Production Secrets (Environment-based):**
```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    minio_access_key: str
    minio_secret_key: str
    openai_api_key: str = ""
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
```

**Docker Secrets (Production):**
```yaml
backend:
  secrets:
    - database_password
    - api_keys
  environment:
    DATABASE_URL_FILE: /run/secrets/database_password
```

### CI/CD Pattern (GitHub Actions Example)

**`.github/workflows/ci.yml`:**
```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: ankane/pgvector:latest
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pip install -r backend/requirements-test.txt
      - run: cd backend && pytest tests/
      
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: docker-compose build
      - run: docker-compose up -d
      - run: docker-compose exec -T backend python app/init_db.py
      - run: docker-compose exec -T backend pytest tests/
```

---

## Key Principles Summary

1. **Separation of Concerns**: Clear boundaries between layers
2. **Dual Frontend**: Gradio for testing, React for production
3. **Containerization**: Everything runs in Docker
4. **Comprehensive Documentation**: Multiple focused README files
5. **Automation**: Makefile and scripts for common tasks
6. **Vector Search**: pgvector for semantic similarity
7. **Async Processing**: Celery for background jobs
8. **Type Safety**: Pydantic models for validation
9. **Testing**: Comprehensive test suite with fixtures
10. **Scalability**: Horizontal scaling ready architecture
11. **Production Ready**: Migrations, logging, connection pooling, error handling

---

## Quick Reference Checklist

When creating a new project with these patterns:

- [ ] Set up Docker Compose with all services
- [ ] Create backend FastAPI application structure
- [ ] Set up PostgreSQL + pgvector database
- [ ] Create SQLAlchemy models with vector columns
- [ ] Implement database initialization script
- [ ] Create API route handlers
- [ ] Set up service layer for business logic
- [ ] Configure Celery workers
- [ ] Create Gradio testing interface
- [ ] Set up React production frontend
- [ ] Create Makefile with common commands
- [ ] Create startup scripts (start.sh, start.bat)
- [ ] Write comprehensive README files
- [ ] Set up testing infrastructure
- [ ] Create .gitignore and .env.example
- [ ] Document architecture patterns
- [ ] Set up Alembic for database migrations
- [ ] Configure structured logging
- [ ] Set up database connection pooling
- [ ] Implement global exception handlers
- [ ] Configure API versioning
- [ ] Set up graceful shutdown
- [ ] Configure CI/CD pipeline (optional)
- [ ] Set up secrets management

---

## Production Deployment Checklist

Before deploying to production:

- [ ] **Database**: Set up Alembic migrations (not `create_all()`)
- [ ] **Security**: Implement authentication/authorization
- [ ] **Security**: Configure proper CORS origins (not `["*"]`)
- [ ] **Security**: Enable HTTPS/TLS
- [ ] **Security**: Set up rate limiting
- [ ] **Logging**: Configure structured JSON logging
- [ ] **Monitoring**: Set up error tracking (Sentry, etc.)
- [ ] **Monitoring**: Set up metrics collection (Prometheus)
- [ ] **Database**: Configure connection pooling
- [ ] **Database**: Set up automated backups
- [ ] **Secrets**: Use secrets management (not `.env` in production)
- [ ] **Performance**: Optimize database indexes
- [ ] **Performance**: Configure caching (Redis)
- [ ] **Reliability**: Set up health checks (liveness/readiness)
- [ ] **Reliability**: Configure graceful shutdown
- [ ] **CI/CD**: Set up automated testing and deployment

---

This pattern reference guide should be sufficient to recreate the entire project structure and patterns. Use it as a blueprint when working with AI assistants to maintain consistency across projects.

**Note**: The patterns shown are production-ready when the production deployment checklist items are implemented. The base structure is solid and follows best practices, but production deployment requires additional security, monitoring, and reliability measures.

