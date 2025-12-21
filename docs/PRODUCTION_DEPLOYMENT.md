# Production Deployment Guide with LangWatch

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
BEDROCK_MODEL_ID=global.amazon.nova-2-lite-v1:0

# Security
ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
MAX_REQUEST_SIZE=1048576
RATE_LIMIT_PER_MINUTE=60

# Redis (Production)
REDIS_URL=redis://<prod-redis-host>:6379
REDIS_TTL=86400

# LangWatch (Production)
LANGWATCH_API_KEY=lw_prod_xxxxxxxxxxxxx
LANGWATCH_ENDPOINT=https://app.langwatch.ai
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

### 3. Dependencies Check

```bash
# Install production dependencies
make install

# Verify installations
python -c "import langwatch; print('LangWatch OK')"
python -c "import fastapi; print('FastAPI OK')"
python -c "import redis; print('Redis OK')"
```

## Deployment Options

### Option 1: Docker (Recommended)

**1. Build image:**
```bash
docker build -t krea-chatbot:latest .
```

**2. Run with docker-compose:**
```yaml
# docker-compose.prod.yml
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

**3. Deploy:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Option 2: AWS ECS/Fargate

**1. Push to ECR:**
```bash
aws ecr get-login-password --region ap-southeast-3 | docker login --username AWS --password-stdin <account>.dkr.ecr.ap-southeast-3.amazonaws.com

docker tag krea-chatbot:latest <account>.dkr.ecr.ap-southeast-3.amazonaws.com/krea-chatbot:latest
docker push <account>.dkr.ecr.ap-southeast-3.amazonaws.com/krea-chatbot:latest
```

**2. Create ECS Task Definition:**
```json
{
  "family": "krea-chatbot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "<account>.dkr.ecr.ap-southeast-3.amazonaws.com/krea-chatbot:latest",
      "portMappings": [{"containerPort": 8000}],
      "environment": [
        {"name": "ENVIRONMENT", "value": "production"},
        {"name": "LANGWATCH_ENABLED", "value": "true"}
      ],
      "secrets": [
        {"name": "AWS_ACCESS_KEY_ID", "valueFrom": "arn:aws:secretsmanager:..."},
        {"name": "LANGWATCH_API_KEY", "valueFrom": "arn:aws:secretsmanager:..."}
      ],
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

**3. Use ElastiCache for Redis:**
```bash
aws elasticache create-cache-cluster \
  --cache-cluster-id krea-redis \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --num-cache-nodes 1
```

### Option 3: Kubernetes

**deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: krea-chatbot
spec:
  replicas: 3
  selector:
    matchLabels:
      app: krea-chatbot
  template:
    metadata:
      labels:
        app: krea-chatbot
    spec:
      containers:
      - name: app
        image: krea-chatbot:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LANGWATCH_ENABLED
          value: "true"
        envFrom:
        - secretRef:
            name: krea-secrets
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
---
apiVersion: v1
kind: Service
metadata:
  name: krea-chatbot
spec:
  selector:
    app: krea-chatbot
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Post-Deployment Verification

### 1. Health Check

```bash
curl https://api.yourdomain.com/health
```

Expected response:
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

### 2. LangWatch Verification

```bash
# Send test message
curl -X POST https://api.yourdomain.com/start-message \
  -H "Content-Type: application/json" \
  -d '{"session_id": null}'
```

**Check LangWatch Dashboard:**
1. Go to https://app.langwatch.ai
2. Select your project
3. Verify trace appears with label `production`
4. Check metadata includes endpoint, environment

### 3. Widget Test

```html
<!-- test.html -->
<script>
  window.KREA_API_URL = 'https://api.yourdomain.com';
</script>
<link rel="stylesheet" href="https://api.yourdomain.com/static/widget/css/widget.css">
<script src="https://api.yourdomain.com/static/widget/js/widget.js"></script>
```

### 4. Load Test

```bash
# Install k6
brew install k6

# Run load test
k6 run loadtest.js
```

**loadtest.js:**
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 0 },
  ],
};

