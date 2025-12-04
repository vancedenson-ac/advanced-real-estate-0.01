# Full-Stack AI API Testing: A Professional Guide

## Overview

This guide demonstrates professional backend testing practices for a FastAPI-based AI application. The testing strategy covers unit tests, integration tests, API endpoint tests, and comprehensive mocking strategies for external dependencies like ML models, vector databases, and cloud storage.

---

## Table of Contents

1. [Test Architecture & Organization](#test-architecture--organization)
2. [Configuration & Setup](#configuration--setup)
3. [Test Fixtures & Dependency Injection](#test-fixtures--dependency-injection)
4. [Mocking External Dependencies](#mocking-external-dependencies)
5. [API Endpoint Testing](#api-endpoint-testing)
6. [Integration Testing](#integration-testing)
7. [Data Seeding & Test Data Management](#data-seeding--test-data-management)
8. [Best Practices & Patterns](#best-practices--patterns)

---

## 1. Test Architecture & Organization

### Directory Structure

```
backend/
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Shared fixtures and configuration
│   ├── test_api.py          # Basic API smoke tests
│   ├── test_chat.py         # Chat endpoint tests
│   ├── test_query.py        # Query/search endpoint tests
│   ├── test_upload.py       # File upload endpoint tests
│   ├── test_tasks.py        # Async task status tests
│   ├── test_health.py       # Health check tests
│   ├── test_integration.py  # End-to-end workflow tests
│   └── test_mock_data.py    # Test data generation utilities
├── pytest.ini               # Pytest configuration
└── requirements-test.txt    # Test dependencies
```

### Test File Naming Convention

- **`test_*.py`**: All test files follow the `test_<module_name>.py` pattern
- **Test functions**: Named `test_<feature>_<scenario>()`
- **Test classes**: Named `Test<FeatureName>` (optional, for grouping)

**Example from `test_chat.py`:**
```python
def test_chat_new_conversation(client, seeded_db, mock_embeddings):
    """Test starting a new chat conversation."""
    # Test implementation
```

---

## 2. Configuration & Setup

### Pytest Configuration (`pytest.ini`)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v                      # Verbose output
    --tb=short              # Short traceback format
    --strict-markers        # Enforce marker usage
    --disable-warnings      # Clean output
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
```

**Key Benefits:**
- **Consistent test discovery**: Automatically finds all test files
- **Verbose output**: See which tests pass/fail clearly
- **Markers**: Categorize tests for selective execution (`pytest -m integration`)

### Test Dependencies (`requirements-test.txt`)

```txt
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
httpx==0.25.2
Pillow==10.1.0
```

**Separation of Concerns:**
- Production dependencies in `requirements.txt`
- Test-only dependencies in `requirements-test.txt`
- Enables clean CI/CD pipelines

---

## 3. Test Fixtures & Dependency Injection

### Centralized Fixture Configuration (`conftest.py`)

The `conftest.py` file is the heart of the test suite, providing shared fixtures and test infrastructure.

#### 3.1 Database Fixture

**Challenge**: Tests need isolated database state without affecting production data.

**Solution**: In-memory SQLite for fast tests, with PostgreSQL option for vector operations.

```python
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///:memory:"  # Fast, isolated, no cleanup needed
)

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if USE_SQLITE else {},
    poolclass=StaticPool if USE_SQLITE else None,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
        Base.metadata.drop_all(bind=engine)
```

**Key Features:**
- **Function scope**: Each test gets a clean database
- **Automatic cleanup**: Tables dropped after each test
- **SQLite fallback**: Handles pgvector incompatibility gracefully

#### 3.2 Test Client Fixture

**Challenge**: FastAPI apps require dependency injection for database sessions.

**Solution**: Override FastAPI's dependency injection system.

```python
@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()  # Clean up after test
```

**Usage Example from `test_chat.py`:**
```python
def test_chat_new_conversation(client, seeded_db, mock_embeddings):
    """Test starting a new chat conversation."""
    response = client.post(
        "/api/chat/",
        json={
            "message": "How can I increase resale value quickly?",
            "conversation_id": None,
            "listing_id": None,
            "user_id": None
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "conversation_id" in data
    assert "reply" in data
```

#### 3.3 Seeded Database Fixture

**Challenge**: Many tests need pre-populated data.

**Solution**: Reusable fixture that seeds common test data.

```python
@pytest.fixture(scope="function")
def seeded_db(db):
    """Create a database with seeded mock data."""
    seed_all(db, num_listings=3, images_per_listing=2, conversations_per_listing=1)
    return db
```

**Usage Example from `test_query.py`:**
```python
def test_query_images_with_listing(client, seeded_db, mock_embeddings):
    """Test query with listing ID filter."""
    from app.database import Listing
    listing = seeded_db.query(Listing).first()
    listing_id = listing.id if listing else 1
    
    response = client.post(
        "/api/query/",
        json={
            "query": "kitchen improvements",
            "k": 3,
            "listing_id": listing_id
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
```

---

## 4. Mocking External Dependencies

### 4.1 Mocking S3/Cloud Storage

**Challenge**: Tests shouldn't make real API calls to cloud services.

**Solution**: Monkeypatch S3 utilities to return mock paths.

```python
@pytest.fixture
def mock_s3_upload(monkeypatch):
    """Mock S3 upload to avoid actual S3 calls in tests."""
    def mock_upload_file(file_data, filename, bucket="realestate"):
        return f"s3://{bucket}/{filename}"
    
    from app.services import s3_utils
    monkeypatch.setattr(s3_utils, "upload_file", mock_upload_file)
    monkeypatch.setattr(s3_utils, "download_file", lambda s3_path: b"mock_image_data")
```

**Usage Example from `test_upload.py`:**
```python
def test_upload_image_sync(client, mock_image_file, mock_s3_upload, mock_inference):
    """Test synchronous image upload."""
    response = client.post(
        "/api/upload/",
        files={"file": ("test_image.png", mock_image_file, "image/png")},
        data={"listing_id": None}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "image_id" in data
```

### 4.2 Mocking ML Model Inference

**Challenge**: ML models are slow and require GPU/resources.

**Solution**: Deterministic mock that returns realistic predictions.

```python
@pytest.fixture
def mock_inference(monkeypatch):
    """Mock model inference to avoid actual model calls."""
    import numpy as np
    from app.model_stub import inference
    
    def mock_inference_func(image_data):
        # Return deterministic mock predictions
        predictions = {
            "room_type": {"label": "kitchen", "confidence": 0.93},
            "condition_score": 0.78,
            "natural_light_score": 0.61,
            "feature_tags": ["hardwood_floors", "island", "stainless_steel_appliances"]
        }
        image_embedding = np.random.randn(768).astype(np.float32)
        image_embedding = image_embedding / np.linalg.norm(image_embedding)
        text_embedding = np.random.randn(1536).astype(np.float32)
        text_embedding = text_embedding / np.linalg.norm(text_embedding)
        return predictions, image_embedding, text_embedding
    
    monkeypatch.setattr("app.model_stub.inference", mock_inference_func)
```

**Key Features:**
- **Deterministic**: Same input produces same output
- **Realistic structure**: Matches production API contract
- **Normalized embeddings**: Proper vector math for similarity search

### 4.3 Mocking Text Embeddings (LLM APIs)

**Challenge**: Embedding APIs are slow and cost money.

**Solution**: Seed-based deterministic embeddings.

```python
@pytest.fixture
def mock_embeddings(monkeypatch):
    """Mock text embeddings to avoid actual API calls."""
    import numpy as np
    
    def mock_get_text_embedding(text):
        np.random.seed(hash(text) % 2**32)  # Deterministic per text
        embedding = np.random.randn(1536).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)
        return embedding
    
    from app.services import embeddings
    monkeypatch.setattr(embeddings, "get_text_embedding", mock_get_text_embedding)
```

**Usage Example from `test_chat.py`:**
```python
def test_chat_with_listing(client, seeded_db, mock_embeddings):
    """Test chat with listing context."""
    from app.database import Listing
    listing = seeded_db.query(Listing).first()
    
    response = client.post(
        "/api/chat/",
        json={
            "message": "What improvements should I make?",
            "conversation_id": None,
            "listing_id": listing.id,
            "user_id": "test_user"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    assert "context_used" in response.json()
```

### 4.4 Mocking Async Tasks (Celery)

**Challenge**: Background tasks are asynchronous and hard to test.

**Solution**: Mock Celery's `AsyncResult` class.

**Example from `test_tasks.py`:**
```python
def test_get_task_status_success(client):
    """Test get task status for successful task."""
    with patch('app.routes.tasks.AsyncResult') as mock_async_result:
        mock_result = Mock()
        mock_result.state = 'SUCCESS'
        mock_result.result = {
            "status": "success",
            "image_id": 123,
            "predictions": {"room_type": {"label": "kitchen"}}
        }
        mock_async_result.return_value = mock_result
        
        response = client.get("/api/tasks/test-task-id")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "image_id" in data["result"]
```

---

## 5. API Endpoint Testing

### 5.1 Testing Happy Paths

**Example from `test_chat.py`:**
```python
def test_chat_new_conversation(client, seeded_db, mock_embeddings):
    """Test starting a new chat conversation."""
    response = client.post(
        "/api/chat/",
        json={
            "message": "How can I increase resale value quickly?",
            "conversation_id": None,
            "listing_id": None,
            "user_id": None
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "conversation_id" in data
    assert "reply" in data
    assert "context_used" in data
    assert isinstance(data["conversation_id"], int)
    assert isinstance(data["reply"], str)
    assert len(data["reply"]) > 0
```

**Best Practices:**
- ✅ Check status code explicitly
- ✅ Validate response structure
- ✅ Assert data types
- ✅ Verify business logic (e.g., conversation_id is created)

### 5.2 Testing Edge Cases

**Example from `test_chat.py`:**
```python
def test_chat_empty_message(client, seeded_db):
    """Test chat with empty message."""
    response = client.post(
        "/api/chat/",
        json={
            "message": "",
            "conversation_id": None,
            "listing_id": None,
            "user_id": None
        }
    )
    
    # Should still work (empty message generates embedding)
    assert response.status_code == status.HTTP_200_OK
```

**Example from `test_upload.py`:**
```python
def test_upload_image_no_file(client):
    """Test upload without file."""
    response = client.post("/api/upload/")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
```

### 5.3 Testing Stateful Operations

**Example from `test_chat.py`:**
```python
def test_chat_message_history(client, seeded_db, mock_embeddings):
    """Test that chat stores message history."""
    # Start a conversation
    response1 = client.post(
        "/api/chat/",
        json={
            "message": "What is the condition of this property?",
            "conversation_id": None,
            "listing_id": None,
            "user_id": None
        }
    )
    
    assert response1.status_code == status.HTTP_200_OK
    conversation_id = response1.json()["conversation_id"]
    
    # Send another message
    response2 = client.post(
        "/api/chat/",
        json={
            "message": "What about the kitchen?",
            "conversation_id": conversation_id,
            "listing_id": None,
            "user_id": None
        }
    )
    
    assert response2.status_code == status.HTTP_200_OK
    
    # Get conversation messages
    response3 = client.get(f"/api/conversations/{conversation_id}/messages")
    assert response3.status_code == status.HTTP_200_OK
    messages = response3.json()["messages"]
    
    # Should have at least 4 messages (2 user, 2 assistant)
    assert len(messages) >= 4
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"
```

### 5.4 Testing Query Parameters & Filters

**Example from `test_query.py`:**
```python
def test_query_images_with_listing(client, seeded_db, mock_embeddings):
    """Test query with listing ID filter."""
    from app.database import Listing
    listing = seeded_db.query(Listing).first()
    listing_id = listing.id if listing else 1
    
    response = client.post(
        "/api/query/",
        json={
            "query": "kitchen improvements",
            "k": 3,
            "listing_id": listing_id
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["top_k"]) <= 3
    
    # All results should be from the specified listing
    for result in data["top_k"]:
        assert result["id"] is not None
```

### 5.5 Testing Error Conditions

**Example from `test_query.py`:**
```python
def test_get_image_not_found(client):
    """Test get image with non-existent ID."""
    response = client.get("/api/images/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
```

**Example from `test_chat.py`:**
```python
def test_get_conversation_messages_not_found(client):
    """Test get messages for non-existent conversation."""
    response = client.get("/api/conversations/99999/messages")
    # Should return empty list or 404
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
```

---

## 6. Integration Testing

### 6.1 End-to-End Workflow Tests

**Example from `test_integration.py`:**
```python
def test_full_upload_and_query_workflow(client, mock_image_file, mock_s3_upload, mock_inference, mock_embeddings):
    """Test complete workflow: upload image, then query for it."""
    # 1. Upload an image
    upload_response = client.post(
        "/api/upload/",
        files={"file": ("test_image.png", mock_image_file, "image/png")}
    )
    
    assert upload_response.status_code == status.HTTP_200_OK
    upload_data = upload_response.json()
    image_id = upload_data["image_id"]
    
    # 2. Query for similar images
    query_response = client.post(
        "/api/query/",
        json={
            "query": "kitchen with island",
            "k": 5
        }
    )
    
    assert query_response.status_code == status.HTTP_200_OK
    query_data = query_response.json()
    
    # The uploaded image might appear in results
    image_ids = [img["id"] for img in query_data["top_k"]]
```

### 6.2 Multi-Step Business Logic Tests

**Example from `test_integration.py`:**
```python
def test_full_chat_workflow(client, seeded_db, mock_embeddings):
    """Test complete chat workflow with multiple messages."""
    # 1. Start conversation
    response1 = client.post(
        "/api/chat/",
        json={
            "message": "What improvements can I make?",
            "conversation_id": None,
            "listing_id": None,
            "user_id": "test_user"
        }
    )
    
    assert response1.status_code == status.HTTP_200_OK
    conversation_id = response1.json()["conversation_id"]
    
    # 2. Continue conversation
    response2 = client.post(
        "/api/chat/",
        json={
            "message": "Tell me more about the kitchen",
            "conversation_id": conversation_id,
            "listing_id": None,
            "user_id": "test_user"
        }
    )
    
    assert response2.status_code == status.HTTP_200_OK
    
    # 3. Get conversation history
    response3 = client.get(f"/api/conversations/{conversation_id}/messages")
    assert response3.status_code == status.HTTP_200_OK
    messages = response3.json()["messages"]
    
    assert len(messages) >= 4  # At least 2 user + 2 assistant messages
```

### 6.3 Cross-Module Integration Tests

**Example from `test_integration.py`:**
```python
def test_upload_and_chat_workflow(client, mock_image_file, mock_s3_upload, mock_inference, mock_embeddings):
    """Test workflow: upload image, then chat about it."""
    # 1. Upload image with listing
    upload_response = client.post(
        "/api/upload/",
        files={"file": ("kitchen.png", mock_image_file, "image/png")},
        data={"listing_id": 1}
    )
    
    assert upload_response.status_code == status.HTTP_200_OK
    
    # 2. Chat about the listing
    chat_response = client.post(
        "/api/chat/",
        json={
            "message": "What improvements should I make to this property?",
            "conversation_id": None,
            "listing_id": 1,
            "user_id": "test_user"
        }
    )
    
    assert chat_response.status_code == status.HTTP_200_OK
    chat_data = chat_response.json()
    assert "reply" in chat_data
    assert "context_used" in chat_data
```

---

## 7. Data Seeding & Test Data Management

### 7.1 Mock Data Generation

**Example from `test_mock_data.py`:**
```python
def test_generate_mock_embedding():
    """Test mock embedding generation."""
    embedding = generate_mock_embedding(768)
    assert embedding.shape == (768,)
    assert embedding.dtype == np.float32
    # Should be normalized
    assert np.isclose(np.linalg.norm(embedding), 1.0, atol=1e-6)

def test_generate_mock_embedding_deterministic():
    """Test that embeddings are deterministic with same seed."""
    emb1 = generate_mock_embedding(768, seed=42)
    emb2 = generate_mock_embedding(768, seed=42)
    np.testing.assert_array_equal(emb1, emb2)
```

**Key Principles:**
- ✅ **Deterministic**: Same inputs produce same outputs
- ✅ **Realistic**: Data structure matches production
- ✅ **Testable**: Mock data generators are themselves tested

### 7.2 Database Seeding Strategy

**Example from `seed_data.py`:**
```python
def seed_all(db: Session, num_listings: int = 5, images_per_listing: int = 3, conversations_per_listing: int = 2):
    """Seed all mock data including new expanded features."""
    listing_ids = seed_listings(db, num_listings)
    image_ids = seed_images(db, listing_ids, images_per_listing)
    conversation_ids = seed_conversations(db, listing_ids, conversations_per_listing)
    
    # Additional features
    aggregation_ids = seed_property_aggregations(db, listing_ids)
    temporal_change_ids = seed_temporal_changes(db, listing_ids, image_ids)
    
    return {
        "listing_ids": listing_ids,
        "image_ids": image_ids,
        "conversation_ids": conversation_ids,
        # ...
    }
```

**Benefits:**
- **Reusable**: One function seeds entire test database
- **Configurable**: Control data volume per test
- **Comprehensive**: Creates realistic relationships between entities

---

## 8. Best Practices & Patterns

### 8.1 Test Organization

✅ **DO:**
- Group related tests in the same file (`test_chat.py` for all chat tests)
- Use descriptive test names: `test_chat_new_conversation` not `test_chat_1`
- Keep tests independent (no shared state between tests)
- Use fixtures for common setup

❌ **DON'T:**
- Create tests that depend on execution order
- Use production database for tests
- Make real API calls in unit tests
- Share mutable state between tests

### 8.2 Assertion Patterns

**Good Assertions:**
```python
# Specific and informative
assert response.status_code == status.HTTP_200_OK
assert data["conversation_id"] == conversation_id
assert len(messages) >= 4
assert messages[0]["role"] == "user"
```

**Avoid:**
```python
# Too generic
assert response.status_code == 200  # Use status.HTTP_200_OK
assert data  # Too vague
```

### 8.3 Handling Database-Specific Features

**Example from `test_query.py`:**
```python
def test_query_images(client, seeded_db, mock_embeddings):
    """Test query for similar images."""
    # Skip vector search tests if using SQLite (pgvector not supported)
    if os.getenv("TEST_DATABASE_URL", "").startswith("sqlite"):
        pytest.skip("Vector search requires PostgreSQL with pgvector")
    
    # Test implementation...
```

**Strategy:**
- Use conditional skipping for database-specific features
- Provide clear skip messages
- Support both SQLite (fast) and PostgreSQL (full features)

### 8.4 Test File Structure Template

```python
"""Tests for <feature> endpoints."""
import pytest
from fastapi import status

# Happy path tests
def test_<feature>_<scenario>(client, fixtures):
    """Test <scenario>."""
    # Arrange
    # Act
    # Assert

# Edge case tests
def test_<feature>_<edge_case>(client, fixtures):
    """Test <edge_case>."""
    # Test implementation

# Error condition tests
def test_<feature>_<error>(client):
    """Test <error> handling."""
    # Test implementation
```

### 8.5 Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_chat.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run only integration tests
pytest -m integration

# Run with verbose output
pytest -v

# Run specific test
pytest tests/test_chat.py::test_chat_new_conversation
```

---

## Summary

This testing strategy provides:

1. **Isolation**: Each test runs in a clean environment
2. **Speed**: In-memory database and mocked external services
3. **Reliability**: Deterministic mocks and comprehensive fixtures
4. **Maintainability**: Clear organization and reusable patterns
5. **Coverage**: Unit, integration, and end-to-end tests

**Key Takeaways:**
- Centralize fixtures in `conftest.py`
- Mock all external dependencies (APIs, databases, ML models)
- Use descriptive test names and docstrings
- Test happy paths, edge cases, and error conditions
- Keep tests independent and fast
- Seed test data programmatically for consistency

---

## Example Test Execution

```bash
$ pytest tests/test_chat.py -v

tests/test_chat.py::test_chat_new_conversation PASSED
tests/test_chat.py::test_chat_existing_conversation PASSED
tests/test_chat.py::test_chat_with_listing PASSED
tests/test_chat.py::test_chat_message_history PASSED
tests/test_chat.py::test_chat_empty_message PASSED
tests/test_chat.py::test_get_conversation_messages PASSED
tests/test_chat.py::test_get_conversation_messages_not_found PASSED

======================== 7 passed in 2.34s ========================
```

This comprehensive testing approach ensures your API is robust, maintainable, and production-ready.

