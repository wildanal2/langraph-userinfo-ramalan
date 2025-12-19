# Creative Career Fortune Teller 🔮

A gamified chatbot that collects user data through mystical, persuasive conversation using LangGraph and AWS Bedrock Nova models.

## Features

- 🎭 Mystical persona that makes data collection fun
- 🧠 LangGraph state management for conversation flow
- 🤖 AWS Bedrock Nova models for natural language understanding
- 📊 Structured data extraction using Pydantic
- 🚀 FastAPI backend for easy frontend integration
- 🔄 Session state management

## Setup

### 1. Install uv (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Create virtual environment and install dependencies
```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

### 3. Configure AWS credentials
```bash
cp .env.example .env
# Edit .env with your AWS credentials
```

Required environment variables:
- `AWS_ACCESS_KEY_ID`: Your AWS access key
- `AWS_SECRET_ACCESS_KEY`: Your AWS secret key
- `AWS_REGION`: AWS region (default: us-east-1)
- `BEDROCK_MODEL_ID`: Model to use (default: amazon.nova-lite-v1:0)
- `SSO_REGISTER_URL`: Your Google SSO registration URL

## Usage

### Option 1: CLI Testing
```bash
python main.py
```

### Option 2: FastAPI Server
```bash
uvicorn src.api:app --reload --host 0.0.0.0 --port 8000
```

API Endpoints:
- `POST /start-message` - Initialize chat session
- `POST /chat/stream` - Send message and get streaming response
- `POST /reset` - Reset conversation state
- `GET /health` - Health check

### Example API Requests

#### Start Message (SSE Stream)
```bash
curl -X POST "http://localhost:8000/start-message" \
  -H "Content-Type: application/json" \
  -d '{"session_id": null}'
```

#### Chat Stream (SSE Stream)
```bash
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Wildan",
    "session_id": "your-session-id",
    "session_state": null
  }'
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

Standardized button/interaction format returned in `interactive_options`:

#### 1. Fortune Trigger Button
```json
{
  "type": "fortune_trigger",
  "text": "🔮 Ramalan Karir"
}
```
Triggers fortune generation when clicked.

#### 2. SSO Redirect Button
```json
{
  "type": "sso_button",
  "text": "✨ Cek Hasil Lengkapnya",
  "url": "https://sso-url.com?session_id=xxx"
}
```
Redirects to external SSO with session tracking.

#### 3. Quick Reply Buttons
```json
{
  "type": "quick_reply",
  "options": ["Aplikasi", "Desain", "Musik"]
}
```
Multiple choice buttons for quick selection.

#### 4. Select Dropdown
```json
{
  "type": "select",
  "options": ["Option 1", "Option 2"]
}
```
Dropdown selection for many options.

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

## Project Structure

```
.
├── src/
│   ├── __init__.py
│   ├── config.py          # Environment configuration
│   ├── state.py           # State schema definitions
│   ├── nodes.py           # LangGraph node logic
│   ├── graph.py           # LangGraph workflow
│   └── api.py             # FastAPI endpoints
├── main.py                # CLI runner
├── pyproject.toml         # Project dependencies
├── .env.example           # Environment template
└── README.md
```

## Data Collection Flow

1. **Name** - "What do they call you in the creative realm?"
2. **Location** - "Where does your creative energy flow?"
3. **Date of Birth** - "When did you enter this realm?"
4. **Job Field** - "What is your creative calling?"
5. **Email** - "Your digital soul address?"
6. **Fortune** - Generate personalized creative horoscope
7. **CTA** - Google SSO registration link

## Tech Stack

- **Python 3.10+**
- **LangChain** - LLM orchestration
- **LangGraph** - State machine workflow
- **AWS Bedrock** - Nova models for NLU
- **FastAPI** - REST API backend
- **Pydantic** - Data validation
- **uv** - Fast Python package manager

## Development

Run with auto-reload:
```bash
uvicorn src.api:app --reload
```

Test the graph logic:
```bash
python main.py
```
Test html chatbot:
```bash
python -m http.server 8181
```

## License

MIT
