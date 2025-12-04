"""Database CRUD operations."""
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Optional, List
import numpy as np
import json
from datetime import datetime
from ..database import (
    Image, ImageLabel, Listing, Message, Conversation, EmbeddingIndex,
    PropertyAggregation, TemporalChange, ModelDriftDetection, ModelMetrics,
    PerformanceLog, AuditSample
)


def insert_image_record(
    db: Session,
    filename: str,
    s3_path: str,
    embedding: np.ndarray,
    text_embedding: Optional[np.ndarray],
    preds: Dict,
    listing_id: Optional[int] = None,
    uploaded_by: Optional[str] = None,
    model_version: Optional[str] = None,
    inference_timestamp: Optional[datetime] = None,
    gradcam_path: Optional[str] = None,
    sample_input_path: Optional[str] = None
) -> int:
    """
    Insert image record with embeddings and predictions (expanded).
    
    Returns:
        image_id
    """
    from datetime import datetime
    
    # Convert embeddings to lists for pgvector
    embedding_list = embedding.tolist() if embedding is not None else None
    text_embedding_list = text_embedding.tolist() if text_embedding is not None else None
    
    # Insert image record
    image = Image(
        filename=filename,
        s3_path=s3_path,
        listing_id=listing_id,
        embedding=embedding_list,
        text_embedding=text_embedding_list,
        meta=json.dumps({
            "source": model_version or "model_v1",
            "uploaded_by": uploaded_by,
            "inference_timestamp": (inference_timestamp or datetime.utcnow()).isoformat()
        })
    )
    db.add(image)
    db.flush()  # Get the image_id
    
    # Insert image labels with expanded fields
    if preds:
        label = ImageLabel(
            image_id=image.id,
            room_type=preds.get("room_type", {}).get("label"),
            room_confidence=preds.get("room_type", {}).get("confidence"),
            condition_score=preds.get("condition_score"),
            natural_light_score=preds.get("natural_light_score"),
            features=preds.get("feature_tags", []),
            # New fields
            localization=preds.get("localization", {}).get("label") if isinstance(preds.get("localization"), dict) else None,
            localization_confidence=preds.get("localization", {}).get("confidence") if isinstance(preds.get("localization"), dict) else None,
            style=preds.get("style", {}).get("label") if isinstance(preds.get("style"), dict) else None,
            style_confidence=preds.get("style", {}).get("confidence") if isinstance(preds.get("style"), dict) else None,
            work_recommendations=preds.get("work_recommendations", []),
            cost_estimates=preds.get("cost_estimates", []),
            model_version=model_version or "model_v1",
            inference_timestamp=inference_timestamp or datetime.utcnow(),
            gradcam_path=gradcam_path,
            sample_input_path=sample_input_path
        )
        db.add(label)
    
    # Optionally add to embeddings_index
    if text_embedding is not None:
        embedding_index = EmbeddingIndex(
            type="image",
            vector=text_embedding_list,
            ref_id=image.id
        )
        db.add(embedding_index)
    
    db.commit()
    return image.id


def get_image_by_id(db: Session, image_id: int) -> Optional[Dict]:
    """Get image record with labels by ID."""
    image = db.query(Image).filter(Image.id == image_id).first()
    if not image:
        return None
    
    label = db.query(ImageLabel).filter(ImageLabel.image_id == image_id).first()
    
    return {
        "id": image.id,
        "filename": image.filename,
        "s3_path": image.s3_path,
        "thumb_path": image.thumb_path,
        "embedding": image.embedding,
        "text_embedding": image.text_embedding,
        "meta": image.meta,
        "room_type": label.room_type if label else None,
        "room_confidence": label.room_confidence if label else None,
        "condition_score": label.condition_score if label else None,
        "natural_light_score": label.natural_light_score if label else None,
        "features": label.features if label else None,
    }


