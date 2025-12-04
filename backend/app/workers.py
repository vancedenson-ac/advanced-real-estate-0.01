"""Celery worker entrypoint."""
from celery import Celery
import os
from .model_stub import inference
from .database import SessionLocal
from .services.crud import insert_image_record
from .services.s3_utils import download_file
from typing import Optional

# Celery configuration
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0")

celery = Celery(
    "realestate_workers",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery.task(name="process_image_s3")
def process_image_s3(s3_bucket: str, s3_key: str, filename: str, listing_id: Optional[int] = None, uploaded_by: Optional[str] = None):
    """
    Process image from S3: download, run inference, persist to database.
    
    Args:
        s3_bucket: S3 bucket name
        s3_key: S3 key (filename)
        filename: Original filename
        listing_id: Optional listing ID
        uploaded_by: Optional user ID
        
    Returns:
        Dict with image_id and predictions
    """
    try:
        # Download from S3
        s3_path = f"s3://{s3_bucket}/{s3_key}"
        image_data = download_file(s3_path)
        
        # Run model inference
        preds, embedding, text_embedding = inference(image_data)
        
        # Persist to database
        db = SessionLocal()
        try:
            image_id = insert_image_record(
                db=db,
                filename=filename,
                s3_path=s3_path,
                embedding=embedding,
                text_embedding=text_embedding,
                preds=preds,
                listing_id=listing_id,
                uploaded_by=uploaded_by
            )
            
            return {
                "status": "success",
                "image_id": image_id,
                "predictions": preds,
                "embedding_dim": len(embedding)
            }
        finally:
            db.close()
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

