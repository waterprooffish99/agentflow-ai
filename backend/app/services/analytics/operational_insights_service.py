import uuid
import datetime as dt
from typing import Dict, Any, List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Tenant, Conversation, WorkflowExecution, WorkflowExecutionStatus
from app.schemas.analytics import OperationalAnomaly

class OperationalInsightsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def platform_health_overview(self) -> Dict[str, Any]:
        """Synthesize a high-level health report of the platform."""
        since_24h = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=24)
        
        # 1. Workflow Success Rate
        total_wf = await self.db.execute(
            select(func.count(WorkflowExecution.id)).where(WorkflowExecution.created_at >= since_24h)
        )
        failed_wf = await self.db.execute(
            select(func.count(WorkflowExecution.id)).where(
                and_(WorkflowExecution.created_at >= since_24h, WorkflowExecution.status == WorkflowExecutionStatus.FAILED)
            )
        )
        
        total = total_wf.scalar() or 0
        failed = failed_wf.scalar() or 0
        success_rate = ((total - failed) / total * 100) if total > 0 else 100.0
        
        # 2. Active Tenants (DAU)
        active_tenants = await self.db.execute(
            select(func.count(func.distinct(Conversation.tenant_id)))
            .where(Conversation.created_at >= since_24h)
        )
        dau = active_tenants.scalar() or 0
        
        return {
            "workflow_success_rate_pct": round(success_rate, 2),
            "daily_active_tenants": dau,
            "status": "HEALTHY" if success_rate > 95 else "DEGRADED"
        }

    async def detect_anomalies(self) -> List[OperationalAnomaly]:
        """Scan for operational anomalies like spikes in failures, drops in usage, or retention risks."""
        anomalies = []
        health = await self.platform_health_overview()
        
        if health["workflow_success_rate_pct"] < 90:
            anomalies.append(OperationalAnomaly(
                anomaly_type="WORKFLOW_FAILURE_SPIKE",
                severity="CRITICAL",
                detected_at=dt.datetime.now(dt.timezone.utc),
                description=f"Workflow success rate dropped to {health['workflow_success_rate_pct']}% in last 24h"
            ))
            
        if health["daily_active_tenants"] == 0:
            anomalies.append(OperationalAnomaly(
                anomaly_type="ZERO_ACTIVITY_DETECTED",
                severity="WARNING",
                detected_at=dt.datetime.now(dt.timezone.utc),
                description="Zero conversation activity detected across all tenants in last 24h"
            ))
            
        # Retention Risk Spike
        risk_dashboard = await self.get_retention_risk_dashboard()
        high_risk_count = sum(1 for r in risk_dashboard if r["risk_level"] == "HIGH")
        if high_risk_count > 5: # Threshold for manual review
             anomalies.append(OperationalAnomaly(
                anomaly_type="RETENTION_RISK_SPIKE",
                severity="WARNING",
                detected_at=dt.datetime.now(dt.timezone.utc),
                description=f"Detected {high_risk_count} tenants at CRITICAL churn risk. Immediate intervention recommended."
            ))
            
        return anomalies

    async def get_retention_risk_dashboard(self) -> List[Dict[str, Any]]:
        """Identify tenants with highest churn risk for immediate intervention using optimized set-based queries."""
        now = dt.datetime.now(dt.timezone.utc)
        since_30d = now - dt.timedelta(days=30)
        since_14d = now - dt.timedelta(days=14)
        since_7d = now - dt.timedelta(days=7)
        
        # 1. Single-pass aggregation over conversations for all tenants
        stats_stmt = (
            select(
                Conversation.tenant_id,
                func.count(func.distinct(func.date(Conversation.created_at))).filter(Conversation.created_at >= since_30d).label("active_days_30d"),
                func.count(Conversation.id).filter(Conversation.created_at >= since_7d).label("tw_vol"),
                func.count(Conversation.id).filter(and_(Conversation.created_at >= since_14d, Conversation.created_at < since_7d)).label("lw_vol")
            )
            .where(Conversation.created_at >= since_30d) # Bounded pass
            .group_by(Conversation.tenant_id)
        ).subquery()

        # 2. Join with active tenants within a 90-day window
        since_90d = now - dt.timedelta(days=90)
        stmt = (
            select(
                Tenant.id,
                Tenant.business_name,
                func.coalesce(stats_stmt.c.active_days_30d, 0).label("active_days_30d"),
                func.coalesce(stats_stmt.c.tw_vol, 0).label("tw_vol"),
                func.coalesce(stats_stmt.c.lw_vol, 0).label("lw_vol")
            )
            .outerjoin(stats_stmt, Tenant.id == stats_stmt.c.tenant_id)
            .where(and_(Tenant.status == "active", Tenant.created_at >= since_90d))
        )
        
        result = await self.db.execute(stmt)
        risk_list = []
        
        for row in result.all():
            # Calculate metrics in Python from aggregated results
            trend = 0.0
            if row.lw_vol > 0:
                trend = (row.tw_vol - row.lw_vol) / row.lw_vol
            elif row.tw_vol > 0:
                trend = 1.0
                
            risk = "LOW"
            if row.active_days_30d == 0:
                risk = "HIGH"
            elif row.active_days_30d < 3 or trend < -0.5:
                risk = "MEDIUM"
                
            if risk in ["HIGH", "MEDIUM"]:
                risk_list.append({
                    "tenant_id": row.id,
                    "business_name": row.business_name,
                    "risk_level": risk,
                    "engagement_trend": round(trend, 2),
                    "active_days_30d": row.active_days_30d
                })
                
        risk_list.sort(key=lambda x: x["engagement_trend"])
        return risk_list[:10]