def search_similar_images(
    db: Session,
    query_embedding: np.ndarray,
    k: int = 6,
    listing_id: Optional[int] = None
) -> List[Dict]:
    """
    Search for similar images using pgvector cosine similarity.
    
    Args:
        db: Database session
        query_embedding: Query vector (768 for image or 1536 for text)
        k: Number of results
        listing_id: Optional filter by listing
        
    Returns:
        List of image records with similarity scores
    """
    embedding_list = query_embedding.tolist()
    dim = len(embedding_list)
    
    # Use cosine distance operator <#> (pgvector)
    # For cosine similarity: 1 - (embedding <#> query_embedding)
    # For Euclidean distance: embedding <-> query_embedding
    
    if listing_id:
        sql = text("""
            SELECT i.id, i.filename, i.s3_path, i.thumb_path, il.room_type, 
                   il.features, il.condition_score, il.natural_light_score,
                   1 - (i.embedding <#> :query) as similarity
            FROM images i
            LEFT JOIN image_labels il ON i.id = il.image_id
            WHERE i.listing_id = :listing_id AND i.embedding IS NOT NULL
            ORDER BY i.embedding <#> :query
            LIMIT :k
        """)
        result = db.execute(sql, {"query": embedding_list, "listing_id": listing_id, "k": k})
    else:
        sql = text("""
            SELECT i.id, i.filename, i.s3_path, i.thumb_path, il.room_type, 
                   il.features, il.condition_score, il.natural_light_score,
                   1 - (i.embedding <#> :query) as similarity
            FROM images i
            LEFT JOIN image_labels il ON i.id = il.image_id
            WHERE i.embedding IS NOT NULL
            ORDER BY i.embedding <#> :query
            LIMIT :k
        """)
        result = db.execute(sql, {"query": embedding_list, "k": k})
    
    rows = result.fetchall()
    
    return [
        {
            "id": row[0],
            "filename": row[1],
            "s3_path": row[2],
            "thumb_path": row[3],
            "room_type": row[4],
            "room_confidence": float(row[5]) if row[5] is not None else None,
            "features": row[6],
            "condition_score": float(row[7]) if row[7] is not None else None,
            "natural_light_score": float(row[8]) if row[8] is not None else None,
            "similarity": float(row[9])
        }
        for row in rows
    ]


def create_conversation(db: Session, user_id: Optional[str] = None, listing_id: Optional[int] = None) -> int:
    """Create a new conversation."""
    conversation = Conversation(user_id=user_id, listing_id=listing_id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation.id


def add_message(
    db: Session,
    conversation_id: int,
    role: str,
    text: str,
    embedding: Optional[np.ndarray] = None,
    embedding_latency_ms: Optional[float] = None,
    retrieval_latency_ms: Optional[float] = None,
    llm_latency_ms: Optional[float] = None
) -> int:
    """Add a message to a conversation with performance metrics."""
    embedding_list = embedding.tolist() if embedding is not None else None
    
    message = Message(
        conversation_id=conversation_id,
        role=role,
        text=text,
        embedding=embedding_list,
        embedding_latency_ms=embedding_latency_ms,
        retrieval_latency_ms=retrieval_latency_ms,
        llm_latency_ms=llm_latency_ms
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message.id


def get_conversation_messages(db: Session, conversation_id: int) -> List[Dict]:
    """Get all messages for a conversation."""
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
    return [
        {
            "id": msg.id,
            "role": msg.role,
            "text": msg.text,
            "created_at": msg.created_at.isoformat()
        }
        for msg in messages
    ]


def search_similar_messages(
    db: Session,
    query_embedding: np.ndarray,
    conversation_id: Optional[int] = None,
    k: int = 5
) -> List[Dict]:
    """Search for similar messages using embedding similarity."""
    embedding_list = query_embedding.tolist()
    
    if conversation_id:
        sql = text("""
            SELECT id, conversation_id, role, text, 
                   1 - (embedding <#> :query) as similarity
            FROM messages
            WHERE embedding IS NOT NULL AND conversation_id = :conversation_id
            ORDER BY embedding <#> :query
            LIMIT :k
        """)
        result = db.execute(sql, {"query": embedding_list, "conversation_id": conversation_id, "k": k})
    else:
        sql = text("""
            SELECT id, conversation_id, role, text, 
                   1 - (embedding <#> :query) as similarity
            FROM messages
            WHERE embedding IS NOT NULL
            ORDER BY embedding <#> :query
            LIMIT :k
        """)
        result = db.execute(sql, {"query": embedding_list, "k": k})
    
    rows = result.fetchall()
    
    return [
        {
            "id": row[0],
            "conversation_id": row[1],
            "role": row[2],
            "text": row[3],
            "similarity": float(row[4])
        }
        for row in rows
    ]

