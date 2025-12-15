# Complete Deployment & Dockerization Guide

## Overview

This guide covers deploying the Social Media Content Manager to production using Docker, Kubernetes, and cloud platforms (AWS, GCP, Azure).

## Table of Contents

1. [Docker Setup](#docker-setup)
2. [Docker Compose Deployment](#docker-compose-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Cloud Platform Deployment](#cloud-platform-deployment)
5. [CI/CD Pipeline](#cicd-pipeline)
6. [Monitoring & Logging](#monitoring--logging)
7. [Backup & Recovery](#backup--recovery)
8. [Scaling](#scaling)

---

## Docker Setup

### Prerequisites

- Docker 20.10+ ([Install](https://docs.docker.com/get-docker/))
- Docker Compose 2.0+ ([Install](https://docs.docker.com/compose/install/))
- FFmpeg installed in container (included in Dockerfile)

### Build Docker Image

```bash
# Build the backend image
docker build -t content-manager-backend:latest .

# Tag for registry
docker tag content-manager-backend:latest ghcr.io/username/content-manager-backend:latest

# Push to registry
docker push ghcr.io/username/content-manager-backend:latest
```

### Dockerfile Overview

```dockerfile
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (FFmpeg, image libraries)
RUN apt-get update && apt-get install -y ffmpeg libsm6 libxext6 libxrender-dev

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD python -c "..."
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Key Features:**
- Slim Python image (reduces size ~60%)
- Multi-stage builds support (add for optimization)
- Health checks enabled
- Non-root user recommended (add in production)

---

## Docker Compose Deployment

### Quick Start

```bash
# 1. Create environment file
cp .env.example .env
# Edit .env with your API keys and credentials

# 2. Start all services
docker-compose up -d

# 3. Initialize database
docker-compose exec backend alembic upgrade head

# 4. Verify services
docker-compose ps
docker-compose logs -f backend
```

### Service Architecture

```
┌─────────────────────────────────────────────────────┐
│              Docker Compose Services                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────┐  │
│  │  FastAPI     │  │  PostgreSQL  │  │  Redis   │  │
│  │  Backend     │  │  Database    │  │  Cache   │  │
│  │  :8000       │  │  :5432       │  │  :6379   │  │
│  └──────────────┘  └──────────────┘  └──────────┘  │
│         ↓                                           │
│  ┌──────────────────────────────────────────────┐  │
│  │      Celery Worker (Video Processing)       │  │
│  │      Celery Beat (Scheduled Tasks)           │  │
│  │      Flower (Monitoring :5555)               │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Service Details

| Service | Purpose | Port | Health Check |
|---------|---------|------|--------------|
| `backend` | FastAPI application | 8000 | `/api/v1/health` |
| `postgres` | PostgreSQL database | 5432 | `pg_isready` |
| `redis` | Cache & message broker | 6379 | `redis-cli ping` |
| `celery_worker` | Async task processing | - | `celery inspect active` |
| `celery_beat` | Scheduled tasks | - | Process check |
| `flower` | Celery monitoring | 5555 | Web dashboard |

### Common Operations

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker

# Scale workers
docker-compose up -d --scale celery_worker=3

# Execute commands
docker-compose exec backend python -c "import app; print('OK')"

# Database migrations
docker-compose exec backend alembic upgrade head
docker-compose exec backend alembic downgrade -1

# Backup database
docker-compose exec postgres pg_dump -U contentmanager content_manager > backup.sql

# Stop services
docker-compose down
docker-compose down -v  # Also remove volumes
```

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (1.24+)
- `kubectl` configured
- Helm 3.0+ (optional, for package management)

### Deployment Manifests

#### 1. Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: content-manager
```

#### 2. ConfigMap (Environment Variables)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: content-manager
data:
  FASTAPI_ENV: "production"
  DB_HOST: "postgres.content-manager.svc.cluster.local"
  DB_PORT: "5432"
  DB_NAME: "content_manager"
  REDIS_HOST: "redis.content-manager.svc.cluster.local"
  REDIS_PORT: "6379"
```

#### 3. Secrets (Sensitive Data)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
  namespace: content-manager
type: Opaque
data:
  DB_USER: Y29udGVudG1hbmFnZXI=  # base64 encoded
  DB_PASSWORD: c2VjdXJlX3Bhc3N3b3Jk  # base64 encoded
  GROQ_API_KEY: YWJjZGVmZ2hpams=
  OPENAI_API_KEY: c2stLXByb2plY3Qta2V5
```

#### 4. PostgreSQL StatefulSet

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: content-manager
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:16-alpine
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DB_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secrets
              key: DB_PASSWORD
        - name: POSTGRES_DB
          value: content_manager
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
        livenessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U ${POSTGRES_USER}
          initialDelaySeconds: 30
          periodSeconds: 10
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 20Gi
```

#### 5. FastAPI Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: content-manager
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - backend
              topologyKey: kubernetes.io/hostname
      containers:
      - name: backend
        image: ghcr.io/username/content-manager-backend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 1000m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 20
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

#### 6. Celery Worker Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: celery-worker
  namespace: content-manager
spec:
  replicas: 2
  selector:
    matchLabels:
      app: celery-worker
  template:
    metadata:
      labels:
        app: celery-worker
    spec:
      containers:
      - name: worker
        image: ghcr.io/username/content-manager-backend:latest
        command: ["celery", "-A", "app.tasks.celery_tasks", "worker", "--loglevel=info", "--concurrency=4"]
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: app-secrets
        resources:
          requests:
            cpu: 1000m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 2Gi
```

#### 7. Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: content-manager
spec:
  type: LoadBalancer
  selector:
    app: backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
    name: http
```

#### 8. Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: backend-ingress
  namespace: content-manager
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.contentmanager.com
    secretName: backend-tls
  rules:
  - host: api.contentmanager.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
```

### Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secrets.yaml
kubectl apply -f postgres-statefulset.yaml
kubectl apply -f redis-deployment.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f celery-worker-deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Verify deployment
kubectl get deployments -n content-manager
kubectl get pods -n content-manager
kubectl get services -n content-manager

# Check logs
kubectl logs -n content-manager deployment/backend -f
kubectl logs -n content-manager deployment/celery-worker -f

# Port forward for local access
kubectl port-forward -n content-manager svc/backend-service 8000:80
```

---

## Cloud Platform Deployment

### AWS ECS/Fargate

```yaml
# ecs-task-definition.json
{
  "family": "content-manager",
  "requiresCompatibilities": ["FARGATE"],
  "networkMode": "awsvpc",
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/content-manager:latest",
      "portMappings": [{"containerPort": 8000, "protocol": "tcp"}],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/content-manager",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "environment": [
        {"name": "DATABASE_URL", "value": "postgresql://..."},
        {"name": "REDIS_URL", "value": "redis://..."}
      ]
    }
  ]
}
```

Deploy:
```bash
# Push image to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com
docker tag content-manager-backend:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/content-manager:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/content-manager:latest

# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create service
aws ecs create-service --cluster content-manager --service-name backend --task-definition content-manager --desired-count 3 --launch-type FARGATE --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=ENABLED}"
```

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT-ID/content-manager:latest .

# Deploy
gcloud run deploy content-manager \
  --image gcr.io/PROJECT-ID/content-manager:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgresql://...,REDIS_URL=redis://... \
  --memory 2Gi \
  --cpu 2
```

### Azure Container Instances

```bash
# Login to Azure
az login

# Build image
az acr build --registry myregistry --image content-manager:latest .

# Deploy
az container create \
  --resource-group myresourcegroup \
  --name content-manager \
  --image myregistry.azurecr.io/content-manager:latest \
  --cpu 2 --memory 2 \
  --registry-login-server myregistry.azurecr.io \
  --registry-username <username> \
  --registry-password <password> \
  --environment-variables DATABASE_URL=postgresql://... REDIS_URL=redis://...
```

---

## CI/CD Pipeline

GitHub Actions workflow automatically:

1. **Lint & Format** - Code quality checks
2. **Unit Tests** - Run pytest suite
3. **Security Scan** - Vulnerability detection
4. **Build Docker Image** - Create and push container
5. **Integration Tests** - Full workflow testing
6. **Deploy to Staging** - Automatic on `develop` push
7. **Deploy to Production** - Automatic on `main` push

### Setup GitHub Actions

1. Add secrets to repository:
   - `STAGING_DEPLOY_KEY`
   - `STAGING_HOST`
   - `PROD_DEPLOY_KEY`
   - `PROD_HOST`

2. Enable Actions in repository settings

3. Trigger on push:
```bash
git push origin main  # Triggers production deployment
git push origin develop  # Triggers staging deployment
```

---

## Monitoring & Logging

### ELK Stack (Elasticsearch, Logstash, Kibana)

```yaml
# docker-compose addition
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.0.0
  environment:
    discovery.type: single-node
  ports:
    - "9200:9200"

kibana:
  image: docker.elastic.co/kibana/kibana:8.0.0
  ports:
    - "5601:5601"
```

### Application Metrics

```python
# In app/main.py
from prometheus_client import Counter, Histogram, make_wsgi_app
from prometheus_fastapi_instrumentator import Instrumentator

Instrumentator().instrument(app).expose(app)

# Access metrics at http://localhost:8000/metrics
```

### Monitoring Dashboards

- **Flower** - Celery task monitoring (port 5555)
- **Prometheus** - Metrics collection
- **Grafana** - Visualization dashboards

---

## Backup & Recovery

### Database Backup

```bash
# Automated daily backup
0 2 * * * docker-compose exec -T postgres pg_dump -U contentmanager content_manager > /backups/content_manager_$(date +\%Y\%m\%d).sql

# Manual backup
docker-compose exec postgres pg_dump -U contentmanager content_manager > backup.sql

# Restore from backup
docker-compose exec -T postgres psql -U contentmanager content_manager < backup.sql
```

### Disaster Recovery

```bash
# Point-in-time recovery (PITR) configuration
# In docker-compose.yml:
postgres:
  environment:
    POSTGRES_INITDB_ARGS: "-c wal_level=replica -c max_wal_senders=10"
```

---

## Scaling

### Horizontal Scaling

```bash
# Docker Compose
docker-compose up -d --scale celery_worker=5

# Kubernetes
kubectl scale deployment celery-worker -n content-manager --replicas=5

# Auto-scaling (Kubernetes)
kubectl autoscale deployment backend -n content-manager --min=3 --max=10 --cpu-percent=80
```

### Vertical Scaling

Increase resource limits in deployment configuration:

```yaml
resources:
  requests:
    cpu: 2000m
    memory: 2Gi
  limits:
    cpu: 4000m
    memory: 4Gi
```

---

## Troubleshooting

### Service won't start
```bash
# Check logs
docker-compose logs backend

# Verify configuration
docker-compose config

# Test connectivity
docker-compose exec backend curl http://localhost:8000/api/v1/health
```

### Database connection issues
```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready

# Test connection
docker-compose exec backend psql -h postgres -U contentmanager content_manager
```

### Celery tasks stuck
```bash
# Monitor active tasks
docker-compose exec celery_worker celery -A app.tasks.celery_tasks inspect active

# Purge queue
docker-compose exec celery_worker celery -A app.tasks.celery_tasks purge

# Restart worker
docker-compose restart celery_worker
```

---

## Production Checklist

- [ ] Environment variables configured
- [ ] Database backups enabled
- [ ] SSL/TLS certificates installed
- [ ] Firewall rules configured
- [ ] Monitoring and alerting setup
- [ ] API rate limiting enabled
- [ ] CORS properly configured
- [ ] Logging centralized
- [ ] Secrets stored in secure vault
- [ ] Auto-scaling configured
- [ ] Health checks enabled
- [ ] Disaster recovery plan tested
- [ ] Performance benchmarks established
- [ ] Security scan passed
- [ ] Load testing completed
