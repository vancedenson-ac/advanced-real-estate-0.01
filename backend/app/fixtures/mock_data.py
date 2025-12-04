"""Mock data generators for testing."""
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random


def generate_mock_embedding(dim: int = 768, seed: Optional[int] = None) -> np.ndarray:
    """Generate a mock embedding vector."""
    if seed is not None:
        np.random.seed(seed)
    embedding = np.random.randn(dim).astype(np.float32)
    embedding = embedding / np.linalg.norm(embedding)  # Normalize
    return embedding


def generate_mock_predictions() -> Dict:
    """Generate comprehensive mock predictions for an image."""
    room_types = ["kitchen", "bathroom", "bedroom", "living_room", "dining_room", "office", "hallway", "basement"]
    feature_tags_pool = [
        "hardwood_floors", "island", "stainless_steel_appliances", "granite_countertops",
        "marble_bathroom", "walk_in_closet", "fireplace", "bay_windows", "crown_molding",
        "recessed_lighting", "vaulted_ceiling", "patio", "balcony", "updated_plumbing",
        "granite_floors", "tile_backsplash", "double_sink", "jacuzzi", "skylight"
    ]
    
    localizations = ["urban", "suburban", "rural", "coastal", "mountain", "desert"]
    styles = ["modern", "traditional", "contemporary", "rustic", "minimalist", "industrial", "colonial", "mediterranean"]
    
    # Generate work recommendations
    work_recommendations = [
        {
            "type": random.choice(["paint", "renovate", "repair", "upgrade", "replace"]),
            "description": f"Update {random.choice(['cabinets', 'fixtures', 'flooring', 'lighting'])}",
            "priority": random.choice(["high", "medium", "low"]),
            "estimated_roi": round(random.uniform(0.5, 2.5), 2)
        }
        for _ in range(random.randint(1, 4))
    ]
    
    # Generate cost estimates
    cost_estimates = [
        {
            "recommendation_id": i,
            "low_estimate": round(random.uniform(500, 2000), 2),
            "high_estimate": round(random.uniform(2000, 10000), 2),
            "currency": "USD"
        }
        for i in range(len(work_recommendations))
    ]
    
    return {
        "room_type": {
            "label": random.choice(room_types),
            "confidence": round(random.uniform(0.75, 0.98), 2)
        },
        "condition_score": round(random.uniform(0.5, 0.95), 2),
        "natural_light_score": round(random.uniform(0.4, 0.9), 2),
        "feature_tags": random.sample(feature_tags_pool, random.randint(2, 5)),
        "localization": {
            "label": random.choice(localizations),
            "confidence": round(random.uniform(0.7, 0.95), 2)
        },
        "style": {
            "label": random.choice(styles),
            "confidence": round(random.uniform(0.7, 0.95), 2)
        },
        "work_recommendations": work_recommendations,
        "cost_estimates": cost_estimates
    }


def generate_mock_listing() -> Dict:
    """Generate comprehensive mock listing data."""
    cities_states = [
        ("New York", "NY", "10001", 40.7128, -74.0060),
        ("Los Angeles", "CA", "90001", 34.0522, -118.2437),
        ("Chicago", "IL", "60601", 41.8781, -87.6298),
        ("Houston", "TX", "77001", 29.7604, -95.3698),
        ("Phoenix", "AZ", "85001", 33.4484, -112.0740),
        ("Philadelphia", "PA", "19101", 39.9526, -75.1652),
    ]
    
    city, state, zip_code, lat, lon = random.choice(cities_states)
    
    base_price = round(random.uniform(200000, 2000000), 2)
    estimated_price = base_price * random.uniform(0.9, 1.1)  # ±10% of base price
    
    return {
        "address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Park', 'Oak', 'Elm', 'Maple'])} St, {city}",
        "price": base_price,
        "estimated_price": round(estimated_price, 2),
        "price_confidence": round(random.uniform(0.7, 0.95), 2),
        "zip_code": zip_code,
        "city": city,
        "state": state,
        "country": "USA",
        "latitude": lat + random.uniform(-0.1, 0.1),
        "longitude": lon + random.uniform(-0.1, 0.1),
        "created_at": datetime.utcnow() - timedelta(days=random.randint(0, 30)),
        "updated_at": datetime.utcnow()
    }


