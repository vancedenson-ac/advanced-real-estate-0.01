# Architecture Expansion Documentation

Comprehensive expansion of the Real Estate AI Platform to support advanced image intelligence features.

## Overview

This document describes the expanded architecture to support a truly comprehensive real estate image intelligence system with:

- Enhanced scene classification (room type, style, localization)
- Property condition inference
- Work recommendations and cost estimates
- Home price prediction
- Temporal change detection
- Property-level aggregation
- Model drift detection
- Performance monitoring
- Audit and compliance tracking

## Expanded Database Schema

### Core Tables (Enhanced)

#### `listings`
**New Fields:**
- `estimated_price` - AI-predicted home price
- `price_confidence` - Confidence in price estimate
- `city`, `state`, `country` - Location details
- `latitude`, `longitude` - GPS coordinates
- `dominant_room_types` - Aggregated room type data
- `overall_condition_score` - Property-level condition
- `room_counts` - Count of each room type
- `total_images` - Total images for property

#### `image_labels`
**New Fields:**
- `localization` - Region/area identification
- `localization_confidence` - Confidence in localization
- `style` - Architectural/style classification
- `style_confidence` - Confidence in style
- `work_recommendations` - JSON array of recommended improvements
- `cost_estimates` - JSON array of cost estimates per recommendation
- `model_version` - Model version used
- `inference_timestamp` - When inference was run
- `gradcam_path` - Path to GradCAM visualization
- `sample_input_path` - Path to sample input for audit

#### `messages`
**New Fields:**
- `embedding_latency_ms` - Time to generate embedding
- `retrieval_latency_ms` - Time for vector search
- `llm_latency_ms` - Time for LLM call

### New Tables

#### `property_aggregations`
Property-level aggregation of image outputs.

**Fields:**
- `listing_id` - Reference to listing
- `overall_condition_score` - Average condition across images
- `avg_natural_light_score` - Average light score
- `room_counts` - JSON count of each room type
- `dominant_room_type` - Most common room type
- `common_features` - Most common features
- `dominant_style` - Most common style
- `style_distribution` - Style distribution
- `primary_localization` - Most common localization
- `localization_distribution` - Localization distribution
- `total_images` - Total images aggregated
- `last_calculated_at` - Last calculation timestamp
- `calculation_version` - Algorithm version

#### `temporal_changes`
Track changes in property condition over time.

**Fields:**
- `listing_id`, `image_id` - Property and image references
- `change_type` - Type of change (condition, light, feature, style)
- `change_magnitude` - Absolute change value
- `change_direction` - improved/degraded/stable
- `previous_value`, `current_value` - Values being compared
- `previous_image_id` - Previous image for comparison
- `time_delta_days` - Days between images
- `detected_at` - When change was detected
- `model_version` - Model version used
- `flagged_for_review` - Flag for manual review

#### `model_drift_detection`
Track distribution shifts in model outputs.

**Fields:**
- `detection_date` - When drift was detected
- `model_version` - Model version
- `metric_name` - Metric being tracked (e.g., "natural_light_good_ratio")
- `baseline_mean`, `baseline_std` - Baseline distribution
- `current_mean`, `current_std` - Current distribution
- `drift_score` - Statistical test score (KS, PSI, etc.)
- `drift_magnitude` - Effect size
- `drift_detected` - Boolean flag
- `alert_sent` - Whether alert was sent
- `alert_threshold` - Threshold for alerts
- `sample_size` - Sample size used
- `window_start`, `window_end` - Time window

#### `model_metrics`
Per-head metrics for model evaluation.

**Fields:**
- `model_version` - Model version
- `head_name` - Head name (room_type, condition, features, etc.)
- `class_name` - Specific class for multi-class heads
- `precision`, `recall`, `f1_score`, `mAP` - Metrics
- `validation_set_size` - Size of validation set
- `evaluation_date` - When evaluated
- `evaluation_split` - validation/test/rolling
- `window_start`, `window_end` - Time window for rolling metrics
- `true_positives`, `false_positives`, `false_negatives`, `true_negatives` - Confusion matrix

#### `performance_logs`
Log latencies and performance metrics.

**Fields:**
- `operation_type` - embedding/retrieval/llm/inference
- `operation_name` - Specific operation
- `latency_ms` - Operation latency
- `p50_latency_ms`, `p95_latency_ms`, `p99_latency_ms` - Percentiles
- `cpu_usage_percent`, `memory_usage_mb`, `gpu_usage_percent` - Resource usage
- `image_id`, `listing_id`, `conversation_id` - Context
- `model_version`, `service_name` - Service metadata
- `success` - Success/failure flag
- `error_message` - Error details if failed
- `started_at`, `completed_at` - Timestamps

