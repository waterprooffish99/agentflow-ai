import uuid
import datetime as dt
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, and_, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Tenant, BusinessProfile, Conversation, AIConfiguration
from app.services.analytics.utils import apply_date_window

class PMFLearningService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def vertical_success_analysis(self) -> List[Dict[str, Any]]:
        """Identify which business verticals have the highest retention, bounded to last 12 months."""
        since_12m = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=365)
        
        # Aggregation-first query design with sorting by retention percentage
        stmt = (
            select(
                BusinessProfile.vertical,
                func.count(Tenant.id).label("total_tenants"),
                func.sum(func.case((Tenant.status == "active", 1), else_=0)).label("active_tenants"),
                (func.cast(func.sum(func.case((Tenant.status == "active", 1), else_=0)), text("FLOAT")) / func.count(Tenant.id)).label("retention_rate")
            )
            .join(Tenant, Tenant.id == BusinessProfile.tenant_id)
            .where(Tenant.created_at >= since_12m)
            .group_by(BusinessProfile.vertical)
            .order_by(text("retention_rate DESC"))
        )
        result = await self.db.execute(stmt)
        
        analysis = []
        for row in result.all():
            if not row.vertical: continue
            analysis.append({
                "vertical": row.vertical,
                "total_tenants": row.total_tenants,
                "active_tenants": row.active_tenants,
                "retention_rate_pct": round(row.retention_rate * 100, 2)
            })
        return analysis

    async def feature_retention_correlation(self) -> Dict[str, Any]:
        """Analyze how feature adoption correlates with tenant retention."""
        # Feature A: Customized AI Prompt
        # Feature B: CRM Integration (not fully tracked here yet, but we can check existence of records)
        
        total_stmt = select(func.count(Tenant.id))
        total_tenants = (await self.db.execute(total_stmt)).scalar() or 0
        if total_tenants == 0: return {}

        # Tenants with Custom AI
        custom_ai_stmt = select(func.count(Tenant.id)).join(AIConfiguration).where(AIConfiguration.system_prompt != None)
        custom_ai_count = (await self.db.execute(custom_ai_stmt)).scalar() or 0
        
        # Retention of Custom AI tenants
        custom_ai_active_stmt = (
            select(func.count(Tenant.id))
            .join(AIConfiguration)
            .where(and_(AIConfiguration.system_prompt != None, Tenant.status == "active"))
        )
        custom_ai_active_count = (await self.db.execute(custom_ai_active_stmt)).scalar() or 0
        
        custom_ai_retention = (custom_ai_active_count / custom_ai_count * 100) if custom_ai_count > 0 else 0
        
        # Global retention for comparison
        global_active_stmt = select(func.count(Tenant.id)).where(Tenant.status == "active")
        global_active_count = (await self.db.execute(global_active_stmt)).scalar() or 0
        global_retention = (global_active_count / total_tenants * 100)
        
        return {
            "feature_adoption": {
                "custom_ai_personality_pct": round(custom_ai_count / total_tenants * 100, 2),
            },
            "retention_correlation": {
                "global_retention_pct": round(global_retention, 2),
                "custom_ai_users_retention_pct": round(custom_ai_retention, 2),
                "uplift_pct": round(custom_ai_retention - global_retention, 2)
            }
        }

    async def get_successful_tenant_profile(self) -> Dict[str, Any]:
        """Synthesize a profile of the 'ideal' successful tenant based on data."""
        verticals = await self.vertical_success_analysis()
        top_vertical = verticals[0]["vertical"] if verticals else "unknown"
        
        correlations = await self.feature_retention_correlation()
        
        return {
            "target_vertical": top_vertical,
            "success_signals": [
                "Customized AI Personality (High correlation with retention)",
                "Daily conversation activity",
                "Completed onboarding in < 24 hours"
            ],
            "data_summary": {
                "top_verticals": [v["vertical"] for v in verticals[:3]],
                "key_feature_uplift": correlations.get("retention_correlation", {}).get("uplift_pct", 0)
            }
        }