def generate_mock_image_data(listing_id: Optional[int] = None, timestamp: Optional[datetime] = None) -> Dict:
    """Generate comprehensive mock image data with all new fields."""
    filename = f"image_{random.randint(1000, 9999)}.jpg"
    s3_path = f"s3://realestate/{filename}"
    
    predictions = generate_mock_predictions()
    image_embedding = generate_mock_embedding(768, seed=hash(filename) % 2**32)
    text_embedding = generate_mock_embedding(1536, seed=hash(filename) % 2**32 + 1000)
    
    inference_time = timestamp or datetime.utcnow()
    model_version = f"model_v{random.randint(1, 3)}"
    
    return {
        "listing_id": listing_id,
        "filename": filename,
        "s3_path": s3_path,
        "thumb_path": f"s3://realestate/thumbs/{filename}",
        "embedding": image_embedding.tolist(),
        "text_embedding": text_embedding.tolist(),
        "predictions": predictions,
        "meta": {
            "source": model_version,
            "uploaded_at": inference_time.isoformat(),
            "width": random.randint(800, 1920),
            "height": random.randint(600, 1080),
            "file_size_kb": random.randint(100, 2000)
        },
        # New fields for expanded schema
        "model_version": model_version,
        "inference_timestamp": inference_time,
        "gradcam_path": f"s3://realestate/gradcams/{filename}",
        "sample_input_path": f"s3://realestate/samples/{filename}" if random.random() < 0.1 else None  # 10% sample rate
    }


def generate_mock_conversation(listing_id: Optional[int] = None, user_id: Optional[str] = None) -> Dict:
    """Generate mock conversation data."""
    return {
        "user_id": user_id or f"user_{random.randint(1000, 9999)}",
        "listing_id": listing_id,
        "created_at": datetime.utcnow() - timedelta(days=random.randint(0, 7))
    }


def generate_mock_message(conversation_id: int, role: str = "user", text: Optional[str] = None) -> Dict:
    """Generate mock message data."""
    user_messages = [
        "How can I increase resale value quickly?",
        "What improvements would you recommend for this kitchen?",
        "Is this property in good condition?",
        "What are the best features of this listing?",
        "How much would it cost to renovate the bathroom?",
        "What are the lighting issues in this room?",
        "Can you suggest staging ideas?",
        "What ROI can I expect from these improvements?",
    ]
    
    assistant_messages = [
        "Top 3 quick improvements: 1) Repaint kitchen cabinets (Medium cost, High ROI). 2) Replace dated hardware & fixtures (Low cost, Medium ROI). 3) Stage with a few potted plants & lighting (Low cost, Medium ROI).",
        "Based on the images, I recommend focusing on the kitchen with new cabinet hardware and fresh paint. The bathroom could benefit from updated fixtures.",
        "The property shows good overall condition with a score of 0.78. The kitchen and living areas are well-maintained, but the bathrooms could use some updates.",
        "Key features include hardwood floors, stainless steel appliances, and good natural lighting. The kitchen island is a standout feature.",
        "Estimated bathroom renovation costs: Low ($500-$1500) for fixtures and paint, Medium ($1500-$5000) for tile and vanity updates, High ($5000+) for full renovation.",
        "Natural light score is 0.61, which is moderate. Consider adding recessed lighting and removing heavy curtains to improve brightness.",
        "For staging, I suggest: 1) Add plants and fresh flowers, 2) Use neutral color palette, 3) Improve lighting with lamps, 4) Declutter and organize spaces.",
        "Expected ROI: Kitchen improvements (High ROI), Bathroom updates (Medium ROI), Lighting enhancements (Medium ROI), Cosmetic updates (High ROI)."
    ]
    
    if text is None:
        if role == "user":
            text = random.choice(user_messages)
        else:
            text = random.choice(assistant_messages)
    
    message_embedding = generate_mock_embedding(1536, seed=hash(text) % 2**32)
    
    return {
        "conversation_id": conversation_id,
        "role": role,
        "text": text,
        "embedding": message_embedding.tolist(),
        "created_at": datetime.utcnow() - timedelta(hours=random.randint(0, 24))
    }


