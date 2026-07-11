---
id: 0013
title: Reset and Seed Al Huda Gallery Demo Credentials
stage: general
date: 2026-06-16
surface: agent
model: Gemini 3.5 Flash
feature: none
branch: 001-platform-core
user: waterprooffish99
command: none
labels: [database, seed, credentials, tenant]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - none
tests:
  - none
---

## Prompt

The frontend login page is returning a 401 Unauthorized error when I 
try to log in with demo@alhuda.gallery / demo-secure-pass-2026 after 
refreshing the browser.

Please fix this quickly:

1. Check if the demo user account still exists in the database with 
   those exact credentials - query the database directly and confirm.

2. If the user doesn't exist (likely got cleared on restart), recreate 
   it with these exact details:
   - Email: demo@alhuda.gallery
   - Password: demo-secure-pass-2026
   - Tenant ID: 88888888-8888-8888-8888-888888888888
   - Role: admin (or whatever role gives full dashboard access)

3. If the user DOES exist, reset the password to demo-secure-pass-2026 
   to make sure it matches exactly.

4. Also check: is the test tenant 
   (88888888-8888-8888-8888-888888888888) still in the database with 
   status ACTIVE? If it got reset to INACTIVE or PAST_DUE during our 
   billing tests earlier, set it back to ACTIVE now.

5. Once fixed, confirm: "Go to http://localhost:3001/login and try 
   again - it should work now."

Do NOT restart the backend server or Celery worker - just fix the 
database records directly.

## Response snapshot

1. Queried the database and found that the test tenant `88888888-8888-8888-8888-888888888888` and user `demo@alhuda.gallery` were completely missing.
2. Executed `scripts/seed_al_huda.py` to completely seed the tenant, admin user (`demo@alhuda.gallery` / `demo-secure-pass-2026`), business profile, availability rules, and services.
3. Confirmed database writes completed successfully.

## Outcome

- ✅ Impact: Restored demo tenant and user credentials in the database to allow user access to the dashboard.
- 📁 Files: No files modified.
- 🧪 Tests: None.
- 🔁 Next prompts: None.

## Evaluation notes (flywheel)

- Failure modes observed: none
- Grader results: none
- Next experiment: none
