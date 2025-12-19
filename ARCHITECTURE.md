# Architecture Overview

Production-ready chatbot architecture using LangGraph and AWS Bedrock Nova.

## Structure

```
src/
├── api/                    # API Layer (HTTP Interface)
│   ├── routes/            # Endpoint definitions
│   │   ├── chat.py        # Chat endpoints (start, stream, reset)
│   │   └── health.py      # Health check endpoint
│   ├── dependencies.py    # FastAPI dependency injection
│   ├── middleware.py      # Request/response middleware
│   └── main.py           # FastAPI app factory
│
├── core/                  # Core Utilities
│   ├── config.py         # Environment configuration (Pydantic)
│   ├── exceptions.py     # Custom exception classes
│   ├── logging.py        # Structured logging setup
│   └── security.py       # Input validation & sanitization
│
├── services/             # Business Logic Layer
│   ├── llm_service.py    # LLM abstraction with retry logic
│   ├── session_service.py # Session management (Redis)
│   └── prompt_service.py # Prompt templates & constants
│
├── models/               # Data Models
│   ├── state.py          # LangGraph state definitions
│   └── schemas.py        # API request/response schemas
│
├── graph/                # LangGraph Workflow
│   ├── nodes.py          # Graph nodes (chatbot, rag, classifier)
│   └── workflow.py       # Graph definition & routing
│
└── infrastructure/       # External Services
    ├── redis.py          # Redis client (singleton)
    └── aws.py            # AWS Bedrock client (singleton)
```

## Design Principles

### 1. Separation of Concerns
- **API Layer**: HTTP handling only
- **Services**: Business logic
- **Models**: Data structures
- **Infrastructure**: External integrations

### 2. Dependency Injection
- Services injected via FastAPI dependencies
- Easy to mock for testing
- Loose coupling between layers

### 3. Error Handling
- Custom exception hierarchy
- Graceful degradation
- Structured error responses
- Comprehensive logging

### 4. Security
- Input validation (Pydantic)
- Input sanitization (HTML, SQL)
- CORS configuration (environment-aware)
- Request size limits

### 5. Reliability
- Retry logic with exponential backoff (Tenacity)
- Connection pooling (Redis)
- Singleton pattern (expensive clients)
- Health checks (dependencies)

## Data Flow

```
Client Request
    ↓
API Layer (routes/chat.py)
    ↓
Middleware (logging, CORS)
    ↓
Dependencies (services injection)
    ↓
Service Layer (session, LLM)
    ↓
Graph Workflow (LangGraph)
    ↓
Infrastructure (Redis, Bedrock)
    ↓
Response (SSE stream)
```

## Key Components

### LangGraph Workflow
- **Entry Point**: Route based on user type (new/returning)
- **Classifier Node**: Determine intent (asking/answering)
- **Chatbot Node**: Collect user data step-by-step
- **RAG Node**: Answer questions about creative economy
- **Routing**: Conditional edges based on state

### Session Management
- Redis for session storage
- TTL-based expiration (24h default)
- User data persistence
- Session reset capability

### LLM Service
- AWS Bedrock Nova integration
- Automatic retry (3 attempts, exponential backoff)
- Timeout handling (30s default)
- Structured output (Pydantic)

### Security Layer
- Email validation (regex)
- Phone validation (regex)
- HTML sanitization (bleach)
- SQL injection prevention
- XSS protection

## Configuration

Environment-based configuration via `.env`:

```env
# Environment
ENVIRONMENT=production|development

# AWS
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0

# Redis
REDIS_URL=redis://127.0.0.1:6379
REDIS_TTL=86400

# Security
ALLOWED_ORIGINS=["https://yourdomain.com"]
MAX_REQUEST_SIZE=1048576

# LLM
LLM_TIMEOUT=30
LLM_MAX_RETRIES=3

# Logging
LOG_LEVEL=INFO|WARNING|ERROR
```

## Deployment

### Development
```bash
make run-dev
```

### Production
```bash
ENVIRONMENT=production python run.py
```

### Docker
```bash
docker-compose up -d
```

## Testing

```bash
make test          # Run all tests
make test-cov      # With coverage
```

## Monitoring

### Health Check
```bash
GET /health
```

Response:
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

### Logs
- Structured JSON logging
- Request/response tracking
- Error context
- Performance metrics

## Scalability

### Horizontal Scaling
- Stateless API (session in Redis)
- Load balancer ready
- No in-memory state

### Vertical Scaling
- Connection pooling
- Lazy initialization
- Efficient resource usage

### Caching
- Redis for session data
- TTL-based expiration
- Future: Response caching

## Security Checklist

- ✅ Input validation (Pydantic)
- ✅ Input sanitization (HTML, SQL)
- ✅ CORS whitelist (production)
- ✅ Request size limits
- ✅ Error message sanitization
- ✅ Structured logging (no PII)
- ✅ Timeout configuration
- ✅ Retry limits

## Performance

- **Response Time**: <2s for chat
- **Throughput**: Limited by LLM API
- **Memory**: ~100MB base
- **Redis**: Minimal overhead

## Future Enhancements

- [ ] Rate limiting middleware
- [ ] Authentication/authorization
- [ ] Metrics collection (Prometheus)
- [ ] Distributed tracing (OpenTelemetry)
- [ ] Response caching
- [ ] API versioning
- [ ] WebSocket support
- [ ] Database integration
- [ ] Message queue (async processing)
- [ ] Admin dashboard

---

**Version**: 1.0.0  
**Status**: Production Ready
