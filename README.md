# Real Estate AI Platform (base concept - experimental code)

A comprehensive full-stack real estate AI platform for intelligent property analysis, image understanding, and AI-powered home improvement recommendations.

## Mission

To revolutionize real estate analysis by combining computer vision, natural language processing, and vector search to provide actionable insights for property owners, buyers, and real estate professionals. Our platform enables users to:

- **Analyze Properties**: Upload property images and receive detailed analysis including room type classification, condition assessment, feature detection, and lighting analysis
- **Get AI Recommendations**: Receive personalized, data-driven home improvement suggestions with cost estimates and ROI projections
- **Search & Discover**: Use natural language queries to find similar properties, rooms, or features across your portfolio
- **Intelligent Conversations**: Engage with an AI assistant that understands context from your property images and provides tailored advice

## Purpose

This platform serves as a production-ready foundation for real estate AI applications, demonstrating best practices in:

- **Microservices Architecture**: Separated concerns across frontend, backend, and middleware layers
- **Vector Search**: Leveraging pgvector for semantic similarity search
- **RAG (Retrieval-Augmented Generation)**: Combining image embeddings with LLM capabilities for context-aware responses
- **Async Processing**: Background job processing with Celery for scalable image analysis
- **Modern Stack**: FastAPI, React, PostgreSQL, Redis, MinIO, and containerized deployment

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Application Layer                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐         ┌──────────────┐                       │
│  │   Frontend   │         │   Gradio     │                       │
│  │  (React/UI)  │         │  (Testing)  │                       │
│  └──────┬───────┘         └──────┬───────┘                       │
│         │                        │                                │
│         └────────────┬───────────┘                                │
│                      │                                             │
│         ┌────────────▼────────────┐                               │
│         │   Backend API (FastAPI) │                               │
│         │  - REST Endpoints       │                               │
│         │  - WebSocket Support    │                               │
│         │  - RAG Chat Engine      │                               │
│         └────────────┬────────────┘                               │
│                      │                                             │
└──────────────────────┼─────────────────────────────────────────────┘
                       │
┌──────────────────────┼─────────────────────────────────────────────┐
│                    Middleware Layer                                 │
│                      │                                             │
│  ┌───────────────────┼───────────────────┐                       │
│  │  Celery Workers    │  Model Service     │                       │
│  │  (Async Tasks)    │  (Inference)       │                       │
│  └───────────────────┴───────────────────┘                       │
│                      │                                             │
│  ┌───────────────────┼───────────────────┐                       │
│  │  Vector Store     │  Object Storage    │                       │
│  │  (Postgres+pgvec)│  (MinIO/S3)        │                       │
│  └───────────────────┴───────────────────┘                       │
│                      │                                             │
│  ┌───────────────────┴───────────────────┐                       │
│  │      Message Broker (Redis)             │                       │
│  └─────────────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Overview

### Frontend
User-facing interfaces for property management, image upload, and AI chat assistance.

**See:** [README-frontend.md](docs/README-frontend.md)

### Backend
FastAPI application providing REST and WebSocket APIs, business logic, and ML model integration.

**See:** [README-backend.md](docs/README-backend.md)

### Middleware
Infrastructure components including databases, message queues, object storage, and model serving.

**See:** [README-middleware.md](docs/README-middleware.md)

## Quick Start

### Prerequisites

- Docker and Docker Compose
- (Optional) OpenAI API key for embeddings/LLM

### One-Command Start

**Linux/macOS:**
```bash
chmod +x start.sh && ./start.sh
```

**Windows:**
```cmd
start.bat
```

**Using Make (Linux/macOS):**
```bash
make start
```

### One-Command Test

**Linux/macOS:**
```bash
chmod +x run_tests.sh && ./run_tests.sh
```

**Windows:**
```cmd
run_tests.bat
```

**Using Make:**
```bash
make test-cov
```

### Manual Setup (Alternative)

1. **Clone the repository:**
```bash
git clone <repository-url>
cd advanced-real-estate-0.01
```

2. **Create environment file:**
```bash
cp .env.example .env
# Edit .env and add your API keys if needed
```

3. **Start all services:**
```bash
docker-compose up -d
```

4. **Initialize database:**
```bash
docker-compose exec backend python init_db.py
```

5. **Seed with mock data (optional):**
```bash
make seed
# or
docker-compose exec backend python seed_db.py
```

**See:** [SEED_DATA.md](docs/SEED_DATA.md) for detailed seeding guide.

### Access Services

