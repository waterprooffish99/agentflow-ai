import time
import uuid
from contextlib import asynccontextmanager
from typing import Callable

import structlog
from fastapi import FastAPI, Request, Response, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware

from app.api import admin, api_router
from app.core.config import settings
from app.core.database import close_db, engine
from app.core.exceptions import AppException
from app.core.observability import metrics, setup_tracing
from app.core.rate_limit import DistributedRateLimiter
from app.core.redis import redis_healthcheck
from app.core.startup_checks import run_startup_checks
from app.core.tenant_context import get_tenant_id as get_ctx_tenant_id
from app.core.tenant_context import set_request_id, set_tenant_id
from app.core.tenant_guard import tenant_status_guard

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger()

api_limiter = DistributedRateLimiter(limit=settings.api_rate_limit_per_minute, window_seconds=60)
auth_limiter = DistributedRateLimiter(limit=settings.auth_rate_limit_per_minute, window_seconds=60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Tracing initialization
    setup_tracing(app, engine)

    # Startup logic
    await run_startup_checks()
    logger.info("startup", message="Starting AgentFlow AI Platform API")
    yield
    # Shutdown logic
    logger.info("shutdown", message="Shutting down AgentFlow AI Platform API")
    await close_db()


app = FastAPI(
    title="AgentFlow AI Platform API",
    description="Multi-tenant AI receptionist and lead automation platform",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    dependencies=[Depends(tenant_status_guard)],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[h.strip() for h in settings.allowed_hosts.split(",")]
)


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)
        set_request_id(request_id)
        tenant_hint = request.headers.get("X-Tenant-ID")
        try:
            set_tenant_id(uuid.UUID(tenant_hint) if tenant_hint else None)
        except ValueError:
            set_tenant_id(None)

        client_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
        limiter = auth_limiter if request.url.path.startswith("/api/v1/auth") else api_limiter
        allowed, retry_after = await limiter.allow(f"{client_ip}:{request.url.path}")
        if not allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": {"code": "RATE_LIMITED", "message": "Too many requests"}},
                headers={"Retry-After": str(retry_after)},
            )

        if request.url.path.startswith("/api/v1/chat/") and settings.public_api_key:
            inbound_api_key = request.headers.get("X-API-Key")
            auth_header = request.headers.get("Authorization")
            
            # Allow EITHER X-API-Key OR a valid Bearer token for internal testing
            if inbound_api_key != settings.public_api_key and not auth_header:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"error": {"code": "UNAUTHORIZED", "message": "Invalid API key or missing authorization"}},
                )

        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000
        metrics.track_request(request.url.path, duration_ms, response.status_code >= 500)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{duration_ms:.2f}"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        logger.info(
            "request_processed",
            path=request.url.path,
            method=request.method,
            status_code=response.status_code,
            duration_ms=duration_ms,
            tenant_id=str(get_ctx_tenant_id()) if get_ctx_tenant_id() else None,
        )
        return response


app.add_middleware(RequestIDMiddleware)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    metrics.track_request(request.url.path, 0.0, True)
    return JSONResponse(status_code=exc.status_code, content=exc.detail)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled_exception", path=request.url.path, error=str(exc))
    metrics.track_request(request.url.path, 0.0, True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}},
    )


app.include_router(api_router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict:
    return {"status": "ok", "timestamp": time.time(), "metrics": metrics.snapshot()}


@app.get("/health/ready")
async def ready_check() -> JSONResponse:
    db_ok = True
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    redis_ok = await redis_healthcheck()
    healthy = db_ok and redis_ok
    return JSONResponse(
        status_code=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "status": "ready" if healthy else "degraded",
            "checks": {"database": db_ok, "redis": redis_ok},
        },
    )


@app.get("/health/deployment")
async def deployment_safety_check() -> dict:
    required = {
        "DATABASE_URL": bool(settings.database_url),
        "REDIS_URL": bool(settings.redis_url),
        "JWT_SECRET_LEN_OK": len(settings.jwt_secret) >= 32,
        "PUBLIC_API_KEY_SET": bool(settings.public_api_key),
        "APP_ENV": settings.app_env,
        "APP_DEBUG": settings.app_debug,
    }
    ready = all(v for k, v in required.items() if isinstance(v, bool))
    return {"status": "pass" if ready else "fail", "checks": required}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
