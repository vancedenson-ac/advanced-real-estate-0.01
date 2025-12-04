"""Application settings."""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings."""
    database_url: str = "postgresql://postgres:postgres@db:5432/realestate"
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minio"
    minio_secret_key: str = "minio123"
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"
    openai_api_key: Optional[str] = None
    
    # Security settings
    cors_origins: list = ["*"]  # In production, specify exact origins
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

