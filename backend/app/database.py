"""PostgreSQL + pgvector database setup and session management."""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.types import Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from sqlalchemy.dialects.postgresql import JSONB
from pgvector.sqlalchemy import Vector
import os
from datetime import datetime

Base = declarative_base()


class Listing(Base):
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, nullable=False)
    price = Column(Float, index=True)  # Listed price
    estimated_price = Column(Float, nullable=True)  # AI-predicted price
    price_confidence = Column(Float, nullable=True)  # Confidence in price estimate
    
    # Location details
    zip_code = Column(String, index=True)
    city = Column(String, nullable=True, index=True)
    state = Column(String, nullable=True, index=True)
    country = Column(String, nullable=True, default="USA")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Property-level aggregations (from PropertyAggregation)
    dominant_room_types = Column(JSONB, nullable=True)  # Most common room types
    overall_condition_score = Column(Float, nullable=True, index=True)
    room_counts = Column(JSONB, nullable=True)  # Count of each room type
    total_images = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Image(Base):
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, nullable=True, index=True)
    filename = Column(String, nullable=False)
    s3_path = Column(String, nullable=False)
    thumb_path = Column(String, nullable=True)
    embedding = Column(Vector(768), nullable=True)  # Image embedding dimension
    text_embedding = Column(Vector(1536), nullable=True)  # Text embedding (OpenAI dimension)
    meta = Column(JSONB, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ImageLabel(Base):
    __tablename__ = "image_labels"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, nullable=False, index=True)
    
    # Core classifications
    room_type = Column(String, nullable=True, index=True)
    room_confidence = Column(Float, nullable=True)
    condition_score = Column(Float, nullable=True, index=True)
    natural_light_score = Column(Float, nullable=True, index=True)
    features = Column(JSONB, nullable=True)  # Feature tags as JSON array
    
    # Expanded features
    localization = Column(String, nullable=True, index=True)  # Region/area identification
    localization_confidence = Column(Float, nullable=True)
    style = Column(String, nullable=True, index=True)  # Architectural/style classification
    style_confidence = Column(Float, nullable=True)
    
    # Work recommendations and estimates
    work_recommendations = Column(JSONB, nullable=True)  # List of recommended improvements
    cost_estimates = Column(JSONB, nullable=True)  # Cost estimates per recommendation
    
    # Model metadata
    model_version = Column(String, nullable=True)  # Model version used for inference
    inference_timestamp = Column(DateTime, nullable=True)  # When inference was run
    gradcam_path = Column(String, nullable=True)  # Path to GradCAM visualization
    sample_input_path = Column(String, nullable=True)  # Path to sample input for audit
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EmbeddingIndex(Base):
    __tablename__ = "embeddings_index"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False, index=True)  # 'image' or 'text'
    vector = Column(Vector(1536), nullable=False)  # Unified dimension
    ref_id = Column(Integer, nullable=False, index=True)  # Reference to images.id or messages.id


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=True, index=True)
    listing_id = Column(Integer, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, nullable=False, index=True)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    text = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=True)
    
    # Performance metrics
    embedding_latency_ms = Column(Float, nullable=True)  # Time to generate embedding
    retrieval_latency_ms = Column(Float, nullable=True)  # Time for vector search
    llm_latency_ms = Column(Float, nullable=True)  # Time for LLM call
    
    created_at = Column(DateTime, default=datetime.utcnow)


