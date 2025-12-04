"""Image upload endpoints."""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from ..database import get_db
from ..services.s3_utils import upload_file
from ..services.crud import insert_image_record
from ..model_stub import inference
from ..schemas.prediction import UploadResponse, PredictionResponse, RoomTypePrediction
from ..workers import process_image_s3  # For async endpoint

router = APIRouter()


@router.post("/upload/", response_model=UploadResponse)
async def upload_image_sync(
    file: UploadFile = File(...),
    listing_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Synchronous image upload - runs inference immediately.
    """
    try:
        contents = await file.read()
        
        # Upload to S3/MinIO
        s3_path = upload_file(contents, file.filename)
        
        # Run model inference (synchronous)
        preds, embedding, text_embedding = inference(contents)
        
        # Persist to database
        image_id = insert_image_record(
            db=db,
            filename=file.filename,
            s3_path=s3_path,
            embedding=embedding,
            text_embedding=text_embedding,
            preds=preds,
            listing_id=listing_id
        )
        
        return UploadResponse(
            status="success",
            image_id=image_id,
            filename=file.filename,
            predictions=PredictionResponse(
                room_type=RoomTypePrediction(
                    label=preds["room_type"]["label"],
                    confidence=preds["room_type"]["confidence"]
                ),
                condition_score=preds["condition_score"],
                natural_light_score=preds["natural_light_score"],
                feature_tags=preds["feature_tags"]
            ),
            embeddings={
                "image_embedding_length": len(embedding),
                "image_embedding": embedding.tolist()[:10],  # Truncated for response
                "text_embedding_length": len(text_embedding) if text_embedding is not None else 0
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/upload/async")
async def upload_image_async(
    file: UploadFile = File(...),
    listing_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Asynchronous image upload - returns task_id for polling.
    """
    try:
        contents = await file.read()
        
        # Upload to S3/MinIO first
        s3_path = upload_file(contents, file.filename)
        
        # Parse bucket and key from s3_path
        # s3_path format: s3://bucket/key
        parts = s3_path[5:].split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else ""
        
        # Enqueue Celery task
        task = process_image_s3.delay(bucket, key, file.filename, listing_id)
        
        return {
            "status": "queued",
            "task_id": task.id,
            "s3_path": s3_path
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

