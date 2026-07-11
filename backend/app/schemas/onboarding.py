import uuid
from datetime import datetime, time
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl

# --- Base Schemas ---

class OnboardingBase(BaseModel):
    model_config = {"from_attributes": True}

# --- Business Profile ---

class BusinessProfileBase(OnboardingBase):
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[HttpUrl] = None
    industry: Optional[str] = None

class BusinessProfileCreate(BusinessProfileBase):
    pass

class BusinessProfileUpdate(BusinessProfileBase):
    pass

class BusinessProfileResponse(BusinessProfileBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

# --- Service ---

class ServiceBase(OnboardingBase):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: Optional[Decimal] = None
    duration_minutes: int = Field(default=30, ge=1)
    is_active: bool = True

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(ServiceBase):
    name: Optional[str] = None

class ServiceResponse(ServiceBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

# --- Availability ---

class AvailabilityRuleBase(OnboardingBase):
    day_of_week: str # Enum validation handled in router or via Field
    start_time: time
    end_time: time
    is_available: bool = True

class AvailabilityRuleCreate(AvailabilityRuleBase):
    pass

class AvailabilityRuleUpdate(AvailabilityRuleBase):
    pass

class AvailabilityRuleResponse(AvailabilityRuleBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

# --- FAQ ---

class FAQEntryBase(OnboardingBase):
    question: str = Field(..., min_length=1)
    answer: str = Field(..., min_length=1)
    category: Optional[str] = None
    is_active: bool = True

class FAQEntryCreate(FAQEntryBase):
    pass

class FAQEntryUpdate(FAQEntryBase):
    pass

class FAQEntryResponse(FAQEntryBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

# --- AI Configuration ---

class AIConfigurationBase(OnboardingBase):
    name: str = Field(default="default", max_length=100)
    system_prompt: Optional[str] = None
    personality_traits: dict = Field(default_factory=dict)
    temperature: float = Field(default=0.7, ge=0, le=2)
    model_name: str = Field(default="gpt-4", max_length=100)
    tools_enabled: List[str] = Field(default_factory=list)

class AIConfigurationCreate(AIConfigurationBase):
    pass

class AIConfigurationUpdate(AIConfigurationBase):
    pass

class AIConfigurationResponse(AIConfigurationBase):
    id: uuid.UUID
    tenant_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
