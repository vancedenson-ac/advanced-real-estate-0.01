"""Seed database with mock data."""
from sqlalchemy.orm import Session
from ..database import (
    Listing, Image, ImageLabel, Conversation, Message, EmbeddingIndex,
    PropertyAggregation, TemporalChange, ModelDriftDetection, ModelMetrics,
    PerformanceLog, AuditSample
)
from .mock_data import (
    generate_mock_listing,
    generate_mock_image_data,
    generate_mock_conversation,
    generate_mock_conversation_with_messages,
    generate_mock_property_aggregation,
    generate_mock_temporal_change,
    generate_mock_drift_detection,
    generate_mock_model_metrics,
    generate_mock_performance_log,
    generate_mock_audit_sample
)
import json
import random
from typing import List
from datetime import datetime, timedelta


def seed_listings(db: Session, count: int = 5) -> List[int]:
    """Seed database with mock listings."""
    listing_ids = []
    for i in range(count):
        listing_data = generate_mock_listing()
        listing = Listing(**listing_data)
        db.add(listing)
        db.flush()
        listing_ids.append(listing.id)
    
    db.commit()
    print(f"Created {count} listings: {listing_ids}")
    return listing_ids


def seed_images(db: Session, listing_ids: List[int], images_per_listing: int = 3) -> List[int]:
    """Seed database with mock images including all new fields."""
    image_ids = []
    
    for listing_id in listing_ids:
        # Create images with timestamps spread over time for temporal change detection
        base_time = datetime.utcnow() - timedelta(days=30)
        
        for i in range(images_per_listing):
            # Spread timestamps over time
            timestamp = base_time + timedelta(days=i * 10)
            image_data = generate_mock_image_data(listing_id, timestamp)
            predictions = image_data.pop("predictions")
            
            # Create image record
            image = Image(
                listing_id=image_data["listing_id"],
                filename=image_data["filename"],
                s3_path=image_data["s3_path"],
                thumb_path=image_data["thumb_path"],
                embedding=image_data["embedding"],
                text_embedding=image_data["text_embedding"],
                meta=json.dumps(image_data["meta"])
            )
            db.add(image)
            db.flush()
            
            # Create image label with all new fields
            label = ImageLabel(
                image_id=image.id,
                room_type=predictions["room_type"]["label"],
                room_confidence=predictions["room_type"]["confidence"],
                condition_score=predictions["condition_score"],
                natural_light_score=predictions["natural_light_score"],
                features=predictions["feature_tags"],
                # New fields
                localization=predictions.get("localization", {}).get("label"),
                localization_confidence=predictions.get("localization", {}).get("confidence"),
                style=predictions.get("style", {}).get("label"),
                style_confidence=predictions.get("style", {}).get("confidence"),
                work_recommendations=predictions.get("work_recommendations", []),
                cost_estimates=predictions.get("cost_estimates", []),
                model_version=image_data.get("model_version"),
                inference_timestamp=image_data.get("inference_timestamp"),
                gradcam_path=image_data.get("gradcam_path"),
                sample_input_path=image_data.get("sample_input_path")
            )
            db.add(label)
            
            # Create embedding index entry
            if image_data["text_embedding"]:
                embedding_index = EmbeddingIndex(
                    type="image",
                    vector=image_data["text_embedding"],
                    ref_id=image.id
                )
                db.add(embedding_index)
            
            image_ids.append(image.id)
    
    db.commit()
    print(f"Created {len(image_ids)} images")
    return image_ids


def seed_conversations(db: Session, listing_ids: List[int], conversations_per_listing: int = 2) -> List[int]:
    """Seed database with mock conversations and messages."""
    conversation_ids = []
    
    for listing_id in listing_ids:
        for i in range(conversations_per_listing):
            conv_data = generate_mock_conversation(listing_id)
            conversation = Conversation(**conv_data)
            db.add(conversation)
            db.flush()
            
            # Generate messages for this conversation
            messages_data = generate_mock_conversation_with_messages(
                conversation.id,
                num_messages=random.randint(4, 8)
            )
            
            for msg_data in messages_data:
                message = Message(**msg_data)
                db.add(message)
            
            conversation_ids.append(conversation.id)
    
    db.commit()
    print(f"Created {len(conversation_ids)} conversations with messages")
    return conversation_ids


def seed_property_aggregations(db: Session, listing_ids: List[int]) -> List[int]:
    """Seed property-level aggregations."""
    aggregation_ids = []
    
    for listing_id in listing_ids:
        agg_data = generate_mock_property_aggregation(listing_id)
        aggregation = PropertyAggregation(**agg_data)
        db.add(aggregation)
        db.flush()
        aggregation_ids.append(aggregation.id)
        
        # Update listing with aggregated data
        listing = db.query(Listing).filter(Listing.id == listing_id).first()
        if listing:
            listing.dominant_room_types = json.dumps([agg_data["dominant_room_type"]])
            listing.overall_condition_score = agg_data["overall_condition_score"]
            listing.room_counts = json.dumps(agg_data["room_counts"])
            listing.total_images = agg_data["total_images"]
    
    db.commit()
    print(f"Created {len(aggregation_ids)} property aggregations")
    return aggregation_ids


