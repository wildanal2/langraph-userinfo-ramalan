# Krea.ai - Temukan Takdir Kreatifmu 🔮

Production-ready chatbot untuk mengumpulkan data user melalui percakapan yang engaging menggunakan LangGraph dan AWS Bedrock Nova. Dilengkapi dengan embeddable widget yang dapat diintegrasikan ke website manapun.

## Features

- 🎨 **Embeddable Chat Widget** - Mudah diintegrasikan ke website
- 🎭 Persona menarik untuk data collection
- 🧠 LangGraph state management
- 🤖 AWS Bedrock Nova models
- 📊 Structured data extraction (Pydantic)
- 🚀 FastAPI production-ready architecture
- 🔄 Redis session management
- 🛡️ Security (validation, CORS, sanitization)
- 📝 Logging & error handling
- 🔁 Automatic retry logic
- 🏥 Health checks
- 🔍 **LangWatch Tracing** - Full observability & monitoring
- 🔎 **RAG (Retrieval-Augmented Generation)** - Knowledge base integration

## Architecture

```
src/
├── api/                    # API layer
│   ├── routes/            # API endpoints
│   │   ├── chat.py        # Chat endpoints
│   │   ├── health.py      # Health checks
│   │   └── widget.py      # Widget routes
│   ├── dependencies.py    # FastAPI dependencies
│   ├── middleware.py      # Custom middleware
│   └── main.py           # App factory
├── core/                  # Core utilities
│   ├── config.py         # Configuration management
│   ├── exceptions.py     # Custom exceptions
│   ├── logging.py        # Logging setup
│   └── security.py       # Security utilities
├── services/             # Business logic
│   ├── llm_service.py    # LLM abstraction with retry
│   ├── session_service.py # Session management
│   └── prompt_service.py # Prompt templates
├── models/               # Data models
│   ├── state.py          # State definitions
│   └── schemas.py        # API schemas
├── graph/                # LangGraph workflow
│   ├── nodes.py          # Graph nodes
│   └── workflow.py       # Graph definition
├── infrastructure/       # External services
│   ├── redis.py          # Redis client
│   ├── aws.py            # AWS Bedrock client
│   └── langwatch.py      # LangWatch tracing
├── rag/                  # RAG system
│   ├── db/               # Vector & document stores
│   ├── ingestion/        # Document ingestion
│   ├── retrieval/        # Retrieval logic
│   └── utils/            # RAG utilities
└── static/               # Static files
    └── widget/           # Chat widget
        ├── css/          # Widget styles
        ├── js/           # Widget scripts
        └── images/       # Widget assets
```

## Quick Setup

```bash
# 1. Install dependencies
uv venv && source .venv/bin/activate
make install

# 2. Start Redis (pilih salah satu)
docker run -d -p 6379:6379 redis:alpine  # Docker
brew services start redis                 # macOS
sudo systemctl start redis                # Linux

# 3. Configure environment
cp .env.example .env
# Edit .env dengan AWS credentials Anda

# 4. Run Server FastAPI
make run-dev

# 5. Test Widget (pilih salah satu)
open http://localhost:8000/widget/demo      # Demo page
open http://localhost:8000/widget/embed     # Embed code
```

**Environment variables penting:**
```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=ap-southeast-3
AWS_EMBEDDING_REGION=ap-northeast-1
BEDROCK_MODEL_ID=global.amazon.nova-2-lite-v1:0
BEDROCK_EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0
ENVIRONMENT=development
REDIS_URL=redis://127.0.0.1:6379
LANGWATCH_API_KEY=your_langwatch_key
LANGWATCH_ENABLED=true
```

## Usage

```bash
make run          # Production
make run-dev      # Development (auto-reload)
make test         # Run tests
make docker-up    # Docker deployment
```

### Widget Integration

**Demo & Testing:**
```bash
open http://localhost:8000/widget/demo   # Demo page
open http://localhost:8000/widget/embed  # Embed code
```

**Embed di website Anda:**
```html
<script>
  window.KREA_API_URL = 'http://localhost:8000';
</script>
<link rel="stylesheet" href="http://localhost:8000/static/widget/css/widget.css">
<script src="http://localhost:8000/static/widget/js/widget.js"></script>
```

**Production:**
```html
<script>
  window.KREA_API_URL = 'https://api.yourdomain.com';
</script>
<link rel="stylesheet" href="https://api.yourdomain.com/static/widget/css/widget.css">
<script src="https://api.yourdomain.com/static/widget/js/widget.js"></script>
```

## API Endpoints

### Chat API
- **POST /start-message** - Initialize chat session (SSE stream)
- **POST /chat/stream** - Send message & get response (SSE stream)
- **POST /reset** - Reset chat session

