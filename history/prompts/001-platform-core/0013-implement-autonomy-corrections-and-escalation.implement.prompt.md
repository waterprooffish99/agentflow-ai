---
id: 0013
title: Implement autonomy models, draft auto-logging hook, and permission budget escalation interceptor
stage: implement
date: 2026-07-08
surface: backend
model: Gemini 3.5 Flash (High)
feature: 001-platform-core
branch: 001-platform-core
user: waterprooffish99
command: pytest
labels: ["platform", "autonomy", "corrections", "permission-policy", "escalation", "fastapi"]
links:
  spec: specs/001-platform-core/spec.md
  ticket: specs/001-platform-core/tasks.md
  adr: null
  pr: null
files:
 - backend/app/models/tenant.py
 - backend/app/models/correction.py
 - backend/app/models/permission_policy.py
 - backend/app/models/__init__.py
 - backend/app/schemas/tenant.py
 - backend/app/schemas/correction.py
 - backend/app/schemas/permission_policy.py
 - backend/app/schemas/__init__.py
 - backend/app/services/ai_orchestrator_service.py
 - backend/app/agents/escalation.py
 - backend/app/api/corrections.py
 - backend/app/api/__init__.py
tests:
 - backend/tests/unit/test_digital_fte_models.py
 - backend/tests/unit/test_escalation.py
 - backend/tests/integration/test_corrections_api.py
---

## Prompt

<USER_REQUEST>
Implement T029a, T029b, and T090 exactly as defined in specs/001-platform-core/tasks.md 
(Phase 2 Setup and Phase 9 Escalation) and specs/001-platform-core/plan.md. Follow this 
repo's existing TDD discipline — write failing tests first, then implement, matching the 
style of the existing 30 passing tests. Do not modify any already-completed/verified code 
(billing, async Celery architecture, booking flow) except for the minimal integration 
hooks described below.

STEP 1 — T029a: Correction model
- SQLAlchemy model + Pydantic schema for Correction: id, tenant_id (FK), conversation_id 
  (FK), ai_draft_message (text), human_edited_message (text, nullable), was_edited 
  (bool, nullable — null means "not yet reviewed"), reviewed_by (User FK, nullable), 
  created_at, reviewed_at (nullable).
- Alembic migration for the new table.
- Unit tests for model creation, nullable fields, and tenant isolation.

STEP 2 — T029b: PermissionPolicy model
- SQLAlchemy model + Pydantic schema for PermissionPolicy: id, tenant_id (FK, one-to-one), 
  always_allowed_actions (JSONB list), always_escalate_actions (JSONB list), 
  created_at, updated_at.
- Also add autonomy_level (enum: mode_1_supervised [default], mode_2_autonomous) to the 
  existing Tenant model.
- Seed sensible defaults matching the Permission Budget spec: always_allowed = 
  ["answer_faq", "quote_price", "check_availability", "capture_lead", "propose_slot"]; 
  always_escalate = ["discount_or_refund", "cancellation", "negative_sentiment_detected", 
  "outside_seeded_data"].
- Alembic migration for the new table and the Tenant field.
- Unit tests confirming defaults are created automatically when a new Tenant is created.

STEP 3 — Auto-logging hook (required for both models to be useful)
- Wherever the AI/Celery worker currently produces a final response (do not restructure 
  this pipeline — just add a hook), automatically create a Correction row the moment a 
  draft is generated: ai_draft_message populated immediately, was_edited left null 
  (pending review).
- This must work identically regardless of autonomy_level — Mode 1 and Mode 2 both log 
  every draft; the difference is only whether a human reviews it before send.
- Add a test confirming a Correction row is created for every AI-generated reply, without 
  breaking any of the 30 existing tests.

STEP 4 — T090: Permission Budget escalation interceptor
- In escalation.py, before an AI-proposed action is executed or sent, check the action 
  type against the tenant's PermissionPolicy: if it matches always_escalate_actions, or 
  basic sentiment analysis on the incoming customer message flags frustration/anger, route 
  to human escalation instead of auto-completing the action — this applies even if the 
  tenant is in mode_2_autonomous.
- If the action matches always_allowed_actions, proceed normally.
- Unit tests for both branches (allowed action passes through; escalate-listed action or 
  negative sentiment routes to escalation) using mocked tenant policies.

STEP 5 — Minimal pilot review endpoint (new, small, separate from T065)
- Add ONE simple internal-only endpoint (or a lightweight authenticated admin page if 
  faster) where I can: list pending (unreviewed) Correction rows for a tenant, and mark 
  one as either "sent as-is" (was_edited=false) or "sent edited" with the final text 
  pasted in (was_edited=true, human_edited_message=<text>). Keep this intentionally bare 
  — no design polish, just functional — since the full review UI comes later in T065.
- This is what I'll use during the WhatsApp pilot to log what I actually sent after 
  copy-pasting into WhatsApp manually.

FINISH
- Run the full test suite and confirm all existing 30 tests plus all new tests pass.
- Give me a summary: files changed, migration files created, new test count, and exact 
  steps for me to manually verify in the browser (e.g. send a test chat message, then 
  check the pending Corrections list shows it).
</USER_REQUEST>

## Response snapshot

Successfully implemented the database models, Alembic migrations, draft auto-logging hook, Permission Budget escalation interceptor, and FastAPI pilot review endpoints:
1. Created the `Correction` database model and schemas.
2. Created the `PermissionPolicy` database model and schemas, updated the `Tenant` model with `autonomy_level` and graduation properties, and implemented a SQLAlchemy `init` listener to automatically attach default policies upon Tenant creation.
3. Applied Alembic migrations and successfully stamps `agentflow` database schema at `be8eac7fc050`.
4. Embedded the auto-logging hook in `AIOrchestratorService` to log a pending `Correction` record on every generated response.
5. Created the interceptor logic in `app/agents/escalation.py` for keyword-based negative sentiment detection and tool action restriction, and successfully wired it into `AIOrchestratorService`.
6. Built the `GET /corrections/pending` and `POST /corrections/{id}/review` endpoints.
7. Wrote 8 new tests verifying the full spectrum of behaviors, resulting in a 100% passing test suite (38 out of 38 tests).

## Outcome

- ✅ Impact: Backend infrastructure for Mode 1/Mode 2 Digital FTE worker constraints, auditability, and WhatsApp pilot reviews is fully operational.
- 🧪 Tests: pytest (38 passed)
- 📁 Files: backend/app/models/correction.py, backend/app/models/permission_policy.py, backend/app/models/tenant.py, backend/app/api/corrections.py, backend/app/agents/escalation.py, backend/app/services/ai_orchestrator_service.py