#### `audit_samples`
Record sample inputs and GradCAMs for manual audits.

**Fields:**
- `image_id`, `listing_id` - References
- `sample_type` - gradcam/input/output/error_case
- `sample_reason` - Why sample was selected
- `priority` - high/medium/low
- `original_image_path`, `gradcam_path`, `sample_input_path`, `sample_output_path` - File paths
- `predictions_snapshot` - Model predictions at time of sampling
- `model_version` - Model version
- `audit_status` - pending/reviewed/resolved
- `reviewed_by`, `reviewed_at`, `review_notes` - Review details
- `flagged_for_review` - Flag for review

## Mock Data Generators

### Enhanced Generators

#### `generate_mock_predictions()`
Now includes:
- `localization` - Region identification
- `style` - Architectural style
- `work_recommendations` - Improvement recommendations
- `cost_estimates` - Cost estimates per recommendation

#### `generate_mock_listing()`
Now includes:
- `estimated_price` - AI-predicted price
- `price_confidence` - Confidence score
- `city`, `state`, `country` - Location details
- `latitude`, `longitude` - GPS coordinates

#### `generate_mock_image_data()`
Now includes:
- `model_version` - Model version
- `inference_timestamp` - Inference time
- `gradcam_path` - GradCAM visualization path
- `sample_input_path` - Sample input path

### New Generators

- `generate_mock_property_aggregation()` - Property-level aggregations
- `generate_mock_temporal_change()` - Temporal change detection
- `generate_mock_drift_detection()` - Model drift detection
- `generate_mock_model_metrics()` - Per-head model metrics
- `generate_mock_performance_log()` - Performance logging
- `generate_mock_audit_sample()` - Audit samples

## Expanded Seed Functions

### New Seed Functions

- `seed_property_aggregations()` - Seed property aggregations
- `seed_temporal_changes()` - Seed temporal change records
- `seed_drift_detection()` - Seed drift detection records
- `seed_model_metrics()` - Seed model metrics
- `seed_performance_logs()` - Seed performance logs
- `seed_audit_samples()` - Seed audit samples

### Enhanced `seed_all()`
Now seeds all new features automatically.

## Feature Capabilities

### 1. Scene Classification

**Room Type:**
- Classification: kitchen, bathroom, bedroom, living_room, dining_room, office, hallway, basement
- Confidence scores per room type
- Property-level aggregation (dominant room types, counts)

**Style:**
- Architectural styles: modern, traditional, contemporary, rustic, minimalist, industrial, colonial, mediterranean
- Style distribution across property
- Style confidence scores

**Localization:**
- Region/area identification: urban, suburban, rural, coastal, mountain, desert
- Localization distribution
- Geographic context

### 2. Property Condition

**Condition Assessment:**
- Per-image condition scores
- Property-level aggregated condition
- Temporal change tracking
- Condition trends over time

**Natural Light:**
- Per-image light scores
- Average light score per property
- Light improvement recommendations

### 3. Feature Detection

**Feature Presence:**
- Comprehensive feature tags
- Feature frequency analysis
- Common features per property
- Feature-based recommendations

### 4. Work Recommendations & Cost Estimates

**Recommendations:**
- Type: paint, renovate, repair, upgrade, replace
- Priority: high, medium, low
- Estimated ROI
- Description and details

**Cost Estimates:**
- Low/high estimate ranges
- Currency support
- Per-recommendation costs
- Total property improvement costs

### 5. Home Price Prediction

**Price Estimation:**
- AI-predicted price
- Confidence scores
- Comparison with listed price
- Price factors (condition, features, location)

### 6. Temporal Change Detection

**Change Tracking:**
- Condition changes over time
- Light improvement/degradation
- Feature additions/removals
- Style changes
- Automatic flagging of significant changes

### 7. Property-Level Aggregation

**Aggregation Model:**
- Ingests per-image outputs
- Produces final property metadata
- Room type counts and distributions
- Overall condition scores
- Feature aggregations
- Style and localization distributions

### 8. Model Drift Detection

**Distribution Tracking:**
- Track per-image model outputs distribution
- Alert on data distribution shift
- Metrics: natural_light_good_ratio, condition_excellent_ratio, etc.
- Statistical tests (KS, PSI)
- Automated alerting

### 9. Audit & Compliance