def seed_temporal_changes(db: Session, listing_ids: List[int], image_ids: List[int]) -> List[int]:
    """Seed temporal change detection records."""
    change_ids = []
    
    # Create changes for a subset of listings
    for listing_id in listing_ids[:len(listing_ids)//2]:  # 50% of listings
        listing_images = [img_id for img_id in image_ids if random.random() < 0.3]  # 30% of images
        
        if len(listing_images) >= 2:
            # Create a change record comparing two images
            current_image_id = listing_images[0]
            previous_image_id = listing_images[1] if len(listing_images) > 1 else None
            
            change_data = generate_mock_temporal_change(listing_id, current_image_id, previous_image_id)
            change = TemporalChange(**change_data)
            db.add(change)
            db.flush()
            change_ids.append(change.id)
    
    db.commit()
    print(f"Created {len(change_ids)} temporal change records")
    return change_ids


def seed_drift_detection(db: Session, num_records: int = 5) -> List[int]:
    """Seed model drift detection records."""
    drift_ids = []
    
    for i in range(num_records):
        drift_data = generate_mock_drift_detection(f"model_v{random.randint(1, 3)}")
        drift = ModelDriftDetection(**drift_data)
        db.add(drift)
        db.flush()
        drift_ids.append(drift.id)
    
    db.commit()
    print(f"Created {len(drift_ids)} drift detection records")
    return drift_ids


def seed_model_metrics(db: Session, num_records: int = 10) -> List[int]:
    """Seed model metrics records."""
    metric_ids = []
    
    heads = ["room_type", "condition", "features", "natural_light", "style", "localization"]
    
    for i in range(num_records):
        head_name = random.choice(heads)
        metric_data = generate_mock_model_metrics(f"model_v{random.randint(1, 3)}", head_name)
        metric = ModelMetrics(**metric_data)
        db.add(metric)
        db.flush()
        metric_ids.append(metric.id)
    
    db.commit()
    print(f"Created {len(metric_ids)} model metrics records")
    return metric_ids


def seed_performance_logs(db: Session, num_records: int = 20) -> List[int]:
    """Seed performance log records."""
    log_ids = []
    
    operation_types = ["embedding", "retrieval", "llm", "inference"]
    
    for i in range(num_records):
        operation_type = random.choice(operation_types)
        log_data = generate_mock_performance_log(operation_type)
        log = PerformanceLog(**log_data)
        db.add(log)
        db.flush()
        log_ids.append(log.id)
    
    db.commit()
    print(f"Created {len(log_ids)} performance log records")
    return log_ids


def seed_audit_samples(db: Session, image_ids: List[int], sample_rate: float = 0.1) -> List[int]:
    """Seed audit sample records."""
    sample_ids = []
    
    # Sample 10% of images for audit
    sampled_images = random.sample(image_ids, int(len(image_ids) * sample_rate))
    
    for image_id in sampled_images:
        sample_data = generate_mock_audit_sample(image_id, listing_id=None)
        sample = AuditSample(**sample_data)
        db.add(sample)
        db.flush()
        sample_ids.append(sample.id)
    
    db.commit()
    print(f"Created {len(sample_ids)} audit sample records")
    return sample_ids


def seed_all(db: Session, num_listings: int = 5, images_per_listing: int = 3, conversations_per_listing: int = 2):
    """Seed all mock data including new expanded features."""
    print("Seeding database with comprehensive mock data...")
    
    listing_ids = seed_listings(db, num_listings)
    image_ids = seed_images(db, listing_ids, images_per_listing)
    conversation_ids = seed_conversations(db, listing_ids, conversations_per_listing)
    
    # New expanded features
    aggregation_ids = seed_property_aggregations(db, listing_ids)
    temporal_change_ids = seed_temporal_changes(db, listing_ids, image_ids)
    drift_ids = seed_drift_detection(db, num_records=5)
    metric_ids = seed_model_metrics(db, num_records=10)
    performance_log_ids = seed_performance_logs(db, num_records=20)
    audit_sample_ids = seed_audit_samples(db, image_ids, sample_rate=0.1)
    
    print(f"\n✅ Seed complete!")
    print(f"- Listings: {len(listing_ids)}")
    print(f"- Images: {len(image_ids)}")
    print(f"- Conversations: {len(conversation_ids)}")
    print(f"- Property Aggregations: {len(aggregation_ids)}")
    print(f"- Temporal Changes: {len(temporal_change_ids)}")
    print(f"- Drift Detection: {len(drift_ids)}")
    print(f"- Model Metrics: {len(metric_ids)}")
    print(f"- Performance Logs: {len(performance_log_ids)}")
    print(f"- Audit Samples: {len(audit_sample_ids)}")
    
    return {
        "listing_ids": listing_ids,
        "image_ids": image_ids,
        "conversation_ids": conversation_ids,
        "aggregation_ids": aggregation_ids,
        "temporal_change_ids": temporal_change_ids,
        "drift_ids": drift_ids,
        "metric_ids": metric_ids,
        "performance_log_ids": performance_log_ids,
        "audit_sample_ids": audit_sample_ids
    }

