# AgentFlow — Production AI Agent Platform

AgentFlow is a production-style LangGraph Agent API Service with MCP tool integration, multi-provider LLM support, PostgreSQL persistence, and a responsive React frontend.

## Architecture

```
Browser → React/Vite
           ↓ HTTPS
        FastAPI REST API
           ↓
        Agent Service
           ↓
        LangGraph StateGraph
         ├── LLM Provider Factory
         │     ├── Gemini
         │     ├── OpenRouter
         │     └── Mock (always available)
         └── MCP Client
               ↓ MCP Server
               ├── calculator
               ├── current_time
               └── text_stats

Persistence: FastAPI → Supabase PostgreSQL
```

## LangGraph Graph

```
START → analyze_request → [route]
  ├── direct_response → END
  └── select_tool → execute_mcp_tool → final_response → END
```

## MCP Tools

| Tool | Input | Output |
|------|-------|--------|
| calculator | expression | Safe math result (no eval()) |
| current_time | timezone | ISO time + date |
| text_stats | text | Characters, words, sentences |

## LLM Providers

| Provider | Key | Free Tier |
|----------|-----|-----------|
| Gemini | `GEMINI_API_KEY` | gemini-1.5-flash |
| OpenRouter | `OPENROUTER_API_KEY` | Multiple free models |
| Mock | None | Always available |

## REST API

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | System health |
| GET | /api/models | Available models |
| GET | /api/providers | Provider status |
| GET | /api/tools | MCP tool catalog |
| POST | /api/agents | Create agent |
| GET | /api/agents | List agents |
| POST | /api/sessions | Create session |
| GET | /api/sessions | List sessions |
| POST | /api/chat | Run agent |
| GET | /api/executions | Execution history |
| GET | /api/executions/{id} | Execution detail |

## Local Setup

### Backend

```bash
cd agentflow/backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
cp .env.example .env   # Edit with your credentials
.venv\Scripts\uvicorn app.main:app --reload --port 8001
```

### Frontend

```bash
cd agentflow/frontend
npm install
cp .env.example .env   # Set VITE_API_URL=http://localhost:8001
npm run dev
```

### Tests

```bash
cd agentflow/backend
.venv\Scripts\pytest -q
# Expected: 37 passed
```

## Environment Variables

### Backend (.env)

```
APP_NAME=AgentFlow
APP_ENV=development
DATABASE_URL=postgresql://user:pass@host:5432/db
GEMINI_API_KEY=         # Optional — enables Gemini provider
GEMINI_MODEL=gemini-1.5-flash
OPENROUTER_API_KEY=     # Optional — enables OpenRouter provider
OPENROUTER_MODEL=openrouter/auto
DEFAULT_PROVIDER=mock
ENABLE_PROVIDER_FALLBACK=true
FALLBACK_CHAIN=gemini,openrouter,mock
CORS_ORIGINS=http://localhost:5173
```

### Frontend (.env)

```
VITE_API_URL=http://localhost:8001
```

## Deployment

### Frontend → Vercel
Set `VITE_API_URL` to your Render backend URL.

### Backend → Render
```
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Environment: DATABASE_URL, GEMINI_API_KEY, OPENROUTER_API_KEY, CORS_ORIGINS
```

### Database → Supabase
Free PostgreSQL. Set `DATABASE_URL` in Render environment.

## Security Notes

- No API keys in frontend
- Calculator uses `asteval` — no `eval()` or arbitrary code execution
- All inputs validated before tool execution  
- Safe structured errors — no stack traces exposed to browser
- Secrets only in environment variables

## Scaling Roadmap

| Phase | Feature |
|-------|---------|
| 1 | Current production architecture |
| 2 | pgvector RAG (retrieval_service.py already stubbed) |
| 3 | Document ingestion pipeline |
| 4 | Background jobs (Celery/RQ) |
| 5 | Redis caching |
| 6 | Streaming/SSE responses |
| 7 | Authentication/RBAC |
| 8 | Multi-agent orchestration |
