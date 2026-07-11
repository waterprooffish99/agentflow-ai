---
id: 0011
title: Update platform core data model
stage: spec
date: 2026-07-07
surface: agent
model: Gemini 3.5 Flash (High)
feature: 001-platform-core
branch: 001-platform-core
user: waterprooffish99
command: none
labels: ["platform", "data-model", "autonomy", "corrections", "permission-policy"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-platform-core/data-model.md
tests: []
---

## Prompt

<USER_REQUEST>
now this "# 🗄️ Part 3: Core Data Model & Schema
SQLAlchemy models structured for multi-tenancy and scheduling.
All entities are linked with a `tenant_id` for row-level security and isolation.

### 🧩 Core Entities
1. **Tenant**: Business configuration, subscription tier (`free`, `starter`,
   `growth`, `enterprise`), settings, `autonomy_level` (enum:
   `mode_1_supervised` [default], `mode_2_autonomous`), and graduation
   thresholds (`min_reviewed_conversations`, `max_correction_rate` — plan-tier
   defaults, overridable per tenant).
2. **User**: System users with RBAC (`super_admin`, `business_admin`, `staff`).
3. **Customer**: Customer profiles, unique name/email/phone per tenant.
4. **Lead**: Pipeline transitions: `unqualified` → `partially_qualified` →
   `qualified` → `booked` → `lost`.
5. **Conversation**: Chat sessions. `messages` stores a JSONB array of Message
   objects.
6. **Appointment**: Confirmed bookings. Enforces non-overlapping times,
   timezone-aware.
7. **Workflow**: Automated follow-up sequences (cold lead, confirmations,
   no-shows).
8. **Notification**: Queue for outgoing email, SMS, WhatsApp alerts.
9. **AuditLog**: Full compliance trail. Logs every AI action's type, tool(s)
   called, recommendation made, approving human (if any), and outcome —
   this is what answers SC-010 in under 2 minutes.
10. **Correction** *(new)*: The Mode 1 training/proof record. Fields:
    `conversation_id` (FK), `ai_draft_message`, `human_edited_message`
    (nullable if approved as-is), `was_edited` (bool), `reviewed_by` (User FK),
    `timestamp`. Every supervised reply creates one row here — this is both
    your correction dataset and the raw material for Graduation Criteria.
11. **PermissionPolicy** *(new)*: Per-tenant JSONB config listing
    always-allowed action types vs always-escalate action types, with sane
    defaults from the Permission Budget spec, overridable per tenant.

### 🚦 Entity Relationships Diagram
```
Tenant (1) ──────< User (many)
  │                    │
  ├──< Customer (many)
  │
  ├──< Lead (many) ────── (1) Customer
  │       │
  │       ├──< Conversation (many)
  │       │       │
  │       │       ├──< Message (stored as JSONB)
  │       │       └──< Correction (many)
  │       │
  │       └──< Appointment (many) ──── (1) Customer
  │
  ├──< Workflow (many)
  ├──< Notification (many)
  ├──< PermissionPolicy (1)
  └──< AuditLog (many)
```"
</USER_REQUEST>

## Response snapshot

Successfully updated the Core Data Model Specification at `specs/001-platform-core/data-model.md` to define the database structures for Autonomy levels, graduation thresholds, the new `Correction` tracking entity, the new `PermissionPolicy` rule engine, and enhanced the `AuditLog` structure to enable detailed tracing of tool invocation, recommendations, approvals, and outcomes.

## Outcome

- ✅ Impact: Documented the database schemas, tables, relationships, indexes, and constraints required to support supervised reviews, human correction workflows, autonomy promotions, and permission filters.
- 🧪 Tests: N/A (data model specifications update)
- 📁 Files: specs/001-platform-core/data-model.md
- 🔁 Next prompts: Proceed to implementation tasks planning
