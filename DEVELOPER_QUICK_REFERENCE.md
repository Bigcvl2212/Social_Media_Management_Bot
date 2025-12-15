# Developer Quick Reference Guide

## 🚀 Essential Commands

### Development Startup

```bash
# Full stack with Docker Compose (10 seconds)
docker-compose up -d

# Check all services are healthy
docker-compose ps
docker-compose logs -f backend

# Initialize database
docker-compose exec backend alembic upgrade head

# Access services
# API Docs:    http://localhost:8000/docs
# Flower:      http://localhost:5555
# PostgreSQL:  localhost:5432
# Redis:       localhost:6379
```

### Testing

```bash
# Run all tests
pytest backend/tests/test_complete.py -v

# Run specific test class
pytest backend/tests/test_complete.py::TestVideoProcessingService -v

# Run with coverage
pytest backend/tests/test_complete.py --cov=app --cov-report=html

# Run async tests
pytest -m asyncio backend/tests/test_complete.py -v
```

### Code Quality

```bash
# Format code
black app tests

# Sort imports
isort app tests

# Lint check
flake8 app tests --max-line-length=120

# Type checking
mypy app --ignore-missing-imports

# All at once
black app && isort app && flake8 app && mypy app
```

### Database

```bash
# Create migration
docker-compose exec backend alembic revision --autogenerate -m "Add new table"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback
docker-compose exec backend alembic downgrade -1

# Check current version
docker-compose exec backend alembic current

# Database shell
docker-compose exec postgres psql -U contentmanager content_manager
```

### API Testing

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload video
curl -X POST http://localhost:8000/api/v1/content/upload/video \
  -F "file=@video.mp4" \
  -F "title=My Video"

# Generate captions
curl -X POST http://localhost:8000/api/v1/generate/captions \
  -H "Content-Type: application/json" \
  -d '{
    "content_description": "Fitness workout",
    "platform": "instagram",
    "hashtags": true
  }'

# View Swagger docs
open http://localhost:8000/docs
```

### Celery Management

```bash
# Monitor active tasks
docker-compose exec celery_worker celery -A app.tasks.celery_tasks inspect active

# Check worker stats
docker-compose exec celery_worker celery -A app.tasks.celery_tasks inspect stats

# Purge queue (DANGEROUS - clears pending tasks)
docker-compose exec celery_worker celery -A app.tasks.celery_tasks purge

# Restart worker
docker-compose restart celery_worker

# View Flower dashboard
open http://localhost:5555
```

### Logging

```bash
# Backend logs
docker-compose logs -f backend

# Worker logs
docker-compose logs -f celery_worker

# Beat logs
docker-compose logs -f celery_beat

# Database logs
docker-compose logs -f postgres

# Redis logs
docker-compose logs -f redis

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Deployment

```bash
# Build Docker image
docker build -t content-manager-backend:latest .

# Push to registry
docker push ghcr.io/username/content-manager-backend:latest

# Deploy to Kubernetes
kubectl apply -f k8s/manifests/
kubectl get pods -n content-manager

# Check deployment status
kubectl rollout status deployment/backend -n content-manager

# View pod logs
kubectl logs -n content-manager deployment/backend

# Port forward
kubectl port-forward -n content-manager svc/backend-service 8000:80
```

---

## 📚 File Organization

### Frontend (`/frontend`)
```
src/components/
├── ContentUploadManager.tsx      # Upload videos/images
├── VideoEditorPanel.tsx          # Video editing
├── ImageEditorPanel.tsx          # Image editing
├── ContentScheduler.tsx          # Schedule posts
├── AnalyticsDashboard.tsx        # Analytics view
├── ClipLibrary.tsx               # Clip browser
├── PlatformConnector.tsx         # OAuth setup
└── NotificationCenter.tsx        # Status notifications
```

### Backend Services (`/backend/app/services`)
```
├── content_processing.py         # Video/image ops
├── ai_generation.py              # Content generation
├── platform_integration.py       # Social media
└── __init__.py
```

### Backend Routes (`/backend/app/routes`)
```
├── content.py                    # API endpoints
└── __init__.py
```

### Database (`/backend/app/models`)
```
├── content.py                    # SQLAlchemy models
└── __init__.py
```

### Tasks (`/backend/app/tasks`)
```
├── celery_tasks.py              # Async tasks
└── __init__.py
```

### Tests (`/backend/tests`)
```
├── test_complete.py             # All tests
└── __init__.py
```

---

## 🔌 API Endpoints Quick Reference

### Upload
```
POST   /api/v1/content/upload/video
POST   /api/v1/content/upload/image
POST   /api/v1/content/upload/batch
```

### Video Editing
```
POST   /api/v1/video/trim
POST   /api/v1/video/apply-effect
POST   /api/v1/video/extract-clips
```

### Image Editing
```
POST   /api/v1/image/apply-filter
POST   /api/v1/image/add-text
POST   /api/v1/image/optimize
```

### AI Generation
```
POST   /api/v1/generate/captions
POST   /api/v1/generate/script
POST   /api/v1/generate/image
POST   /api/v1/generate/ideas
POST   /api/v1/generate/hashtags
```

### Posting
```
POST   /api/v1/post/to-platform
POST   /api/v1/post/multi-platform
POST   /api/v1/post/schedule
GET    /api/v1/post/{post_id}/status
```

### Analytics
```
GET    /api/v1/analytics/platform
GET    /api/v1/analytics/content
GET    /api/v1/analytics/trending
GET    /api/v1/analytics/summary
```

### OAuth
```
GET    /api/v1/oauth/{platform}/authorize
GET    /api/v1/oauth/{platform}/callback
```

