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
- `POST /chat` - Send message and get response
- `POST /reset` - Reset conversation state
- `GET /health` - Health check

### Example API Request
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello!",
    "session_state": null
  }'
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

## License

MIT
