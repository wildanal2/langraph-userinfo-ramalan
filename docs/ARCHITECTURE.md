# Architecture Overview

Production-ready chatbot architecture using LangGraph and AWS Bedrock Nova.

## Structure

```
src/
├── api/                    # API Layer (HTTP Interface)
│   ├── routes/            # Endpoint definitions
│   │   ├── chat.py        # Chat endpoints (start, stream, reset)
│   │   ├── health.py      # Health check endpoint
│   │   └── widget.py      # Widget routes (demo, embed)
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
├── infrastructure/       # External Services
│   ├── redis.py          # Redis client (singleton)
│   └── aws.py            # AWS Bedrock client (singleton)
│
└── static/               # Static Files
    └── widget/           # Chat Widget
        ├── css/          # Widget styles
        ├── js/           # Widget scripts
        └── images/       # Widget assets
```

## Design Principles

### 1. Separation of Concerns
- **API Layer**: HTTP handling + static files serving
- **Services**: Business logic
- **Models**: Data structures
- **Infrastructure**: External integrations
- **Static**: Frontend widget assets

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

### Chat API Flow
```
Client Request (Web/Widget)
    ↓
API Layer (routes/chat.py)
    ↓
Middleware (logging, CORS, error handling)
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

### Widget Integration Flow
```
User Website
    ↓
Widget Script Load (/static/widget/js/widget.js)
    ↓
Widget CSS Load (/static/widget/css/widget.css)
    ↓
Widget Initialize (KreaChatWidget class)
    ↓
User Interaction (click bubble)
    ↓
API Calls (POST /start-message, POST /chat/stream)
    ↓
SSE Streaming Response
    ↓
Widget UI Update (real-time)
```

## Key Components

### Embeddable Widget
- **Auto-initialize**: Loads on page ready
- **Session Persistence**: localStorage for session_id
- **SSE Streaming**: Real-time response rendering
- **Interactive UI**: Quick reply, fortune trigger, SSO buttons
- **Responsive Design**: Mobile & desktop optimized
- **Customizable**: Logo, colors, API URL configurable

### Widget Endpoints
- **GET /widget/demo**: Demo page with integrated widget
- **GET /widget/embed**: Embed code & documentation
- **GET /static/widget/***: Static assets (CSS, JS, images)

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

## API Endpoints

### Chat Endpoints
- **POST /start-message**: Initialize chat session (SSE)
- **POST /chat/stream**: Send message & stream response (SSE)
- **POST /reset**: Reset chat session

### Widget Endpoints
- **GET /widget/demo**: Demo page
- **GET /widget/embed**: Embed documentation

### Health & Static
- **GET /health**: Health check
- **GET /static/widget/***: Widget assets

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
# Widget demo: http://localhost:8000/widget/demo
```

### Production
```bash
ENVIRONMENT=production python run.py
# Update widget API URL in embed code
```

### Docker
```bash
docker-compose up -d
```

### Widget Deployment
1. Deploy FastAPI backend
2. Update `KREA_API_URL` in widget embed code
3. Embed widget script in target website
4. Optional: Serve static files via CDN

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
- [ ] Widget analytics & tracking
- [ ] Multi-language widget support
- [ ] Widget theme customization API

## Related Documentation

- **[WIDGET_QUICKSTART.md](WIDGET_QUICKSTART.md)** - Widget setup guide
- **[WIDGET.md](WIDGET.md)** - Widget full documentation
- **[WIDGET_STRUCTURE.md](WIDGET_STRUCTURE.md)** - Widget structure details
- **[../README.md](../README.md)** - Main project README

---

**Version**: 1.1.0  
**Status**: Production Ready  
**Last Updated**: Widget Integration Added
