# Morrow

> **Evidence-Driven Long-Horizon Agentic Memory**

Morrow is a Python-first agent runtime designed to maintain persistent, evidence-grounded memory across long-running research, technical investigation, and knowledge-work tasks.

```
Remember → Reason → Act → Observe → Learn → Remember
```

---

## Stage 1 — Engineering Foundation

This repository currently implements **Stage 1 (Repository + Engineering Foundation)**:
- **FastAPI** asynchronous application runtime with `/health` and `/version` endpoints.
- **Pydantic v2** & **pydantic-settings** typed configurations.
- **SQLModel** (SQLAlchemy 2.0 + Pydantic v2) & **asyncpg** persistence foundation configured for PostgreSQL / NeonDB with `pgvector`.
- **Alembic** database migration framework configured for asynchronous operations.
- **Ruff** for high-performance linting and formatting.
- **Mypy** strict type checking.
- **pytest** + **pytest-asyncio** + **httpx** test suite.
- **Multi-stage Dockerfile** utilizing Astral's `uv` package manager and unprivileged runtime user.
- **docker-compose** setup provisioning the API, background worker, and `pgvector/pgvector:pg16`.
- **GitHub Actions CI** pipeline enforcing lint, format, type checks, unit tests, and Docker image builds.

---

## Directory Structure

```
morrow/
├── apps/
│   ├── api/                 # FastAPI application factory, lifespan, routes
│   │   ├── routes/          # Health, version, and future domain routes
│   │   └── main.py          # App entrypoint
│   └── worker/              # Background async daemon worker
│       └── main.py
│
├── core/
│   ├── config/              # Pydantic BaseSettings & environment loaders
│   ├── logging/             # Structured console and JSON formatters
│   └── types/               # Shared domain schemas and protocols
│
├── db/
│   ├── models/              # SQLAlchemy 2.0 declarative models & mixins
│   ├── repositories/        # Generic asynchronous repository pattern
│   └── session.py           # Async engine, sessionmaker, and health probes
│
├── memory/                  # (Phase 2) Ingestion, retrieval, ranking, consolidation
├── agents/                  # (Phase 3-4) Orchestrator and specialized subagents
├── workflows/               # (Phase 5) Durable execution, checkpoints, recovery
├── tools/                   # (Phase 3 & 6) Safe tool execution and MCP integration
├── evaluation/              # (Phase 7) Benchmarks, Ragas, and DeepEval metrics
├── sandbox/                 # (Phase 6) Secure Docker execution and limits
│
├── migrations/              # Alembic database migrations
├── tests/
│   ├── unit/                # Fast, deterministic unit tests
│   ├── integration/         # API lifecycle and service integration tests
│   ├── evaluation/          # Retrieval and reasoning evaluation benchmarks
│   └── security/            # Sandbox and permission tests
│
├── .github/workflows/       # GitHub Actions CI workflow
├── docker-compose.yml       # PostgreSQL pgvector + API + Worker orchestration
├── Dockerfile               # Multi-stage production container
├── pyproject.toml           # Unified project, dependency, and tool configuration
├── AGENTS.md                # Architectural constitution for coding agents
└── README.md
```

---

## Quickstart

### Prerequisites
- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) (recommended)
- Docker & Docker Compose (optional for local database container)

### 1. Environment Setup

Copy example environment variables:
```bash
cp .env.example .env
```

Install dependencies using `uv`:
```bash
uv sync --extra dev
```

### 2. Run Locally

Start the development server:
```bash
uv run uvicorn apps.api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`:
- Interactive Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)
- Version info: [http://localhost:8000/version](http://localhost:8000/version)

### 3. Run with Docker Compose

To spin up the full stack including PostgreSQL with `pgvector`:
```bash
docker compose up --build
```

---

## Development & Quality Assurance

### Run Tests
```bash
uv run pytest -v
```

### Run Linter & Formatter
```bash
# Check formatting
uv run ruff format --check .

# Format code
uv run ruff format .

# Check lint rules
uv run ruff check .

# Fix auto-fixable lint issues
uv run ruff check --fix .
```

### Type Checking
```bash
uv run mypy apps core db tests
```

---

## API Endpoints (Stage 1)

### `GET /health`
Returns the operational health of the application and its database connectivity.

**Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "2026-10-04T00:00:00.000000Z",
  "version": "0.1.0",
  "environment": "development",
  "database": "connected",
  "details": null
}
```

### `GET /version`
Returns semantic versioning and system identity metadata.

**Response (200 OK):**
```json
{
  "name": "Morrow",
  "version": "0.1.0",
  "tagline": "Evidence-Driven Long-Horizon Agentic Memory",
  "environment": "development"
}
```

---

## Architectural Principles

See [`AGENTS.md`](./AGENTS.md) for the project constitution:
1. **Evidence-Grounded**: Responses must cite verifiable evidence (commits, experiments, documents, tool outputs).
2. **Least-Privilege Tools**: Safe, sandboxed execution with human-in-the-loop approval on destructive actions.
3. **Durable Workflows**: Resilient workflows that survive restarts and failures through checkpoints.
4. **Observable**: Full execution traces via structured events and Langfuse.
