# Seed Data Guide

Quick guide for populating the database with mock data to view UI components.

## Quick Seed

### Using Make (Recommended)
```bash
make seed
```

### Using Docker
```bash
docker-compose exec backend python seed_db.py
```

### Direct Python
```bash
cd backend
python seed_db.py
```

## What Gets Seeded

The seed script creates comprehensive mock data for all tables:

### Core Data
- **5 Listings** - Properties with addresses, prices, locations
- **15 Images** - 3 images per listing with full predictions
- **10 Conversations** - 2 conversations per listing
- **40+ Messages** - 4-8 messages per conversation

### Expanded Features
- **5 Property Aggregations** - Property-level metadata
- **Temporal Changes** - Condition changes over time
- **5 Drift Detection Records** - Model drift alerts
- **10 Model Metrics** - Per-head performance metrics
- **20 Performance Logs** - Latency tracking
- **Audit Samples** - Sample inputs and GradCAMs (10% of images)

## Seed Function Details

### `seed_db.py`
Main entry point that:
1. Initializes database (creates tables)
2. Seeds all mock data
3. Prints summary of created records

### `seed_all()` Function
Located in `backend/app/fixtures/seed_data.py`, this function:

```python
seed_all(
    db=db_session,
    num_listings=5,           # Number of listings to create
    images_per_listing=3,     # Images per listing
    conversations_per_listing=2  # Conversations per listing
)
```

## Customizing Seed Data

### Change Amounts
Edit `backend/seed_db.py`:

```python
seed_all(db, num_listings=10, images_per_listing=5, conversations_per_listing=3)
```

### Programmatic Seeding
```python
from app.database import SessionLocal
from app.fixtures.seed_data import seed_all

db = SessionLocal()
result = seed_all(
    db, 
    num_listings=10,
    images_per_listing=5,
    conversations_per_listing=3
)
print(f"Created {result['listing_ids']} listings")
db.close()
```

## Data Structure

### Listings
Each listing includes:
- Address, city, state, zip code
- Listed price and AI-estimated price
- GPS coordinates (latitude/longitude)
- Property aggregations (room counts, condition scores)

### Images
Each image includes:
- Room type classification (kitchen, bathroom, etc.)
- Condition score (0-1)
- Natural light score (0-1)
- Feature tags (hardwood_floors, island, etc.)
- **NEW**: Localization, style, work recommendations, cost estimates
- Embeddings (image and text)
- Model metadata (version, timestamps, GradCAM paths)

### Conversations
Each conversation includes:
- User and assistant messages
- Message embeddings
- Performance latencies (embedding, retrieval, LLM)
- Conversation history

### Property Aggregations
Each aggregation includes:
- Overall condition score
- Average natural light score
- Room type counts
- Dominant room type
- Common features
- Style and localization distributions

## Viewing in UI

After seeding, you can view data in:

### Frontend (React)
- **Home Page**: Upload images, view image grid with predictions
- **Insights Page**: Analytics dashboard with property statistics
- **Chat Panel**: RAG chat with property context

### API Endpoints
- `GET /api/images/{image_id}` - View image with all predictions
- `POST /api/query/` - Search images by text query
- `POST /api/chat/` - Chat with RAG assistant
- `GET /api/conversations/{id}/messages` - View conversation history

### Gradio Interface
- Upload images
- Query similar images
- Test chat functionality
- View image metadata

## Verification

### Check Seed Success
```bash
# Using psql
docker-compose exec db psql -U postgres -d realestate -c "SELECT COUNT(*) FROM listings;"
docker-compose exec db psql -U postgres -d realestate -c "SELECT COUNT(*) FROM images;"
docker-compose exec db psql -U postgres -d realestate -c "SELECT COUNT(*) FROM conversations;"
```

### Expected Counts
After default seed:
- Listings: 5
- Images: 15 (3 per listing)
- Image Labels: 15 (one per image)
- Conversations: 10 (2 per listing)
- Messages: ~40-80 (4-8 per conversation)
- Property Aggregations: 5
- Temporal Changes: ~2-5
- Drift Detection: 5
- Model Metrics: 10
- Performance Logs: 20
- Audit Samples: ~1-2 (10% of images)

## Troubleshooting

### Database Not Initialized
```bash
# Initialize first
docker-compose exec backend python init_db.py
# Then seed
docker-compose exec backend python seed_db.py
```

### Seed Fails
```bash
# Check database connection
docker-compose logs db

# Check backend logs
docker-compose logs backend

# Try reinitializing
docker-compose exec backend python init_db.py
docker-compose exec backend python seed_db.py
```

### No Data in UI
1. Verify seed completed successfully
2. Check API is running: `curl http://localhost:8000/api/health`
3. Check frontend can connect to API
4. Verify database has data (see verification above)

## Resetting Data

### Clear All Data
```bash
# Stop services
docker-compose down

# Remove volumes (deletes all data)
docker-compose down -v

# Restart and re-seed
docker-compose up -d
docker-compose exec backend python init_db.py
docker-compose exec backend python seed_db.py
```

### Clear Specific Tables
```bash
# Using psql
docker-compose exec db psql -U postgres -d realestate -c "TRUNCATE TABLE images CASCADE;"
docker-compose exec db psql -U postgres -d realestate -c "TRUNCATE TABLE listings CASCADE;"
# Then re-seed
docker-compose exec backend python seed_db.py
```

## Advanced Seeding

### Seed Specific Features Only
```python
from app.database import SessionLocal
from app.fixtures.seed_data import (
    seed_listings, seed_images, seed_property_aggregations
)

db = SessionLocal()
listing_ids = seed_listings(db, count=10)
image_ids = seed_images(db, listing_ids, images_per_listing=5)
seed_property_aggregations(db, listing_ids)
db.close()
```

### Seed with Specific Data
```python
from app.database import SessionLocal, Listing
from app.fixtures.mock_data import generate_mock_listing

db = SessionLocal()
# Create custom listing
listing_data = generate_mock_listing()
listing_data["address"] = "123 Custom St, New York, NY"
listing_data["price"] = 500000.0
listing = Listing(**listing_data)
db.add(listing)
db.commit()
db.close()
```

## Related Files

- `backend/seed_db.py` - Main seed script
- `backend/app/fixtures/seed_data.py` - Seed functions
- `backend/app/fixtures/mock_data.py` - Mock data generators
- `backend/app/database.py` - Database models

## Quick Reference

```bash
# Full workflow: Start → Initialize → Seed
make start          # Starts services and initializes DB
make seed           # Seeds mock data

# Or manually:
docker-compose up -d
docker-compose exec backend python init_db.py
docker-compose exec backend python seed_db.py
```