**Sample Recording:**
- Record sample inputs for manual audits
- GradCAM visualization storage
- Error case tracking
- Review workflow (pending/reviewed/resolved)
- Priority-based sampling

### 10. Model Evaluation

**Per-Head Metrics:**
- Per-class precision, recall, mAP
- Rolling validation set evaluation
- Confusion matrix tracking
- Performance trends over time

### 11. Performance Monitoring

**Latency Logging:**
- Embedding creation latency
- Vector retrieval latency
- LLM call latency
- Inference latency
- Resource usage (CPU, memory, GPU)
- Percentile tracking (p50, p95, p99)

## Model Architecture

### Multi-Head Design

Each task has its own head but shares a unified visual backbone:

```
Visual Backbone (ViT/CLIP)
    ├── Room Type Head
    ├── Condition Head
    ├── Feature Detection Head
    ├── Natural Light Head
    ├── Localization Head
    ├── Style Head
    └── Price Estimation Head
```

**Benefits:**
- Modularity: Each task independent
- Scalability: Easy to add new heads
- Transfer Learning: Shared backbone enables efficient learning
- Performance: Optimized for each task

## Workflow

### 1. Image Upload & Inference

```
Image Upload
    ↓
S3 Storage
    ↓
Model Inference (Multi-Head)
    ↓
Per-Image Predictions
    ↓
Database Storage (image_labels)
    ↓
Property Aggregation Update
```

### 2. Temporal Change Detection

```
New Image Upload
    ↓
Retrieve Previous Images
    ↓
Compare Predictions
    ↓
Detect Changes
    ↓
Flag Significant Changes
    ↓
Store Temporal Change Record
```

### 3. Drift Detection

```
Daily/Weekly Batch
    ↓
Calculate Distribution Metrics
    ↓
Compare with Baseline
    ↓
Statistical Test (KS/PSI)
    ↓
Detect Drift
    ↓
Alert if Threshold Exceeded
    ↓
Store Drift Detection Record
```

### 4. Model Evaluation

```
Rolling Validation Set
    ↓
Evaluate Per-Head Performance
    ↓
Calculate Metrics (Precision, Recall, mAP)
    ↓
Store Model Metrics
    ↓
Track Performance Trends
```

### 5. Performance Monitoring

```
Each Operation
    ↓
Start Timer
    ↓
Execute Operation
    ↓
End Timer
    ↓
Log Latency & Resources
    ↓
Store Performance Log
```

## Testing

### Test Coverage

- `test_expanded_features.py` - Tests for all new features
- Property aggregation tests
- Temporal change detection tests
- Drift detection tests
- Model metrics tests
- Performance logging tests
- Audit sample tests

### Test Data

All new features have comprehensive mock data generators for testing.

## Migration Guide

### Database Migration

1. **Backup existing database:**
```bash
docker exec realestate-db pg_dump -U postgres realestate > backup.sql
```

2. **Run migration:**
```bash
docker-compose exec backend python init_db.py
```

3. **Seed with expanded data:**
```bash
docker-compose exec backend python seed_db.py
```

### Code Migration

1. **Update model inference:**
   - Return expanded predictions (localization, style, recommendations)
   - Include model version and timestamps
   - Generate GradCAMs for audit samples

2. **Update aggregation service:**
   - Implement property-level aggregation logic
   - Update listings with aggregated data

3. **Update temporal tracking:**
   - Implement change detection logic
   - Flag significant changes

4. **Update drift detection:**
   - Implement distribution tracking
   - Add statistical tests
   - Set up alerting

5. **Update performance logging:**
   - Add latency tracking to all operations
   - Log resource usage
   - Store performance logs

## Next Steps

1. **Model Training:**
   - Train multi-head model with all heads
   - Fine-tune on real estate data
   - Validate per-head performance

2. **Aggregation Implementation:**
   - Implement aggregation algorithms
   - Update listings on image upload
   - Schedule periodic recalculation

3. **Temporal Tracking:**
   - Implement change detection algorithms
   - Set up automated flagging
   - Create review workflow

4. **Drift Detection:**
   - Implement statistical tests
   - Set up baseline distributions
   - Configure alert thresholds

5. **Performance Monitoring:**
   - Add latency tracking to all endpoints
   - Set up dashboards
   - Configure alerts

6. **Audit System:**
   - Implement sampling logic
   - Set up review interface
   - Create audit workflows

## Related Documentation

- [README.md](README.md) - Main documentation
- [README-backend.md](README-backend.md) - Backend documentation
- [README-tests.md](README-tests.md) - Testing documentation

