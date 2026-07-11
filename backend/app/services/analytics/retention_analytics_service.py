import uuid
import datetime as dt
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Tenant, Conversation
from app.schemas.analytics import RetentionMetrics
from app.services.analytics.utils import apply_tenant_filter, apply_date_window

class RetentionAnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_tenant_retention_metrics(self, tenant_id: uuid.UUID) -> RetentionMetrics:
        """Analyze retention and engagement trends for a specific tenant."""
        # 1. Determine Cohort
        tenant_stmt = select(Tenant.created_at).where(Tenant.id == tenant_id)
        created_at = (await self.db.execute(tenant_stmt)).scalar()
        cohort_month = created_at.strftime("%Y-%m") if created_at else "unknown"
        
        # 2. Active days in last 30
        since_30d = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)
        active_days_stmt = (
            select(func.count(func.distinct(func.date(Conversation.created_at))))
            .where(and_(Conversation.tenant_id == tenant_id, Conversation.created_at >= since_30d))
        )
        active_days = (await self.db.execute(active_days_stmt)).scalar() or 0
        
        # 3. Engagement Trend (Week-over-Week)
        now = dt.datetime.now(dt.timezone.utc)
        since_7d = now - dt.timedelta(days=7)
        since_14d = now - dt.timedelta(days=14)
        
        this_week_stmt = (
            select(func.count(Conversation.id))
            .where(and_(Conversation.tenant_id == tenant_id, Conversation.created_at >= since_7d))
        )
        last_week_stmt = (
            select(func.count(Conversation.id))
            .where(and_(
                Conversation.tenant_id == tenant_id, 
                Conversation.created_at >= since_14d,
                Conversation.created_at < since_7d
            ))
        )
        
        this_week_vol = (await self.db.execute(this_week_stmt)).scalar() or 0
        last_week_vol = (await self.db.execute(last_week_stmt)).scalar() or 0
        
        trend = 0.0
        if last_week_vol > 0:
            trend = (this_week_vol - last_week_vol) / last_week_vol
        elif this_week_vol > 0:
            trend = 1.0 # Significant increase from zero
            
        # 4. Churn Risk Heuristic
        risk = "LOW"
        if active_days == 0:
            risk = "HIGH"
        elif active_days < 3 or trend < -0.5:
            risk = "MEDIUM"
            
        return RetentionMetrics(
            tenant_id=tenant_id,
            cohort_month=cohort_month,
            active_days_last_30=active_days,
            churn_risk=risk,
            engagement_trend=round(trend, 2)
        )

    async def platform_retention_summary(self) -> Dict[str, Any]:
        """Aggregate retention data across cohorts, bounded to last 12 months (SUPER_ADMIN only)."""
        since_12m = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=365)

        # Basic cohort active counts with 12-month boundary
        stmt = (
            select(
                func.strftime("%Y-%m", Tenant.created_at).label("cohort"),
                func.count(Tenant.id).label("total"),
                func.sum(func.case((Tenant.status == "active", 1), else_=0)).label("active")
            )
            .where(Tenant.created_at >= since_12m)
            .group_by("cohort")
            .order_by("cohort")
        )
        result = await self.db.execute(stmt)
        cohorts = []
        for row in result.all():
            cohorts.append({
                "cohort": row.cohort,
                "total_tenants": row.total,
                "active_tenants": row.active,
                "retention_rate_pct": round((row.active / row.total) * 100, 2) if row.total > 0 else 0
            })

        return {
            "cohort_analysis": cohorts,
            "generated_at": dt.datetime.now(dt.timezone.utc),
            "window_days": 365
        }

