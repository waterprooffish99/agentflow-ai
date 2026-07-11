# Research: AgentFlow AI Platform Core

## Tech Stack Decisions

### Backend: Python 3.12+ with FastAPI

**Decision**: Python 3.12 (asyncio-native), FastAPI 0.115+, SQLAlchemy 2.0 (async), Pydantic v2.

**Rationale**: FastAPI provides the fastest path to typed async APIs with OpenAPI auto-generation. Python 3.12's improved async performance and free-threading benefits AI-heavy workloads. SQLAlchemy 2.0 async removes the event loop blocking that plagued sync ORMs. Pydantic v2 is 50x faster than v1 and integrates natively with FastAPI.

**Alternatives considered**:
- Node.js/Express: Rejected — Python has superior AI SDK ecosystem and async ML tooling
- Go: Rejected — slower development velocity for AI integration, less mature web framework ecosystem
- Django: Rejected — synchronous by default, requires额外 work for async AI workloads

### Frontend: Next.js 14 (App Router) + TypeScript + TailwindCSS

**Decision**: Next.js 14 with App Router, TypeScript strict mode, TailwindCSS, Shadcn UI, Framer Motion.

**Rationale**: Next.js App Router provides server components for optimal dashboard performance. TypeScript ensures frontend-backend type consistency via shared schema definitions. TailwindCSS + Shadcn UI delivers Vercel/Linear-quality UX at a fraction of the cost. Framer Motion adds the subtle polish that differentiates SaaS products.

**Alternatives considered**:
- Vite + React: Rejected — no SSR for dashboard, weaker routing, less ecosystem
- Nuxt.js: Rejected — smaller ecosystem, less optimal for pure SPA dashboard
- plain React: Rejected — too much boilerplate for a complex dashboard

### AI Provider: OpenRouter as Unified Gateway

**Decision**: OpenRouter SDK with provider abstraction. Primary: Gemini 2.0 Flash. Fallback: GPT-4o. Future: Claude 3.5.

**Rationale**: OpenRouter provides a unified API gateway that abstracts away provider-specific quirks and supports model switching without code changes. Gemini 2.0 Flash offers the best price-performance for high-volume conversational AI. Provider abstraction means a single bad release from one provider does not break the platform.

**Alternatives considered**:
- Direct OpenAI API: Rejected — vendor lock-in, no model flexibility
- Direct Google AI: Rejected — no unified gateway for multi-model support
- Azure AI: Rejected — higher cost, slower deployment, more complexity

### Database: PostgreSQL 16 (Neon) + Qdrant

**Decision**: PostgreSQL via Neon (serverless) for production, local Docker Postgres for dev. Qdrant (Docker) for vector storage and AI memory.

**Rationale**: Neon provides serverless PostgreSQL with branching and auto-scaling — ideal for a multi-tenant SaaS. Qdrant is the best open-source vector database with mature Rust implementation, excellent filtering, and simple Docker deployment. The combination covers all structured data and AI memory needs.

**Alternatives considered**:
- MySQL: Rejected — weaker JSON support, inferior for complex tenant queries
- MongoDB: Rejected — less structured, harder to enforce schema constraints for multi-tenant
- Pinecone: Rejected — managed-only, higher cost at scale, less control

### Containerization: Docker Compose (dev) + Multi-stage Dockerfiles

**Decision**: Docker Compose orchestrates all services (backend, frontend, postgres, qdrant, mailhog for dev email). Multi-stage Dockerfiles for minimal production images.

**Rationale**: Docker Compose provides the fastest local development experience with hot-reload. Multi-stage builds keep production images minimal. No Kubernetes for MVP — Render handles orchestration.

**Alternatives considered**:
- Kubernetes: Rejected — overkill for MVP; adds operational complexity without immediate benefit
- Docker Compose in production: Rejected — Render handles scaling; keep compose for dev only

### Authentication: JWT with Refresh Tokens

**Decision**: JWT access tokens (24h expiry) + HTTP-only refresh tokens (30d expiry) stored in httpOnly cookies. Password hashing via argon2-cffi.

**Rationale**: Standard JWT pattern for stateless API auth. argon2 is the best available password hashing (winner of Password Hashing Competition). HTTP-only cookies prevent XSS token theft. Short access token expiry limits damage from token leakage.

**Alternatives considered**:
- Sessions: Rejected — doesn't scale well for stateless microservices
- OAuth2/OIDC: Rejected for MVP — adds complexity; JWT covers the use case

