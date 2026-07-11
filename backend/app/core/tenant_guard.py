import json
import uuid
from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import AppException
from app.core.tenant_context import get_tenant_id as get_ctx_tenant_id
from app.core.tenant_context import set_tenant_id


class TenantIsolationError(ValueError):
    pass


def assert_tenant_match(actual_tenant_id: uuid.UUID | None, expected_tenant_id: uuid.UUID) -> None:
    if actual_tenant_id != expected_tenant_id:
        raise TenantIsolationError("Tenant isolation violation")


async def tenant_status_guard(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> None:
    path = request.url.path
    
    # 1. Define allowlist of routes that bypass status checks
    is_allowed = (
        path in ["/health", "/health/ready", "/health/deployment", "/api/docs", "/api/redoc", "/api/openapi.json"]
        or path.startswith("/api/v1/auth/")
        or path.startswith("/api/v1/billing/")
    )
    
    if is_allowed:
        return
        
    # 2. Resolve tenant_id
    tenant_id = get_ctx_tenant_id()
    
    # A. Resolve from JWT Token (Authorization header or Cookie)
    if not tenant_id:
        token = None
        authorization = request.headers.get("Authorization")
        auth_token = request.cookies.get("auth_token")
        
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
        elif auth_token:
            token = auth_token
            
        if token:
            from app.core.security import decode_token
            try:
                payload = decode_token(token)
                if payload and payload.get("tenant_id"):
                    tenant_id = uuid.UUID(payload["tenant_id"])
                    set_tenant_id(tenant_id)
            except Exception:
                pass
                
    # B. Resolve from request body (specifically for /api/v1/chat/*)
    if not tenant_id and path.startswith("/api/v1/chat/"):
        try:
            body_bytes = await request.body()
            if body_bytes:
                body_json = json.loads(body_bytes)
                tenant_id_str = body_json.get("tenant_id")
                if tenant_id_str:
                    tenant_id = uuid.UUID(tenant_id_str)
                    set_tenant_id(tenant_id)
                
                # Restore body for downstream route handlers
                async def receive():
                    return {"type": "http.request", "body": body_bytes, "more_body": False}
                request._receive = receive
        except Exception:
            pass

    # 3. Perform status enforcement
    if tenant_id:
        from app.models import Tenant, TenantStatus
        tenant = await db.get(Tenant, tenant_id)
        if tenant:
            status_val = tenant.status
            
            if status_val in [TenantStatus.ACTIVE, TenantStatus.TRIAL]:
                return
            elif status_val == TenantStatus.PAST_DUE:
                if request.method != "GET":
                    raise AppException(
                        status_code=status.HTTP_402_PAYMENT_REQUIRED,
                        code="PAYMENT_REQUIRED",
                        message="Payment is past due. Action required."
                    )
            else:
                raise AppException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    code="PAYMENT_REQUIRED",
                    message="Tenant subscription is inactive"
                )
