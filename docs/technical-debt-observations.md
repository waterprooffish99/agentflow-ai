# Technical Debt Observations

1. Initial Alembic migration uses metadata create/drop and should be replaced with explicit migration operations.
2. Several modules still rely on in-memory metrics; production needs Prometheus/OpenTelemetry exporters.
3. Redis fallback behavior is availability-first and may under-enforce quotas/rate limits during outages.
4. Some legacy APIs need explicit tenant ownership checks on every mutable entity path.
5. Startup checks currently short-circuit in `APP_ENV=test`; dedicated integration checks should be added in CI staging jobs.
6. Celery queue depth metrics are not yet exported to a monitoring backend.
