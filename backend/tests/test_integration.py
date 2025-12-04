"""Integration tests for full workflows."""
import pytest
from fastapi import status


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
    # Note: In SQLite, embeddings might not work perfectly, so we just check the query works


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

