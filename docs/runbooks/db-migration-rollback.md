# DB Migration Rollback Runbook

## Trigger
- Failed migration at deploy or runtime schema incompatibility.

## Procedure
1. Freeze writes (maintenance mode or deployment rollback).
2. Run `alembic downgrade -1` (or target revision).
3. Redeploy previous backend image.
4. Validate schema/version consistency.

## Verification
- `alembic_version` matches expected rollback revision.
- `/health/ready` green.
- Core tenant read/write smoke tests pass.
