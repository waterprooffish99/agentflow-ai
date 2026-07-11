import uuid
import datetime as dt
from typing import Dict, Any, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Tenant, Conversation, Appointment, SupportIssue

class PilotSuccessService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_pilot_metrics(self) -> Dict[str, Any]:
        """Aggregate real-time metrics for pilot customers (5-20 users)."""
        
        # 1. Active Pilots
        tenants_stmt = select(Tenant).where(Tenant.status == "active")
        tenants = (await self.db.execute(tenants_stmt)).scalars().all()
        
        pilot_data = []
        for t in tenants:
            # 2. Activity in last 24h
            since_24h = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=24)
            convs_24h = await self.db.execute(
                select(func.count(Conversation.id)).where(
                    Conversation.tenant_id == t.id,
                    Conversation.created_at >= since_24h
                )
            )
            
            # 3. Successful Bookings in last 24h
            bookings_24h = await self.db.execute(
                select(func.count(Appointment.id)).where(
                    Appointment.tenant_id == t.id,
                    Appointment.created_at >= since_24h
                )
            )
            
            # 4. Open Support Issues
            support_issues = await self.db.execute(
                select(func.count(SupportIssue.id)).where(
                    SupportIssue.tenant_id == t.id,
                    SupportIssue.status == "open"
                )
            )

            pilot_data.append({
                "tenant_id": t.id,
                "business_name": t.business_name,
                "conversations_24h": convs_24h.scalar() or 0,
                "bookings_24h": bookings_24h.scalar() or 0,
                "open_support_issues": support_issues.scalar() or 0,
                "onboarding_status": t.settings.get("onboarding_step", "complete") if t.settings else "unknown"
            })
            
        return {
            "total_active_pilots": len(tenants),
            "pilots": pilot_data,
            "system_health": "stable" # Heuristic
        }

    async def get_onboarding_friction_summary(self) -> List[Dict[str, Any]]:
        """Identify where pilot users are dropping off or failing setup."""
        # Check SupportIssues categorized as 'onboarding_friction'
        stmt = select(SupportIssue).where(SupportIssue.issue_type == "onboarding_friction")
        results = await self.db.execute(stmt)
        issues = results.scalars().all()
        
        return [
            {
                "title": i.title,
                "description": i.description,
                "tenant_id": i.tenant_id,
                "created_at": i.created_at
            } for i in issues
        ]
