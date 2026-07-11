import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ConversationResponse(BaseModel):
    id: uuid.UUID
    lead_id: uuid.UUID
    customer_id: uuid.UUID
    status: str
    message_count: int
    started_at: uuid.UUID
    ended_at: uuid.UUID | None
    escalated_to: uuid.UUID | None

    model_config = {"from_attributes": True}


class Message(BaseModel):
    role: str  # user, assistant, system, staff
    content: str
    timestamp: datetime
    tool_calls: list | None = None
    metadata: dict | None = None


class ConversationDetailResponse(ConversationResponse):
    messages: list[Message]
    escalated_reason: str | None
    resolved_by: uuid.UUID | None


class EscalateRequest(BaseModel):
    reason: str


class WidgetMessageRequest(BaseModel):
    message: str = Field(..., max_length=2000)
    conversation_id: uuid.UUID | None = None
    customer_id: uuid.UUID | None = None


class WidgetMessageResponse(BaseModel):
    conversation_id: uuid.UUID
    message: str
    lead_id: uuid.UUID
    confidence: float
    should_escalate: bool


class AnalyticsDashboard(BaseModel):
    total_leads: int
    total_bookings: int
    conversion_rate: float
    conversation_count: int
    missed_leads: int
    avg_response_time_ms: float


class AIMetrics(BaseModel):
    avg_response_time_ms: float
    escalation_rate: float
    booking_conversion: float
    satisfaction_score: float | None = None
