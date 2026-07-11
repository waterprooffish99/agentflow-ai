---
id: "0008"
title: "Seed Al Huda Gallery tenant and admin user for end-to-end testing"
stage: "misc"
date: "2026-06-15"
surface: "agent"
model: "Gemini 3.5 Flash"
feature: "001-platform-core"
branch: "001-platform-core"
user: "waterprooffish99"
command: "python scripts/seed_al_huda.py"
labels: ["seeding", "demo-data", "testing", "al-huda-gallery"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - backend/scripts/seed_al_huda.py
tests:
  - Seeding completed successfully and validated via python script run
---

## Prompt

I want to set up a complete test business profile so I can pretend to 
be a customer and test the full system end-to-end. Please do this in 
plain language for a non-technical person.

Please:
1. Use the existing test tenant from earlier sessions (or create a new 
   one if needed) - confirm which one we're using.
2. Walk through the onboarding wizard data setup for this business 
   profile (either via the UI if it's running, or by setting up the 
   data directly if that's faster) with this info:
   - Business name: Al Huda Gallery
   - Business type: Balochi cultural & premium handmade dress shop
   - About: We sell handmade Balochi dresses, bridal wear, and custom 
     stitched outfits for women, serving customers in Pakistan and the 
     Gulf region.
   - Services: 
     a) Ready-made Balochi dress (price range PKR 5,000-15,000)
     b) Custom stitched bridal dress (price range PKR 25,000-60,000, 
        takes 2-3 weeks)
     c) Fitting appointment (free, 30 minutes)
   - Availability: Open Monday-Saturday, 11 AM - 7 PM (Pakistan time), 
     closed Friday afternoon for prayer (1 PM - 2:30 PM)
   - FAQs:
     - "Do you ship internationally?" -> "Yes, we ship to UAE, Saudi 
       Arabia, and other Gulf countries. Shipping takes 5-10 days."
     - "Can I customize the design?" -> "Yes! Custom designs are 
       available, please share your preferred colors and style during 
       booking."
   - AI personality: Friendly

3. Give me the EXACT URL/address I should open in my browser to access 
   the chat widget as a customer would see it.
4. Confirm: is everything ready for me to start chatting as a test 
   customer right now?

Give me a simple summary: "Setup complete, here's the link to open in 
your browser" or "Here's what's still needed before you can test."

## Response snapshot

Created a python seeding script `seed_al_huda.py` and successfully populated the local database with the Al Huda Gallery tenant (`88888888-8888-8888-8888-888888888888`), its business profile, services, availability rules, FAQs, and a demo admin user (`demo@alhuda.gallery`). Started the Next.js development server on port 3001. Provided the login credentials and exact URL path to test the chat widget on the dashboard.

## Outcome

- ✅ Impact: The database has been fully seeded with Al Huda Gallery information, enabling the user to run live end-to-end tests via the chat widget.
- 🧪 Tests: Script executed successfully and committed database transactions.
- 📁 Files: Modified/created `backend/scripts/seed_al_huda.py`
- 🔁 Next prompts: None
- 🧠 Reflection: Creating a demo admin user for the tenant was necessary so the user can easily log in to access the dashboard where the chat widget is loaded.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): None
