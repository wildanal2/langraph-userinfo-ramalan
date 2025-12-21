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
- 🧪 Test structure

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
├── rag/                  # RAG logic
│   ├── db/               # Knowledge storage
│   │   ├── docstore.py        # Redis (document store)
│   │   └── vectorstore.py     # ChromaDB (vector store)
│   ├── ingestion/             # Ingestion logic
│   │   ├── loader.py          # Loader for handling documents from AWS S3 Bucket
│   │   ├── splitter.py        # Chunking logic (Parent-Child Chunking)
│   │   ├── indexer.py         # Indexing logic to store Child Chunk in ChromaDB and Parent Chunk in Redis
│   │   └── ingestion_pipeline.py     # Full ingestion pipeline
│   ├── retrieval/             # RAG logic
│   │   ├── retriever.py       # Retrieval logic
│   │   └── rag_pipeline.py    # Full RAG pipeline
│   ├── utils/                 # RAG helper function
│   │   ├── collection_handler.py     # Logic for managing collection in ChromaDB and Redis
│   │   ├── document_serializer.py    # Serialization logic to store Langchain Documents in Redis
│   │   └── parser.py                 # Parser logic for retrieved chunk
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
│   └── aws.py            # AWS Bedrock client
└── static/               # Static files
    └── widget/           # Chat widget
        ├── css/          # Widget styles
        ├── js/           # Widget scripts
        └── images/       # Widget assets
data/
├── chroma/                 # ChromaDB data
└── active_collection.json  # File to track Active Collection configuration
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
  window.KREA_API_URL = "http://localhost:8000";
</script>
<link
  rel="stylesheet"
  href="http://localhost:8000/static/widget/css/widget.css"
/>
<script src="http://localhost:8000/static/widget/js/widget.js"></script>
```

**Production:**

```html
<script>
  window.KREA_API_URL = "https://api.yourdomain.com";
</script>
<link
  rel="stylesheet"
  href="https://api.yourdomain.com/static/widget/css/widget.css"
/>
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
- **GET /static/widget/\*** - Widget assets (CSS, JS, images)

### Health

- **GET /health** - Health check endpoint

### Ingest

- **POST /ingest** - Trigger ingestion document process from AWS S3 bucket (running on the Background Tasks for non-blocking operation) for RAG feature
- **GET /ingest/status** - Track the status of the ingestion process, wether if it's 'in progress', 'completed;, or 'failed'

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

### Trigger Ingestion RAG

```bash
POST /ingest
Content-Type: application/json

{
  "s3_bucket": "iccn-rag-knowledge",
  "s3_prefix": "general-docs/",
  "parent_chunk_size": 900,
  "parent_chunk_overlap": 100,
  "child_chunk_size": 350,
  "child_chunk_overlap": 50
}
```

### Ingestion Status

```bash
GET /ingest/status
```

Response:

```json
{
  "status": "completed",
  "message": "Ingestion completed successfully",
  "config": {
    "collection_name": "rag_v_20251221_220537",
    "updated_at": "2025-12-21T22:06:04.868235",
    "chunking_config": {
      "parent_chunk_size": 1000,
      "parent_chunk_overlap": 100,
      "child_chunk_size": 350,
      "child_chunk_overlap": 50
    }
  }
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

| Issue                   | Solution                                                        |
| ----------------------- | --------------------------------------------------------------- |
| Redis connection failed | `redis-cli ping` atau `docker run -d -p 6379:6379 redis:alpine` |
| AWS credentials error   | `aws configure` atau check `.env`                               |
| Import errors           | `make clean && make install`                                    |
| Port in use             | `lsof -i :8000` dan kill process                                |
| Widget tidak muncul     | Check browser console, pastikan API URL benar                   |
| CORS error di widget    | Update `ALLOWED_ORIGINS` di config                              |

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Setup cepat 5 menit
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Architecture overview
- **[docs/WIDGET_QUICKSTART.md](docs/WIDGET_QUICKSTART.md)** - Widget quick start
- **[docs/WIDGET.md](docs/WIDGET.md)** - Widget documentation
- **[docs/WIDGET_STRUCTURE.md](docs/WIDGET_STRUCTURE.md)** - Widget structure
- **[MIGRATION.md](MIGRATION.md)** - Panduan migrasi dari struktur lama
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Checklist production
- **[CHANGELOG.md](CHANGELOG.md)** - Version history

## License

MIT
