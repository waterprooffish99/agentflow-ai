---
id: 0002
title: Update Constitution to Digital FTE and AIFF Standards
stage: constitution
date: 2026-07-07
surface: agent
model: Gemini 3.5 Flash (High)
feature: none
branch: 001-platform-core
user: waterprooffish99
command: none
labels: ["constitution", "digital-fte", "aiff-standards", "mcp", "autonomy"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests: []
---

## Prompt

<USER_REQUEST>
I want you to update constitution with this "# 🧠 Part 1: AgentFlow AI Constitution
Authoritative rules governing development, quality, safety, and tech stack.

### 📌 Vision & Core Value
AgentFlow AI manufactures **Digital FTEs (AI Workers)** — not chatbots. A business
owner (the **Principal**) registers, configures an AI receptionist through a simple
setup wizard, and hands it real customer-facing work: qualifying leads, answering
questions, and booking appointments.

The product is not "software the business uses" — it is "an employee the business
hires." Every Digital FTE crosses the **FTE Threshold** the day it stops waiting for
a prompt and starts monitoring its domain — tracking leads, following up, replying
around the clock — with the reliability expected of a real team member, always
inside an **authority envelope** the Principal defines and can audit at any time.

### ⚙️ Core Principles
- **Spec-Driven Development First**: Features MUST start with specifications,
  plans, and tasks. All implementation follows: `Constitution → Specifications →
  Plan → Tasks`.
- **Production-Grade Architecture**: Enforces modular architecture, clean
  separation of concerns, row-level multi-tenant isolation, and explicit
  Architectural Decision Records (ADRs).
- **AI Employee, Not a Chatbot**: Every tenant's AI Worker starts in **Mode 1
  (Supervised)** — a human approves every reply before it reaches the customer —
  and only advances to **Mode 2 (Autonomous)** — the AI replies directly,
  unsupervised — once it meets that tenant's **Graduation Criteria** (see
  Specifications → Autonomy Management). Autonomy is earned per tenant. It is
  never a global default.
- **Portable by Standard, Not by Lock-In**: Wherever the AI Worker reaches a tool,
  data source, or channel (calendar, CRM, WhatsApp, payments), it connects through
  **MCP (Model Context Protocol)** rather than one-off custom integrations.
  Business-specific knowledge (catalogs, policies, tone) is packaged as versioned
  **Agent Skills**, not buried in prompt strings. Agent operating instructions
  live in a single **AGENTS.md** per project so any AI coding agent can pick up
  the project with full context. These three — MCP, Agent Skills, AGENTS.md —
  are the AIFF Standards; following them keeps every Digital FTE portable and
  resellable, not locked to one vendor.
- **Modern SaaS UX**: Clean, minimal, mobile-first, and highly responsive.
  Inspired by Vercel, Linear, and Stripe.
- **Security & Safety**: Enforces secure authentication, RBAC, input
  sanitization, and GDPR principles. The AI is grounded in verified business
  context to avoid hallucinations. Every AI action is logged and traceable
  (see AuditLog). Every AI Worker has an explicit **Permission Budget**: actions
  it may always take unsupervised (answer FAQs, quote listed prices, check
  availability) versus actions that always require human approval regardless of
  autonomy level (refunds, discounts beyond policy, cancellations, anything
  directed at an upset customer).
- **Scalability**: Multi-tenant database schema designed to support at least 10
  concurrent businesses with 100+ daily interactions each out-of-the-box.

### 🛠️ Technical Stack
- **Backend**: Python 3.12+, FastAPI (async-first), SQLAlchemy 2.0, PostgreSQL,
  Qdrant (vector database), Pydantic (data validation).
- **Frontend**: Next.js (React), TypeScript, TailwindCSS, Shadcn UI, Framer
  Motion.
- **AI Orchestration**: Direct integration with Gemini/OpenRouter (no bloated
  frameworks like LangChain). Agent instructions and business-context packages
  follow the AGENTS.md and Agent Skills conventions for portability.
- **Infrastructure**: Docker & Docker Compose, GitHub Actions, Vercel (Frontend),
  Render/Railway (Backend), Neon (Production DB).

### 🚫 Non-Negotiables
- Never hardcode secrets or credentials (always use `.env`).
- Never skip input validation or bypass CSRF/CORS checks.
- Never mix business logic into Next.js UI components.
- Never advance a tenant to Mode 2 (Autonomous) without its Graduation Criteria
  being met and logged.
- Never let the AI take an action outside its Permission Budget without human
  approval — regardless of autonomy level."
</USER_REQUEST>

## Response snapshot

Successfully updated the AgentFlow AI Constitution file at `.specify/memory/constitution.md` to reflect the updated vision of "Digital FTEs", the AIFF Standards (MCP, Agent Skills, AGENTS.md), and stricter controls around tenant Autonomy and Permission Budgets. Cleanly merged new content with prior developer rules (Code Quality, Git, Governance), bumped semantic version to `1.1.0`, and recorded prompt history details.

## Outcome

- ✅ Impact: Solidified the platform's vision as an autonomous worker engine rather than simple chat software, ensuring portability and safety standards are built into the constitution.
- 🧪 Tests: N/A
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: None
