import asyncio
import logging
from celery import shared_task
from app.core.celery import celery_app
from app.core.database import async_session_maker
from app.services.analytics.growth_automation_service import GrowthAutomationService
from app.services.analytics.founder_dashboard_service import FounderDashboardService
from app.services.analytics.operational_insights_service import OperationalInsightsService
from app.core.redis import redis_client
import json

logger = logging.getLogger(__name__)

@celery_app.task(name="growth_ops.run_automation_cycles")
def run_growth_automation_cycles():
    """Daily job to run all growth and rescue workflows."""
    async def _run():
        async with async_session_maker() as db:
            service = GrowthAutomationService(db)
            
            logger.info("Starting growth automation cycle...")
            
            # 1. Onboarding Rescue
            onboarding_res = await service.run_onboarding_rescue_workflow()
            
            # 2. Retention Rescue
            retention_res = await service.run_retention_rescue_workflow()
            
            logger.info(
                "Growth automation cycle completed",
                **onboarding_res,
                **retention_res
            )

    asyncio.run(_run())

@celery_app.task(name="growth_ops.refresh_executive_cache")
def refresh_executive_insights_cache():
    """Hourly job to refresh the Founder Dashboard and Anomaly cache."""
    async def _run():
        async with async_session_maker() as db:
            # 1. Refresh Founder Dashboard
            founder_svc = FounderDashboardService(db)
            summary = await founder_svc.get_executive_summary()
            await redis_client.set("admin_insight:founder_summary", json.dumps(summary), ex=3600)
            
            # 2. Refresh Anomaly Detection
            ops_svc = OperationalInsightsService(db)
            anomalies = await ops_svc.detect_anomalies()
            serialized = [a.model_dump(mode='json') for a in anomalies]
            await redis_client.set("admin_insight:operational_anomalies", json.dumps(serialized), ex=3600)
            
            logger.info("Executive insights cache refreshed")

    asyncio.run(_run())

@celery_app.task(name="growth_ops.cleanup_expired_trials")
def cleanup_expired_trials():
    """Job to handle trial expirations and status transitions."""
    # Placeholder for production trial lifecycle logic
    pass
