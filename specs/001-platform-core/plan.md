# Implementation Plan: AgentFlow AI Platform Core

**Branch**: `001-platform-core` | **Date**: 2026-07-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-platform-core/spec.md`

---

## Summary

AgentFlow AI is a multi-tenant SaaS platform that manufactures **Digital FTEs (AI Workers)** — not simple chatbots. Businesses embed a chat widget on their website; the AI Worker conducts natural conversations to qualify leads and book appointments under a supervised Mode 1 (requires human review of drafts) or autonomous Mode 2 (replies directly after meeting graduation thresholds). The system consists of a Next.js frontend, a FastAPI backend, PostgreSQL for data, and Qdrant for vector memory. The MVP covers authentication, supervised/autonomous lead qualification, appointment booking, CRM, analytics dashboards with Digital FTE Performance views, multi-tenant isolation, human escalation based on a Permission Budget policy, and workflow automation.

---

## Technical Context

**Language/Version**: Python 3.12+ (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, SQLAlchemy 2.x (async), Pydantic v2, Next.js 14, TailwindCSS, Shadcn UI, Framer Motion, OpenRouter SDK
**Storage**: PostgreSQL 16+ (Neon in production, local Docker in dev), Qdrant (vector store), S3-compatible for media/assets
**Testing**: pytest, pytest-asyncio, Playwright (e2e)
**Target Platform**: Linux (Docker), Web (Chrome/Firefox/Safari), Mobile-responsive
**Project Type**: Web application — backend API + frontend SPA + AI agent layer
**Performance Goals**: API p95 < 500ms, dashboard load < 3s, AI response < 5s, 100 tenants x 50 concurrent conversations
**Constraints**: Multi-tenant isolation at DB level, JWT auth, HTTPS-only, no hardcoded secrets
**Scale/Scope**: 10 tenants (MVP) → 1,000+ tenants (production). 36 functional requirements, 11 entities, 8 user stories

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status |
|-----------|-------------|--------|
| I. Spec-Driven Dev | spec.md exists before plan.md | ✅ Pass |
| II. Production Architecture | modular, typed APIs, containerized | ✅ Pass — Web app (backend/frontend), containerized, typed |
| III. AI Employee, Not Chatbot | Mode 1 / Mode 2 controls, Graduation Criteria | ✅ Pass — Supervised Mode 1, Graduation checklist tracking, Correction logs |
| IV. Portable by Standard (AIFF) | Model Context Protocol (MCP), Agent Skills, AGENTS.md | ✅ Pass — Built with MCP integrations, versioned Skills, AGENTS.md workspace index |
| V. Modern UX | minimal, responsive, SaaS-grade | ✅ Pass — Next.js, TailwindCSS, Shadcn UI, Framer Motion |
| VI. Security & Safety | Permission Budget check, JWT, RBAC, tenant isolation, env secrets | ✅ Pass — RBAC at auth, strict permission limits, isolation, env-only secrets |
| VII. Scalability | multi-tenant, horizontal scaling, future voice/omnichannel | ✅ Pass — schema-per-tenant isolation, stateless backend, future-ready |
| VIII. Developer Experience | UV, Docker, local dev, documentation, env vars, git workflows | ✅ Pass — UV package manager, Docker Compose, .env templates, conventional commits |

All gates pass. No violations.

---

## Project Structure

### Documentation (this feature)

```text
specs/001-platform-core/
├── plan.md              # This file (/sp.plan output)
├── spec.md              # Feature spec (/sp.specify output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── auth.yaml
│   ├── tenants.yaml
│   ├── leads.yaml
│   ├── conversations.yaml
│   ├── appointments.yaml
│   ├── workflows.yaml
│   └── notifications.yaml
└── checklists/
    └── requirements.md
```

### Source Code (repository root)

```text
# Web application: backend API + frontend SPA