export default function () {
  let res = http.post('https://api.yourdomain.com/start-message',
    JSON.stringify({ session_id: null }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  
  check(res, {
    'status is 200': (r) => r.status === 200,
  });
  
  sleep(1);
}
```

## Monitoring Setup

### 1. LangWatch Alerts

**Dashboard → Alerts → Create Alert:**

- **High Error Rate**: Error rate > 5% in 5 minutes
- **Slow Responses**: P95 latency > 3 seconds
- **Token Spike**: Token usage > 10K in 1 hour
- **Failed Sessions**: Failed completions > 10% in 15 minutes

### 2. CloudWatch (AWS)

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

### 3. Application Metrics

Add to `src/api/middleware.py`:

```python
from prometheus_client import Counter, Histogram
import time

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency')

class MetricsMiddleware:
    async def __call__(self, request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.observe(duration)
        return response
```

## Scaling Strategy

### Horizontal Scaling

**Auto-scaling based on:**
- CPU > 70%
- Memory > 80%
- Request rate > 1000/min

**ECS Auto Scaling:**
```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/krea-cluster/krea-chatbot \
  --min-capacity 2 \
  --max-capacity 10

aws application-autoscaling put-scaling-policy \
  --policy-name cpu-scaling \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/krea-cluster/krea-chatbot \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration \
    '{"TargetValue":70.0,"PredefinedMetricSpecification":{"PredefinedMetricType":"ECSServiceAverageCPUUtilization"}}'
```

### Redis Scaling

**Option 1: Redis Cluster**
```bash
aws elasticache create-replication-group \
  --replication-group-id krea-redis-cluster \
  --replication-group-description "Krea Redis Cluster" \
  --engine redis \
  --cache-node-type cache.r6g.large \
  --num-cache-clusters 3
```

**Option 2: Redis Sentinel**
- Master-slave replication
- Automatic failover
- Read replicas for scaling

## Backup & Recovery

### 1. Redis Backup

```bash
# Enable AOF persistence
redis-cli CONFIG SET appendonly yes

# Manual backup
redis-cli BGSAVE

# Automated backup (cron)
0 2 * * * redis-cli BGSAVE && cp /var/lib/redis/dump.rdb /backup/redis-$(date +\%Y\%m\%d).rdb
```

### 2. Application State

User data stored in Redis with 24h TTL. For long-term storage:

```python
# Add to session_service.py
def backup_to_s3(session_id: str, user_data: dict):
    import boto3
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket='krea-user-data',
        Key=f'sessions/{session_id}.json',
        Body=json.dumps(user_data)
    )
```

### 3. Disaster Recovery

**RTO (Recovery Time Objective):** < 15 minutes  
**RPO (Recovery Point Objective):** < 5 minutes

**Recovery steps:**
1. Restore Redis from latest backup
2. Deploy application from ECR
3. Update DNS to new endpoint
4. Verify health checks
5. Monitor LangWatch for errors

## Security Hardening

### 1. Network Security

```bash
# Security group (AWS)
aws ec2 create-security-group \
  --group-name krea-app-sg \
  --description "Krea Chatbot Security Group"

# Allow HTTPS only
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Allow Redis from app only
aws ec2 authorize-security-group-ingress \
  --group-id sg-redis \
  --protocol tcp \
  --port 6379 \
  --source-group sg-xxxxx
```

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

### 3. Rate Limiting

Add to `src/api/middleware.py`:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/chat/stream")
@limiter.limit("60/minute")
async def chat_stream(request: Request):
    ...
```

## Cost Optimization

### 1. AWS Bedrock

- Use Nova Lite for simple queries
- Cache frequent prompts
- Monitor token usage in LangWatch

**Estimated costs:**
- Nova Lite: $0.00006/1K input tokens, $0.00024/1K output tokens
- 1M conversations: ~$50-100/month

### 2. Redis

- Use ElastiCache t3.micro for <10K sessions/day
- Enable eviction policy: `maxmemory-policy allkeys-lru`
- Monitor memory usage

### 3. LangWatch

- Free tier: 10K traces/month
- Pro: $49/month (100K traces)
- Optimize by sampling in high-traffic periods

### 4. Infrastructure

**Cost breakdown (AWS):**
- ECS Fargate (2 tasks): ~$50/month
- ElastiCache (t3.micro): ~$15/month
- ALB: ~$20/month
- Data transfer: ~$10/month
- **Total: ~$95/month** (excluding Bedrock & LangWatch)

## Rollback Plan

### Quick Rollback

```bash
# Docker
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --force-recreate

# ECS
aws ecs update-service \
  --cluster krea-cluster \
  --service krea-chatbot \
  --task-definition krea-chatbot:PREVIOUS_VERSION \
  --force-new-deployment

# Kubernetes
kubectl rollout undo deployment/krea-chatbot
```

### Blue-Green Deployment

1. Deploy new version to "green" environment
2. Test thoroughly
3. Switch traffic via load balancer
4. Monitor for 30 minutes
5. Rollback if issues detected

## Maintenance

### Weekly
- [ ] Review LangWatch error traces
- [ ] Check Redis memory usage
- [ ] Monitor API latency (P95, P99)
- [ ] Review security logs

### Monthly
- [ ] Update dependencies
- [ ] Review token usage & costs
- [ ] Optimize prompts based on traces
- [ ] Backup Redis data

### Quarterly
- [ ] Security audit
- [ ] Load testing
- [ ] Disaster recovery drill
- [ ] Cost optimization review

## Support Contacts

- **LangWatch Support**: support@langwatch.ai
- **AWS Support**: AWS Support Center
- **On-call**: [Your team contact]

## Useful Commands

```bash
# View logs
docker-compose logs -f app

# Redis CLI
redis-cli -h <host> -p 6379

# Check health
watch -n 5 curl -s https://api.yourdomain.com/health | jq

# Monitor traces
open https://app.langwatch.ai/projects/your-project

# Restart service
docker-compose restart app
```
