import uuid
from datetime import datetime
from pydantic import BaseModel

class PermissionPolicyResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    always_allowed_actions: list[str]
    always_escalate_actions: list[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class PermissionPolicyUpdateRequest(BaseModel):
    always_allowed_actions: list[str] | None = None
    always_escalate_actions: list[str] | None = None
