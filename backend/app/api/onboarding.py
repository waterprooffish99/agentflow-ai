from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_tenant_id, require_role
from app.models import (
    BusinessProfile, Service, AvailabilityRule, FAQEntry, AIConfiguration, UserRole
)
from app.services.onboarding_analytics_service import OnboardingAnalyticsService
from app.schemas.onboarding import (
    BusinessProfileCreate, BusinessProfileUpdate, BusinessProfileResponse,
    ServiceCreate, ServiceUpdate, ServiceResponse,
    AvailabilityRuleCreate, AvailabilityRuleUpdate, AvailabilityRuleResponse,
    FAQEntryCreate, FAQEntryUpdate, FAQEntryResponse,
    AIConfigurationCreate, AIConfigurationUpdate, AIConfigurationResponse
)

router = APIRouter(prefix="/onboarding", tags=["onboarding"])

# --- Business Profile ---

@router.get("/business-profile", response_model=BusinessProfileResponse)
async def get_business_profile(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    result = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not found")
    return profile

@router.post("/business-profile", response_model=BusinessProfileResponse)
async def create_or_update_business_profile(
    data: BusinessProfileCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    result = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant_id)
    )
    profile = result.scalar_one_or_none()
    
    if profile:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(profile, key, value)
    else:
        profile = BusinessProfile(**data.model_dump(), tenant_id=tenant_id)
        db.add(profile)
    
    await db.commit()
    await db.refresh(profile)
    return profile

# --- Services ---

@router.get("/services", response_model=List[ServiceResponse])
async def list_services(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    result = await db.execute(
        select(Service).where(Service.tenant_id == tenant_id)
    )
    return result.scalars().all()

@router.post("/services", response_model=ServiceResponse)
async def create_service(
    data: ServiceCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    service = Service(**data.model_dump(), tenant_id=tenant_id)
    db.add(service)
    await db.commit()
    await db.refresh(service)
    return service

# --- Availability ---

@router.get("/availability", response_model=List[AvailabilityRuleResponse])
async def list_availability(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    result = await db.execute(
        select(AvailabilityRule).where(AvailabilityRule.tenant_id == tenant_id)
    )
    return result.scalars().all()

@router.post("/availability", response_model=AvailabilityRuleResponse)
async def create_availability_rule(
    data: AvailabilityRuleCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    rule = AvailabilityRule(**data.model_dump(), tenant_id=tenant_id)
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule

# --- FAQs ---

@router.get("/faqs", response_model=List[FAQEntryResponse])
async def list_faqs(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    result = await db.execute(
        select(FAQEntry).where(FAQEntry.tenant_id == tenant_id)
    )
    return result.scalars().all()

@router.post("/faqs", response_model=FAQEntryResponse)
async def create_faq(
    data: FAQEntryCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    faq = FAQEntry(**data.model_dump(), tenant_id=tenant_id)
    db.add(faq)
    await db.commit()
    await db.refresh(faq)
    return faq

# --- AI Configuration ---

@router.get("/ai-config", response_model=AIConfigurationResponse)
async def get_ai_config(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    result = await db.execute(
        select(AIConfiguration).where(AIConfiguration.tenant_id == tenant_id)
    )
    config = result.scalar_one_or_none()
    if not config:
        # Return default config if not set
        return AIConfiguration(tenant_id=tenant_id)
    return config

@router.post("/ai-config", response_model=AIConfigurationResponse)
async def create_or_update_ai_config(
    data: AIConfigurationCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    result = await db.execute(
        select(AIConfiguration).where(AIConfiguration.tenant_id == tenant_id)
    )
    config = result.scalar_one_or_none()
    
    if config:
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(config, key, value)
    else:
        config = AIConfiguration(**data.model_dump(), tenant_id=tenant_id)
        db.add(config)
    
    await db.commit()
    await db.refresh(config)
    return config

@router.get("/status")
async def get_onboarding_status(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    """Get the current progress of the onboarding walkthrough."""
    service = OnboardingAnalyticsService(db)
    return await service.get_tenant_onboarding_stats(tenant_id)


@router.get("/recommendations", response_model=List[str])
async def get_onboarding_recs(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id)
):
    """Get recommended actions to complete onboarding."""
    service = OnboardingAnalyticsService(db)
    return await service.get_onboarding_recommendations(tenant_id)


from sqlalchemy import func
