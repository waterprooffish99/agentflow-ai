import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class LeadResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    status: str
    urgency: str
    budget_range: str | None
    preferred_service: str | None
    preferred_times: list
    conversation_summary: str | None
    source: str | None
    assigned_to: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LeadCreateRequest(BaseModel):
    customer_name: str
    customer_email: str | None = None
    customer_phone: str | None = None
    customer_location: str | None = None
    source: str = "manual"
    notes: str | None = None


class LeadUpdateRequest(BaseModel):
    status: str | None = None
    urgency: str | None = None
    preferred_service: str | None = None
    budget_range: str | None = None
    preferred_times: list | None = None
    assigned_to: uuid.UUID | None = None


class LeadNoteRequest(BaseModel):
    content: str = Field(..., max_length=2000)


class LeadAssignRequest(BaseModel):
    user_id: uuid.UUID


class CustomerResponse(BaseModel):
    id: uuid.UUID
    name: str
    email: str | None
    phone: str | None
    location: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class LeadWithCustomer(LeadResponse):
    customer: CustomerResponse


class AppointmentResponse(BaseModel):
    id: uuid.UUID
    service_type: str
    start_time: datetime
    end_time: datetime
    status: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ConversationSummary(BaseModel):
    id: uuid.UUID
    status: str
    message_count: int
    started_at: datetime
    ended_at: datetime | None
    escalated_to: uuid.UUID | None


class LeadDetailResponse(LeadResponse):
    customer: CustomerResponse
    conversations: list[ConversationSummary]
    appointments: list[AppointmentResponse]
