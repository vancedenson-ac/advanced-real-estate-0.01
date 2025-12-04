"""Image query/search endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.crud import search_similar_images
from ..services.embeddings import get_text_embedding
from ..schemas.prediction import QueryRequest, QueryResponse, ImageResult

router = APIRouter()


@router.post("/query/", response_model=QueryResponse)
async def query_images(
    request: QueryRequest,
    db: Session = Depends(get_db)
):
    """
    Search for similar images using text query.
    Converts text to embedding and searches pgvector.
    """
    try:
        # Convert text query to embedding
        query_embedding = get_text_embedding(request.query)
        
        # Search for similar images using text embedding
        results = search_similar_images(
            db=db,
            query_embedding=query_embedding,  # 1536-d text embedding
            k=request.k or 6,
            listing_id=request.listing_id,
            use_text_embedding=True  # Use text_embedding column for text queries
        )
        
        return QueryResponse(
            query=request.query,
            top_k=[
                ImageResult(
                    id=r["id"],
                    filename=r["filename"],
                    s3_path=r["s3_path"],
                    thumb_path=r.get("thumb_path"),
                    room_type=r.get("room_type"),
                    features=r.get("features"),
                    condition_score=r.get("condition_score"),
                    natural_light_score=r.get("natural_light_score"),
                    similarity=r["similarity"]
                )
                for r in results
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@router.get("/images/{image_id}")
async def get_image(
    image_id: int,
    db: Session = Depends(get_db)
):
    """Get image metadata by ID."""
    from ..services.crud import get_image_by_id
    
    image = get_image_by_id(db, image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Optionally truncate embeddings in response
    response = image.copy()
    if response.get("embedding"):
        response["embedding"] = response["embedding"][:10]  # Truncated
    if response.get("text_embedding"):
        response["text_embedding"] = response["text_embedding"][:10]  # Truncated
    
    return response

