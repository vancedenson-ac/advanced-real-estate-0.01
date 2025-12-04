# Backend Documentation

FastAPI backend application providing REST and WebSocket APIs, business logic, ML model integration, and RAG-powered chat functionality.

## Overview

The backend is a stateless FastAPI application that handles:
- Image upload and processing
- Vector similarity search
- RAG-powered chat with context retrieval
- Background job orchestration
- Database operations with pgvector
- Object storage integration

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI application entrypoint
│   ├── database.py          # Database models and session management
│   ├── model_stub.py         # ML model inference interface
│   ├── workers.py            # Celery worker tasks
│   ├── routes/               # API route handlers
│   │   ├── upload.py         # Image upload endpoints
│   │   ├── query.py          # Image search endpoints
│   │   ├── chat.py           # RAG chat endpoints
│   │   ├── health.py         # Health check
│   │   └── tasks.py          # Async task status
│   ├── services/             # Business logic services
│   │   ├── crud.py           # Database CRUD operations
│   │   ├── embeddings.py     # Text/image embedding utilities
│   │   └── s3_utils.py        # S3/MinIO operations
│   ├── schemas/               # Pydantic request/response models
│   │   └── prediction.py     # API schemas
│   └── fixtures/              # Mock data generators
│       ├── mock_data.py       # Data generation functions
│       └── seed_data.py       # Database seeding
├── tests/                     # Test suite
├── requirements.txt            # Python dependencies
└── Dockerfile                 # Container definition
```

## API Endpoints

### Upload

#### `POST /api/upload/`
Synchronous image upload with immediate inference.

**Request:**
- `file`: Image file (multipart/form-data)
- `listing_id`: Optional listing ID (form data)

**Response:**
```json
{
  "status": "success",
  "image_id": 123,
  "filename": "image.jpg",
  "predictions": {
    "room_type": {"label": "kitchen", "confidence": 0.93},
    "condition_score": 0.78,
    "natural_light_score": 0.61,
    "feature_tags": ["hardwood_floors", "island"]
  },
  "embeddings": {
    "image_embedding_length": 768,
    "text_embedding_length": 1536
  }
}
```

#### `POST /api/upload/async`
Asynchronous image upload with task ID.

**Request:** Same as synchronous upload

**Response:**
```json
{
  "status": "queued",
  "task_id": "abc-123-def",
  "s3_path": "s3://realestate/image.jpg"
}
```

### Query

#### `POST /api/query/`
Search for similar images using text query.

**Request:**
```json
{
  "query": "How can I increase resale value quickly?",
  "k": 6,
  "listing_id": null
}
```

**Response:**
```json
{
  "query": "How can I increase resale value quickly?",
  "top_k": [
    {
      "id": 42,
      "filename": "kitchen.jpg",
      "s3_path": "s3://realestate/kitchen.jpg",
      "room_type": "kitchen",
      "features": ["hardwood_floors", "island"],
      "condition_score": 0.78,
      "similarity": 0.92
    }
  ]
}
```

#### `GET /api/images/{image_id}`
Get image metadata by ID.

**Response:**
```json
{
  "id": 42,
  "filename": "kitchen.jpg",
  "s3_path": "s3://realestate/kitchen.jpg",
  "room_type": "kitchen",
  "condition_score": 0.78,
  "natural_light_score": 0.61,
  "features": ["hardwood_floors", "island"]
}
```

### Chat

#### `POST /api/chat/`
RAG-enabled chat endpoint with property context.

**Request:**
```json
{
  "message": "What improvements should I make?",
  "conversation_id": null,
  "listing_id": 1,
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "conversation_id": 99,
  "reply": "Top 3 quick improvements: 1) Repaint kitchen cabinets...",
  "context_used": {
    "images_count": 6,
    "messages_count": 3
  }
}
```

#### `GET /api/conversations/{conversation_id}/messages`
Get conversation message history.

**Response:**
```json
{
  "conversation_id": 99,
  "messages": [
    {
      "id": 1,
      "role": "user",
      "text": "What improvements should I make?",
      "created_at": "2024-01-01T12:00:00"
    },
    {
      "id": 2,
      "role": "assistant",
      "text": "Top 3 quick improvements...",
      "created_at": "2024-01-01T12:00:01"
    }
  ]
}
```

### Tasks

#### `GET /api/tasks/{task_id}`
Get status of async task.

**Response:**
```json
{
  "task_id": "abc-123",
  "status": "success",
  "result": {
    "image_id": 123,
    "predictions": {...}
  },
  "error": null
}
```

### Health

#### `GET /api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "database": "healthy"
}
```

## Database Models

### Listings
- `id`: Primary key
- `address`: Property address
- `price`: Listing price
- `zip_code`: ZIP code
- `created_at`, `updated_at`: Timestamps

### Images
- `id`: Primary key
- `listing_id`: Foreign key to listings
- `filename`: Original filename
- `s3_path`: S3 object path
- `thumb_path`: Thumbnail path
- `embedding`: Image embedding vector (768-d)
- `text_embedding`: Text embedding vector (1536-d)
- `meta`: JSON metadata

### ImageLabels
- `id`: Primary key
- `image_id`: Foreign key to images
- `room_type`: Detected room type
- `room_confidence`: Confidence score
- `condition_score`: Condition assessment
- `natural_light_score`: Lighting assessment
- `features`: JSON array of feature tags

### Conversations
- `id`: Primary key
- `user_id`: User identifier
- `listing_id`: Associated listing
- `created_at`: Timestamp

### Messages
- `id`: Primary key
- `conversation_id`: Foreign key to conversations
- `role`: "user" or "assistant"
- `text`: Message content
- `embedding`: Message embedding (1536-d)
- `created_at`: Timestamp

### EmbeddingIndex
- `id`: Primary key
- `type`: "image" or "text"
- `vector`: Embedding vector (1536-d)
- `ref_id`: Reference to image or message ID

## Development

### Prerequisites

- Python 3.11+
- PostgreSQL with pgvector extension
- Redis (for Celery)
- MinIO or S3 (for object storage)

### Setup

1. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

2. **Set environment variables:**
```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/realestate"
export MINIO_ENDPOINT="minio:9000"
export CELERY_BROKER_URL="redis://localhost:6379/0"
```

3. **Initialize database:**
```bash
python init_db.py
```

4. **Seed with mock data (optional):**
```bash
python seed_db.py
```

5. **Run development server:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Celery Worker

```bash
celery -A app.workers.celery worker --loglevel=INFO
```

### Testing

#### Quick Test Commands

**Using Make:**
```bash
make test        # Run all tests
make test-cov    # Run tests with coverage report
make test-watch  # Run tests in watch mode
```

**Direct Commands:**
```bash
cd backend
pytest                    # Run all tests
pytest --cov=app --cov-report=html  # With coverage
pytest -v tests/         # Verbose output
pytest tests/test_upload.py  # Specific test file
```

**See:** [Testing Documentation](README-tests.md) for comprehensive testing guide.

**See also:** [backend/tests/README.md](backend/tests/README.md) for test suite details.

## Model Integration

### Image Model

Replace `app/model_stub.py` with your actual model:

```python
def inference(image_data: bytes) -> Tuple[Dict, np.ndarray, Optional[np.ndarray]]:
    """
    Returns:
    - predictions: Dict with room_type, condition_score, etc.
    - image_embedding: numpy array (768-d)
    - text_embedding: numpy array (1536-d) or None
    """
    # Your model implementation
    pass
