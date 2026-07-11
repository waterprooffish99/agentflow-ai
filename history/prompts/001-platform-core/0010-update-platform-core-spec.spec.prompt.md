---
id: 0010
title: Update platform core spec
stage: spec
date: 2026-07-07
surface: agent
model: Gemini 3.5 Flash (High)
feature: 001-platform-core
branch: 001-platform-core
user: waterprooffish99
command: none
labels: ["platform", "specifications", "autonomy", "supervised", "permission-budget"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - specs/001-platform-core/spec.md
tests: []
---

## Prompt

<USER_REQUEST>
now specifications "# 📝 Part 2: Core Platform Specifications (MVP)
Functional scope, user scenarios, and target metrics.

### 👥 Primary User Scenarios
1. **Business Onboarding (P1)**: Business Admins sign up, configure business
   hours, services, and AI personality. The AI receptionist starts qualifying
   leads within 30 minutes of registration, in Mode 1 (Supervised) by default.
2. **AI Lead Qualification (P1)**: Leads are qualified automatically during
   natural, goal-oriented conversations. AI captures: Name, requested service,
   urgency, location, budget range, and preferred availability.
3. **Appointment Booking (P1)**: The AI checks real-time slot availability and
   confirms bookings directly inside the conversation, creating appointment
   records.
4. **CRM & Lead Management (P2)**: Dashboard and list view to manage customers,
   filter by lead status (`unqualified`, `partially_qualified`, `qualified`,
   `booked`, `lost`), and add manual staff notes.
5. **Analytics & Performance (P2)**: Tracking conversion rates, AI response
   time, escalation rates, correction rates, and customer satisfaction metrics.
6. **AI Escalation & Human Handoff (P2)**: Graceful escalation to a human when
   AI confidence drops, the customer explicitly requests a person, or the
   action falls outside the AI Worker's Permission Budget (see below).
7. **Autonomy Management (P1)**: The Business Admin sets and views the AI
   Worker's `autonomy_level` per tenant (`mode_1_supervised` default, or
   `mode_2_autonomous`). The dashboard shows live Graduation Progress against
   defined criteria, and the admin can manually upgrade or downgrade at any
   time.

### 🔐 Permission Budget & Escalation Policy
- **Always allowed unsupervised** (any autonomy level): answer FAQ/policy
  questions, quote listed service prices, check appointment availability,
  capture lead info, propose booking slots.
- **Always requires human approval** (regardless of autonomy level): discounts
  or refunds, cancellations, any reply where sentiment analysis flags
  frustration/anger, anything outside seeded business data.

### 🎯 Key Performance Targets (Success Criteria)
- **Setup Speed (SC-001)**: Registration to active AI widget takes <30 minutes.
- **Automation Handoff (SC-002)**: 90% of routine booking inquiries complete
  without human escalation.
- **Accuracy (SC-003)**: Required lead fields captured in ≥80% of successful
  interactions.
- **Responsiveness (SC-006)**: API response time <500ms for 95% of requests.
- **Isolation (SC-008)**: Zero cross-tenant data leakage (verified by automated
  tests).
- **Graduation Readiness (SC-009)**: A tenant becomes eligible to request Mode 2
  after ≥50 supervised conversations reviewed, a correction rate <10% over the
  most recent 20 conversations, and zero critical errors (wrong booking, wrong
  price, policy violation) in that window. Defaults configurable per plan tier.
- **Auditability (SC-010)**: For any AI action, the Business Admin can answer
  "what did it do, what did it recommend, who approved it, what happened next"
  from the dashboard in under 2 minutes."
</USER_REQUEST>

## Response snapshot

Successfully updated the Core Platform Specification file at `specs/001-platform-core/spec.md` to incorporate the Autonomy Management metrics, Supervision Mode (Mode 1 Supervised / Mode 2 Autonomous default controls), explicit Permission Budgets, and the new Graduation Readiness criteria and Auditability metrics.

## Outcome

- ✅ Impact: Solidified specifications for implementing multi-step supervised/autonomous workflows, graduation checkpoints, and human-in-the-loop validation metrics.
- 🧪 Tests: N/A (specification modification)
- 📁 Files: specs/001-platform-core/spec.md
- 🔁 Next prompts: Proceed to planning or implementation adjustments
