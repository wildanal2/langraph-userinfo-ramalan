# Creative Career Fortune Teller 🔮

Production-ready chatbot untuk mengumpulkan data user melalui percakapan yang engaging menggunakan LangGraph dan AWS Bedrock Nova.

## Features

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
- 🧪 Test structure

## Architecture

```
src/
├── api/                    # API layer
│   ├── routes/            # API endpoints
│   │   ├── chat.py        # Chat endpoints
│   │   └── health.py      # Health checks
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
└── infrastructure/       # External services
    ├── redis.py          # Redis client
    └── aws.py            # AWS Bedrock client
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

# 5. Run Html Testing
python -m http.server 8181
```

**Environment variables penting:**
```env
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-lite-v1:0
ENVIRONMENT=development
REDIS_URL=redis://127.0.0.1:6379
```

## Usage

```bash
make run          # Production
make run-dev      # Development (auto-reload)
make test         # Run tests
make docker-up    # Docker deployment
python main.py    # CLI testing
```

## API Endpoints

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

```bash
# Docker (Recommended)
docker-compose up -d

# Manual
ENVIRONMENT=production python run.py
```

**Production checklist:**
- Set `ENVIRONMENT=production`
- Configure `ALLOWED_ORIGINS` dengan domain spesifik
- Set `LOG_LEVEL=WARNING`
- Gunakan production Redis
- Enable HTTPS
- Monitor `/health` endpoint

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
└── infrastructure/   # External services
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

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Setup cepat 5 menit
- **[MIGRATION.md](MIGRATION.md)** - Panduan migrasi dari struktur lama
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Checklist production
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

## License

MIT
