# Tasks: AgentFlow AI Platform Core

**Input**: Design documents from `/specs/001-platform-core/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/, research.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Initialize both backend and frontend repositories with proper tooling.

- [ ] T001 Create backend directory structure per plan.md (`backend/src/` with api, models, schemas, services, agents, core subdirs)
- [ ] T002 [P] Initialize backend Python project with `uv init` and add FastAPI, SQLAlchemy 2.x async, Pydantic v2, uvicorn, alembic, pytest-asyncio, argon2-cffi, python-jose, structlog, httpx, openrouter-sdk dependencies to pyproject.toml
- [ ] T003 [P] Initialize frontend Next.js 14 project with TypeScript: `npx create-next-app@latest frontend --typescript --tailwind --app --no-src-dir --import-alias "@/*" --no-eslint`
- [ ] T004 [P] Configure frontend dependencies: install shadcn-ui, framer-motion, @tanstack/react-query, zustand, zod, date-fns, recharts, socket.io-client
- [ ] T005 [P] Initialize Shadcn UI: run `npx shadcn@latest init` with defaults, add components: button, input, label, card, dialog, dropdown-menu, select, table, tabs, badge, avatar, separator, toast, calendar, form
- [ ] T006 Configure backend linting: add ruff, mypy, pre-commit with configs for pyproject.toml
- [ ] T007 Configure frontend linting: add ESLint, Prettier configs and scripts in package.json
- [ ] T008 Create `.env.example` at project root with all required environment variables (DATABASE_URL, QDRANT_URL, JWT_SECRET, SMTP_*, OPENROUTER_API_KEY, FRONTEND_URL, etc.)
- [ ] T009 Create `docker-compose.yml` at project root defining services: postgres (image: postgres:16-alpine), qdrant (image: qdrant/qdrant:latest), mailhog (image: mailhog/mailhog:latest), backend, frontend
- [ ] T010 [P] Create backend Dockerfile (multi-stage: builder + production) in `backend/Dockerfile`
- [ ] T011 [P] Create frontend Dockerfile (multi-stage) in `frontend/Dockerfile`
- [ ] T012 Initialize GitHub Actions workflow in `.github/workflows/ci.yml` with pytest, type check, lint, and Playwright e2e stages
- [ ] T013 Add `.gitignore` files to backend/ and frontend/ (use GitHub python-gitignore and node-gitignore)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story implementation.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [ ] T014 [P] Create `backend/src/core/database.py` with async SQLAlchemy engine, session factory, Alembic setup, and tenant-scoped session dependency
- [ ] T015 [P] Create `backend/src/core/config.py` with Pydantic Settings, env var validation, type casting for all .env vars
- [ ] T016 [P] Create `backend/src/models/base.py` with DeclarativeBase, TimestampMixin, UUID primary keys, tenant_id mixin
- [ ] T017 Create `backend/src/models/tenant.py` — Tenant model with business_name (unique, indexed), domain, timezone, subscription_tier, status, settings (JSONB), autonomy_level (enum), and graduation thresholds
- [ ] T018 Create `backend/src/models/user.py` — User model with tenant_id (nullable for super_admin), email (unique indexed), password_hash, role (super_admin/business_admin/staff), status, email_verified, last_login
- [ ] T019 [P] Create `backend/src/core/security.py` with RBAC dependency, tenant isolation helper, password hashing (argon2), JWT token creation/validation
- [ ] T020 Create `backend/src/core/exceptions.py` with custom exception classes (HTTPException subclasses with consistent error codes), global exception handler for FastAPI app
- [ ] T021 Create `backend/src/core/email.py` with async email sending via SMTP (dev) / SendGrid (prod), email templates for verification, password reset, booking confirmation
- [ ] T022 Create `backend/src/api/deps.py` with dependency injection: get_db (tenant-scoped), get_current_user (JWT), require_role (RBAC), get_tenant
- [ ] T023 [P] Create `backend/src/schemas/` base schemas: ErrorResponse, PaginatedResponse, CursorPagination
- [ ] T024 Create `backend/src/api/auth.py` with endpoints: POST /auth/register (create tenant + user, send verification email), POST /auth/verify-email, POST /auth/login (JWT), POST /auth/refresh, POST /auth/logout, POST /auth/reset-password-request, POST /auth/reset-password-confirm
- [ ] T025 [P] Create `backend/src/services/auth_service.py` implementing: tenant creation (seeding default PermissionPolicy), user registration, email verification token, JWT access/refresh token generation, password reset flow, argon2 password hashing
- [ ] T026 [P] Create `backend/src/services/notification_service.py` with email sending, notification record creation, retry logic for failed sends
- [ ] T027 Configure Alembic: create `backend/alembic.ini`, create `backend/src/migrations/` with env.py and initial migration generating all base tables
- [ ] T028 Create `backend/src/main.py` with FastAPI app initialization: CORS middleware (allow frontend origin), rate limiting middleware, request ID middleware, structured logging, all routers included, health check endpoints (/health, /health/ready)
- [ ] T029 [P] Create core models: `backend/src/models/customer.py`, `backend/src/models/lead.py`, `backend/src/models/conversation.py`, `backend/src/models/appointment.py`, `backend/src/models/workflow.py`, `backend/src/models/notification.py`, `backend/src/models/audit_log.py`
- [x] T029a [P] Create `backend/src/models/correction.py` — Mode 1 reply review records tracking human message edits
- [x] T029b [P] Create `backend/src/models/permission_policy.py` — Tenant action budgets configuration mapping always-allowed actions vs human-required escalations
- [ ] T030 Create `backend/src/models/__init__.py` exporting all models (including Correction and PermissionPolicy) for clean imports
- [ ] T031 [P] Create Pydantic schemas: auth.py, tenant.py, user.py, lead.py, conversation.py, correction.py, permission_policy.py, appointment.py, workflow.py, notification.py, analytics.py
- [ ] T032 Create `backend/src/api/tenants.py` with endpoints: GET /tenants/me, PATCH /tenants/me (update settings, autonomy settings, graduation configurations), GET /admin/tenants (super admin), POST /admin/tenants/{id}/suspend, GET /admin/platform-metrics
- [ ] T033 [P] Create `backend/src/api/users.py` with: GET /users, GET /users/{id}, PATCH /users/{id}, POST /users/invite
- [ ] T034 [P] Create `backend/src/api/leads.py` with: GET /leads, POST /leads, GET /leads/{id}, PATCH /leads/{id}, POST /leads/{id}/notes, POST /leads/{id}/assign
- [ ] T035 [P] Create `backend/src/api/conversations.py` with: GET /conversations, GET /conversations/{id}, POST /conversations/{id}/close, POST /conversations/{id}/escalate, POST /conversations/{id}/approve-reply (for Mode 1 supervised workflow), POST /api/v1/widget/conversations/{tenant_id}/send
- [ ] T036 [P] Create `backend/src/api/appointments.py` with: GET /appointments/availability, GET /appointments, POST /appointments, GET /appointments/{id}, PATCH /appointments/{id}, POST /appointments/{id}/cancel, POST /appointments/{id}/reschedule, POST /appointments/{id}/complete, POST /appointments/{id}/no-show
- [ ] T037 [P] Create `backend/src/api/workflows.py` with: GET /workflows, POST /workflows, GET /workflows/{id}, PATCH /workflows/{id}, DELETE /workflows/{id}, POST /workflows/{id}/trigger, GET /workflows/{id}/executions
- [ ] T038 [P] Create `backend/src/api/notifications.py` with: GET /notifications, POST /notifications/{id}/retry
- [ ] T039 [P] Create `backend/src/api/analytics.py` with: GET /analytics/dashboard (tenant metrics: total leads, booking rate, conversations, conversion rate, correction rate, missed leads), GET /analytics/ai-metrics (response time, escalation rate, correction rate, satisfaction)
- [ ] T040 Create `backend/src/api/__init__.py` importing and including all routers in main.py
- [ ] T041 Create `frontend/src/types/` with TypeScript interfaces matching all backend Pydantic schemas (including Correction and PermissionPolicy)
- [ ] T042 [P] Create `frontend/src/lib/api.ts` with fetch wrapper supporting: auth headers, JWT token refresh on 401, error handling, request/response typing
- [ ] T043 [P] Create `frontend/src/lib/auth.ts` with: token storage, login/logout/register helpers, auth context provider
- [ ] T044 Create `frontend/src/app/(auth)/layout.tsx` with auth layout
- [ ] T045 Create `frontend/src/app/(auth)/login/page.tsx` with email/password login form
- [ ] T046 Create `frontend/src/app/(auth)/register/page.tsx` with business signup form including setup parameters for naming the AI Worker and reviewing the default Mode 1 (Supervised) onboarding configuration
- [ ] T047 Create `frontend/src/app/(auth)/reset-password/page.tsx` with password reset request and confirm forms
- [ ] T048 Create `frontend/src/app/(dashboard)/layout.tsx` with sidebar navigation, responsive collapse, auth guard
- [ ] T049 Create `frontend/src/components/dashboard/Sidebar.tsx` with navigation links, tenant name, user avatar, logout button
- [ ] T050 Create `frontend/src/components/ui/` wrappers for all shadcn components

**Checkpoint**: Foundation ready — auth, database, API, frontend auth pages, and navigation all working.

---

## Phase 3: User Story 1 - Business Onboarding (Priority: P1) 🎯 MVP

**Goal**: A business admin can sign up, configure their AI receptionist, and have it active and responding to test inquiries within 30 minutes, defaulting to Mode 1 (Supervised).

**Independent Test**: Create a new business account, configure AI settings, embed the widget script on a test page, send a test message, and verify the AI drafts a pending reply and creates a lead record.

### Implementation for User Story 1

- [ ] T051 [P] [US1] Create `backend/src/services/ai_service.py` with OpenRouter client initialization, provider abstraction layer, streaming response support, and context injection from tenant settings.
- [ ] T052 [P] [US1] Create `backend/src/agents/tools.py` with AI tool definitions (create_lead, check_availability, book_appointment, send_notification, log_note, escalate).
- [ ] T053 [P] [US1] Create `backend/src/agents/prompts.py` with system prompt template, lead qualification prompt, booking confirmation prompt, escalation prompt, and FAQ handling prompt.
- [ ] T054 [US1] Create `backend/src/agents/pipeline.py` implementing the main agent pipeline: receive message → validate input → check autonomy_level → classify intent → retrieve business context → execute tools → store memory → draft/send response.
- [ ] T055 [US1] Create `backend/src/agents/escalation.py` with confidence scoring, explicit human request detection, escalation triggers, and staff notifications.
- [ ] T056 [US1] Create `backend/src/services/lead_service.py` with lead creation, status qualification, lead merging, and conversation summary generation.
- [ ] T057 [US1] Create `backend/src/services/booking_service.py` with slot detection, overlap prevention, appointment creation, and timezone-aware handling.
- [ ] T058 [US1] Create `backend/src/services/analytics_service.py` with real-time dashboard aggregation and Digital FTE Performance calculators.
- [ ] T059 [US1] Create `backend/src/services/workflow_service.py` with workflow trigger evaluation and delayed action queues.
- [ ] T060 [US1] Update `/api/v1/widget/conversations/{tenant_id}/send` in `backend/src/api/conversations.py` to invoke the AI pipeline, draft a reply if supervised, or send directly if autonomous.
- [ ] T061 [US1] Create WebSocket endpoint `/api/v1/ws/chat/{tenant_id}` for real-time bidirectional chat.
- [ ] T062 [US1] Create `frontend/src/components/chat/ChatWidget.tsx` with chat bubble floating UI, message history, text input, and loading states.
- [ ] T063 [US1] Create `frontend/public/widget.js` — embeddable JavaScript that injects the chat widget and handles connection parameters.
- [ ] T064 [US1] Create `frontend/src/app/(dashboard)/overview/page.tsx` with metrics cards, recent conversations, and a live Graduation Progress panel (SC-009).
- [ ] T065 [US1] Create `frontend/src/app/(dashboard)/settings/page.tsx` with business hours config, services offered, staff, AI settings, embed code, and the `autonomy_level` selection step (Mode 1 Supervised / Mode 2 Autonomous toggle).
- [ ] T066 [US1] Create `frontend/src/app/(dashboard)/leads/page.tsx` with lead list table, status filter tabs, date filter, and assignee filter.
- [ ] T067 [US1] Create `frontend/src/app/(dashboard)/leads/[id]/page.tsx` with lead detail view, customer info, conversation timeline, appointments, notes, and manual status tools.

**Checkpoint**: User Story 1 complete — AI receptionist is live in Supervised Mode, business can sign up, configure, and receive qualified leads.

---

## Phase 4: User Story 2 - AI Lead Qualification (Priority: P1)

**Goal**: AI captures all 6 lead fields in at least 80% of conversations, with lead records created and visible in the CRM.

**Independent Test**: Simulate a customer conversation via the widget — AI captures all fields — verify the resulting lead record in the backend has all 6 fields correctly populated and the lead status is qualified.

- [ ] T068 [P] [US2] Create `backend/src/services/customer_service.py` with customer creation, deduplication, and customer lookup.
- [ ] T069 [US2] Update `backend/src/agents/prompts.py` lead qualification prompt to ensure all 6 fields are collected with proper validation.
- [ ] T070 [US2] Update `backend/src/agents/pipeline.py` to validate lead qualification completeness before marking lead as qualified.
- [ ] T071 [US2] Create `frontend/src/app/(dashboard)/conversations/page.tsx` with conversation lists showing reviewed vs pending drafts.
- [ ] T072 [US2] Create `frontend/src/app/(dashboard)/conversations/[id]/page.tsx` with message timeline, draft editor, and single-click approval button (`approve-reply`) for supervised replies, logging results in Correction table.

**Checkpoint**: User Story 2 complete — lead qualification rate measurable and visible.

---

## Phase 5: User Story 3 - Appointment Booking (Priority: P1)

**Goal**: Customers can complete a full booking from first message to confirmation in under 5 minutes, with appointment records created and visible in the calendar.

**Independent Test**: Submit a booking request through the AI chat, verify the appointment is created, confirmation email sent, and calendar updated.

- [ ] T073 [P] [US3] Create `frontend/src/app/(dashboard)/appointments/page.tsx` with calendar view, appointment list, and status filters.
- [ ] T074 [P] [US3] Create `frontend/src/components/dashboard/AppointmentCalendar.tsx` with month grid calendar.
- [ ] T075 [US3] Create `frontend/src/app/(dashboard)/appointments/[id]/page.tsx` with appointment details, reschedule, cancel, and complete buttons.
- [ ] T076 [US3] Update booking confirmation flow: ensure AI confirms booking with date/time, creates appointment record, sends email notification, updates lead status to booked.

**Checkpoint**: User Story 3 complete — booking flow end-to-end works, calendar shows appointments.

---

## Phase 6: User Story 4 - CRM & Customer Management (Priority: P2)

**Goal**: Business can manage all customer relationships from a unified CRM view with lead history, notes, and status tracking.

**Independent Test**: Create customer records manually, update lead status through the CRM, add notes, and verify history persists correctly across all views.

- [ ] T077 [P] [US4] Enhance lead detail page with customer merge capability, duplicate detection alerts, follow-up scheduling, and bulk status updates.
- [ ] T078 [US4] Create `frontend/src/app/(dashboard)/customers/page.tsx` with customer list and search by name/email/phone.
- [ ] T079 [US4] Create `frontend/src/app/(dashboard)/customers/[id]/page.tsx` with customer profile and tabbed views for leads, appointments, and conversations.
- [ ] T080 [US4] Create `frontend/src/components/dashboard/LeadStatusTimeline.tsx` showing status transitions with timestamps and actor (AI vs staff).

**Checkpoint**: User Story 4 complete — CRM is fully functional for customer management.

---

## Phase 7: User Story 5 - Business Dashboard & Analytics (Priority: P2)

**Goal**: Business admin sees real-time metrics updated within 5 minutes of any event, with date range filtering and Digital FTE Performance analytics.

**Independent Test**: Generate a dashboard report with test data, verify all metrics are calculated correctly and displayed without errors.

- [ ] T081 [P] [US5] Create `frontend/src/app/(dashboard)/analytics/page.tsx` with date range selector, key metrics cards, and a specialized **Digital FTE Performance** view displaying reviewed chats, correction rates (from Correction table), and graduation readiness indicators (SC-009).
- [ ] T082 [P] [US5] Create `frontend/src/components/dashboard/AnalyticsChart.tsx` with line charts for trends and bar charts for comparisons.
- [ ] T083 [US5] Create `frontend/src/components/dashboard/MissedLeadRecovery.tsx` with list of unconverted leads, reasons, and recovery actions.
- [ ] T084 [US5] Create export functionality generating a structured CSV/JSON summary of dashboard metrics.

**Checkpoint**: User Story 5 complete — analytics dashboard is data-rich and actionable.

---

## Phase 8: User Story 6 - Multi-Tenant Platform Management (Priority: P2)

**Goal**: Platform super admin can manage all tenants, monitor system health, and handle billing from a single interface.

**Independent Test**: Create multiple business tenants, assign different subscription tiers, and verify each tenant only sees their own data while the super admin sees all.

- [ ] T085 [P] [US6] Create `frontend/src/app/(admin)/layout.tsx` with admin-specific sidebar.
- [ ] T086 [P] [US6] Create `frontend/src/app/(admin)/tenants/page.tsx` with tenant list table, status filter tabs, search, and suspend/reactivate actions.
- [ ] T087 [US6] Create `frontend/src/app/(admin)/tenants/[id]/page.tsx` with tenant overview, Settings view, usage logs, and billing controls.
- [ ] T088 [US6] Create `frontend/src/app/(admin)/platform/page.tsx` with platform-wide aggregate metrics and per-tenant drill-down tables.
- [ ] T089 [US6] Update analytics service to compute platform-wide aggregates for super admin queries.

**Checkpoint**: User Story 6 complete — platform admin has full visibility and control.

---

## Phase 9: User Story 7 - AI Escalation & Human Handoff (Priority: P2)

**Goal**: AI Worker handles safety rules and escalates conversations to human staff when confidence is low, customer requests human, or actions fall outside the Permission Budget.

**Independent Test**: Trigger escalation scenarios (unclear intent, customer requests human, or tool call violating PermissionPolicy) and verify escalation fires, staff is notified, and handoff occurs smoothly.

- [x] T090 [P] [US7] Enhance `backend/src/agents/escalation.py` with: confidence thresholds, auto-assignment to available staff, and a **Permission Budget interceptor** validating all tool calls or user sentiment against the tenant's `PermissionPolicy`.
- [ ] T091 [US7] Create `frontend/src/components/dashboard/EscalationBanner.tsx` with in-conversation escalation indicator.
- [ ] T092 [US7] Update conversation page to show escalation status, allow staff replies, and enable staff to mark resolved and resume AI.
- [ ] T093 [US7] Implement in-app escalation notifications via Socket.IO real-time triggers.

**Checkpoint**: User Story 7 complete — human escalation and Permission Budget guardrails work reliably.

---

## Phase 10: User Story 8 - AI Workflow Automation (Priority: P3)

**Goal**: Business admin can configure automated workflows (follow-up reminders, no-show recovery, cold-lead re-engagement) and the AI executes them without manual intervention.

**Independent Test**: Create a follow-up workflow, trigger it with a test appointment, and verify the automated message is sent at the scheduled time with correct content.

- [ ] T094 [P] [US8] Create `frontend/src/app/(dashboard)/workflows/page.tsx` with workflow list and trigger configs.
- [ ] T095 [P] [US8] Create `frontend/src/app/(dashboard)/workflows/new/page.tsx` with workflow builder forms.
- [ ] T096 [US8] Implement workflow execution engine: evaluate triggers, schedule delayed actions, execute, retry, and log execution results.
- [ ] T097 [US8] Create `frontend/src/app/(dashboard)/workflows/[id]/page.tsx` with workflow details, execution history logs, and edit configuration page.

**Checkpoint**: User Story 8 complete — workflow automation is configurable and reliably executing.

---

## Phase 11: Polish & Cross-Cutting Concerns

- [ ] T098 [P] Add comprehensive logging to all services with structured JSON (structlog) including request_id, tenant_id, user_id, action, duration_ms.
- [ ] T099 [P] Add request ID propagation across all API layers.
- [ ] T100 Add health check endpoint `/health/ready` that verifies database connectivity, Qdrant connectivity, and AI provider availability.
- [ ] T101 [P] Implement rate limiting (100 req/min per tenant for AI endpoints, 1000 req/min for standard APIs).
- [ ] T102 Add CORS configuration to only allow the configured frontend URL, reject all other origins.
- [ ] T103 [P] Add input sanitization middleware.
- [ ] T104 Create `backend/src/core/audit.py` that auto-logs all state-changing operations and AI actions to the AuditLog table.
- [ ] T105 [P] Optimize database queries (indexing, pagination, eager loading).
- [ ] T106 Add API versioning with `/api/v1/` prefix.
- [ ] T107 Update frontend `next.config.js` with image optimization and security headers.
- [ ] T108 Create comprehensive `.env.example` at root.
- [ ] T109 Add README.md at project root.
- [ ] T110 [P] Polish UI across all pages with spacing, typography, skeletons, empty states, and toasts.
- [ ] T111 Add mobile responsive styles for tables, widgets, and menus.
- [ ] T112 Run quickstart.md validation to verify setup instructions.

---

## Phase 12: Live Customer Optimization & PMF Refinement (Priority: P2)

**Goal**: Refine customer activation, retention, and operational visibility using production-safe analytical insights.

*(⚠️ DO NOT MODIFY: Already implemented and verified task items)*

- [x] T113 [P] Create modular analytics infrastructure: `backend/app/services/analytics/` package and `utils.py` for tenant isolation
- [x] T114 [P] Implement `ActivationAnalyticsService` for time-to-first-value and bottleneck tracking
- [x] T115 [P] Implement `RetentionAnalyticsService` for cohort analysis and churn-risk detection
- [x] T116 [P] Implement `SupportAnalyticsService` for issue clustering and friction pattern detection
- [x] T117 [P] Implement `PMFLearningService` for vertical success and feature correlation
- [x] T118 [P] Implement `ConversionAnalyticsService` for trial-to-paid funnel tracking
- [x] T119 [P] Implement `OperationalInsightsService` for platform health and anomaly detection
- [x] T120 Integrate modular analytics into API: `/api/v1/analytics/` (tenant-scoped) and `/api/v1/admin/insights/` (platform-wide)
- [x] T121 [P] Create frontend Admin Insights Dashboard to visualize activation, retention, and platform health
- [x] T122 [P] Create frontend Tenant Analytics views for activation and conversion probability

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion — **BLOCKS all user stories**
- **Phase 3 (US1 Onboarding + AI Core)**: Depends on Phase 2 — delivers **MVP**
- **Phase 4–10 (US2–US8)**: All depend on Phase 2; US1 is recommended before US2–US5 for logical flow
- **Phase 11 (Polish)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Depends On | Independent Test |
|-------|-----------|-----------------|
| US1 — Onboarding + AI Core | Phase 2 | Create account → configure AI/autonomy → chat → draft created |
| US2 — Lead Qualification | Phase 2 + US1 (AI pipeline) | AI captures all 6 fields → lead record complete |
| US3 — Appointment Booking | Phase 2 + US1 (booking service) | Request → slot → confirm → appointment created |
| US4 — CRM | Phase 2 + US1 (lead model) | Create/merge leads, add notes, update status |
| US5 — Dashboard & Analytics | Phase 2 + US1 (analytics service) | View metrics & Digital FTE Performance → verify |
| US6 — Multi-Tenant Admin | Phase 2 | Manage tenants → verify isolation |
| US7 — Escalation | Phase 2 + US1 (AI pipeline) | Trigger escalation or budget breach → staff notification |
| US8 — Workflow Automation | Phase 2 + US3 (appointments) | Create workflow → trigger → verify execution |