### Widget
- **GET /widget/demo** - Demo page dengan widget
- **GET /widget/embed** - Embed code & dokumentasi
- **GET /static/widget/*** - Widget assets (CSS, JS, images)

### Health
- **GET /health** - Health check endpoint

### RAG Ingestion
- **POST /ingest** - Trigger document ingestion from S3
- **GET /ingest/status** - Check ingestion status

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

### Start Message (SSE Stream)
```bash
POST /start-message
Content-Type: application/json

{
  "session_id": null
}
```

### Chat Stream (SSE Stream)
```bash
POST /chat/stream
Content-Type: application/json

{
  "message": "Wildan",
  "session_id": "your-session-id",
  "session_state": null
}
```

### Reset Session
```bash
POST /reset
Content-Type: application/json

{
  "session_id": "your-session-id"
}
```

## API Response Format

### Streaming Response (SSE)
Both `/start-message` and `/chat/stream` return Server-Sent Events:

**Streaming chunks:**
```json
data: {"content": "word", "done": false}
```

**Final chunk:**
```json
data: {
  "content": "",
  "done": true,
  "session_id": "uuid",
  "user_data": {...},
  "interactive_options": {...}
}
```

### Interactive Options Format

#### 1. Fortune Trigger Button
```json
{
  "type": "fortune_trigger",
  "text": "🔮 Ramalan Karir"
}
```

#### 2. SSO Redirect Button
```json
{
  "type": "sso_button",
  "text": "✨ Cek Hasil Lengkapnya",
  "url": "https://sso-url.com?session_id=xxx"
}
```

#### 3. Quick Reply Buttons
```json
{
  "type": "quick_reply",
  "options": ["Aplikasi", "Desain", "Musik"]
}
```

### User Data Structure
```json
{
  "nama": "string",
  "kota": "string",
  "tanggal_lahir": "string",
  "bidang_ekraf": "string",
  "jumlah_komunitas_ekraf_disekitar": "string",
  "email": "string",
  "no_telepon": "string"
}
```

## Production Deployment

### Docker (Recommended)
```bash
docker-compose up -d
```

### Manual
```bash
ENVIRONMENT=production python run.py
```

### Widget Production Setup
1. Deploy FastAPI backend ke production
2. Update `KREA_API_URL` di embed code dengan domain production
3. Embed widget script di website target
4. (Optional) Serve static files via CDN untuk performa lebih baik

**Production checklist:**
- ✅ Set `ENVIRONMENT=production`
- ✅ Configure `ALLOWED_ORIGINS` dengan domain spesifik
- ✅ Set `LOG_LEVEL=WARNING`
- ✅ Gunakan production Redis
- ✅ Enable HTTPS
- ✅ Monitor `/health` endpoint
- ✅ Update widget `KREA_API_URL` ke production domain
- ✅ Test widget di staging environment

**Security features:**
- ✅ Input validation & sanitization
- ✅ CORS whitelist
- ✅ Request size limits
- ✅ Error handling
- ✅ Structured logging
- ✅ Health checks
- ✅ Retry logic

## Tech Stack

- Python 3.10+ | FastAPI | LangChain | LangGraph
- AWS Bedrock (Nova) | Redis | Pydantic | Tenacity

## Development

**Project structure:**
```
src/
├── api/              # HTTP endpoints & middleware
├── core/             # Config, logging, security
├── services/         # Business logic
├── models/           # Data models
├── graph/            # LangGraph workflow
├── infrastructure/   # External services
└── static/           # Widget assets
```

**Adding features:**
1. Business logic → `services/`
2. API endpoints → `api/routes/`
3. Models → `models/`
4. Tests → `tests/`

**Code quality:**
```bash
make format    # Format code
make lint      # Check linting
make quality   # Run all checks
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Redis connection failed | `redis-cli ping` atau `docker run -d -p 6379:6379 redis:alpine` |
| AWS credentials error | `aws configure` atau check `.env` |
| Import errors | `make clean && make install` |
| Port in use | `lsof -i :8000` dan kill process |
| Widget tidak muncul | Check browser console, pastikan API URL benar |
| CORS error di widget | Update `ALLOWED_ORIGINS` di config |

## Documentation

### Core Documentation
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Architecture overview
- **[docs/PRODUCTION_DEPLOYMENT.md](docs/PRODUCTION_DEPLOYMENT.md)** - Production deployment guide

### Widget Documentation
- **[docs/WIDGET_QUICKSTART.md](docs/WIDGET_QUICKSTART.md)** - Widget setup 3 menit
- **[docs/WIDGET.md](docs/WIDGET.md)** - Widget complete guide
- **[docs/WIDGET_STRUCTURE.md](docs/WIDGET_STRUCTURE.md)** - Widget structure

### Optional Features
- **[docs/LANGWATCH_QUICKSTART.md](docs/LANGWATCH_QUICKSTART.md)** - LangWatch setup 5 menit
- **[docs/LANGWATCH.md](docs/LANGWATCH.md)** - LangWatch complete guide

## License

MIT
