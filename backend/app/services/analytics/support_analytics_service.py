import uuid
import datetime as dt
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import SupportIssue
from app.schemas.analytics import SupportMetrics
from app.services.analytics.utils import apply_tenant_filter, apply_date_window

class SupportAnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_tenant_support_metrics(self, tenant_id: uuid.UUID) -> SupportMetrics:
        """Analyze support issues for a specific tenant."""
        # 1. Open issues count
        open_count_stmt = (
            select(func.count(SupportIssue.id))
            .where(and_(SupportIssue.tenant_id == tenant_id, SupportIssue.status == "open"))
        )
        open_count = (await self.db.execute(open_count_stmt)).scalar() or 0
        
        # 2. Top categories for this tenant
        cat_stmt = (
            select(SupportIssue.category, func.count(SupportIssue.id))
            .where(SupportIssue.tenant_id == tenant_id)
            .group_by(SupportIssue.category)
            .order_by(func.count(SupportIssue.id).desc())
            .limit(5)
        )
        cat_result = await self.db.execute(cat_stmt)
        categories = [{"category": row[0], "count": row[1]} for row in cat_result.all()]
        
        return SupportMetrics(
            tenant_id=tenant_id,
            open_issues_count=open_count,
            top_issue_categories=categories
        )

    async def platform_support_analytics(self) -> Dict[str, Any]:
        """Aggregate support metrics across the platform, bounded to last 90 days (SUPER_ADMIN only)."""
        since_90d = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=90)
        
        # 1. Platform-wide workload
        stmt = (
            select(SupportIssue.status, func.count(SupportIssue.id))
            .where(SupportIssue.created_at >= since_90d)
            .group_by(SupportIssue.status)
        )
        workload_result = await self.db.execute(stmt)
        workload = {row[0]: row[1] for row in workload_result.all()}
        
        # 2. Clustering: Top issues by category and type
        cluster_stmt = (
            select(SupportIssue.category, SupportIssue.issue_type, func.count(SupportIssue.id))
            .where(SupportIssue.created_at >= since_90d)
            .group_by(SupportIssue.category, SupportIssue.issue_type)
            .order_by(func.count(SupportIssue.id).desc())
            .limit(10)
        )
        cluster_result = await self.db.execute(cluster_stmt)
        clusters = [
            {"category": row[0], "issue_type": row[1], "count": row[2]} 
            for row in cluster_result.all()
        ]
        
        # 3. Onboarding Friction Patterns
        friction_stmt = (
            select(SupportIssue.title, func.count(SupportIssue.id))
            .where(and_(SupportIssue.issue_type == "onboarding_friction", SupportIssue.created_at >= since_90d))
            .group_by(SupportIssue.title)
            .order_by(func.count(SupportIssue.id).desc())
            .limit(5)
        )
        friction_result = await self.db.execute(friction_stmt)
        friction_patterns = [{"title": row[0], "count": row[1]} for row in friction_result.all()]
        
        return {
            "workload": workload,
            "top_issue_clusters": clusters,
            "onboarding_friction_patterns": friction_patterns,
            "total_open_issues": workload.get("open", 0),
            "window_days": 90
        }
