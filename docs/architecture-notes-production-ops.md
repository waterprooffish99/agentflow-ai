# Architecture Notes: Production Operations + Resilience

## Product Validation & Commercial Execution
- **Operational Usability**: Every feature is validated against real-world SMB workflows (Hair Salon, MedSpa, etc.) as defined in `docs/pilot-onboarding-sop.md`.
- **End-to-End Determinism**: Verification of the full journey from "Public Message Ingestion" to "CRM Lead Update" and "Executive KPI Refresh".
- **SaaS-Grade UX**: Implementation of comprehensive empty states, loading skeletons, and mobile-responsive layouts for all core dashboard views.
- **Commercial Guardrails**: Final production validation of Stripe billing events, tenant isolation, and JWT rotation logic.
- **QA Automation**: Integration of `live_smoke_test.py` into the deployment pipeline for environment-specific regression testing.

## Growth Operations & Customer Scale
- **Proactive Customer Success**: Integration of `CSAutomationService` with `NotificationService` to trigger automated "rescue" touches for stalled trials.
- **Sales Operations Instrumentation**: Comprehensive lead source (UTM) and campaign tracking at the `Tenant` level to calculate CAC and channel ROI.
- **Unified Founder Dashboard**: High-level KPI aggregation service providing real-time MRR, Churn, and PMF signals for executive decision-making.
- **Growth Experimentation Rails**: Standardized A/B testing framework for onboarding and pricing variants, integrated with core conversion analytics.
- **Feedback Intelligence Layer**: Rule-based categorization of support and onboarding friction to identify recurring setup patterns at scale.
- **Revenue Operations (RevOps)**: Instrumented billing lifecycle tracking to distinguish between expansion revenue, contraction, and churn.

## Live Customer Optimization & PMF Refinement
- **Modular Analytics Domains**: Specialized services in `backend/app/services/analytics/` handle activation, retention, support, PMF, and conversion analytics.
- **Activation Intelligence**: Detailed onboarding bottleneck analysis and `time_to_first_value` tracking to optimize tenant conversion.
- **Retention Heuristics**: Automated engagement trend detection (week-over-week) and churn-risk categorization (LOW/MEDIUM/HIGH).
- **PMF Signals**: Data-driven correlation between business verticals, feature adoption (e.g., AI personality customization), and retention success.
- **Operational Reporting**: High-level platform health dashboards with anomaly detection for workflow success rates and DAU drops.
- **Analytics Utilities**: Centralized helpers in `utils.py` for tenant isolation, date windowing, and safe async aggregations.

## Live Production & Pilot Execution
- **Live Smoke Testing**: Automated verification of core business flows in live regions.
- **Pilot Monitoring**: Specialized tracking for initial user cohorts (5-20 users) to detect early-stage friction.
- **Billing Live Mode**: Production-ready Stripe synchronization with strict dunning and state validation.
- **Incident Escalation**: High-priority alert thresholds for real user issues.

## Commercial Launch & UX Polish
- **Demo Readiness**: Automated demo tenant seeding for sales and realistic SMB walkthroughs.
- **Onboarding Intelligence**: Contextual helper guidance and recommended next actions based on setup progress.
- **Support Center**: Integrated self-service FAQ surfacing and streamlined issue reporting.
- **Commercial Guardrails**: Finalized CSP, HSTS, and multi-tier billing sync for production safety.

## Monetization & PMF Optimization
- **Real Billing Execution**: Stripe integration with secure webhook verification and deterministic state synchronization.
- **PMF Analytics**: Activation rate tracking and cohort-based feature adoption analysis to measure product-market fit.
- **Retention Heuristics**: Multi-factor engagement scoring (0-100) to categorize tenants for targeted success interventions.
- **Experimentation Engine**: Unified A/B testing framework with deterministic tenant assignment and variant-aware analytics.
- **Scaling Intelligence**: Automated infrastructure capacity diagnostics with utilization-based scaling recommendations.

## Public Beta Growth & Product Intelligence
- **Growth Analytics**: Frontend event ingestion (`/analytics/events`) provides robust behavioral tracking for drop-offs and feature adoption.
- **Customer Success Automation**: Automated background jobs proactively identify high-risk tenants (inactivity) and trigger intervention alerts.
- **Support Scalability**: Admin support queues utilize priority and status sorting for scalable SLA enforcement.
- **Revenue Operations**: Safe billing telemetry (`track_billing_event`) ensures SaaS metrics are aggregated without exposing sensitive payment workflows.

## Production Stabilization & Scale
- **Endurance Testing**: 24h soak tests with Locust to validate memory stability and connection pool endurance.
- **Incident Management**: Severity-based incident tracking (low to critical) with resolution workflows and audit trails.
- **Feature Rollout**: Dynamic feature flags with support for staged rollout (percentage-based) and tenant-specific overrides.
- **Advanced Analytics**: Unified internal analytics for booking conversions, platform SLA (workflow success), and tenant engagement rankings.

## Pilot & Public Beta Readiness
- **Onboarding Analytics**: Activation scoring (0-100) based on setup completeness and first engagement.
- **Support Infrastructure**: Integrated feedback and issue tracking for rapid beta iteration.
- **Operational Alerting**: `AlertManager` handles provider-level and infrastructure-level degradation alerts.
- **Billing Scaffolding**: Stripe-ready webhook handlers and subscription lifecycle state management.
- **Security Posture**: Enhanced CSP, HSTS, and abuse protection heuristics for public-facing safety.

## Commercial & Operational Readiness
- **Plan-Based Quotas**: Usage limits (AI tokens, bookings, contacts) are enforced based on `SubscriptionTier`.
- **Governance**: `AIGovernanceService` enforces daily/monthly ceilings to prevent cost overruns and abuse.
- **Admin Visibility**: Operational dashboard for super-admins to monitor platform health and tenant onboarding status.
- **Security Hardening**: `TrustedHostMiddleware` and strict CORS enforcement for SaaS production posture.
- **Scalability**: Baseline load testing with Locust to identify async orchestration bottlenecks.

## Production Infrastructure Maturity
- **Lifespan Management**: FastAPI lifespan handlers replace deprecated events for deterministic startup/shutdown.
- **Migration Integrity**: Explicit revision-based Alembic migrations with linear head validation.
- **Audit Logging**: Persistent, tenant-aware audit trail for administrative and destructive operations.
- **Telemetry**: OpenTelemetry integration for tracing and metrics across API, DB, Redis, and Celery.
- **Deployment Safety**: Automated verification scripts and staging parity checks.

## New Operational Primitives
- Tenant context propagation via request middleware context vars.
- Redis key namespace standard `tenant:{tenant_id}:...` to avoid cross-tenant key collisions.
- Shared resilience components: retry wrapper + circuit breaker.
- Startup dependency checks for env, DB, Redis, and migration verification.
- Idempotency service for duplicate suppression in booking/follow-up paths.

## Tenant Isolation Reinforcements
- Service-level tenant assertions for conversations and booking references.
- Tenant-scoped message listing and lead-history queries.
- Tenant-keyed follow-up task dedupe locks.

## Runtime Degradation Model
- Redis down: fallback to local in-memory rate limit / fail-open idempotency.
- AI provider instability: retry + fallback model + circuit protection.
- SSE disconnect: cancellation-safe stream termination with keepalive frames.

## Cost Governance Foundation
- Tenant daily/monthly AI usage counters in Redis.
- Token, latency, request, error aggregation by tenant/provider.
- Quota enforcement hook before AI call execution.
