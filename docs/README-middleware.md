# Middleware Documentation

Infrastructure components, services, and data storage systems that power the Real Estate AI Platform.

## Overview

The middleware layer consists of:
- **PostgreSQL + pgvector**: Primary database with vector search capabilities
- **Redis**: Message broker and cache
- **MinIO**: S3-compatible object storage
- **Celery**: Distributed task queue
- **Model Service**: ML inference service (containerized)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Middleware Services                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  PostgreSQL  │  │    Redis     │  │    MinIO     │       │
│  │  + pgvector  │  │  (Broker)    │  │  (S3 Store)  │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│         │                │                │                   │
│         └────────────────┼────────────────┘                   │
│                          │                                   │
│         ┌────────────────▼────────────────┐                  │
│         │      Celery Workers             │                  │
│         │  (Background Processing)         │                  │
│         └─────────────────────────────────┘                  │
│                          │                                   │
│         ┌────────────────▼────────────────┐                  │
│         │      Model Service              │                  │
│         │  (CV Inference Container)       │                  │
│         └─────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## PostgreSQL + pgvector

### Purpose

Primary database storing:
- Property listings
- Image metadata and embeddings
- Conversation history
- Vector embeddings for similarity search

### Setup

1. **Use pgvector image:**
```bash
docker run -d \
  --name realestate-db \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=realestate \
  -p 5432:5432 \
  ankane/pgvector:latest
```

2. **Initialize database:**
```bash
docker exec -it realestate-db psql -U postgres -d realestate
CREATE EXTENSION vector;
```

3. **Create tables:**
```bash
python backend/init_db.py
```

### Schema

See [backend/app/database.py](backend/app/database.py) for full schema.

Key tables:
- `listings`: Property listings
- `images`: Image records with embeddings
- `image_labels`: Predictions (room type, condition, features)
- `conversations`: Chat conversations
- `messages`: Conversation messages with embeddings
- `embeddings_index`: Unified embedding index

### Vector Operations

#### Create Vector Index

