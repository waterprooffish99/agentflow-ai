# 🧠 AGENTFLOW AI - MASTER PROJECT CONTEXT

## 📌 1. WHAT IS THIS PROJECT?
**AgentFlow AI** is a multi-tenant SaaS platform built for SMBs (salons, clinics, real estate, service businesses).
**Core Value Proposition:** A business owner signs up, configures an AI receptionist via a simple wizard, and the AI handles inbound customer inquiries, qualifies leads, and books appointments autonomously.
**The Goal:** Allow an SMB owner to set this up and pay for it without any technical assistance.

## 🏗️ 2. SYSTEM ARCHITECTURE & TECH STACK
*   **Backend:** Python, FastAPI, SQLAlchemy (Async), PostgreSQL (Multi-tenant schema), Redis (Caching/Rate Limiting), Celery (Background Jobs).
*   **Frontend:** Next.js (React), Tailwind CSS, SaaS Dashboard UI.
*   **AI Orchestration:** OpenRouter API (GPT-4/3.5 default). Custom tool-based orchestration loop natively built in Python (no bloated frameworks like LangChain/LangGraph).
*   **Billing:** Stripe (Subscriptions, Webhooks).
*   **Observability:** OpenTelemetry instrumentation.
*   **Infrastructure:** Dockerized local environment, Alembic migrations.

## ✅ 3. WHAT IS DONE SO FAR (The Current State)
The system is currently **"Engineering Complete"** but not yet **"Market Proven."**
*   **AI Orchestration:** The core AI loop is functional. It supports multi-turn reasoning and tool feedback. The AI can successfully use tools like `capture_lead_info`, `search_knowledge_base`, `check_availability`, `create_booking`, `get_business_services`, and `escalate_to_human`. Token optimization and history windowing (last 10 messages) are implemented.
*   **Onboarding Flow:** A multi-step Next.js wizard successfully captures and persists Business Profile, Services, Availability, FAQs, and AI Configuration to the backend.
*   **CRM & Booking:** Lead qualification, customer tracking, activity timelines, and appointment booking logic are built and connected.
*   **Multi-tenancy:** Data isolation is enforced at the service layer.
*   **API Foundation:** Fully functional REST API with authentication and role-based access.

## 🔴 4. WHAT ARE THE REAL ISSUES & RISKS?
We are at the dangerous phase where the code works in a vacuum, but will likely break upon contact with the real world.
1.  **Billing Robustness (Critical):** The Stripe integration is mostly scaffolding. Webhook verification exists, but robust handling for real-world scenarios (payment failures, cancellations, prorations) is missing. If a payment fails, the system won't automatically lock out the tenant.
2.  **Test Suite Blind Spots (Critical):** The automated integration test suite (`pytest`) is currently failing due to a missing `db_session` fixture. We are flying blind on core business logic regressions (billing, quotas).
3.  **Security/Edge Cases:** If `STRIPE_WEBHOOK_SECRET` is missing, the backend currently bypasses signature verification.
4.  **AI Concurrency/Load:** The AI loop holds the FastAPI request open while waiting for the LLM. Under high traffic, this will exhaust server worker threads.
5.  **UX Friction:** The onboarding flow has been technically fixed, but has not been stress-tested by a non-technical user on a mobile device.

## 🚀 5. WHAT IS LEFT TO DO?
1.  **Fix the Test Suite:** Repair the `db_session` fixture in the backend tests to ensure CI/CD actually protects the codebase.
2.  **Harden Stripe Webhooks:** Implement the exact logic for handling `invoice.payment_failed` and `customer.subscription.deleted` to ensure autonomous revenue protection.
3.  **Real User Pilot (Manual Testing):** Put the system in front of 5 real SMB owners. Watch where they get confused during onboarding. Fix that specific friction.
4.  **Production Infrastructure:** Move from `docker-compose` local testing to a live staging environment (Vercel for Frontend, Render/Render for Backend, managed Postgres).

## 🎯 6. WHAT IS THE RIGHT NEXT MOVE?
**DO NOT BUILD NEW FEATURES.** No new analytics, no new dashboards, no new AI tools.

**The Immediate Next Action:**
Ask the AI to: *"Fix the `db_session` fixture in the backend test suite so we can run our tests, and then help me harden the Stripe webhook handlers for payment failures."* 

Once the tests pass and billing is secure, deploy a staging link and get a real human to try breaking it.
