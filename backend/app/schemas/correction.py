import uuid
from datetime import datetime
from pydantic import BaseModel

class CorrectionResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID | None
    conversation_id: uuid.UUID
    ai_draft_message: str
    human_edited_message: str | None
    was_edited: bool | None
    reviewed_by: uuid.UUID | None
    created_at: datetime
    reviewed_at: datetime | None

    model_config = {"from_attributes": True}

class CorrectionCreate(BaseModel):
    conversation_id: uuid.UUID
    ai_draft_message: str

class CorrectionReviewRequest(BaseModel):
    was_edited: bool
    human_edited_message: str | None = None
