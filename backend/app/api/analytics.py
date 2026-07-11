import uuid
import structlog
from typing import Dict, Any, Optional
from pydantic import BaseModel

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_tenant_id
from app.services.analytics_service import AnalyticsService
from app.services.analytics.activation_analytics_service import ActivationAnalyticsService
from app.services.analytics.retention_analytics_service import RetentionAnalyticsService
from app.services.analytics.support_analytics_service import SupportAnalyticsService
from app.services.analytics.conversion_analytics_service import ConversionAnalyticsService
from app.schemas.analytics import ActivationMetrics, RetentionMetrics, SupportMetrics, ConversionMetrics

router = APIRouter(prefix="/analytics", tags=["analytics"])
logger = structlog.get_logger()

class AnalyticsEvent(BaseModel):
    event_name: str
    metadata_json: Optional[Dict[str, Any]] = None

@router.post("/events")
async def track_user_behavior_event(
    event: AnalyticsEvent,
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Ingest operational user behavior events (e.g., feature adoption, onboarding friction)."""
    logger.info(
        "user_behavior_event",
        tenant_id=str(tenant_id),
        event_name=event.event_name,
        metadata=event.metadata_json or {}
    )
    return {"status": "recorded"}

@router.get("/kpis")
async def get_kpis(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await AnalyticsService(db).kpis(tenant_id)


@router.get("/booking-trends")
async def get_booking_trends(
    days: int = Query(30, ge=7, le=365),
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await AnalyticsService(db).booking_trends(tenant_id, days)


@router.get("/pipeline")
async def get_pipeline_analytics(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    return await AnalyticsService(db).pipeline_analytics(tenant_id)


@router.get("/retention", response_model=RetentionMetrics)
async def get_retention(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Analyze retention cohorts and churn risk for the tenant."""
    return await RetentionAnalyticsService(db).get_tenant_retention_metrics(tenant_id)


@router.get("/activation", response_model=ActivationMetrics)
async def get_activation_metrics(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Detailed onboarding activation and bottleneck analysis."""
    return await ActivationAnalyticsService(db).get_tenant_activation_metrics(tenant_id)


@router.get("/support-summary", response_model=SupportMetrics)
async def get_support_analytics(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Aggregated support workload and issue categories for the tenant."""
    return await SupportAnalyticsService(db).get_tenant_support_metrics(tenant_id)


@router.get("/conversion", response_model=ConversionMetrics)
async def get_conversion_potential(
    db: AsyncSession = Depends(get_db),
    tenant_id: uuid.UUID = Depends(get_tenant_id),
):
    """Analyze conversion probability and trial status."""
    return await ConversionAnalyticsService(db).get_tenant_conversion_metrics(tenant_id)