- **Frontend**: http://localhost:3000
- **Gradio Interface**: http://localhost:7860
- **API Docs**: http://localhost:8000/docs
- **MinIO Console**: http://localhost:9001 (minio/minio123)
- **Database Viewer (Adminer)**: http://localhost:8081
  - System: PostgreSQL
  - Server: `db`
  - Username: `postgres`
  - Password: `postgres`
  - Database: `realestate`
- **PostgreSQL**: localhost:5432 (postgres/postgres)

## Key Features

### Core Intelligence
- 🖼️ **Image Analysis**: Multi-head model for room type, condition, features, lighting, style, and localization
- 🏠 **Property Aggregation**: Property-level metadata from per-image outputs
- 💰 **Price Prediction**: AI-powered home price estimation with confidence scores
- 🔧 **Work Recommendations**: Personalized improvement suggestions with cost estimates
- 📊 **Property Insights**: Analytics dashboard with condition scores and improvement recommendations

### Advanced Capabilities
- ⏱️ **Temporal Change Detection**: Track property condition changes over time
- 📈 **Model Drift Detection**: Monitor distribution shifts in model outputs with automated alerts
- 📉 **Model Evaluation**: Per-head metrics (precision, recall, mAP) on rolling validation sets
- 🎯 **Audit & Compliance**: Sample inputs and GradCAMs for manual audits
- ⚡ **Performance Monitoring**: Latency logging for embeddings, retrieval, and LLM calls

### Infrastructure
- 🔍 **Vector Search**: Semantic similarity search across property images and metadata
- 💬 **AI Chat Assistant**: RAG-powered conversations with context from property images
- ⚡ **Async Processing**: Background image processing with Celery workers
- 🔐 **Scalable Architecture**: Microservices-ready with containerized deployment

**See:** [ARCHITECTURE-EXPANSION.md](docs/ARCHITECTURE-EXPANSION.md) for comprehensive feature documentation.

## Technology Stack

- **Frontend**: React, Next.js (optional)
- **Backend**: FastAPI, Python 3.11+
- **Database**: PostgreSQL + pgvector
- **Cache/Broker**: Redis
- **Storage**: MinIO (S3-compatible)
- **Background Jobs**: Celery
- **ML**: Computer Vision models (ViT/CLIP), LLM integration
- **Deployment**: Docker, Docker Compose

## Development

For detailed development instructions, see component-specific READMEs:

- [Frontend Development Guide](docs/README-frontend.md#development)
- [Backend Development Guide](docs/README-backend.md#development)
- [Middleware Setup Guide](docs/README-middleware.md#setup)

## Testing

Run the test suite:

```bash
cd backend
pytest
```

With coverage:

```bash
pytest --cov=app --cov-report=html
```

See [backend/tests/README.md](backend/tests/README.md) for detailed testing documentation.

## Project Structure

```
realestate-ai-prototype/
├── backend/              # FastAPI backend application
│   ├── app/             # Application code
│   ├── tests/           # Test suite
│   └── requirements.txt # Python dependencies
├── frontend/             # Frontend applications
│   ├── react-app/       # React production UI
│   └── gradio-interface/# Gradio testing UI
├── docker-compose.yml    # Container orchestration
├── .env.example         # Environment template
└── README.md            # This file
```

## Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get started in seconds!
- **[Architecture Expansion](docs/ARCHITECTURE-EXPANSION.md)** - Comprehensive feature documentation
- [Frontend Documentation](docs/README-frontend.md)
- [Backend Documentation](docs/README-backend.md)
- [Middleware Documentation](README-middleware.md)
- **[Testing Documentation](docs/README-tests.md)** - Comprehensive testing guide
- [API Documentation](http://localhost:8000/docs) (when running)

## Quick Commands (Makefile)

### Service Management
```bash
make start       # Start all services and initialize database
make stop        # Stop all services
make restart     # Restart all services
make logs        # View logs from all services
make up          # Start services (docker-compose up -d)
make down        # Stop services (docker-compose down)
```

### Testing
```bash
make test        # Run all tests
make test-cov    # Run tests with coverage report
make test-watch  # Run tests in watch mode (requires pytest-watch)
```

### Data Management
```bash
make seed        # Seed database with mock data
make migrate     # Initialize database schema
```

### Development
```bash
make dev-backend   # Start backend in development mode (hot reload)
make dev-frontend  # Start frontend in development mode (hot reload)
```

### Build & Cleanup
```bash
make build       # Build all Docker images
make clean       # Clean up containers and volumes
```

See [QUICKSTART.md](QUICKSTART.md) for detailed usage examples.

## Contributing

1. Review the component-specific READMEs for architecture details
2. Follow the development setup in each component's documentation
3. Write tests for new features
4. Ensure all tests pass before submitting

## License

MIT
