import uuid
from datetime import datetime

from pydantic import BaseModel


class TenantResponse(BaseModel):
    id: uuid.UUID
    business_name: str
    domain: str | None
    timezone: str
    subscription_tier: str
    status: str
    autonomy_level: str
    min_reviewed_conversations: int
    max_correction_rate: float
    settings: dict
    ai_config: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class TenantUpdateRequest(BaseModel):
    business_name: str | None = None
    domain: str | None = None
    timezone: str | None = None
    autonomy_level: str | None = None
    min_reviewed_conversations: int | None = None
    max_correction_rate: float | None = None
    settings: dict | None = None
    ai_config: dict | None = None


class TenantListItem(BaseModel):
    id: uuid.UUID
    business_name: str
    timezone: str
    subscription_tier: str
    status: str
    created_at: datetime
    active_leads: int = 0
    monthly_bookings: int = 0

    model_config = {"from_attributes": True}


class PlatformMetrics(BaseModel):
    total_tenants: int
    active_tenants: int
    total_leads: int
    total_bookings: int
    monthly_revenue: float = 0.0
    avg_conversion_rate: float = 0.0
    total_conversations: int = 0
    escalation_rate: float = 0.0