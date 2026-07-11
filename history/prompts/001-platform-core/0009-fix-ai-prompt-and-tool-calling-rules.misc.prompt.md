---
id: "0009"
title: "Fix AI receptionist system prompt context and tool selection rules"
stage: "misc"
date: "2026-06-15"
surface: "agent"
model: "Gemini 3.5 Flash"
feature: "001-platform-core"
branch: "001-platform-core"
user: "waterprooffish99"
command: "pytest -v"
labels: ["bug-fix", "prompt-engineering", "testing", "ai-orchestration"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/agents/prompts.py
tests:
  - ran test_al_huda_response.py scratch script (passed)
  - pytest integration/unit tests (29/29 passed)
---

## Prompt

We found the root cause of why the AI doesn't know about its own 
business. Please fix it - two specific issues, explained in plain 
English for a non-technical person.

ISSUE 1: The business description ("About" info) is loaded from the 
database but is missing from the system prompt sent to Gemini 
(prompts.py). Please add it - the prompt should include a clear 
sentence like: "Business description: [the About text from the 
database]" so the AI knows what the business actually does/sells.

ISSUE 2: When a customer asks about a PRODUCT or SERVICE (e.g. "do you 
have Balochi dresses?", "what's the price for X?"), the AI incorrectly 
calls search_knowledge_base (FAQs) instead of get_business_services. 
Please update the CORE RULES in the system prompt to make this 
distinction clearer - something like:

"3. If the user asks about a PRODUCT, SERVICE, ITEM, or PRICE the 
business offers (e.g. 'do you have X', 'how much for Y', 'what services 
do you provide'), call `get_business_services` FIRST. Only call 
`search_knowledge_base` for general questions not related to a specific 
product/service (e.g. shipping policy, store hours, customization 
process)."

After making both changes:
1. Restart the backend/Celery worker to apply the new prompt.
2. Re-send the EXACT SAME test message as before: "Assalam o Alaikum, 
   do you have Balochi dresses?" to the same Al Huda Gallery test tenant.
3. Show me the new reply.
4. Run the test suite to confirm nothing broke: cd backend && pytest -v

Give me a simple before/after: "Before: AI said it didn't know. After: 
AI now says [X]."

## Response snapshot

Modified the system prompt template in `backend/app/agents/prompts.py` to:
1. Include the `business_description` parameter.
2. Clarify that product, service, item, and price inquiries should call `get_business_services` first, and `search_knowledge_base` is only for general questions not related to offerings.

Restarted the backend server and Celery worker. Ran the verification script to send the target message. The AI successfully called the `get_business_services` tool and provided a detailed, accurate response listing the Balochi dresses and pricing we seeded. Ran `pytest -v` and confirmed all 29 tests passed.

## Outcome

- ✅ Impact: Successfully corrected AI's behavior. The AI now knows about Balochi dresses and calls the correct tool when asked about services.
- 🧪 Tests: Scratch verification script succeeded; 29/29 unit and integration tests passed.
- 📁 Files: Modified `backend/app/agents/prompts.py`
- 🔁 Next prompts: None
- 🧠 Reflection: Giving the AI a proper business description in the system prompt prevents it from starting blind, and clarifying tool usage rules helps it navigate between catalog queries (services) vs info queries (knowledge base/FAQs).

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): None