---

## AI Agent Pipeline Design

### Pipeline Architecture

```
1. Receive message → validate input
2. Classify intent → determine action type (qualify, book, cancel, faq, escalate)
3. Retrieve business context → fetch tenant settings, hours, services, staff, past history from DB
4. Execute workflow → run AI with tools + context
5. Store memory → log conversation to DB, update lead, store vectors in Qdrant
6. Respond → stream response back to customer
```

### Tool Definitions

| Tool | Purpose | Parameters |
|------|---------|------------|
| create_lead | Create/update lead record | name, email, phone, service, urgency, location, budget, availability |
| check_availability | Check open slots | date_range, service_type, duration |
| book_appointment | Create appointment | customer_id, slot, service_type, notes |
| reschedule_appointment | Update appointment time | appointment_id, new_slot |
| cancel_appointment | Cancel with notification | appointment_id, reason |
| send_notification | Email/SMS customer | customer_id, template, channel |
| log_note | Add CRM note | lead_id, content |
| escalate | Flag for human handoff | conversation_id, reason, priority |
| get_lead_history | Retrieve lead context | customer_id |

### Context Injection

At conversation start and every 5 messages, inject: business name, timezone, hours (with current time context), services offered, staff names/roles, FAQ answers, any pending appointments for this customer.

---

## Multi-Tenant Isolation Strategy

**Decision**: Row-level isolation with `tenant_id` foreign key on all tables. Database-level enforcement viaRLS (Row-Level Security) policies. Future: schema-per-tenant for stricter isolation when scaling.

**Rationale**: Row-level isolation with RLS provides strong tenant boundaries without the operational overhead of multiple schemas. All queries automatically filter by tenant_id via a request dependency. Schema-per-tenant can be added as a future migration.

**Implementation**: Every API endpoint injects `tenant_id` from the authenticated user's session. The `deps.py` dependency creates a scoped database session that enforces RLS automatically. No application code should ever query without tenant context.

---

## API Design Patterns

### REST Conventions

- `GET /api/v1/leads` — list (with pagination, filtering)
- `GET /api/v1/leads/{id}` — get single
- `POST /api/v1/leads` — create
- `PATCH /api/v1/leads/{id}` — update
- `DELETE /api/v1/leads/{id}` — soft delete (status change)

### Pagination

All list endpoints use cursor-based pagination for efficiency at scale.

```
GET /api/v1/leads?cursor=<opaque>&limit=20&status=qualified
Response: { data: [...], next_cursor: "...", has_more: true }
```

### Error Responses

All errors follow a consistent structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Email address is invalid",
    "field": "email",
    "request_id": "req_abc123"
  }
}
```

### WebSocket for Live Chat

For the chat widget, use WebSocket (Socket.IO) for real-time bidirectional communication. The AI processes messages asynchronously; responses stream back via the WebSocket connection.

---

## Key Non-Functional Decisions

### Performance Budget

- API p95 < 500ms: Achieved via async FastAPI + PostgreSQL connection pooling (25 connections)
- AI response < 5s: Achieved via OpenRouter streaming + prompt caching
- Dashboard < 3s: Achieved via Next.js server components + aggressive caching
- Calendar updates < 10s: Achieved via optimistic UI updates + background job confirmation

### Security Posture

- All API routes require authentication except `/api/v1/auth/*`
- RBAC enforced at both API layer (FastAPI dependencies) and DB layer (RLS)
- CORS configured to only allow frontend origins
- Rate limiting: 100 req/min per tenant for AI endpoints (prevent abuse)
- Input validation on every endpoint via Pydantic schemas
- SQL injection prevented via SQLAlchemy ORM (no raw SQL)

### Observability

- Structured JSON logging (structlog)
- Request ID propagation for distributed tracing
- Key metrics: API latency, AI response time, booking conversion rate, escalation rate
- Health check endpoints: `/health` (basic), `/health/ready` (DB + AI connectivity)

---

## Future-Proofing Decisions

| Future Feature | Design Decision |
|--------------|-----------------|
| Voice AI | Agent pipeline is input-agnostic; voice becomes a new input adapter |
| WhatsApp | Conversation layer is channel-agnostic; add WhatsApp adapter |
| RAG Knowledge Base | Qdrant already deployed; add document ingestion workflow |
| Vector Memory | Qdrant stores conversation embeddings; retrieval at context injection step |
| Payments | Appointment entity has `payment_status` field预留; notification service handles receipts |