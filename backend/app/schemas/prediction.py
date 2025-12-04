"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class RoomTypePrediction(BaseModel):
    label: str
    confidence: float


class PredictionResponse(BaseModel):
    room_type: RoomTypePrediction
    condition_score: float
    natural_light_score: float
    feature_tags: List[str]


class UploadResponse(BaseModel):
    status: str
    image_id: int
    filename: str
    predictions: PredictionResponse
    embeddings: Dict[str, Any]


class QueryRequest(BaseModel):
    query: str
    k: Optional[int] = 6
    listing_id: Optional[int] = None


class ImageResult(BaseModel):
    id: int
    filename: str
    s3_path: str
    thumb_path: Optional[str]
    room_type: Optional[str]
    features: Optional[List[str]]
    condition_score: Optional[float]
    natural_light_score: Optional[float]
    similarity: float


class QueryResponse(BaseModel):
    query: str
    top_k: List[ImageResult]


class ChatMessage(BaseModel):
    role: str
    text: str


class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    message: str
    listing_id: Optional[int] = None
    user_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: int
    reply: str
    context_used: Optional[Dict[str, Any]] = None


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