backend/
├── src/
│   ├── main.py                 # FastAPI app entry, CORS, middleware
│   ├── config.py               # Environment config, validation
│   ├── api/                    # API route modules
│   │   ├── __init__.py
│   │   ├── deps.py             # Dependency injection (auth, db, tenant)
│   │   ├── auth.py             # Auth endpoints (login, register, reset, verify)
│   │   ├── tenants.py          # Tenant management (CRUD, settings, autonomy settings)
│   │   ├── users.py            # User management (CRUD, roles)
│   │   ├── leads.py            # Lead management (list, update, notes)
│   │   ├── conversations.py     # Conversation management, messages, corrections
│   │   ├── appointments.py     # Appointment CRUD, availability
│   │   ├── workflows.py        # Workflow CRUD, triggers
│   │   ├── notifications.py   # Notification management
│   │   └── analytics.py        # Dashboard metrics, aggregations, FTE Performance
│   ├── models/                 # SQLAlchemy models (async)
│   │   ├── __init__.py
│   │   ├── base.py             # Declarative base, mixins
│   │   ├── tenant.py           # Autonomy level & graduation settings
│   │   ├── user.py
│   │   ├── customer.py
│   │   ├── lead.py
│   │   ├── conversation.py
│   │   ├── correction.py        # Mode 1 training/proof records (was_edited, human_edited)
│   │   ├── permission_policy.py # Sane default policy engine config
│   │   ├── appointment.py
│   │   ├── workflow.py
│   │   ├── notification.py
│   │   └── audit_log.py
│   ├── schemas/                # Pydantic request/response schemas
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── tenant.py
│   │   ├── user.py
│   │   ├── lead.py
│   │   ├── conversation.py
│   │   ├── correction.py
│   │   ├── permission_policy.py
│   │   ├── appointment.py
│   │   ├── workflow.py
│   │   └── analytics.py
│   ├── services/               # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py     # JWT, password hashing, session management
│   │   ├── ai_service.py       # AI orchestration, tool-calling, context injection
│   │   ├── lead_service.py     # Lead qualification, status management
│   │   ├── booking_service.py  # Slot detection, booking, rescheduling
│   │   ├── workflow_service.py  # Workflow execution, scheduling
│   │   ├── notification_service.py  # Email, notification dispatch
│   │   └── analytics_service.py  # Metrics aggregation, dashboard queries, FTE Performance
│   ├── agents/                 # AI agent pipeline
│   │   ├── __init__.py
│   │   ├── pipeline.py         # Main agent pipeline (checks autonomy_level, filters via PermissionPolicy)
│   │   ├── tools.py            # AI tool definitions (create_lead, check_availability, book_appointment, etc.)
│   │   ├── prompts.py          # System prompts, conversation templates
│   │   └── escalation.py       # Human handoff logic, confidence scoring, Permission Budget checks
│   ├── core/                   # Shared utilities
│   │   ├── __init__.py
│   │   ├── security.py         # RBAC, tenant isolation helpers
│   │   ├── database.py         # Async SQLAlchemy engine, session factory
│   │   ├── email.py            # Email sending (SMTP/SendGrid)
│   │   └── exceptions.py       # Custom exceptions, error handlers
│   └── migrations/             # Alembic migration files
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── unit/                   # Unit tests
│   ├── integration/            # API integration tests
│   └── contract/               # API contract tests
├── alembic.ini
├── pyproject.toml
├── uv.lock
└── Dockerfile

frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── (auth)/             # Auth pages (login, register, reset)
│   │   │   ├── login/
│   │   │   ├── register/       # Onboarding wizard with autonomy_level selection
│   │   │   └── reset-password/
│   │   ├── (dashboard)/        # Protected dashboard pages
│   │   │   ├── layout.tsx      # Dashboard layout with sidebar
│   │   │   ├── overview/       # Main dashboard with Graduation Progress
│   │   │   ├── leads/          # Lead list, lead detail
│   │   │   ├── conversations/   # Conversation history with Mode 1 reply approval workflow
│   │   │   ├── appointments/   # Calendar view, appointment list
│   │   │   ├── workflows/      # Workflow configuration
│   │   │   ├── settings/       # Business settings, AI config, PermissionPolicy thresholds
│   │   │   └── analytics/      # Analytics reports (includes Digital FTE Performance)
│   │   ├── (admin)/            # Super admin pages
│   │   │   ├── tenants/        # Tenant management
│   │   │   ├── platform/       # Platform-wide metrics
│   │   │   └── billing/        # Billing management
│   │   └── api/                # Next.js API routes (optional BFF)
│   ├── components/
│   │   ├── ui/                 # Shadcn UI components
│   │   ├── chat/               # AI chat widget, conversation UI
│   │   ├── dashboard/          # Dashboard-specific components
│   │   └── forms/              # Reusable form components
│   ├── lib/
│   │   ├── api.ts              # API client (fetch wrapper)
│   │   ├── auth.ts             # Auth helpers, token management
│   │   └── utils.ts            # Utility functions
│   ├── hooks/                  # Custom React hooks
│   ├── types/                  # TypeScript types matching backend schemas
│   └── styles/
│       └── globals.css
├── public/
│   └── widget.js              # Embeddable chat widget script
├── package.json
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
└── Dockerfile

docker-compose.yml            # Full stack: backend, frontend, postgres, qdrant
.env.example                  # Environment variable template
```

---

## Mapping Specifications to Implementation Components

### 1. Onboarding Autonomy Setup (US-1)
*   **Backend Model & Settings**: [Tenant](file:///home/waterprooffish99/projects/ai-apointment-setter-lead-qualification-agent/specs/001-platform-core/data-model.md#L36) stores `autonomy_level` (Mode 1 Supervised / Mode 2 Autonomous). Default is `mode_1_supervised`.
*   **Registration Flow**: The signup wizard in `frontend/src/app/(auth)/register/page.tsx` includes a step where the user names their Digital FTE and reviews the supervised vs autonomous settings.
*   **Seeding Sane Defaults**: The `PermissionPolicy` table gets populated on tenant creation with default rules for what can run unsupervised (quoting, FAQs) vs what must be supervised (discounts, refunds, cancellations).

### 2. Autonomy & Supervision Logic (Mode 1 vs Mode 2)
*   **Supervised Mode (Mode 1)**: For incoming chats, the AI pipeline executes tools and drafts a reply, but saves the message in a pending state. Staff reviews it in the Next.js `conversations/` list, can edit the draft, and then sends it.
*   **Autonomy Training Records**: Every draft approval/edit is saved in the [Correction](file:///home/waterprooffish99/projects/ai-apointment-setter-lead-qualification-agent/specs/001-platform-core/data-model.md#L185) table.
*   **Autonomous Mode (Mode 2)**: Once active, the AI pipeline responds to allowed user prompts directly without waiting for a review action.

### 3. Permission Budgets & Safety Filter (US-7)
*   **Interception in Pipeline**: The `backend/src/agents/escalation.py` implements a Permission Budget interceptor.
*   **Rules Evaluation**: When the AI attempts a tool execution (like appointment cancellation or applying a discount) or when sentiment classification logs an angry user, the service compares it against the tenant's `PermissionPolicy`.
*   **Fallback & Handoff**: If a violation is caught, the action is blocked, the AI drafts a polite transition message ("Let me pull in a supervisor for this..."), and the chat status switches to `escalated` in the database, notifying staff.

### 4. Digital FTE Performance Dashboard (US-5)
*   **Dashboard view**: `frontend/src/app/(dashboard)/analytics/page.tsx` features a distinct **Digital FTE Performance** tab.
*   **Metric Computations**:
    *   *Correction Rate*: Percentage of Mode 1 messages that were modified by staff in the `Correction` table.
    *   *Graduation Readiness Tracker*: Compares the number of reviewed conversations and current correction rate against the tenant's graduation thresholds.
    *   *Audit Trails*: Connects directly with the enhanced `AuditLog` records for 2-minute trace resolution (SC-010).

---

## Phase 0: Research

See `research.md` for detailed technology evaluations and decisions.

---

## Phase 1: Design & Contracts

See `data-model.md`, `contracts/`, and `quickstart.md` for detailed outputs.

---

## Complexity Tracking

No complexity violations requiring justification. All specifications align with simpler alternatives.