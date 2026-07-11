# Celery Worker Recovery Runbook

## Trigger
- Task backlog growth, worker crash loops, queue lag.

## Recovery
1. Restart worker processes.
2. Verify broker connectivity and queue depth.
3. Confirm `task_acks_late` and visibility timeout behavior.
4. Re-drive safe idempotent tasks only.

## Verification
- Queue depth stabilizes.
- No duplicate follow-up processing (dedupe lock keys present).
