import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_log import AuditLog
from app.core.tenant_context import get_tenant_id

class AuditService:
    @staticmethod
    async def log(
        db: AsyncSession,
        action: str,
        entity_type: str,
        entity_id: Optional[uuid.UUID] = None,
        user_id: Optional[uuid.UUID] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        tenant_id: Optional[uuid.UUID] = None,
    ) -> AuditLog:
        """Create a new audit log entry."""
        if tenant_id is None:
            tenant_id = get_tenant_id()
            
        audit_log = AuditLog(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=datetime.now(timezone.utc),
        )
        db.add(audit_log)
        await db.flush() # Ensure it gets an ID but don't commit yet if in a transaction
        return audit_log

audit_service = AuditService()
