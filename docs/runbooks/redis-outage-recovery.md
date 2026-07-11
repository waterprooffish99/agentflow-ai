# Redis Outage Recovery Runbook

## Detection
- `/health/ready` reports `redis=false`
- Increased rate-limit fallback logs or auth replay protection degradation

## Immediate Actions
1. Confirm provider outage (Upstash/host status page).
2. Scale backend read-only critical paths if needed.
3. Keep API online: platform degrades to local limiter and best-effort idempotency.

## Recovery
1. Restore Redis connectivity and credentials.
2. Validate with `PING` and `/health/ready`.
3. Confirm rate limiting and idempotency keys are repopulating.

## Verification Checklist
- `redis=true` on readiness endpoint.
- Auth refresh replay keys being set.
- Tenant AI usage counters incrementing.
