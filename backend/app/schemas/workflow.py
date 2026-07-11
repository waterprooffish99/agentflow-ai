import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class WorkflowCreateRequest(BaseModel):
    name: str
    description: str | None = None
    trigger_type: str
    trigger_config: dict | None = None
    actions: list[dict] = Field(..., min_length=1)


class WorkflowUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    trigger_config: dict | None = None
    actions: list[dict] | None = None
    is_active: bool | None = None


class WorkflowTriggerRequest(BaseModel):
    entity_type: str = Field(..., pattern="^(lead|appointment|customer)$")
    entity_id: uuid.UUID


class WorkflowResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    trigger_type: str
    trigger_config: dict
    actions: list
    is_active: bool
    last_run_at: datetime | None
    run_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkflowExecutionResponse(BaseModel):
    id: uuid.UUID
    workflow_id: uuid.UUID
    trigger_type: str
    entity_type: str
    entity_id: uuid.UUID
    status: str
    started_at: datetime
    completed_at: datetime | None
    error: str | None


class WorkflowDetailResponse(WorkflowResponse):
    last_run_status: str | None = None
    last_run_error: str | None = None
