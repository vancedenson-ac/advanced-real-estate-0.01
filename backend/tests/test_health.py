"""Tests for health endpoints."""
import pytest
from fastapi import status


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/api/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert data["status"] == "healthy" or data["database"] in ["healthy", "unhealthy"]


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data

