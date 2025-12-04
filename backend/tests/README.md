# Testing Guide

This directory contains comprehensive tests for all API endpoints.

## Test Structure

- `conftest.py` - Pytest fixtures and configuration
- `test_upload.py` - Upload endpoint tests
- `test_query.py` - Query/search endpoint tests
- `test_chat.py` - Chat/RAG endpoint tests
- `test_health.py` - Health check tests
- `test_tasks.py` - Async task status tests
- `test_integration.py` - End-to-end integration tests
- `test_api.py` - Basic smoke tests

## Running Tests

### Run all tests
```bash
pytest
```

### Run with coverage
```bash
pytest --cov=app --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_upload.py
```

### Run specific test
```bash
pytest tests/test_upload.py::test_upload_image_sync
```

### Run with verbose output
```bash
pytest -v
```

## Test Fixtures

The test suite includes several fixtures:

- `client` - FastAPI test client with database override
- `db` - Fresh database session for each test
- `seeded_db` - Database with pre-seeded mock data
- `mock_image_file` - Mock image file for upload tests
- `mock_s3_upload` - Mocks S3/MinIO operations
- `mock_inference` - Mocks model inference
- `mock_embeddings` - Mocks text embedding generation

## Mock Data

Mock data is generated using functions in `app/fixtures/mock_data.py`:

- `generate_mock_embedding()` - Generate mock embedding vectors
- `generate_mock_predictions()` - Generate mock image predictions
- `generate_mock_listing()` - Generate mock listing data
- `generate_mock_image_data()` - Generate complete mock image data
- `generate_mock_conversation()` - Generate mock conversation data
- `generate_mock_message()` - Generate mock message data

## Seeding Database

To seed the database with mock data for development:

```bash
python seed_db.py
```

Or programmatically:

```python
from app.database import SessionLocal
from app.fixtures.seed_data import seed_all

db = SessionLocal()
seed_all(db, num_listings=5, images_per_listing=3, conversations_per_listing=2)
```

## Test Database

Tests use an in-memory SQLite database by default. For PostgreSQL testing, set:

```bash
export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/realestate_test"
```

Note: Vector operations (pgvector) may not work perfectly with SQLite. For full vector testing, use PostgreSQL.

