"""Tests for query endpoints."""
import pytest
import os
from fastapi import status


def test_query_images(client, seeded_db, mock_embeddings):
    """Test query for similar images."""
    import os
    # Skip vector search tests if using SQLite (pgvector not supported)
    if os.getenv("TEST_DATABASE_URL", "").startswith("sqlite"):
        pytest.skip("Vector search requires PostgreSQL with pgvector")
    
    response = client.post(
        "/api/query/",
        json={
            "query": "How can I increase resale value quickly?",
            "k": 5,
            "listing_id": None
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "query" in data
    assert "top_k" in data
    assert isinstance(data["top_k"], list)
    assert len(data["top_k"]) > 0
    
    # Check structure of results
    if len(data["top_k"]) > 0:
        result = data["top_k"][0]
        assert "id" in result
        assert "filename" in result
        assert "s3_path" in result
        assert "similarity" in result
        assert 0 <= result["similarity"] <= 1


def test_query_images_with_listing(client, seeded_db, mock_embeddings):
    """Test query with listing ID filter."""
    import os
    # Skip vector search tests if using SQLite (pgvector not supported)
    if os.getenv("TEST_DATABASE_URL", "").startswith("sqlite"):
        pytest.skip("Vector search requires PostgreSQL with pgvector")
    
    # Get a listing ID from seeded data
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
        # Verify listing_id in database (would need to query)
        assert result["id"] is not None


def test_query_images_empty_query(client):
    """Test query with empty query string."""
    response = client.post(
        "/api/query/",
        json={
            "query": "",
            "k": 5
        }
    )
    
    # Should still work (empty query generates embedding)
    assert response.status_code == status.HTTP_200_OK


def test_query_images_large_k(client, seeded_db, mock_embeddings):
    """Test query with large k value."""
    response = client.post(
        "/api/query/",
        json={
            "query": "test query",
            "k": 100
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    # Should return at most available images
    assert len(data["top_k"]) <= 100


def test_get_image_by_id(client, seeded_db):
    """Test get image by ID."""
    from app.database import Image
    image = seeded_db.query(Image).first()
    
    if image:
        response = client.get(f"/api/images/{image.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == image.id
        assert "filename" in data
        assert "s3_path" in data
        # Embeddings should be truncated
        if "embedding" in data and data["embedding"]:
            assert len(data["embedding"]) <= 10


def test_get_image_not_found(client):
    """Test get image with non-existent ID."""
    response = client.get("/api/images/99999")
    assert response.status_code == status.HTTP_404_NOT_FOUND

