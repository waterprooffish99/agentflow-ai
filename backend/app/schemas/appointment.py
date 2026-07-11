import uuid
from datetime import datetime

from pydantic import BaseModel


class AppointmentCreateRequest(BaseModel):
    customer_id: uuid.UUID
    lead_id: uuid.UUID | None = None
    service_type: str
    start_time: datetime
    end_time: datetime
    notes: str | None = None


class AppointmentUpdateRequest(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None
    service_type: str | None = None
    status: str | None = None
    notes: str | None = None


class AppointmentCancelRequest(BaseModel):
    reason: str | None = None


class AppointmentRescheduleRequest(BaseModel):
    new_start_time: datetime
    new_end_time: datetime
    notes: str | None = None


class AppointmentResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    service_type: str
    start_time: datetime
    end_time: datetime
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TimeSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    staff_id: uuid.UUID | None = None


class AvailabilityResponse(BaseModel):
    slots: list[TimeSlot]