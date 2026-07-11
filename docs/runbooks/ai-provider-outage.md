# AI Provider Outage Runbook

## Trigger
- Elevated AI completion failures or circuit open events.

## Recovery
1. Confirm provider incident.
2. Validate fallback model path is active.
3. Reduce optional AI-heavy workflows temporarily.
4. Monitor tenant quota/error metrics.

## Verification
- Fallback provider success rate acceptable.
- Core booking and CRM non-AI operations remain operational.
