import asyncio
import httpx
import uuid
import sys
from app.core.config import settings

async def run_live_smoke_test():
    """Automated smoke test for live production environments."""
    print("🚬 Running Live Production Smoke Tests...")
    
    base_url = f"http://localhost:{settings.app_port}"
    if settings.app_env == "production":
        # In real prod, this might be the actual domain
        base_url = settings.frontend_url.replace(":3000", ":8000") # simplified for this demo

    async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
        # 1. Basic Connectivity
        try:
            resp = await client.get("/health/ready")
            assert resp.status_code == 200
            print("  ✅ [Health] Platform Ready")
        except Exception as e:
            print(f"  ❌ [Health] FAILED: {e}")
            sys.exit(1)

        # 2. Public API Key check (if set)
        if settings.public_api_key:
            print("  [Security] Verifying Public API Key enforcement...")
            resp = await client.post("/api/v1/chat/message", json={
                "conversation_id": str(uuid.uuid4()),
                "tenant_id": str(uuid.uuid4()),
                "content": "test"
            })
            # Expect 401 if key is missing or invalid
            assert resp.status_code == 401
            print("  ✅ [Security] API Protection Active")

        # 3. Environment Separation Check
        print(f"  [Config] APP_ENV: {settings.app_env}")
        if settings.app_env == "production":
            assert settings.app_debug is False
            print("  ✅ [Config] Debug mode DISABLED")

    print("\n✅ Smoke tests passed. Environment is stable.")

if __name__ == "__main__":
    asyncio.run(run_live_smoke_test())
