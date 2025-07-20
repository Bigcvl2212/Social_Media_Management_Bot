# Production Deployment Guide

## 🚀 Production Readiness Checklist

This guide provides step-by-step instructions for deploying the Social Media Management Bot to production with all necessary security, monitoring, and operational considerations.

### ✅ Pre-Deployment Checklist

Before deploying to production, ensure all these items are completed:

#### Security Configuration
- [ ] Replace all placeholder credentials in `.env.production`
- [ ] Generate strong secrets using `openssl rand -base64 32`
- [ ] Configure SSL/TLS certificates
- [ ] Set up secure credential management
- [ ] Run security audit: `./scripts/security_audit.py`
- [ ] Update dependency vulnerabilities
- [ ] Configure proper CORS origins (remove `*`)

#### Database Setup
- [ ] Configure production PostgreSQL database
- [ ] Run database migrations: `alembic upgrade head`
- [ ] Set up database backup procedures
- [ ] Test backup and restore processes
- [ ] Configure database monitoring

#### Monitoring & Analytics
- [ ] Set up Sentry for error monitoring
- [ ] Configure Google Analytics
- [ ] Set up log aggregation
- [ ] Configure health check endpoints
- [ ] Set up alerting for critical issues

#### Performance & Load Testing
- [ ] Run load testing: `./scripts/load_test.py --users 50 --duration 300`
- [ ] Optimize performance bottlenecks
- [ ] Configure CDN for static assets
- [ ] Set up database connection pooling
- [ ] Verify rate limiting functionality

#### User Acceptance Testing
- [ ] Run UAT suite: `./scripts/uat_testing.py`
- [ ] Test with real social media accounts
- [ ] Verify all integrations work
- [ ] Test user flows end-to-end
- [ ] Validate mobile responsiveness

---

## 🔧 Environment Setup

### 1. Production Environment Variables

Copy `.env.production` to your deployment environment and replace all placeholder values:

```bash
# Generate secure secrets
openssl rand -base64 32  # For SECRET_KEY
openssl rand -base64 32  # For ENCRYPTION_KEY
openssl rand -base64 32  # For NEXTAUTH_SECRET
```

### 2. Required API Keys

Obtain production API keys from:

- **OpenAI**: https://platform.openai.com/api-keys
- **Google OAuth**: https://console.cloud.google.com/
- **Instagram**: https://developers.facebook.com/
- **Twitter**: https://developer.twitter.com/
- **TikTok**: https://developers.tiktok.com/
- **LinkedIn**: https://www.linkedin.com/developers/
- **Sentry**: https://sentry.io/
- **Google Analytics**: https://analytics.google.com/

### 3. SSL Certificate Setup

#### Option A: Let's Encrypt (Recommended)

```bash
# Install Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Generate certificates
sudo certbot certonly --webroot -w /var/www/certbot \
  -d your-domain.com \
  -d www.your-domain.com \
  -d api.your-domain.com

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/your-domain.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/your-domain.key
```

#### Option B: Custom SSL Certificate

```bash
# Create nginx/ssl directory
mkdir -p nginx/ssl

# Copy your SSL certificates
cp your-domain.pem nginx/ssl/your-domain.pem
cp your-domain.key nginx/ssl/your-domain.key

# Set proper permissions
chmod 600 nginx/ssl/your-domain.key
chmod 644 nginx/ssl/your-domain.pem
```

---

## 🐳 Docker Deployment

### 1. Production Deployment

```bash
# Clone repository
git clone https://github.com/Bigcvl2212/Social_Media_Management_Bot.git
cd Social_Media_Management_Bot

# Configure environment
cp .env.production .env
# Edit .env with your production values

# Create necessary directories
mkdir -p backups nginx/logs nginx/ssl

# Deploy with Docker Compose
cd docker
docker-compose -f docker-compose.prod.yml up -d

# Verify deployment
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs
```

### 2. Health Checks

```bash
# Check all services are healthy
curl https://your-domain.com/health
curl https://api.your-domain.com/health

# Verify SSL configuration
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Test rate limiting
curl -I https://api.your-domain.com/api/v1/content
```

---

## 🗄️ Database Management

### 1. Database Migration

```bash
# Access backend container
docker exec -it social_media_management_bot_backend_1 bash

# Run migrations
alembic upgrade head

# Verify database structure
python -c "from app.core.database import engine; print('Database connection successful')"
```

### 2. Backup Configuration

```bash
# Set up automated backups (runs daily at 2 AM)
docker exec social_media_management_bot_backup_1 /scripts/backup_database.sh

# Test backup manually
./scripts/backup_database.sh

# List available backups
ls -la backups/
```

### 3. Database Restore (if needed)

```bash
# Interactive restore (select from available backups)
./scripts/restore_database.sh

# Restore specific backup
./scripts/restore_database.sh /backups/socialmedia_bot_backup_20231220_020000.sql.gz
```

---

## 📊 Monitoring Setup

### 1. Sentry Configuration

```bash
# Frontend monitoring (add to frontend/.env.local)
NEXT_PUBLIC_SENTRY_DSN=your-sentry-dsn
SENTRY_ORG=your-sentry-org
SENTRY_PROJECT=your-sentry-project

# Backend monitoring (add to backend/.env)
SENTRY_DSN=your-backend-sentry-dsn
```

### 2. Google Analytics Setup

```bash
# Add to frontend/.env.local
NEXT_PUBLIC_GA_TRACKING_ID=G-XXXXXXXXXX
```

