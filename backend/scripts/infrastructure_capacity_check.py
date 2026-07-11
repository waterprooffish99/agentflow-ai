import asyncio
import psutil
import os
from app.core.config import settings
from app.core.database import engine
from app.core.redis import redis_client
from sqlalchemy import text
import structlog

logger = structlog.get_logger()

async def check_infrastructure_capacity():
    """Analyze current infrastructure utilization and provide scaling recommendations."""
    print("🔋 Infrastructure Capacity & Scaling Intelligence...")
    
    # 1. System Resources
    cpu_usage = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    print(f"  [System] CPU Usage: {cpu_usage}%")
    print(f"  [System] RAM Usage: {memory.percent}% ({memory.used // 1024**2}MB / {memory.total // 1024**2}MB)")

    # 2. Database Pool Status
    try:
        # engine.pool.size() etc.
        pool = engine.pool
        print(f"  [Database] Pool Size: {pool.size()}")
        print(f"  [Database] Checked Out: {pool.checkedout()}")
        print(f"  [Database] Overflow: {pool.overflow()}")
    except Exception as e:
        print(f"  [Database] Pool stats unavailable: {e}")

    # 3. Redis Health
    try:
        info = await redis_client.info()
        print(f"  [Redis] Memory Used: {info['used_memory_human']}")
        print(f"  [Redis] Connected Clients: {info['connected_clients']}")
        print(f"  [Redis] Instantaneous Ops/sec: {info['instantaneous_ops_per_sec']}")
    except Exception as e:
        print(f"  [Redis] Stats unavailable: {e}")

    # 4. Scaling Recommendations
    print("\n📈 Scaling Recommendations:")
    if cpu_usage > 70:
        print("  ⚠️ HIGH CPU: Recommended to increase horizontal pod/container count.")
    if memory.percent > 80:
        print("  ⚠️ HIGH RAM: Recommended to increase node memory or optimize large objects.")
    if pool.overflow() > 5:
        print("  ⚠️ DB POOL OVERFLOW: Recommended to increase DATABASE_POOL_SIZE.")
    
    print("\n✅ Operational scaling assessment complete.")

if __name__ == "__main__":
    asyncio.run(check_infrastructure_capacity())
