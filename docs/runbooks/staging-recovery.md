# Staging Recovery Runbook

## Trigger
- Staging env drift or broken migration state.

## Recovery
1. Recreate staging DB snapshot baseline.
2. Reapply migrations from scratch.
3. Reseed demo tenant scenario.
4. Run full API/test smoke suite.

## Verification
- Deployment safety endpoint passes.
- Demo walkthrough and analytics dashboard healthy.
