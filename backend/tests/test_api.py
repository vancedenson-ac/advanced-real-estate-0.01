"""Basic API tests - kept for backward compatibility."""
from fastapi.testclient import TestClient
from app.main import app

# Note: For comprehensive tests, use the fixtures from conftest.py
# These basic tests are kept for simple smoke tests

client = TestClient(app)


def test_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_health():
    """Test health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert "status" in response.json()

