"""Tests for chat endpoints."""
import pytest
from fastapi import status


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


def test_chat_existing_conversation(client, seeded_db, mock_embeddings):
    """Test continuing an existing conversation."""
    # Get an existing conversation
    from app.database import Conversation
    conversation = seeded_db.query(Conversation).first()
    
    if conversation:
        conversation_id = conversation.id
    else:
        # Create a conversation first
        conversation = Conversation(user_id="test_user", listing_id=None)
        seeded_db.add(conversation)
        seeded_db.commit()
        conversation_id = conversation.id
    
    response = client.post(
        "/api/chat/",
        json={
            "message": "What about the bathroom?",
            "conversation_id": conversation_id,
            "listing_id": None,
            "user_id": None
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["conversation_id"] == conversation_id
    assert "reply" in data


def test_chat_with_listing(client, seeded_db, mock_embeddings):
    """Test chat with listing context."""
    from app.database import Listing
    listing = seeded_db.query(Listing).first()
    listing_id = listing.id if listing else None
    
    response = client.post(
        "/api/chat/",
        json={
            "message": "What improvements should I make?",
            "conversation_id": None,
            "listing_id": listing_id,
            "user_id": "test_user"
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "conversation_id" in data
    assert "reply" in data
    assert "context_used" in data
    # Context should include images from the listing
    assert data["context_used"]["images_count"] >= 0


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
    assert messages[2]["role"] == "user"
    assert messages[3]["role"] == "assistant"


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


def test_get_conversation_messages(client, seeded_db):
    """Test get conversation messages."""
    from app.database import Conversation
    conversation = seeded_db.query(Conversation).first()
    
    if conversation:
        response = client.get(f"/api/conversations/{conversation.id}/messages")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "conversation_id" in data
        assert "messages" in data
        assert isinstance(data["messages"], list)


def test_get_conversation_messages_not_found(client):
    """Test get messages for non-existent conversation."""
    response = client.get("/api/conversations/99999/messages")
    # Should return empty list or 404
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]