def generate_mock_conversation_with_messages(
    conversation_id: int,
    num_messages: int = 4,
    listing_id: Optional[int] = None
) -> List[Dict]:
    """Generate a conversation with alternating user/assistant messages."""
    messages = []
    for i in range(num_messages):
        role = "user" if i % 2 == 0 else "assistant"
        message = generate_mock_message(conversation_id, role)
        # Add performance metrics for assistant messages
        if role == "assistant":
            message["embedding_latency_ms"] = round(random.uniform(50, 200), 2)
            message["retrieval_latency_ms"] = round(random.uniform(10, 50), 2)
            message["llm_latency_ms"] = round(random.uniform(500, 2000), 2)
        messages.append(message)
    return messages


def generate_mock_property_aggregation(listing_id: int, room_counts: Optional[Dict] = None) -> Dict:
    """Generate property-level aggregation data."""
    if room_counts is None:
        room_counts = {
            "kitchen": random.randint(1, 3),
            "bathroom": random.randint(1, 4),
            "bedroom": random.randint(2, 5),
            "living_room": random.randint(1, 2),
            "dining_room": random.randint(0, 1)
        }
    
    total_images = sum(room_counts.values())
    dominant_room = max(room_counts.items(), key=lambda x: x[1])[0] if room_counts else None
    
    styles = ["modern", "traditional", "contemporary", "rustic"]
    localizations = ["urban", "suburban", "rural"]
    
    return {
        "listing_id": listing_id,
        "overall_condition_score": round(random.uniform(0.6, 0.95), 2),
        "avg_natural_light_score": round(random.uniform(0.5, 0.9), 2),
        "room_counts": room_counts,
        "dominant_room_type": dominant_room,
        "common_features": ["hardwood_floors", "recessed_lighting", "updated_plumbing"],
        "dominant_style": random.choice(styles),
        "style_distribution": {s: random.random() for s in styles},
        "primary_localization": random.choice(localizations),
        "localization_distribution": {l: random.random() for l in localizations},
        "total_images": total_images,
        "last_calculated_at": datetime.utcnow(),
        "calculation_version": "v1.0"
    }


def generate_mock_temporal_change(listing_id: int, image_id: int, previous_image_id: Optional[int] = None) -> Dict:
    """Generate temporal change detection data."""
    change_types = ["condition", "natural_light", "feature", "style"]
    change_type = random.choice(change_types)
    
    previous_value = round(random.uniform(0.5, 0.9), 2)
    current_value = round(random.uniform(0.4, 0.95), 2)
    change_magnitude = abs(current_value - previous_value)
    
    if current_value > previous_value:
        change_direction = "improved"
    elif current_value < previous_value:
        change_direction = "degraded"
    else:
        change_direction = "stable"
    
    return {
        "listing_id": listing_id,
        "image_id": image_id,
        "change_type": change_type,
        "change_magnitude": round(change_magnitude, 3),
        "change_direction": change_direction,
        "previous_value": previous_value,
        "current_value": current_value,
        "previous_image_id": previous_image_id,
        "time_delta_days": random.randint(1, 365),
        "model_version": f"model_v{random.randint(1, 3)}",
        "flagged_for_review": change_magnitude > 0.2  # Flag significant changes
    }


def generate_mock_drift_detection(model_version: str = "model_v1") -> Dict:
    """Generate model drift detection data."""
    metric_names = [
        "natural_light_good_ratio",
        "condition_excellent_ratio",
        "kitchen_detection_rate",
        "feature_detection_accuracy"
    ]
    
    metric_name = random.choice(metric_names)
    baseline_mean = round(random.uniform(0.5, 0.9), 3)
    current_mean = baseline_mean + random.uniform(-0.2, 0.2)
    
    drift_score = abs(current_mean - baseline_mean) / baseline_mean if baseline_mean > 0 else 0
    drift_detected = drift_score > 0.15  # Threshold for drift
    
    return {
        "detection_date": datetime.utcnow(),
        "model_version": model_version,
        "metric_name": metric_name,
        "baseline_mean": baseline_mean,
        "baseline_std": round(random.uniform(0.05, 0.15), 3),
        "current_mean": round(current_mean, 3),
        "current_std": round(random.uniform(0.05, 0.15), 3),
        "drift_score": round(drift_score, 4),
        "drift_magnitude": round(abs(current_mean - baseline_mean), 3),
        "drift_detected": drift_detected,
        "alert_sent": drift_detected,
        "alert_threshold": 0.15,
        "sample_size": random.randint(100, 1000),
        "window_start": datetime.utcnow() - timedelta(days=30),
        "window_end": datetime.utcnow()
    }


