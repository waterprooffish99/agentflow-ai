# Failed Deployment Rollback Runbook

## Trigger
- New release fails readiness, elevated 5xx, or auth failures.

## Steps
1. Roll back backend service to previous image revision.
2. Roll back frontend deployment alias in Vercel.
3. Re-run readiness checks and tenant isolation smoke tests.
4. Keep failed artifact for postmortem.

## Verification
- Error rate normalizes.
- Tenant-scoped APIs return expected data boundaries.
