# PHR: User Story 1 - Business Onboarding System

**Date**: 2026-05-11
**Status**: Initial Infrastructure Complete
**Ref**: User Story 1 of `specs/001-platform-core/tasks.md`

## Summary
Established the backend and frontend foundations for the multi-tenant onboarding system. Businesses can now configure their profiles, services, availability, and AI agent settings through a structured stepper UI.

## Completed Tasks (Infrastructure)
- [x] **Models**: Created `business_profiles`, `services`, `availability_rules`, `faq_entries`, and `ai_configurations`.
- [x] **Schemas**: Implemented Pydantic validation for all onboarding entities.
- [x] **APIs**: Created `/api/v1/onboarding/*` endpoints with CRUD support and tenant isolation.
- [x] **UI Scaffolding**: Built Next.js onboarding layout and dynamic stepper flow.
- [x] **Form Components**: Implemented `BusinessProfileForm` and `AIConfigForm`.

## Architectural Decisions
- **RAG Preparation**: `FAQEntry` model designed as a separate table to facilitate future vector embedding and RAG support.
- **Granular Models**: Moved from JSONB settings in `Tenant` to structured tables for better scalability and querying.
- **Client-Side Stepper**: Used a client-side state management for the onboarding flow to ensure smooth transitions.

## Remaining Tasks
- [ ] Implement `ServicesForm`, `AvailabilityForm`, and `FAQForm` UI details.
- [ ] Connect frontend forms to backend onboarding APIs.
- [ ] Trigger AI service initialization after onboarding completion.
- [ ] Generate/Run final Alembic migrations for new models.

## Architectural Risks
- **Context Injection Complexity**: As business data grows, injecting all FAQs/Services into AI prompts may exceed context limits. Mitigation: RAG (Phase 4).
- **Timezone Handling**: Availability rules need strict UTC/Local conversion logic.
