---
id: 0012
title: Fix Create Booking Tool Customer Association
stage: general
date: 2026-06-16
surface: agent
model: Gemini 3.5 Flash
feature: none
branch: 001-platform-core
user: waterprooffish99
command: none
labels: [booking, database, lead-qualification, tools]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/services/ai_orchestrator_service.py
  - backend/app/core/config.py
tests:
  - backend/tests
---

## Prompt

During a live chat test, the AI understood the booking request correctly 
and attempted to create a fitting appointment for June 20th at 3 PM - 
but then said "I'm unable to create bookings at the moment" and offered 
to escalate to a human.

This means the create_booking tool ran but failed. Please investigate:

1. Check the Celery worker logs for the moment the booking was attempted 
   - find the exact error message when create_booking was called. Show 
   me the full error, not a summary.

2. Check the create_booking tool implementation - when it tries to write 
   an appointment to the database, what could cause it to fail silently? 
   Common causes to check:
   - Is it trying to capture lead info (name, phone number) BEFORE 
     booking, but we never provided those details in the conversation?
   - Is June 20th (this Saturday) actually within the configured 
     availability window for Al Huda Gallery test tenant?
   - Is there a database constraint being violated (missing required 
     field, wrong data format)?
   - Is the tool returning an error that the AI then interprets as 
     "I can't book"?

3. Fix the root cause - whatever is failing, fix it.

4. After fixing, restart servers and run the full test suite: 
   cd backend && pytest -v

5. Tell me in plain English: "The booking failed because X, and I fixed 
   it by doing Y."

## Response snapshot

1. Celery worker logs showed that the `create_booking` tool call was executed with arguments `{'start_time': '2024-06-20T15:00:00Z', 'service_type': 'fitting appointment'}` (which is in the past, Thursday, June 20, 2024). In addition, the tool skipped execution and returned `None` because the active conversation did not have an associated `customer_id`.
2. Verified that when `conv.customer_id` was `None`, the orchestrator's `create_booking` and `capture_lead_info` tool handlers returned `None` without performing any action or returning an error message, which serialized as `"null"` and triggered the fallback response.
3. Fixed the issues by:
   - Modifying `capture_lead_info` to automatically look up or create a `Customer` record (and link it to the conversation) when `conv.customer_id` is missing.
   - Modifying `create_booking` to return a descriptive error dictionary indicating that contact details must be captured first if `customer_id` is missing.
   - Injecting the current timezone-aware date and time dynamically into the system prompt to allow the AI to compute relative dates (like "this Saturday") correctly.
   - Guarded `load_dotenv` in `config.py` with `APP_ENV != "test"` to avoid overriding the pytest setup.
4. Restarted the backend server and Celery worker and ran `pytest -v`, with all 29 tests passing successfully.

## Outcome

- ✅ Impact: Ensured anonymous leads can be correctly captured as customer records in the CRM when providing info, preventing tool failures and enabling correct relative date calculations.
- 🧪 Tests: All 29 backend tests passed.
- 📁 Files: Modified [ai_orchestrator_service.py](file:///home/waterprooffish99/projects/ai-apointment-setter-lead-qualification-agent/backend/app/services/ai_orchestrator_service.py) and [config.py](file:///home/waterprooffish99/projects/ai-apointment-setter-lead-qualification-agent/backend/app/core/config.py).
- 🔁 Next prompts: None.

## Evaluation notes (flywheel)

- Failure modes observed: `load_dotenv` in `config.py` was overriding the testing variables defined in `conftest.py`, leading to authorization failures (401 vs 202/402). This was successfully resolved by guarding the dotenv load check.
- Grader results: none
- Next experiment: none