def generate_mock_model_metrics(model_version: str = "model_v1", head_name: str = "room_type") -> Dict:
    """Generate per-head model metrics."""
    class_names = {
        "room_type": ["kitchen", "bathroom", "bedroom", "living_room"],
        "condition": ["excellent", "good", "fair", "poor"],
        "features": ["hardwood_floors", "island", "fireplace"]
    }
    
    class_name = random.choice(class_names.get(head_name, ["unknown"])) if head_name in class_names else None
    
    precision = round(random.uniform(0.7, 0.95), 3)
    recall = round(random.uniform(0.7, 0.95), 3)
    f1_score = round(2 * (precision * recall) / (precision + recall), 3) if (precision + recall) > 0 else 0
    mAP = round(random.uniform(0.75, 0.95), 3)
    
    tp = random.randint(50, 200)
    fp = random.randint(5, 30)
    fn = random.randint(5, 30)
    tn = random.randint(100, 500)
    
    return {
        "model_version": model_version,
        "head_name": head_name,
        "class_name": class_name,
        "precision": precision,
        "recall": recall,
        "f1_score": f1_score,
        "mAP": mAP,
        "validation_set_size": random.randint(500, 2000),
        "evaluation_date": datetime.utcnow(),
        "evaluation_split": random.choice(["validation", "test", "rolling"]),
        "window_start": datetime.utcnow() - timedelta(days=7),
        "window_end": datetime.utcnow(),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn
    }


def generate_mock_performance_log(operation_type: str = "inference") -> Dict:
    """Generate performance log entry."""
    latency_ranges = {
        "embedding": (50, 300),
        "retrieval": (10, 100),
        "llm": (500, 3000),
        "inference": (100, 500)
    }
    
    low, high = latency_ranges.get(operation_type, (100, 1000))
    latency_ms = round(random.uniform(low, high), 2)
    
    return {
        "operation_type": operation_type,
        "operation_name": f"{operation_type}_operation",
        "latency_ms": latency_ms,
        "p50_latency_ms": round(latency_ms * 0.8, 2),
        "p95_latency_ms": round(latency_ms * 1.5, 2),
        "p99_latency_ms": round(latency_ms * 2.0, 2),
        "cpu_usage_percent": round(random.uniform(20, 80), 2),
        "memory_usage_mb": round(random.uniform(500, 2000), 2),
        "gpu_usage_percent": round(random.uniform(30, 90), 2) if operation_type == "inference" else None,
        "image_id": random.randint(1, 1000),
        "listing_id": random.randint(1, 100),
        "model_version": f"model_v{random.randint(1, 3)}",
        "service_name": f"{operation_type}_service",
        "success": random.random() > 0.05,  # 95% success rate
        "error_message": None if random.random() > 0.05 else "Sample error message",
        "started_at": datetime.utcnow() - timedelta(seconds=latency_ms/1000),
        "completed_at": datetime.utcnow()
    }


def generate_mock_audit_sample(image_id: int, listing_id: Optional[int] = None) -> Dict:
    """Generate audit sample entry."""
    sample_types = ["gradcam", "input", "output", "error_case"]
    priorities = ["high", "medium", "low"]
    audit_statuses = ["pending", "reviewed", "resolved"]
    
    sample_type = random.choice(sample_types)
    priority = random.choice(priorities)
    
    return {
        "image_id": image_id,
        "listing_id": listing_id,
        "sample_type": sample_type,
        "sample_reason": f"Random sampling for {sample_type}",
        "priority": priority,
        "original_image_path": f"s3://realestate/images/{image_id}.jpg",
        "gradcam_path": f"s3://realestate/gradcams/{image_id}.jpg" if sample_type == "gradcam" else None,
        "sample_input_path": f"s3://realestate/samples/input/{image_id}.jpg",
        "sample_output_path": f"s3://realestate/samples/output/{image_id}.json",
        "predictions_snapshot": generate_mock_predictions(),
        "model_version": f"model_v{random.randint(1, 3)}",
        "audit_status": random.choice(audit_statuses),
        "reviewed_by": f"reviewer_{random.randint(1, 10)}" if random.random() > 0.5 else None,
        "reviewed_at": datetime.utcnow() - timedelta(days=random.randint(0, 7)) if random.random() > 0.5 else None,
        "review_notes": "Sample review notes" if random.random() > 0.5 else None,
        "flagged_for_review": priority == "high" or random.random() < 0.2
    }

