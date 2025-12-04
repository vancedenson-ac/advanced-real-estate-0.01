"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os
import tempfile
import shutil

from app.database import Base, get_db
from app.main import app
from app.fixtures.seed_data import seed_all


# Use in-memory SQLite for testing (or override with test database URL)
# Note: pgvector operations won't work with SQLite, but basic CRUD tests will
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "sqlite:///:memory:"
)

# For pgvector testing, use a test PostgreSQL database:
# TEST_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/realestate_test"

# Check if using SQLite (for vector column compatibility)
USE_SQLITE = "sqlite" in TEST_DATABASE_URL

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if USE_SQLITE else {},
    poolclass=StaticPool if USE_SQLITE else None,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    # Create tables
    # Note: For SQLite, pgvector Vector columns won't work, but we'll still create tables
    # Vector operations will be skipped in tests that use SQLite
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        # If pgvector fails (e.g., in SQLite), create minimal schema
        if USE_SQLITE:
            # Create basic tables without vector columns
            from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
            from sqlalchemy.ext.declarative import declarative_base
            
            TestBase = declarative_base()
            
            class TestListing(TestBase):
                __tablename__ = "listings"
                id = Column(Integer, primary_key=True, index=True)
                address = Column(String, nullable=False)
                price = Column(Float)
                zip_code = Column(String, index=True)
            
            class TestImage(TestBase):
                __tablename__ = "images"
                id = Column(Integer, primary_key=True, index=True)
                listing_id = Column(Integer, nullable=True, index=True)
                filename = Column(String, nullable=False)
                s3_path = Column(String, nullable=False)
                embedding = Column(JSON, nullable=True)
                text_embedding = Column(JSON, nullable=True)
            
            TestBase.metadata.create_all(bind=engine)
    
    # Create session
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
        # Drop tables
        try:
            Base.metadata.drop_all(bind=engine)
        except Exception:
            pass


@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database dependency override."""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def seeded_db(db):
    """Create a database with seeded mock data."""
    seed_all(db, num_listings=3, images_per_listing=2, conversations_per_listing=1)
    return db


@pytest.fixture(scope="function")
def mock_image_file():
    """Create a mock image file for testing."""
    # Create a simple test image (1x1 pixel PNG)
    import io
    from PIL import Image
    
    img = Image.new('RGB', (1, 1), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes


@pytest.fixture
def mock_s3_upload(monkeypatch):
    """Mock S3 upload to avoid actual S3 calls in tests."""
    def mock_upload_file(file_data, filename, bucket="realestate"):
        return f"s3://{bucket}/{filename}"
    
    from app.services import s3_utils
    monkeypatch.setattr(s3_utils, "upload_file", mock_upload_file)
    monkeypatch.setattr(s3_utils, "download_file", lambda s3_path: b"mock_image_data")


@pytest.fixture
def mock_inference(monkeypatch):
    """Mock model inference to avoid actual model calls."""
    import numpy as np
    from app.model_stub import inference
    
    def mock_inference_func(image_data):
        # Return deterministic mock predictions
        predictions = {
            "room_type": {"label": "kitchen", "confidence": 0.93},
            "condition_score": 0.78,
            "natural_light_score": 0.61,
            "feature_tags": ["hardwood_floors", "island", "stainless_steel_appliances"]
        }
        image_embedding = np.random.randn(768).astype(np.float32)
        image_embedding = image_embedding / np.linalg.norm(image_embedding)
        text_embedding = np.random.randn(1536).astype(np.float32)
        text_embedding = text_embedding / np.linalg.norm(text_embedding)
        return predictions, image_embedding, text_embedding
    
    monkeypatch.setattr("app.model_stub.inference", mock_inference_func)


@pytest.fixture
def mock_embeddings(monkeypatch):
    """Mock text embeddings to avoid actual API calls."""
    import numpy as np
    
    def mock_get_text_embedding(text):
        np.random.seed(hash(text) % 2**32)
        embedding = np.random.randn(1536).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)
        return embedding
    
    from app.services import embeddings
    monkeypatch.setattr(embeddings, "get_text_embedding", mock_get_text_embedding)

