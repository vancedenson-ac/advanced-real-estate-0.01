"""Property-level aggregation service."""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Optional
from datetime import datetime
from ..database import (
    Image, ImageLabel, Listing, PropertyAggregation
)
import json


def calculate_property_aggregation(db: Session, listing_id: int) -> Dict:
    """
    Calculate property-level aggregation from per-image outputs.
    
    Returns:
        Aggregation data dictionary
    """
    # Get all images for this listing
    images = db.query(Image).filter(Image.listing_id == listing_id).all()
    image_ids = [img.id for img in images]
    
    if not image_ids:
        return None
    
    # Get all labels for these images
    labels = db.query(ImageLabel).filter(ImageLabel.image_id.in_(image_ids)).all()
    
    if not labels:
        return None
    
    # Calculate aggregated scores
    condition_scores = [l.condition_score for l in labels if l.condition_score is not None]
    light_scores = [l.natural_light_score for l in labels if l.natural_light_score is not None]
    
    overall_condition_score = sum(condition_scores) / len(condition_scores) if condition_scores else None
    avg_natural_light_score = sum(light_scores) / len(light_scores) if light_scores else None
    
    # Count room types
    room_counts = {}
    for label in labels:
        if label.room_type:
            room_counts[label.room_type] = room_counts.get(label.room_type, 0) + 1
    
    dominant_room_type = max(room_counts.items(), key=lambda x: x[1])[0] if room_counts else None
    
    # Aggregate features
    all_features = []
    for label in labels:
        if label.features:
            all_features.extend(label.features if isinstance(label.features, list) else [])
    
    # Count feature frequency
    feature_counts = {}
    for feature in all_features:
        feature_counts[feature] = feature_counts.get(feature, 0) + 1
    
    # Get most common features
    common_features = sorted(feature_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    common_features = [f[0] for f in common_features]
    
    # Aggregate styles
    style_counts = {}
    for label in labels:
        if label.style:
            style_counts[label.style] = style_counts.get(label.style, 0) + 1
    
    dominant_style = max(style_counts.items(), key=lambda x: x[1])[0] if style_counts else None
    
    # Calculate style distribution
    total_styles = sum(style_counts.values()) if style_counts else 1
    style_distribution = {style: count / total_styles for style, count in style_counts.items()}
    
    # Aggregate localizations
    localization_counts = {}
    for label in labels:
        if label.localization:
            localization_counts[label.localization] = localization_counts.get(label.localization, 0) + 1
    
    primary_localization = max(localization_counts.items(), key=lambda x: x[1])[0] if localization_counts else None
    
    # Calculate localization distribution
    total_localizations = sum(localization_counts.values()) if localization_counts else 1
    localization_distribution = {loc: count / total_localizations for loc, count in localization_counts.items()}
    
    return {
        "listing_id": listing_id,
        "overall_condition_score": round(overall_condition_score, 3) if overall_condition_score else None,
        "avg_natural_light_score": round(avg_natural_light_score, 3) if avg_natural_light_score else None,
        "room_counts": room_counts,
        "dominant_room_type": dominant_room_type,
        "common_features": common_features,
        "dominant_style": dominant_style,
        "style_distribution": style_distribution,
        "primary_localization": primary_localization,
        "localization_distribution": localization_distribution,
        "total_images": len(images),
        "last_calculated_at": datetime.utcnow(),
        "calculation_version": "v1.0"
    }


def update_property_aggregation(db: Session, listing_id: int) -> Optional[int]:
    """
    Calculate and update property aggregation.
    
    Returns:
        aggregation_id
    """
    agg_data = calculate_property_aggregation(db, listing_id)
    if not agg_data:
        return None
    
    # Check if aggregation exists
    existing = db.query(PropertyAggregation).filter(
        PropertyAggregation.listing_id == listing_id
    ).first()
    
    if existing:
        # Update existing
        for key, value in agg_data.items():
            if key != "listing_id":
                setattr(existing, key, value)
        existing.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        return existing.id
    else:
        # Create new
        aggregation = PropertyAggregation(**agg_data)
        db.add(aggregation)
        db.commit()
        db.refresh(aggregation)
        
        # Update listing with aggregated data
        listing = db.query(Listing).filter(Listing.id == listing_id).first()
        if listing:
            listing.dominant_room_types = json.dumps([agg_data["dominant_room_type"]] if agg_data["dominant_room_type"] else [])
            listing.overall_condition_score = agg_data["overall_condition_score"]
            listing.room_counts = json.dumps(agg_data["room_counts"])
            listing.total_images = agg_data["total_images"]
            db.commit()
        
        return aggregation.id

