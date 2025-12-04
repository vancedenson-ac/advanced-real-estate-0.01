"""Tests for expanded features: temporal tracking, drift detection, metrics, etc."""
import pytest
from fastapi import status
from datetime import datetime, timedelta


def test_property_aggregation_creation(client, seeded_db):
    """Test property aggregation creation and retrieval."""
    from app.database import Listing, PropertyAggregation
    from app.fixtures.seed_data import seed_property_aggregations
    from app.fixtures.mock_data import generate_mock_property_aggregation
    
    # Get a listing
    listing = seeded_db.query(Listing).first()
    if listing:
        # Create aggregation
        agg_data = generate_mock_property_aggregation(listing.id)
        aggregation = PropertyAggregation(**agg_data)
        seeded_db.add(aggregation)
        seeded_db.commit()
        
        # Verify aggregation
        assert aggregation.listing_id == listing.id
        assert aggregation.overall_condition_score is not None
        assert aggregation.room_counts is not None
        assert aggregation.dominant_room_type is not None


def test_temporal_change_detection(client, seeded_db):
    """Test temporal change detection."""
    from app.database import Listing, Image, TemporalChange
    from app.fixtures.mock_data import generate_mock_temporal_change
    
    # Get a listing and images
    listing = seeded_db.query(Listing).first()
    if listing:
        images = seeded_db.query(Image).filter(Image.listing_id == listing.id).limit(2).all()
        
        if len(images) >= 2:
            current_image = images[0]
            previous_image = images[1]
            
            # Create temporal change
            change_data = generate_mock_temporal_change(
                listing.id,
                current_image.id,
                previous_image.id
            )
            change = TemporalChange(**change_data)
            seeded_db.add(change)
            seeded_db.commit()
            
            # Verify change
            assert change.listing_id == listing.id
            assert change.image_id == current_image.id
            assert change.previous_image_id == previous_image.id
            assert change.change_type in ["condition", "natural_light", "feature", "style"]
            assert change.change_direction in ["improved", "degraded", "stable"]


def test_drift_detection(client, seeded_db):
    """Test model drift detection."""
    from app.database import ModelDriftDetection
    from app.fixtures.mock_data import generate_mock_drift_detection
    
    # Create drift detection record
    drift_data = generate_mock_drift_detection("model_v1")
    drift = ModelDriftDetection(**drift_data)
    seeded_db.add(drift)
    seeded_db.commit()
    
    # Verify drift detection
    assert drift.model_version == "model_v1"
    assert drift.metric_name is not None
    assert drift.baseline_mean is not None
    assert drift.current_mean is not None
    assert drift.drift_score is not None
    assert isinstance(drift.drift_detected, bool)


def test_model_metrics(client, seeded_db):
    """Test model metrics recording."""
    from app.database import ModelMetrics
    from app.fixtures.mock_data import generate_mock_model_metrics
    
    # Create metrics for different heads
    heads = ["room_type", "condition", "features"]
    
    for head_name in heads:
        metric_data = generate_mock_model_metrics("model_v1", head_name)
        metric = ModelMetrics(**metric_data)
        seeded_db.add(metric)
    
    seeded_db.commit()
    
    # Verify metrics
    metrics = seeded_db.query(ModelMetrics).filter(
        ModelMetrics.model_version == "model_v1"
    ).all()
    
    assert len(metrics) == len(heads)
    for metric in metrics:
        assert metric.head_name in heads
        assert metric.precision is not None
        assert metric.recall is not None
        assert metric.f1_score is not None
        assert metric.mAP is not None