```

### LLM Integration

Replace `call_llm()` in `app/routes/chat.py`:

```python
def call_llm(prompt: str) -> str:
    # OpenAI, Anthropic, or hosted LLM
    response = openai.ChatCompletion.create(...)
    return response.choices[0].message.content
```

### Embedding Service

Replace `get_text_embedding()` in `app/services/embeddings.py`:

```python
def get_text_embedding(text: str) -> np.ndarray:
    # OpenAI API or local model
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return np.array(response['data'][0]['embedding'])
```

## Vector Search

The backend uses pgvector for similarity search:

```python
# Cosine similarity search
SELECT * FROM images
ORDER BY embedding <#> query_embedding
LIMIT k;

# Similarity score: 1 - (embedding <#> query_embedding)
```

## RAG Workflow

1. **User Query**: Convert to embedding (1536-d)
2. **Image Retrieval**: Search similar images using text_embedding
3. **Message Retrieval**: Search similar past messages
4. **Context Building**: Combine images, messages, listing metadata
5. **Prompt Construction**: Build RAG prompt with context
6. **LLM Call**: Generate response with context
7. **Storage**: Save messages with embeddings

## Background Processing

### Celery Tasks

- `process_image_s3`: Process uploaded images from S3
  - Downloads image
  - Runs inference
  - Persists to database

### Task Status

Poll `/api/tasks/{task_id}` to check status:
- `pending`: Task queued
- `in_progress`: Task processing
- `success`: Task completed
- `failure`: Task failed

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request
- `404`: Not found
- `500`: Internal server error

Error responses include:
```json
{
  "detail": "Error message"
}
```

## Security Considerations

- CORS configuration for frontend origins
- Input validation with Pydantic schemas
- SQL injection prevention (SQLAlchemy ORM)
- File upload size limits
- Environment variable management
- API key security (not in code)

## Performance Optimization

- Database connection pooling
- Vector index creation for fast similarity search
- Async endpoints for long-running operations
- Celery workers for background processing
- S3 presigned URLs for direct uploads
- Embedding caching (future)

## Monitoring

- Health check endpoint for load balancer
- Structured logging (JSON format recommended)
- Metrics collection (Prometheus, StatsD)
- Error tracking (Sentry)

## Docker Deployment

```bash
docker build -t realestate-backend ./backend
docker run -p 8000:8000 --env-file .env realestate-backend
```

## Quick Commands

### Development

```bash
make dev-backend   # Start backend with hot reload
make start         # Start all services
make stop          # Stop all services
make logs          # View logs
```

### Testing

```bash
make test          # Run all tests
make test-cov      # Run tests with coverage
make test-watch    # Run tests in watch mode
```

### Data

```bash
make seed          # Seed database with mock data
make migrate       # Initialize database schema
```

## Related Documentation

- [Frontend Documentation](README-frontend.md)
- [Middleware Documentation](README-middleware.md)
- [Testing Documentation](README-tests.md)
- [Main README](README.md)

