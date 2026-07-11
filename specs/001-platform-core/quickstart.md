# Quickstart: AgentFlow AI Platform

**Created**: 2026-05-11
**Branch**: `001-platform-core`

---

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- UV package manager
- Git

---

## Local Setup

### 1. Clone and Install

```bash
# Clone the repository
git clone <repo-url>
cd ai-pappointment-setter-lead-qualification-agent

# Install Python dependencies (backend)
cd backend
uv sync
cp ../.env.example .env
# Edit .env with your values (see .env.example)

# Install Node dependencies (frontend)
cd ../frontend
npm install
cp ../.env.example .env.local
# Edit .env.local with your values
```

### 2. Environment Variables

Create `.env` files based on `.env.example`. Required variables:

**Backend (`backend/.env`)**:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/agentflow
QDRANT_URL=http://localhost:6333
JWT_SECRET=<generate-with: openssl rand -hex 32>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=30
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USER=
SMTP_PASSWORD=
FROM_EMAIL=noreply@agentflow.local
OPENROUTER_API_KEY=<your-key>
FRONTEND_URL=http://localhost:3000
```

**Frontend (`frontend/.env.local`)**:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

### 3. Start Infrastructure

```bash
# From project root
docker compose up -d postgres qdrant mailhog

# Wait for services to be ready
sleep 5
```

### 4. Initialize Database

```bash
cd backend

# Run migrations
uv run alembic upgrade head

# Seed platform data (creates super admin)
uv run python -m app.core.seed
```

### 5. Run Development Servers

```bash
# Terminal 1: Backend
cd backend
uv run uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 6. Open the App

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Mailhog** (dev email): http://localhost:8025

### Default Credentials (Development)

After seeding:
- **Platform Admin**: `admin@agentflow.local` / `admin123`
- **Create a test tenant** via the admin dashboard to test business flows

---

## Project Structure

```
backend/          # FastAPI Python application
├── src/app/      # Application code
├── tests/        # pytest tests
├── alembic/      # Database migrations
└── pyproject.toml

frontend/         # Next.js TypeScript application
├── src/app/      # App Router pages
├── src/components/
└── package.json

docker-compose.yml  # Full stack orchestration
```

---

## Key Commands

```bash
# Backend
uv run alembic revision --autogenerate -m "description"  # Create migration
uv run alembic upgrade head                                  # Apply migrations
uv run pytest                                              # Run tests
uv run pytest tests/integration/                            # Integration tests only
uv run mypy src/                                            # Type check

# Frontend
npm run dev                                                 # Development server
npm run build                                               # Production build
npm run lint                                                # Lint
npx playwright install                                       # Install e2e test browser

# Docker
docker compose up -d                    # Start all services
docker compose down -v                  # Stop and remove volumes
docker compose logs -f backend          # Follow backend logs
```

---

## Testing the AI Chat Widget

1. As a business admin, configure your AI receptionist in Settings
2. Copy the embed code from the widget setup page
3. Open any HTML page and paste the widget script
4. Send a test message — the AI should respond and create a lead

---

## Architecture Overview

```
Customer Browser
    │
    ├── Web Widget (embeddable JS) ──WebSocket──> Backend (FastAPI)
    │                                              │
    └── Admin Browser (Next.js) ◄──── REST API ◄───┘
                                                   │
                                          ┌────────┴────────┐
                                          │                 │
                                       PostgreSQL        Qdrant
                                       (data)          (vectors)
                                          │
                                     OpenRouter ── AI Providers
                                     (Gemini/GPT)
```

---

## Troubleshooting

**Database connection refused**: Ensure Postgres is running `docker compose up -d postgres`

**Alembic migration fails**: Check `DATABASE_URL` in `.env` matches your local Postgres

**AI not responding**: Verify `OPENROUTER_API_KEY` is set and has credits

**Widget not loading**: Check `NEXT_PUBLIC_WS_URL` matches your backend URL

**Email not received**: Check Mailhog is running at port 1025 and 8025