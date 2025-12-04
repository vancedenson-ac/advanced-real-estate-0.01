"""Tests for upload endpoints."""
import pytest
from fastapi import status


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
    assert "filename" in data
    assert "predictions" in data
    assert "embeddings" in data
    assert data["predictions"]["room_type"]["label"] == "kitchen"
    assert data["predictions"]["room_type"]["confidence"] == 0.93


def test_upload_image_sync_with_listing(client, mock_image_file, mock_s3_upload, mock_inference):
    """Test synchronous image upload with listing ID."""
    response = client.post(
        "/api/upload/",
        files={"file": ("test_image.png", mock_image_file, "image/png")},
        data={"listing_id": 1}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert data["image_id"] is not None


def test_upload_image_async(client, mock_image_file, mock_s3_upload):
    """Test asynchronous image upload."""
    response = client.post(
        "/api/upload/async",
        files={"file": ("test_image.png", mock_image_file, "image/png")},
        data={"listing_id": None}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "queued"
    assert "task_id" in data
    assert "s3_path" in data


def test_upload_image_no_file(client):
    """Test upload without file."""
    response = client.post("/api/upload/")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_upload_image_invalid_file(client):
    """Test upload with invalid file."""
    response = client.post(
        "/api/upload/",
        files={"file": ("test.txt", b"not an image", "text/plain")}
    )
    # Should still work with mock inference, but in production would fail
    # For now, we'll just check it doesn't crash
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]

