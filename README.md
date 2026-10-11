# cat-now-me

> **All-in-one AI Development Platform** — Build professional websites, AI agents, and automation workflows with local AI models.

[![CI](https://github.com/sahilrameshthandra-arch/cat-now-me/actions/workflows/ci.yml/badge.svg)](https://github.com/sahilrameshthandra-arch/cat-now-me/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Node.js](https://img.shields.io/badge/Node.js-20+-green.svg)](https://nodejs.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.112-009688.svg)](https://fastapi.tiangolo.com/)

## 🎯 What is this?

A production-ready **monorepo** for building AI-powered applications without cloud dependencies. Everything runs locally:

- **🌐 Web Apps** — Next.js 15 + Tailwind + TypeScript for client websites
- **🤖 AI Agents** — LangGraph + Ollama (codellama, deepseek-coder, llama3.1)
- **🔄 Automation** — n8n visual workflow builder
- **📚 RAG** — ChromaDB + pgvector for document search
- **🐳 Infrastructure** — Docker Compose for local dev

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** — `winget install Docker.DockerDesktop`
- **Node.js 20+** — `winget install OpenJS.NodeJS.LTS`
- **Python 3.11+** — `winget install Python.Python.3.11`
- **Ollama** — `winget install Ollama.Ollama`
- **Git** — `winget install Git.Git`

### 1. Clone & Configure

```bash
git clone https://github.com/sahilrameshthandra-arch/cat-now-me.git
cd cat-now-me
cp .env.example .env
# Edit .env with your settings
```

### 2. Start Infrastructure

```bash
docker-compose up -d
```

This starts:
- **PostgreSQL** (port 5432) — Primary database
- **Redis** (port 6379) — Caching & sessions
- **ChromaDB** (port 8001) — Vector database
- **Ollama** (port 11434) — Local LLMs
- **n8n** (port 5678) — Workflow automation

### 3. Pull AI Models

```bash
ollama pull codellama:13b-instruct
ollama pull deepseek-coder:6.7b
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

### 4. Start Development Servers

```bash
# Terminal 1: API (FastAPI)
cd apps/api
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload

# Terminal 2: Web (Next.js)
cd apps/web
npm install
npm run dev
```

### 5. Access Applications

| Service | URL | Credentials |
|---------|-----|-------------|
| **Web App** | http://localhost:3000 | — |
| **API Docs** | http://localhost:8000/docs | — |
| **n8n** | http://localhost:5678 | admin / changeme |
| **API Health** | http://localhost:8000/api/v1/health | — |

## 📁 Project Structure

```
cat-now-me/
├── apps/
│   ├── web/                 # Next.js 15 Frontend
│   │   ├── src/
│   │   │   ├── app/         # App Router pages
│   │   │   ├── components/  # React components
│   │   │   ├── lib/         # Utilities
│   │   │   └── hooks/       # Custom hooks
│   │   └── Dockerfile
│   │
│   └── api/                 # FastAPI Backend
│       ├── app/
│       │   ├── api/v1/      # API routes
│       │   ├── agents/      # LangGraph agents
│       │   ├── core/        # Config, DB, Security
│       │   ├── models/      # SQLAlchemy models
│       │   ├── schemas/     # Pydantic schemas
│       │   └── services/    # Business logic
│       └── Dockerfile
│
├── packages/
│   └── shared/              # Shared TypeScript types
│
├── n8n/                     # n8n workflow templates
├── docker/                  # Docker configs
├── .github/workflows/       # CI/CD pipelines
├── docker-compose.yml       # Local infrastructure
└── .env.example             # Environment template
```

## 🛠️ Development Commands

```bash
# Root commands (from cat-now-me/)
npm run dev              # Start both web & api
npm run dev:web          # Start only Next.js
npm run dev:api          # Start only FastAPI
npm run build            # Build all packages
npm run lint             # Lint all packages
npm run typecheck        # TypeScript type check

# Web (apps/web/)
npm run dev              # Next.js dev server with Turbopack
npm run build            # Production build
npm run start            # Production server
npm run lint             # ESLint
npm run typecheck        # TypeScript check

# API (apps/api/)
uvicorn app.main:app --reload    # Dev server
pytest                           # Run tests
black app                        # Format code
ruff check app                   # Lint
mypy app                         # Type check

# Database
alembic upgrade head             # Run migrations
alembic revision --autogenerate -m "message"  # Create migration
```

## 🤖 AI Agents

### Available Agents

| Agent | Model | Tools | Use Case |
|-------|-------|-------|----------|
| **Code Agent** | codellama:13b | vector_search, code_exec, file_ops | Write, review, debug code |
| **Research Agent** | llama3.1:8b | vector_search, web_search | Find & synthesize information |
| **Writing Agent** | llama3.1:8b | vector_search, file_ops | Create documentation, blogs |
| **General Agent** | configurable | all tools | General purpose |

### Running Agents

```bash
# Via API
curl -X POST http://localhost:8000/api/v1/agents/run \
  -H "Authorization: Bearer <token>" \
  -d '{"prompt": "Write a REST API for user auth", "agent_type": "code"}'

# Via Python
from app.agents.langgraph_agents import get_code_agent, run_agent

agent = get_code_agent()
result = await run_agent(agent, "Create a FastAPI endpoint for file upload")
```

### Code Review Workflow

```bash
curl -X POST http://localhost:8000/api/v1/agents/code-review \
  -H "Authorization: Bearer <token>" \
  -d '{"code": "def login(user, pwd): ...", "language": "python"}'
```

## 📚 RAG (Retrieval-Augmented Generation)

### Ingest Documents

```bash
# Via API (multipart form)
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer <token>" \
  -F "files=@document.pdf" \
  -F "chunk_size=1000" \
  -F "chunk_overlap=200"

# Or create directly
curl -X POST http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Your document text...", "metadata": {"source": "manual"}}'
```

### Search

```bash
curl -X POST http://localhost:8000/api/v1/documents/search \
  -H "Authorization: Bearer <token>" \
  -d '{"query": "How to authenticate users?", "n_results": 5}'
```

## 🔄 Automation with n8n

1. Open http://localhost:5678
2. Login: `admin` / `changeme`
3. Import workflows from `n8n/templates/`
4. Connect webhooks to API endpoints:
   - `POST /api/v1/workflows/webhook/code-review` → Code Review Agent
   - `POST /api/v1/workflows/webhook/generate-content` → Writing Agent
   - `POST /api/v1/workflows/webhook/process-data` → Document Ingestion

### Example: Auto Code Review on PR

```mermaid
graph LR
    A[GitHub PR Opened] --> B[n8n Webhook]
    B --> C[Fetch PR Code]
    C --> D[Code Review Agent]
    D --> E[Post Review Comments]
```

## 🚢 Deployment

### Vercel (Web)
```bash
cd apps/web
vercel --prod
```

### Railway/Render (API)
```bash
# Connect GitHub repo to Railway
# Set environment variables from .env.example
# Deploy automatically on push to main
```

### Docker (Self-hosted)
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 🔧 Configuration

Key environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | `postgresql://postgres:postgres@localhost:5432/cat_now_me` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_DEFAULT_MODEL` | Default LLM model | `codellama:13b-instruct` |
| `CHROMA_HOST` | ChromaDB host | `localhost` |
| `SECRET_KEY` | JWT secret (32+ chars) | **Change in production!** |
| `CORS_ORIGINS` | Allowed origins | `http://localhost:3000` |

## 📖 API Documentation

Full API docs available at **http://localhost:8000/docs** (Swagger UI) when running locally.

### Key Endpoints

```
GET    /api/v1/health              # Health check
GET    /api/v1/health/detailed     # Detailed health

POST   /api/v1/agents/run          # Run AI agent
GET    /api/v1/agents              # List agents
POST   /api/v1/agents/code-review  # Multi-agent code review

POST   /api/v1/documents           # Create document
POST   /api/v1/documents/upload    # Upload files
POST   /api/v1/documents/search    # Semantic search

POST   /api/v1/chat                # Direct LLM chat
POST   /api/v1/chat/stream         # Streaming chat
POST   /api/v1/chat/embeddings     # Generate embeddings

GET    /api/v1/workflows           # List n8n workflows
POST   /api/v1/workflows/execute   # Execute workflow
POST   /api/v1/workflows/webhook/* # Webhook receivers
```

## 🧪 Testing

```bash
# API tests
cd apps/api
pytest -v --cov=app --cov-report=html

# Web tests
cd apps/web
npm test

# E2E tests (when implemented)
npm run test:e2e
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Code Style

- **TypeScript**: ESLint + Prettier (configured)
- **Python**: Black + Ruff + MyPy (configured)
- **Commits**: Conventional Commits

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Next.js](https://nextjs.org/) — React framework
- [FastAPI](https://fastapi.tiangolo.com/) — Python API framework
- [LangGraph](https://langchain-ai.github.io/langgraph/) — Agent workflows
- [Ollama](https://ollama.ai/) — Local LLMs
- [n8n](https://n8n.io/) — Workflow automation
- [ChromaDB](https://www.trychroma.com/) — Vector database
- [pgvector](https://github.com/pgvector/pgvector) — Postgres vectors
- [Tailwind CSS](https://tailwindcss.com/) — Styling
- [Radix UI](https://www.radix-ui.com/) — Accessible components

---

**Built with ❤️ for developers who want AI without the cloud.**