### Health
```
GET    /api/v1/health
```

---

## 🛠️ Common Debugging

### Service won't start

```bash
# Check configuration
docker-compose config

# Check image exists
docker images | grep content-manager

# Check logs
docker-compose logs backend

# Rebuild image
docker-compose build --no-cache backend
```

### Database connection error

```bash
# Check PostgreSQL running
docker-compose ps postgres

# Check connection string
echo $DATABASE_URL

# Test connection
docker-compose exec backend psql $DATABASE_URL -c "SELECT 1"

# Check PostgreSQL logs
docker-compose logs postgres
```

### API not responding

```bash
# Check if backend running
curl http://localhost:8000/api/v1/health

# Check port in use
lsof -i :8000

# Check firewall
sudo ufw allow 8000

# Restart service
docker-compose restart backend
```

### Celery tasks not processing

```bash
# Check worker running
docker-compose ps celery_worker

# Check queue
docker-compose exec celery_worker celery -A app.tasks.celery_tasks inspect active

# Check Redis connection
docker-compose exec redis redis-cli ping

# Restart worker
docker-compose restart celery_worker

# Clear queue
docker-compose exec celery_worker celery -A app.tasks.celery_tasks purge
```

### High disk usage

```bash
# Docker cleanup
docker system prune -a

# Remove old images
docker rmi $(docker images -q)

# Check volumes
docker volume ls

# Remove unused volumes
docker volume prune
```

---

## 📊 Performance Tips

### Database Optimization
```sql
-- Create indexes for faster queries
CREATE INDEX idx_job_status ON content_jobs(status);
CREATE INDEX idx_clip_job_id ON generated_clips(job_id);
CREATE INDEX idx_post_platform ON scheduled_posts(platforms);

-- Check index usage
EXPLAIN ANALYZE SELECT * FROM content_jobs WHERE status='completed';
```

### Redis Optimization
```bash
# Monitor Redis memory
docker-compose exec redis redis-cli info memory

# Clear cache
docker-compose exec redis redis-cli FLUSHDB

# Set max memory policy
docker-compose exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Celery Optimization
```python
# In celery_tasks.py
app.conf.update(
    worker_prefetch_multiplier=4,        # Prefetch 4 tasks
    worker_max_tasks_per_child=1000,     # Restart after 1000 tasks
    task_compression='gzip',              # Compress tasks
    worker_disable_rate_limits=False,     # Enable rate limiting
)
```

### API Optimization
```python
# In main.py
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

# Enable caching
@app.get("/api/v1/analytics/trending")
@cached(expire=3600)  # Cache for 1 hour
async def get_trending():
    # Expensive operation
    pass
```

---

## 🔐 Security Checklist

- [ ] All secrets in `.env` (never in code)
- [ ] HTTPS enabled in production
- [ ] API rate limiting configured
- [ ] CORS properly restricted
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (SQLAlchemy)
- [ ] Password hashing for users
- [ ] JWT token expiration set
- [ ] Database backups enabled
- [ ] Secrets rotated regularly
- [ ] Logging sensitive data redacted
- [ ] Security headers set

---

## 📈 Monitoring Checklist

- [ ] Health checks passing
- [ ] Error logs monitored
- [ ] Performance metrics tracked
- [ ] Database performance reviewed
- [ ] API response times checked
- [ ] Celery queue depth monitored
- [ ] Redis memory usage watched
- [ ] CPU/Memory usage tracked
- [ ] Alerts configured
- [ ] Backups verified working

---

## 🚀 Deployment Checklist

- [ ] Environment variables set
- [ ] Secrets configured
- [ ] Database migrated
- [ ] Indexes created
- [ ] Health checks passing
- [ ] Tests passing (100% success)
- [ ] Security scan passed
- [ ] Performance benchmarked
- [ ] Load testing completed
- [ ] Backup & recovery tested
- [ ] Monitoring configured
- [ ] Documentation updated
- [ ] Rollback plan ready

---

## 📞 When Things Break

1. **Check logs** - Always start here
   ```bash
   docker-compose logs -f service_name
   ```

2. **Check health** - Services should be running
   ```bash
   docker-compose ps
   curl http://localhost:8000/api/v1/health
   ```

3. **Check configuration** - Verify environment and config
   ```bash
   docker-compose config
   cat .env
   ```

4. **Restart services** - Often fixes transient issues
   ```bash
   docker-compose restart service_name
   ```

5. **Rebuild** - If restart doesn't work
   ```bash
   docker-compose build --no-cache service_name
   docker-compose up -d
   ```

6. **Check connectivity** - Database, cache, external APIs
   ```bash
   docker-compose exec backend curl http://redis:6379
   docker-compose exec backend psql $DATABASE_URL -c "SELECT 1"
   ```

7. **Review recent changes** - What changed?
   ```bash
   git log --oneline -5
   git diff HEAD~1
   ```

8. **Check resources** - Is there enough CPU/memory?
   ```bash
   docker stats
   free -h
   df -h
   ```

---

## 🎯 Key Metrics

Monitor these in production:

| Metric | Target | Alert |
|--------|--------|-------|
| API Response Time | < 200ms | > 500ms |
| Error Rate | < 0.1% | > 1% |
| CPU Usage | < 70% | > 80% |
| Memory Usage | < 70% | > 80% |
| Database Queries | < 100ms | > 500ms |
| Task Queue Depth | < 100 | > 500 |
| Redis Memory | < 500MB | > 1GB |
| Uptime | > 99.9% | Any outage |

---

**Last Updated:** 2024
**Maintained By:** Development Team
**Status:** ✅ Production Ready
