"""Tests for mock data generation."""
import pytest
import numpy as np
from app.fixtures.mock_data import (
    generate_mock_embedding,
    generate_mock_predictions,
    generate_mock_listing,
    generate_mock_image_data,
    generate_mock_conversation,
    generate_mock_message
)


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


def test_generate_mock_predictions():
    """Test mock predictions generation."""
    predictions = generate_mock_predictions()
    assert "room_type" in predictions
    assert "condition_score" in predictions
    assert "natural_light_score" in predictions
    assert "feature_tags" in predictions
    assert "label" in predictions["room_type"]
    assert "confidence" in predictions["room_type"]
    assert 0 <= predictions["condition_score"] <= 1
    assert 0 <= predictions["natural_light_score"] <= 1
    assert isinstance(predictions["feature_tags"], list)


def test_generate_mock_listing():
    """Test mock listing generation."""
    listing = generate_mock_listing()
    assert "address" in listing
    assert "price" in listing
    assert "zip_code" in listing
    assert listing["price"] > 0
    assert len(listing["zip_code"]) == 5


def test_generate_mock_image_data():
    """Test mock image data generation."""
    image_data = generate_mock_image_data(listing_id=1)
    assert "filename" in image_data
    assert "s3_path" in image_data
    assert "embedding" in image_data
    assert "text_embedding" in image_data
    assert "predictions" in image_data
    assert len(image_data["embedding"]) == 768
    assert len(image_data["text_embedding"]) == 1536


def test_generate_mock_conversation():
    """Test mock conversation generation."""
    conversation = generate_mock_conversation(listing_id=1, user_id="test_user")
    assert "user_id" in conversation
    assert "listing_id" in conversation
    assert conversation["user_id"] == "test_user"
    assert conversation["listing_id"] == 1


def test_generate_mock_message():
    """Test mock message generation."""
    message = generate_mock_message(conversation_id=1, role="user")
    assert "conversation_id" in message
    assert "role" in message
    assert "text" in message
    assert "embedding" in message
    assert message["role"] == "user"
    assert len(message["embedding"]) == 1536


def test_generate_mock_message_assistant():
    """Test mock assistant message generation."""
    message = generate_mock_message(conversation_id=1, role="assistant")
    assert message["role"] == "assistant"
    assert len(message["text"]) > 0

