"""Health check endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db, engine

router = APIRouter()


@router.get("/health")
async def health_check():
    """Basic health check."""
    return {"status": "healthy"}


@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check - verifies database connectivity."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={"status": "not ready", "database": "disconnected", "error": str(e)}
        )


@router.get("/health/live")
async def liveness_check():
    """Liveness check - service is running."""
    return {"status": "alive"}