class PropertyAggregation(Base):
    """Property-level aggregation of image outputs."""
    __tablename__ = "property_aggregations"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, nullable=False, unique=True, index=True)
    
    # Aggregated scores
    overall_condition_score = Column(Float, nullable=True)
    avg_natural_light_score = Column(Float, nullable=True)
    
    # Room type counts
    room_counts = Column(JSONB, nullable=True)  # {"kitchen": 3, "bathroom": 2, ...}
    dominant_room_type = Column(String, nullable=True)
    
    # Feature aggregation
    common_features = Column(JSONB, nullable=True)  # Most common features across images
    
    # Style aggregation
    dominant_style = Column(String, nullable=True)
    style_distribution = Column(JSONB, nullable=True)
    
    # Localization
    primary_localization = Column(String, nullable=True)
    localization_distribution = Column(JSONB, nullable=True)
    
    # Calculated fields
    total_images = Column(Integer, default=0)
    last_calculated_at = Column(DateTime, nullable=True)
    calculation_version = Column(String, nullable=True)  # Algorithm version
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TemporalChange(Base):
    """Track changes in property condition over time."""
    __tablename__ = "temporal_changes"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, nullable=False, index=True)
    image_id = Column(Integer, nullable=False, index=True)
    
    # Change detection
    change_type = Column(String, nullable=False, index=True)  # 'condition', 'light', 'feature', etc.
    change_magnitude = Column(Float, nullable=True)  # Absolute change value
    change_direction = Column(String, nullable=True)  # 'improved', 'degraded', 'stable'
    
    # Comparison data
    previous_value = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    previous_image_id = Column(Integer, nullable=True)  # Previous image for comparison
    time_delta_days = Column(Integer, nullable=True)  # Days between images
    
    # Metadata
    detected_at = Column(DateTime, default=datetime.utcnow, index=True)
    model_version = Column(String, nullable=True)
    flagged_for_review = Column(Boolean, default=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelDriftDetection(Base):
    """Track distribution shifts in model outputs (drift detection)."""
    __tablename__ = "model_drift_detection"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Detection metadata
    detection_date = Column(DateTime, default=datetime.utcnow, index=True)
    model_version = Column(String, nullable=False, index=True)
    metric_name = Column(String, nullable=False, index=True)  # 'natural_light_good_ratio', etc.
    
    # Distribution metrics
    baseline_mean = Column(Float, nullable=True)
    baseline_std = Column(Float, nullable=True)
    current_mean = Column(Float, nullable=True)
    current_std = Column(Float, nullable=True)
    
    # Drift metrics
    drift_score = Column(Float, nullable=True)  # Statistical test score (KS, PSI, etc.)
    drift_magnitude = Column(Float, nullable=True)  # Effect size
    drift_detected = Column(Boolean, default=False, index=True)
    
    # Alerting
    alert_sent = Column(Boolean, default=False)
    alert_threshold = Column(Float, nullable=True)
    
    # Sample data
    sample_size = Column(Integer, nullable=True)
    window_start = Column(DateTime, nullable=True)
    window_end = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class ModelMetrics(Base):
    """Per-head metrics for model evaluation (precision, recall, mAP)."""
    __tablename__ = "model_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Model and head identification
    model_version = Column(String, nullable=False, index=True)
    head_name = Column(String, nullable=False, index=True)  # 'room_type', 'condition', 'features', etc.
    class_name = Column(String, nullable=True, index=True)  # Specific class for multi-class heads
    
    # Metrics
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    mAP = Column(Float, nullable=True)  # Mean Average Precision
    
    # Evaluation metadata
    validation_set_size = Column(Integer, nullable=True)
    evaluation_date = Column(DateTime, default=datetime.utcnow, index=True)
    evaluation_split = Column(String, nullable=True)  # 'validation', 'test', 'rolling'
    
    # Rolling window metrics
    window_start = Column(DateTime, nullable=True)
    window_end = Column(DateTime, nullable=True)
    
    # Additional metrics
    true_positives = Column(Integer, default=0)
    false_positives = Column(Integer, default=0)
    false_negatives = Column(Integer, default=0)
    true_negatives = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class PerformanceLog(Base):
    """Log latencies and performance metrics for all operations."""
    __tablename__ = "performance_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Operation identification
    operation_type = Column(String, nullable=False, index=True)  # 'embedding', 'retrieval', 'llm', 'inference'
    operation_name = Column(String, nullable=True)  # Specific operation name
    
    # Latency metrics (in milliseconds)
    latency_ms = Column(Float, nullable=False, index=True)
    p50_latency_ms = Column(Float, nullable=True)
    p95_latency_ms = Column(Float, nullable=True)
    p99_latency_ms = Column(Float, nullable=True)
    
    # Resource usage
    cpu_usage_percent = Column(Float, nullable=True)
    memory_usage_mb = Column(Float, nullable=True)
    gpu_usage_percent = Column(Float, nullable=True)
    
    # Context
    image_id = Column(Integer, nullable=True, index=True)
    listing_id = Column(Integer, nullable=True, index=True)
    conversation_id = Column(Integer, nullable=True, index=True)
    
    # Model/service metadata
    model_version = Column(String, nullable=True)
    service_name = Column(String, nullable=True)  # 'embedding_service', 'llm_service', etc.
    
    # Success/failure
    success = Column(Boolean, default=True, index=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditSample(Base):
    """Record sample inputs and GradCAMs for manual audits."""
    __tablename__ = "audit_samples"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Sample identification
    image_id = Column(Integer, nullable=False, index=True)
    listing_id = Column(Integer, nullable=True, index=True)
    
    # Sample metadata
    sample_type = Column(String, nullable=False, index=True)  # 'gradcam', 'input', 'output', 'error_case'
    sample_reason = Column(String, nullable=True)  # Why this sample was selected
    priority = Column(String, nullable=True, index=True)  # 'high', 'medium', 'low'
    
    # File paths
    original_image_path = Column(String, nullable=True)
    gradcam_path = Column(String, nullable=True)
    sample_input_path = Column(String, nullable=True)
    sample_output_path = Column(String, nullable=True)
    
    # Model predictions at time of sampling
    predictions_snapshot = Column(JSONB, nullable=True)
    model_version = Column(String, nullable=True)
    
    # Audit status
    audit_status = Column(String, nullable=True, index=True)  # 'pending', 'reviewed', 'resolved'
    reviewed_by = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Flags
    flagged_for_review = Column(Boolean, default=False, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Database connection
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/realestate"
)

# Production-ready connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,              # Number of connections to maintain
    max_overflow=10,           # Max connections beyond pool_size
    pool_pre_ping=True,        # Verify connections before using
    pool_recycle=3600,         # Recycle connections after 1 hour
    echo=False                 # Set to True for SQL debugging
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency for FastAPI database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and pgvector extension."""
    from sqlalchemy import text
    
    try:
        # Create pgvector extension
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            conn.commit()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

