---
id: 0016
title: Startup instructions cheat sheet
stage: general
date: 2026-06-18
surface: agent
model: Gemini 3.5 Flash (Medium)
feature: none
branch: 001-platform-core
user: waterprooffish99
command: none
labels: ["docs", "startup", "reboot"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files: []
tests: []
---

## Prompt

Now tell me in short, next time when i turn my laptop on and want to stat agent flow how to do that manually,,, write them all steps in bulleted list so that i do not need to tell you over and over again.

## Response snapshot

Here is a short, step-by-step checklist to start AgentFlow manually when you turn on your laptop:

1. **Start Docker Containers** (Postgres and Redis):
   ```bash
   docker compose -f docker-compose.test.yml up -d postgres_test redis_test
   ```

2. **Start the Backend Server** (in a new terminal):
   ```bash
   cd backend
   .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

3. **Start the Celery Worker** (in a new terminal):
   ```bash
   cd backend
   .venv/bin/celery -A app.core.celery.celery_app worker --loglevel=info
   ```

4. **Start the Frontend Dev Server** (in a new terminal):
   ```bash
   cd frontend
   npm run dev -- -p 3001
   ```

*(Optional)* If you reset the database and need to seed the test user again:
```bash
cd backend
PYTHONPATH=. .venv/bin/python scripts/seed_test_user.py
```

Open your browser and navigate to: http://localhost:3001/login

## Outcome

- ✅ Impact: Provided startup guidelines so the user can easily run the stack themselves.
- 🧪 Tests: None
- 📁 Files: None
- 🔁 Next prompts: None
- 🧠 Reflection: Simple checklist created and cataloged.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): None