def test_performance_logging(client, seeded_db):
    """Test performance log recording."""
    from app.database import PerformanceLog
    from app.fixtures.mock_data import generate_mock_performance_log
    
    # Create performance logs for different operations
    operation_types = ["embedding", "retrieval", "llm", "inference"]
    
    for op_type in operation_types:
        log_data = generate_mock_performance_log(op_type)
        log = PerformanceLog(**log_data)
        seeded_db.add(log)
    
    seeded_db.commit()
    
    # Verify logs
    logs = seeded_db.query(PerformanceLog).all()
    assert len(logs) >= len(operation_types)
    
    for log in logs:
        assert log.operation_type in operation_types
        assert log.latency_ms > 0
        assert log.started_at is not None
        assert log.completed_at is not None


def test_audit_sample_creation(client, seeded_db):
    """Test audit sample creation."""
    from app.database import Image, AuditSample
    from app.fixtures.mock_data import generate_mock_audit_sample
    
    # Get an image
    image = seeded_db.query(Image).first()
    if image:
        # Create audit sample
        sample_data = generate_mock_audit_sample(image.id, image.listing_id)
        sample = AuditSample(**sample_data)
        seeded_db.add(sample)
        seeded_db.commit()
        
        # Verify sample
        assert sample.image_id == image.id
        assert sample.sample_type in ["gradcam", "input", "output", "error_case"]
        assert sample.priority in ["high", "medium", "low"]
        assert sample.audit_status in ["pending", "reviewed", "resolved"]


def test_expanded_image_labels(client, seeded_db):
    """Test expanded image labels with new fields."""
    from app.database import ImageLabel
    
    # Get an image label
    label = seeded_db.query(ImageLabel).first()
    if label:
        # Verify core fields
        assert label.room_type is not None
        assert label.condition_score is not None
        assert label.natural_light_score is not None
        
        # New fields may be None (for backward compatibility)
        # But schema should support them
        assert hasattr(label, 'localization')
        assert hasattr(label, 'style')
        assert hasattr(label, 'work_recommendations')
        assert hasattr(label, 'cost_estimates')
        assert hasattr(label, 'model_version')


def test_listing_with_aggregations(client, seeded_db):
    """Test listing with property aggregations."""
    from app.database import Listing
    
    # Get a listing
    listing = seeded_db.query(Listing).first()
    if listing:
        # Verify new fields exist
        assert hasattr(listing, 'estimated_price')
        assert hasattr(listing, 'price_confidence')
        assert hasattr(listing, 'city')
        assert hasattr(listing, 'state')
        assert hasattr(listing, 'latitude')
        assert hasattr(listing, 'longitude')
        assert hasattr(listing, 'dominant_room_types')
        assert hasattr(listing, 'overall_condition_score')
        assert hasattr(listing, 'room_counts')
        assert hasattr(listing, 'total_images')


def test_message_with_performance_metrics(client, seeded_db):
    """Test message with performance metrics."""
    from app.database import Message
    
    # Get a message
    message = seeded_db.query(Message).first()
    if message:
        # Verify new fields exist
        assert hasattr(message, 'embedding_latency_ms')
        assert hasattr(message, 'retrieval_latency_ms')
        assert hasattr(message, 'llm_latency_ms')


def test_comprehensive_seeding(client, db):
    """Test comprehensive seed function with all new features."""
    from app.fixtures.seed_data import seed_all
    
    # Seed all data
    result = seed_all(db, num_listings=3, images_per_listing=2, conversations_per_listing=1)
    
    # Verify all data types were created
    assert "listing_ids" in result
    assert "image_ids" in result
    assert "conversation_ids" in result
    assert "aggregation_ids" in result
    assert "temporal_change_ids" in result
    assert "drift_ids" in result
    assert "metric_ids" in result
    assert "performance_log_ids" in result
    assert "audit_sample_ids" in result
    
    # Verify counts
    assert len(result["listing_ids"]) == 3
    assert len(result["image_ids"]) == 6  # 3 listings * 2 images
    assert len(result["aggregation_ids"]) == 3
    assert len(result["drift_ids"]) == 5
    assert len(result["metric_ids"]) == 10
    assert len(result["performance_log_ids"]) == 20

