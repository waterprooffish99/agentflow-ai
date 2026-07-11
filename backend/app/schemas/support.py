import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.support import SupportIssueType, SupportIssueStatus, SupportIssuePriority

class SupportIssueBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)
    issue_type: SupportIssueType
    category: Optional[str] = None
    metadata_json: Dict[str, Any] = {}

class SupportIssueCreate(SupportIssueBase):
    priority: SupportIssuePriority = SupportIssuePriority.MEDIUM

class SupportIssueUpdate(BaseModel):
    status: Optional[SupportIssueStatus] = None
    priority: Optional[SupportIssuePriority] = None
    internal_notes: Optional[str] = None

class SupportIssueResponse(SupportIssueBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    status: SupportIssueStatus
    priority: SupportIssuePriority
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
