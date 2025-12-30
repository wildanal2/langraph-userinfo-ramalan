# Production Deployment Guide

Panduan deployment production untuk Krea.ai Chatbot.

## Pre-Deployment Checklist

### 1. Environment Configuration

```env
# Production .env
ENVIRONMENT=production
LOG_LEVEL=WARNING

# AWS
AWS_ACCESS_KEY_ID=<prod-key>
AWS_SECRET_ACCESS_KEY=<prod-secret>
AWS_REGION=ap-southeast-3
AWS_EMBEDDING_REGION=ap-northeast-1
BEDROCK_MODEL_ID=global.amazon.nova-2-lite-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0

# Security
ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
MAX_REQUEST_SIZE=1048576
RATE_LIMIT_PER_MINUTE=60

# Redis (Production)
REDIS_URL=redis://<prod-redis-host>:6379
REDIS_TTL=86400

# LangWatch (Optional)
LANGWATCH_API_KEY=lw_prod_xxxxxxxxxxxxx
LANGWATCH_ENABLED=true

# SSO
SSO_REGISTER_URL=https://sso.yourdomain.com/register
```

### 2. Infrastructure Requirements

**Minimum:**
- CPU: 2 vCPU
- RAM: 4GB
- Storage: 20GB
- Redis: 1GB memory

**Recommended:**
- CPU: 4 vCPU
- RAM: 8GB
- Storage: 50GB
- Redis: 2GB memory, persistence enabled

## Deployment Options

### Option 1: Docker (Recommended)

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  app:
    image: krea-chatbot:latest
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
    restart: unless-stopped

volumes:
  redis_data:
```

**Deploy:**
```bash
# Build
docker build -t krea-chatbot:latest .

# Run
docker-compose -f docker-compose.prod.yml up -d
```

### Option 2: AWS ECS/Fargate

**1. Push to ECR:**
```bash
aws ecr get-login-password --region ap-southeast-3 | \
  docker login --username AWS --password-stdin <account>.dkr.ecr.ap-southeast-3.amazonaws.com

docker tag krea-chatbot:latest <account>.dkr.ecr.ap-southeast-3.amazonaws.com/krea-chatbot:latest
docker push <account>.dkr.ecr.ap-southeast-3.amazonaws.com/krea-chatbot:latest
```

**2. Use ElastiCache for Redis:**
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id krea-redis \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1
```

**3. Create ECS Service** dengan task definition yang include environment variables dari Secrets Manager.

### Option 3: Manual Deployment

```bash
# Install dependencies
uv venv && source .venv/bin/activate
make install

# Run with production settings
ENVIRONMENT=production python run.py
```

## Post-Deployment Verification

### 1. Health Check

```bash
curl https://api.yourdomain.com/health
```

Expected:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "dependencies": {
    "redis": "connected",
    "bedrock": "configured"
  }
}
```

### 2. Widget Test

```html
<script>window.KREA_API_URL = 'https://api.yourdomain.com';</script>
<link rel="stylesheet" href="https://api.yourdomain.com/static/widget/css/widget.css">
<script src="https://api.yourdomain.com/static/widget/js/widget.js"></script>
```

### 3. Load Test

```bash
# Install k6
brew install k6

# Run load test
k6 run loadtest.js
```

## Monitoring

### Health Monitoring

```bash
# Continuous health check
watch -n 30 curl -s https://api.yourdomain.com/health | jq
```

### LangWatch (Optional)

1. Go to https://app.langwatch.ai
2. Select your project
3. Monitor traces, errors, token usage
4. Setup alerts for:
   - Error rate > 5%
   - P95 latency > 3s
   - Token usage spikes

### CloudWatch (AWS)

```bash
# Create log group
aws logs create-log-group --log-group-name /ecs/krea-chatbot

# Create metric filter for errors
aws logs put-metric-filter \
  --log-group-name /ecs/krea-chatbot \
  --filter-name ErrorCount \
  --filter-pattern "ERROR" \
  --metric-transformations \
    metricName=ErrorCount,metricNamespace=KreaChatbot,metricValue=1
```

## Scaling

### Horizontal Scaling

**ECS Auto Scaling:**
```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/krea-cluster/krea-chatbot \
  --min-capacity 2 \
  --max-capacity 10
```

### Redis Scaling

**ElastiCache Cluster:**
```bash
aws elasticache create-replication-group \
  --replication-group-id krea-redis-cluster \
  --replication-group-description "Krea Redis Cluster" \
  --engine redis \
  --cache-node-type cache.r6g.large \
  --num-cache-clusters 3
```

## Security

### 1. Network Security

- Use security groups untuk restrict access
- Allow HTTPS only (port 443)
- Redis accessible only from app

### 2. Secrets Management

**AWS Secrets Manager:**
```bash
aws secretsmanager create-secret \
  --name krea/production/langwatch-api-key \
  --secret-string "lw_prod_xxxxx"

aws secretsmanager create-secret \
  --name krea/production/aws-credentials \
  --secret-string '{"access_key":"xxx","secret_key":"xxx"}'
```

### 3. CORS Configuration

Update `ALLOWED_ORIGINS` dengan domain spesifik:
```env
ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
```

## Backup & Recovery

### Redis Backup

```bash
# Enable AOF persistence
redis-cli CONFIG SET appendonly yes

# Manual backup
redis-cli BGSAVE

# Automated backup (cron)
0 2 * * * redis-cli BGSAVE && cp /var/lib/redis/dump.rdb /backup/redis-$(date +\%Y\%m\%d).rdb
```

### Disaster Recovery

**RTO:** < 15 minutes  
**RPO:** < 5 minutes

**Steps:**
1. Restore Redis from backup
2. Deploy application from ECR
3. Update DNS
4. Verify health checks

## Cost Optimization

### AWS Bedrock
- Nova Lite: $0.00006/1K input, $0.00024/1K output tokens
- Titan Embed: $0.0001/1K tokens
- Estimated: ~$50-100/month for 1M conversations

### Infrastructure (AWS)
- ECS Fargate (2 tasks): ~$50/month
- ElastiCache (t3.micro): ~$15/month
- ALB: ~$20/month
- **Total: ~$85-115/month** (excluding Bedrock)

### LangWatch (Optional)
- Free: 10K traces/month
- Pro: $49/month (100K traces)

## Rollback

```bash
# Docker
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d

# ECS
aws ecs update-service \
  --cluster krea-cluster \
  --service krea-chatbot \
  --task-definition krea-chatbot:PREVIOUS_VERSION \
  --force-new-deployment
```

## Maintenance Checklist

### Weekly
- [ ] Review error logs
- [ ] Check Redis memory usage
- [ ] Monitor API latency

### Monthly
- [ ] Update dependencies
- [ ] Review costs
- [ ] Backup Redis data

### Quarterly
- [ ] Security audit
- [ ] Load testing
- [ ] Disaster recovery drill

## Support

- AWS Support: AWS Support Center
- LangWatch: support@langwatch.ai
- Project Issues: GitHub Issues
