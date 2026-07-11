import asyncio
from typing import Dict, Any
from app.core.config import settings
from app.core.database import async_session_maker
from app.services.internal_analytics_service import InternalAnalyticsService
from app.services.incident_service import IncidentService
from app.core.alerting import AlertManager
import structlog

logger = structlog.get_logger()

async def generate_operational_report():
    """Generate and distribute recurring operational and governance reports."""
    logger.info("Starting Operational Automation Report Generation...")

    async with async_session_maker() as db:
        analytics = InternalAnalyticsService(db)
        incident_svc = IncidentService(db)
        founder_svc = FounderDashboardService(db)
        ops_svc = OperationalInsightsService(db)
        
        # 1. Executive Summary (Founder Dashboard)
        executive_summary = await founder_svc.get_executive_summary()
        
        # 2. Churn Risk Digest
        retention_risks = await ops_svc.get_retention_risk_dashboard()
        
        # 3. Performance and SLA
        sla_metrics = await analytics.platform_sla_metrics()
        
        # 4. Incident Trends
        active_incidents = await incident_svc.list_active_incidents()
        
        governance_status = "HEALTHY" if len(active_incidents) == 0 else "DEGRADED"

        report_payload = {
            "mrr": executive_summary.get("mrr"),
            "active_tenants": executive_summary.get("active_tenants"),
            "activation_rate": executive_summary.get("activation_rate_pct"),
            "high_risk_tenants_count": len(retention_risks),
            "workflow_success_rate": sla_metrics.get("workflow_success_rate"),
            "governance_status": governance_status,
            "timestamp": executive_summary.get("timestamp")
        }
        
        logger.info(
            "recurring_executive_report",
            **report_payload
        )
        
        # If any high-risk tenants, trigger a CS digest alert
        if len(retention_risks) > 0:
             await AlertManager.trigger_alert(
                title="Weekly Churn Risk Digest",
                message=f"Detected {len(retention_risks)} tenants at risk. Action required.",
                severity="medium",
                component="customer_success",
                context={"risks": retention_risks[:5]}
            )

        if governance_status == "DEGRADED":
            await AlertManager.trigger_alert(
                title="Operational Report Warning",
                message="Platform governance status is degraded due to active incidents.",
                severity="high",
                component="operations",
                context=report_payload
            )

from app.services.analytics.founder_dashboard_service import FounderDashboardService
from app.services.analytics.operational_insights_service import OperationalInsightsService

if __name__ == "__main__":
    asyncio.run(generate_operational_report())