### 3. Log Monitoring

```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f nginx

# View access logs
tail -f nginx/logs/access.log

# View error logs
tail -f nginx/logs/error.log
```

---

## 🧪 Testing & Validation

### 1. Load Testing

```bash
# Basic load test
./scripts/load_test.py --url https://api.your-domain.com --users 10 --duration 60

# Heavy load test
./scripts/load_test.py --url https://api.your-domain.com --users 50 --duration 300
```

### 2. Security Audit

```bash
# Run comprehensive security audit
./scripts/security_audit.py

# Check for vulnerable dependencies
cd backend && python -m safety check -r requirements.txt
cd frontend && npm audit
```

### 3. User Acceptance Testing

```bash
# Run automated UAT tests
./scripts/uat_testing.py --url https://your-domain.com \
  --email test@yourdomain.com --password yourpassword

# Run specific test categories
./scripts/uat_testing.py --filter "authentication"
./scripts/uat_testing.py --filter "content"
```

---

## 🔐 Security Hardening

### 1. Server Security

```bash
# Update system packages
sudo apt-get update && sudo apt-get upgrade -y

# Configure firewall
sudo ufw enable
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS

# Set up fail2ban
sudo apt-get install fail2ban
sudo systemctl enable fail2ban
```

### 2. Docker Security

```bash
# Scan Docker images for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  -v $PWD:/tmp/.cache/ aquasec/trivy image \
  social_media_management_bot_backend:latest

# Check container security
docker run --rm -it --cap-add=SYS_ADMIN \
  -v /var/lib/docker:/var/lib/docker \
  aquasec/docker-bench-security
```

### 3. Application Security

```bash
# Set proper file permissions
chmod 600 .env*
chmod 700 scripts/
chmod 600 nginx/ssl/your-domain.key

# Verify security headers
curl -I https://your-domain.com
```

---

## 📈 Performance Optimization

### 1. Frontend Optimization

```bash
# Build optimized frontend
cd frontend
npm run build

# Analyze bundle size
npx @next/bundle-analyzer
```

### 2. Backend Optimization

```bash
# Configure database connection pooling
# Add to backend/.env
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30

# Enable Redis caching
REDIS_CACHE_TTL=3600
```

### 3. CDN Configuration

```bash
# Configure CDN for static assets
# Update nginx configuration to set proper cache headers
# Consider using services like Cloudflare or AWS CloudFront
```

---

## 🚨 Incident Response

### 1. Common Issues

#### Service Down
```bash
# Check service status
docker-compose -f docker-compose.prod.yml ps

# Restart services
docker-compose -f docker-compose.prod.yml restart

# Check logs for errors
docker-compose -f docker-compose.prod.yml logs --tail=100
```

#### Database Issues
```bash
# Check database connection
docker exec postgres pg_isready -U postgres

# View database logs
docker logs social_media_management_bot_postgres_1

# Restore from backup if needed
./scripts/restore_database.sh
```

#### High CPU/Memory Usage
```bash
# Monitor resource usage
docker stats

# Scale services if needed
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=3
```

### 2. Emergency Contacts

- **System Administrator**: admin@yourdomain.com
- **Development Team**: dev@yourdomain.com
- **On-Call Engineer**: +1-555-EMERGENCY

---

## 📋 Maintenance Procedures

### 1. Regular Maintenance

#### Daily
- [ ] Check application health endpoints
- [ ] Review error logs and metrics
- [ ] Verify backup completion
- [ ] Monitor performance metrics

#### Weekly
- [ ] Review security alerts
- [ ] Update dependencies (if security patches available)
- [ ] Analyze performance trends
- [ ] Review user feedback and issues

#### Monthly
- [ ] Run comprehensive security audit
- [ ] Performance optimization review
- [ ] Capacity planning assessment
- [ ] Disaster recovery testing

### 2. Update Procedures

```bash
# Update application
git pull origin main

# Update Docker images
docker-compose -f docker-compose.prod.yml pull

# Deploy updates (with zero downtime)
docker-compose -f docker-compose.prod.yml up -d

# Run database migrations
docker exec backend alembic upgrade head

# Verify deployment
curl https://your-domain.com/health
```

---

## 🆘 Support & Documentation

### Internal Documentation
- **API Documentation**: https://api.your-domain.com/docs
- **Architecture Diagram**: `/docs/architecture.md`
- **Database Schema**: `/docs/database.md`
- **Deployment History**: `/docs/deployment-log.md`

### External Resources
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Next.js Documentation**: https://nextjs.org/docs
- **Docker Documentation**: https://docs.docker.com/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

### Emergency Procedures
1. **Critical Security Issue**: Immediately take application offline
2. **Data Breach**: Follow data breach response plan
3. **Service Outage**: Activate incident response team
4. **Performance Issues**: Scale resources and investigate bottlenecks

---

## ✅ Post-Deployment Verification

After completing the deployment, verify the following:

- [ ] All services are running and healthy
- [ ] SSL certificates are valid and working
- [ ] Authentication and authorization work correctly
- [ ] Social media integrations are functional
- [ ] Database backups are working
- [ ] Monitoring and alerting are active
- [ ] Performance meets requirements
- [ ] Security audit passes
- [ ] UAT tests pass
- [ ] Documentation is updated

## 🎉 Go Live!

Once all checklist items are completed and verified, your Social Media Management Bot is ready for production use!

For ongoing support and maintenance, refer to the operational procedures outlined in this guide.