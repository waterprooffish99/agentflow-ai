#!/bin/bash
set -e

echo "Starting deployment verification..."

# 1. Check environment variables
echo "Checking environment variables..."
python3 -c "from app.core.config import settings; print('Config loaded successfully')"

# 2. Verify database connectivity and migrations
echo "Verifying database migrations..."
alembic current
python3 scripts/validate_migrations.py

# 3. Check Redis connectivity
echo "Checking Redis connectivity..."
python3 -c "import asyncio; from app.core.redis import redis_client; asyncio.run(redis_client.ping())"

# 4. Run health checks (if app is running)
# curl -f http://localhost:8000/health/ready || exit 1

echo "Deployment verification passed!"
