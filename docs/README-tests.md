# Testing Documentation

Comprehensive testing guide for the Real Estate AI Platform.

## Quick Test Commands

### One-Command Test Run

**Linux/macOS:**
```bash
chmod +x run_tests.sh
./run_tests.sh
```

**Windows:**
```cmd
run_tests.bat
```

**Using Make:**
```bash
make test-cov
```

### Make Commands for Testing

```bash
make test        # Run all tests
make test-cov    # Run tests with coverage report
make test-watch  # Run tests in watch mode (requires pytest-watch)
```

## Test Structure

```
backend/tests/
├── conftest.py           # Pytest fixtures and configuration
├── test_upload.py        # Upload endpoint tests
├── test_query.py          # Query/search endpoint tests
├── test_chat.py           # Chat/RAG endpoint tests
├── test_health.py         # Health check tests
├── test_tasks.py          # Async task status tests
├── test_integration.py    # End-to-end workflow tests
├── test_mock_data.py      # Mock data generator tests
└── test_api.py            # Basic smoke tests
```

## Running Tests

### Basic Test Run

```bash
cd backend
pytest
```

### With Coverage

```bash
cd backend
pytest --cov=app --cov-report=html --cov-report=term tests/
```

Coverage report will be generated in `backend/htmlcov/index.html`

### Verbose Output

```bash
pytest -v tests/
```

### Specific Test File

```bash
pytest tests/test_upload.py
```

### Specific Test Function

```bash
pytest tests/test_upload.py::test_upload_image_sync
```

### Run Tests Matching Pattern

```bash
pytest -k "upload" tests/
```

### Run Tests with Markers

```bash
pytest -m unit tests/
pytest -m integration tests/
```

## Test Configuration

### Pytest Configuration

See `backend/pytest.ini` for configuration:

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
    slow: Slow running tests
```

### Test Database

Tests use an in-memory SQLite database by default. For PostgreSQL with pgvector:

```bash
export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/realestate_test"
pytest
```

## Test Fixtures

### Available Fixtures

- **`client`**: FastAPI test client with database override
- **`db`**: Fresh database session for each test
- **`seeded_db`**: Database with pre-seeded mock data
- **`mock_image_file`**: Mock image file for upload tests
- **`mock_s3_upload`**: Mocks S3/MinIO operations
- **`mock_inference`**: Mocks model inference
- **`mock_embeddings`**: Mocks text embedding generation

### Using Fixtures

```python
def test_upload(client, mock_image_file, mock_s3_upload, mock_inference):
    response = client.post(
        "/api/upload/",
        files={"file": ("test.png", mock_image_file, "image/png")}
    )
    assert response.status_code == 200
```

## Test Coverage

### Generate Coverage Report

```bash
make test-cov
# or
cd backend && pytest --cov=app --cov-report=html tests/
```

### View Coverage Report

Open `backend/htmlcov/index.html` in your browser:

```bash
# macOS
open backend/htmlcov/index.html

# Windows
start backend/htmlcov/index.html

# Linux
xdg-open backend/htmlcov/index.html
```

### Coverage Targets

- **Current**: ~60-70% (basic endpoint coverage)
- **Target**: 80%+ (all endpoints, error cases, edge cases)

## Mock Data

### Generating Mock Data

Mock data is generated using functions in `app/fixtures/mock_data.py`:

```python
from app.fixtures.mock_data import (
    generate_mock_embedding,
    generate_mock_predictions,
    generate_mock_listing,
    generate_mock_image_data,
    generate_mock_conversation,
    generate_mock_message
)
```

### Seeding Database

Seed database with mock data for testing:

```bash
make seed
# or
cd backend && python seed_db.py
```

Or programmatically:

```python
from app.database import SessionLocal
from app.fixtures.seed_data import seed_all

db = SessionLocal()
seed_all(db, num_listings=5, images_per_listing=3, conversations_per_listing=2)
```

## Test Categories

### Unit Tests

Fast, isolated tests for individual components:

```bash
pytest -m unit tests/
```

### Integration Tests

End-to-end tests for complete workflows:

```bash
pytest -m integration tests/
```

### Slow Tests

Tests that take longer to run:

```bash
pytest -m "not slow" tests/  # Skip slow tests
```

## Test Examples

### Upload Endpoint Test

```python
def test_upload_image_sync(client, mock_image_file, mock_s3_upload, mock_inference):
    response = client.post(
        "/api/upload/",
        files={"file": ("test.png", mock_image_file, "image/png")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "image_id" in data
```

### Query Endpoint Test

```python
def test_query_images(client, seeded_db, mock_embeddings):
    response = client.post(
        "/api/query/",
        json={"query": "kitchen improvements", "k": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert "top_k" in data
    assert len(data["top_k"]) > 0
```

### Chat Endpoint Test

```python
def test_chat_new_conversation(client, seeded_db, mock_embeddings):
    response = client.post(
        "/api/chat/",
        json={"message": "What improvements should I make?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "conversation_id" in data
    assert "reply" in data
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=app --cov-report=xml tests/
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Test Best Practices

1. **Isolation**: Each test should be independent
2. **Fixtures**: Use fixtures for common setup
3. **Mocking**: Mock external dependencies (S3, models, APIs)
4. **Assertions**: Use specific assertions
5. **Naming**: Use descriptive test names
6. **Coverage**: Aim for high coverage of critical paths
7. **Speed**: Keep tests fast (< 1 second per test when possible)

## Troubleshooting

### Tests Failing

```bash
# Run with verbose output
pytest -v tests/

# Run with full traceback
pytest --tb=long tests/

# Run specific failing test
pytest tests/test_upload.py::test_upload_image_sync -v
```

### Database Issues

```bash
# Clear test database
docker-compose exec db psql -U postgres -d realestate_test -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Reinitialize
cd backend && python init_db.py
```

### Import Errors

```bash
# Install dependencies
cd backend
pip install -r requirements.txt

# Verify installation
pip list | grep pytest
```

### Vector Search Tests

Vector search tests require PostgreSQL with pgvector. If using SQLite, these tests will be skipped:

```bash
# Set PostgreSQL test database
export TEST_DATABASE_URL="postgresql://postgres:postgres@localhost:5432/realestate_test"
pytest tests/test_query.py
```

## Performance Testing

### Load Testing (Future)

```bash
# Install locust
pip install locust

# Run load tests
cd backend
locust -f tests/load_test.py
```

### Benchmark Tests

```bash
pytest tests/test_performance.py --benchmark-only
```

## Test Data Management

### Fixtures Directory

- `app/fixtures/mock_data.py`: Mock data generators
- `app/fixtures/seed_data.py`: Database seeding functions

### Test Data Files

Place test data files in `backend/tests/data/`:
- Sample images: `tests/data/images/`
- Test fixtures: `tests/data/fixtures/`

## Related Documentation

- [Backend Documentation](README-backend.md#testing)
- [Quick Start Guide](QUICKSTART.md)
- [Main README](README.md)