```sql
CREATE INDEX ON images USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

#### Similarity Search

```sql
-- Cosine similarity
SELECT id, 1 - (embedding <#> '[0.1, 0.2, ...]') as similarity
FROM images
ORDER BY embedding <#> '[0.1, 0.2, ...]'
LIMIT 10;

-- Euclidean distance
SELECT id, embedding <-> '[0.1, 0.2, ...]' as distance
FROM images
ORDER BY embedding <-> '[0.1, 0.2, ...]'
LIMIT 10;
```

### Performance Tuning

- **Index Creation**: Use IVFFlat or HNSW indexes for vector search
- **Connection Pooling**: Configure SQLAlchemy pool size
- **Query Optimization**: Use EXPLAIN ANALYZE for slow queries
- **Partitioning**: Consider table partitioning for large datasets

### Backup & Recovery

```bash
# Backup
docker exec realestate-db pg_dump -U postgres realestate > backup.sql

# Restore
docker exec -i realestate-db psql -U postgres realestate < backup.sql
```

## Redis

### Purpose

- **Celery Broker**: Task queue for background jobs
- **Result Backend**: Store Celery task results
- **Cache**: (Future) Cache frequently accessed data

### Setup

```bash
docker run -d \
  --name realestate-redis \
  -p 6379:6379 \
  redis:7-alpine
```

### Configuration

```python
# Celery configuration
CELERY_BROKER_URL = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
```

### Monitoring

```bash
# Connect to Redis CLI
docker exec -it realestate-redis redis-cli

# Monitor commands
MONITOR
INFO stats
KEYS *
```

### Persistence

Redis is configured with persistence:

```bash
# Save to disk
BGSAVE

# Check persistence
CONFIG GET save
```

## MinIO (S3-Compatible Storage)

### Purpose

Object storage for:
- Original uploaded images
- Processed thumbnails
- Generated artifacts

### Setup

```bash
docker run -d \
  --name realestate-minio \
  -p 9000:9000 \
  -p 9001:9001 \
  -e MINIO_ROOT_USER=minio \
  -e MINIO_ROOT_PASSWORD=minio123 \
  minio/minio server /data --console-address ":9001"
```

### Access

- **API**: http://localhost:9000
- **Console**: http://localhost:9001
- **Credentials**: minio / minio123

### Bucket Configuration

1. **Create bucket:**
   - Via console: http://localhost:9001
   - Or via API/boto3

2. **Set bucket policy** (for public access if needed):
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"AWS": ["*"]},
      "Action": ["s3:GetObject"],
      "Resource": ["arn:aws:s3:::realestate/*"]
    }
  ]
}
```

### Presigned URLs

Generate temporary access URLs:

```python
from app.services.s3_utils import get_presigned_url

url = get_presigned_url("s3://realestate/image.jpg", expiration=3600)
```

### Data Migration

```bash
# Copy from local to MinIO
mc alias set myminio http://localhost:9000 minio minio123
mc cp /local/path myminio/realestate/
```

## Celery

### Purpose

Distributed task queue for:
- Async image processing
- Background inference
- Email notifications (future)
- Scheduled tasks (future)

### Setup

1. **Start Redis** (broker)

2. **Start Celery worker:**
```bash
celery -A app.workers.celery worker \
  --loglevel=INFO \
  --concurrency=4
```

3. **Monitor with Flower (optional):**
```bash
pip install flower
celery -A app.workers.celery flower
```

### Task Definition

```python
@celery.task(name="process_image_s3")
def process_image_s3(s3_bucket, s3_key, filename, listing_id=None):
    # Process image
    # Return result
    pass
```

### Task Status

- **PENDING**: Task queued
- **PROGRESS**: Task processing
- **SUCCESS**: Task completed
- **FAILURE**: Task failed

### Retry Configuration

```python
@celery.task(
    name="process_image_s3",
    max_retries=3,
    default_retry_delay=60
)
def process_image_s3(...):
    try:
        # Process
    except Exception as exc:
        raise process_image_s3.retry(exc=exc)
```

### Scaling

- **Horizontal**: Add more worker containers
- **Vertical**: Increase worker concurrency
- **Priority Queues**: Separate queues for different task types

```bash
# Start worker for high-priority queue
celery -A app.workers.celery worker -Q high_priority
```

## Model Service

### Purpose

Containerized ML inference service for:
- Computer vision models (ViT/CLIP)
- Image embeddings
- Multi-head classification
- Optional: Image captioning

### Architecture

Separate container allows:
- GPU acceleration
- Model versioning
- Independent scaling
- Model caching

### Example Setup

```dockerfile
FROM pytorch/pytorch:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY models/ ./models/
COPY inference_service.py .

CMD ["python", "inference_service.py"]
```

### API Integration

```python
# gRPC or HTTP API
import grpc
from model_service_pb2 import InferenceRequest

# Or REST API
import requests
response = requests.post(
    "http://model-service:8001/inference",
    json={"image_data": base64_image}
)
```

### Model Caching

Cache loaded models in memory:

```python
import torch

model_cache = {}

def get_model(model_name):
    if model_name not in model_cache:
        model_cache[model_name] = load_model(model_name)
    return model_cache[model_name]
```

## Docker Compose Setup

All middleware services are configured in `docker-compose.yml`:

```yaml
services:
  db:
    image: ankane/pgvector:latest
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: realestate
    volumes:
      - ./data/postgres:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: minio
      MINIO_ROOT_PASSWORD: minio123
    volumes:
      - ./data/minio:/data
```

## Monitoring & Logging

### Health Checks

- **PostgreSQL**: `pg_isready -U postgres`
- **Redis**: `redis-cli ping`
- **MinIO**: `curl http://localhost:9000/minio/health/live`

### Logging

Configure structured logging:

```python
import logging
import json

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    json.dumps({
        'timestamp': '%(asctime)s',
        'level': '%(levelname)s',
        'message': '%(message)s'
    })
)
handler.setFormatter(formatter)
logger.addHandler(handler)
```

### Metrics

- **PostgreSQL**: pg_stat_statements extension
- **Redis**: INFO command for stats
- **Celery**: Flower for task metrics
- **MinIO**: Prometheus metrics endpoint

## Backup & Recovery

### Database

```bash
# Automated backups
docker exec realestate-db pg_dump -U postgres realestate | \
  gzip > backup_$(date +%Y%m%d).sql.gz
```

### Object Storage

```bash
# Sync to backup location
mc mirror myminio/realestate backup-location/
```

### Disaster Recovery

1. **Database**: Restore from latest backup
2. **Redis**: Restart (data is ephemeral)
3. **MinIO**: Restore from backup location
4. **Celery**: Restart workers

## Security

### Database

- Use strong passwords
- Limit network access
- Enable SSL for connections
- Regular security updates

### Redis

- Set password (requirepass)
- Bind to localhost if possible
- Use Redis ACLs

### MinIO

- Use strong credentials
- Configure bucket policies
- Enable SSL/TLS
- Audit access logs

## Performance Tuning

### PostgreSQL

- Tune `shared_buffers`, `work_mem`, `maintenance_work_mem`
- Create indexes for frequent queries
- Use connection pooling
- Monitor query performance

### Redis

- Configure maxmemory and eviction policy
- Use Redis Cluster for high availability
- Monitor memory usage

### MinIO

- Use multiple disks for performance
- Configure erasure coding
- Enable distributed mode

## Scaling

### Horizontal Scaling

- **Database**: Read replicas, connection pooling
- **Redis**: Redis Cluster or Sentinel
- **MinIO**: Distributed mode with multiple nodes
- **Celery**: Add more worker containers

### Vertical Scaling

- Increase container resources
- Optimize query performance
- Cache frequently accessed data

## Troubleshooting

### Database Connection Issues

```bash
# Check connection
docker exec realestate-db psql -U postgres -c "SELECT 1"

# Check logs
docker logs realestate-db
```

### Redis Issues

```bash
# Check Redis
docker exec realestate-redis redis-cli ping

# Check memory
docker exec realestate-redis redis-cli INFO memory
```

### MinIO Issues

```bash
# Check MinIO health
curl http://localhost:9000/minio/health/live

# Check logs
docker logs realestate-minio
```

## Testing

For middleware testing, see the backend test suite:

```bash
make test        # Run all tests
make test-cov    # Run tests with coverage
```

**See:** [Testing Documentation](README-tests.md) for comprehensive testing guide.

## Related Documentation

- [Backend Documentation](README-backend.md)
- [Frontend Documentation](README-frontend.md)
- [Testing Documentation](README-tests.md)
- [Main README](README.md)

