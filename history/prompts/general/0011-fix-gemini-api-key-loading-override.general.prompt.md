---
id: 0011
title: Fix Gemini API Key Loading Override
stage: general
date: 2026-06-16
surface: agent
model: Gemini 3.5 Flash
feature: none
branch: 001-platform-core
user: waterprooffish99
command: none
labels: [gemini, environment, configuration, logging]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/app/core/config.py
  - backend/app/services/ai_service.py
tests:
  - none
---

## Prompt

The chat widget is returning a repeated canned response: "I'm here to 
help! How can I assist you today with Al Huda Gallery?" for every 
message, regardless of what the customer says. This is the mock 
fallback response - meaning Gemini is not actually being called or 
is failing silently.

Please investigate and fix this urgently:

1. Check the Celery worker logs RIGHT NOW - what happens when a chat 
   message comes in? Is it reaching Gemini? Is there an error being 
   silently caught and swallowed?

2. Check if GEMINI_API_KEY is still correctly loaded by the RUNNING 
   application (not just present in .env - confirm the live app/worker 
   actually loaded it on startup).

3. Check if there is a try/except block somewhere in ai_service.py or 
   chat_tasks.py that catches Gemini errors silently and returns the 
   mock response without logging the actual error. If so, temporarily 
   make it log the full error so we can see what's failing.

4. Make one test call to Gemini directly (outside of the full chat 
   pipeline) with a simple "Hello" message and report: does it succeed 
   or fail, and what is the exact error if it fails?

Tell me in plain English: "Gemini is failing because of X" - one root 
cause, not a list of possibilities.

## Response snapshot

1. Celery worker logs showed that Gemini calls were failing with `400 API key not valid. Please pass a valid API key.` which was caught and swallowed by the fallback block in `ai_service.py`.
2. Verified that `GEMINI_API_KEY` was overridden in the host environment to `YOUR_GEMINI_KEY`, causing uvicorn and Celery to load this placeholder string instead of the `.env` value.
3. Added `exc_info=True` to the catch-all logging block in `ai_service.py` to log tracebacks for provider errors.
4. Resolved the root cause by calling `load_dotenv(override=True)` at the top of `backend/app/core/config.py`. Verified that direct calls and AIService calls now succeed and return live Gemini responses.

## Outcome

- ✅ Impact: Fixed API key loading behavior, restored live Gemini chat capability, and enhanced error observability.
- 🧪 Tests: Verified with a direct test script calling `AIService.chat_completion()`.
- 📁 Files: Modified [config.py](file:///home/waterprooffish99/projects/ai-apointment-setter-lead-qualification-agent/backend/app/core/config.py) and [ai_service.py](file:///home/waterprooffish99/projects/ai-apointment-setter-lead-qualification-agent/backend/app/services/ai_service.py).
- 🔁 Next prompts: None.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Grader results: none
- Next experiment: none
