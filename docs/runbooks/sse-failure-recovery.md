# SSE Failure Recovery Runbook

## Trigger
- Client stream disconnect spikes, missing token stream completions.

## Recovery
1. Verify API node health and proxy timeout settings.
2. Confirm keepalive frames emitted.
3. Validate client reconnect strategy and request id correlation.

## Verification
- Stream completion rate recovers.
- No server-side cancellation cascades.
