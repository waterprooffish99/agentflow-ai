import logging
import structlog
from typing import Any, Dict, Optional
from app.core.config import settings
from app.core.database import async_session_maker
from app.models.incident import IncidentSeverity
from app.services.incident_service import IncidentService

logger = structlog.get_logger()

class AlertManager:
    @staticmethod
    async def trigger_alert(
        title: str,
        message: str,
        severity: str = "medium",
        component: str = "platform",
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """Trigger an operational alert and record incident."""
        logger.error(
            "operational_alert",
            title=title,
            message=message,
            severity=severity,
            component=component,
            context=context or {},
            app_env=settings.app_env
        )
        
        # Record in DB
        try:
            async with async_session_maker() as db:
                service = IncidentService(db)
                await service.create_incident(
                    title=title,
                    description=message,
                    component=component,
                    severity=IncidentSeverity(severity),
                    metadata=context
                )
        except Exception as e:
            logger.exception("failed_to_record_incident", error=str(e))

    @staticmethod
    async def alert_deployment_failure(error_msg: str) -> None:
        await AlertManager.trigger_alert(
            title="Deployment Failure",
            message=f"Deployment validation failed: {error_msg}",
            severity="critical",
            component="deployment"
        )

    @staticmethod
    async def alert_ai_provider_degradation(provider: str, error: str) -> None:
        await AlertManager.trigger_alert(
            title="AI Provider Degradation",
            message=f"Provider {provider} is experiencing errors: {error}",
            severity="high",
            component="ai"
        )

    @staticmethod
    async def alert_queue_saturation(queue_name: str, depth: int) -> None:
        await AlertManager.trigger_alert(
            title="Queue Saturation",
            message=f"Queue {queue_name} has reached {depth} pending tasks",
            severity="high",
            component="worker"
        )

    @staticmethod
    async def alert_redis_outage() -> None:
        await AlertManager.trigger_alert(
            title="Redis Outage",
            message="Redis connection lost or timeout",
            severity="critical",
            component="redis"
        )

    @staticmethod
    async def alert_pilot_onboarding_friction(tenant_id: str, title: str) -> None:
        await AlertManager.trigger_alert(
            title="Pilot User Friction Detected",
            message=f"Pilot tenant {tenant_id} is reporting friction: {title}",
            severity="high",
            component="pilot_onboarding"
        )

    @staticmethod
    async def alert_support_spike(count: int) -> None:
        await AlertManager.trigger_alert(
            title="Support Ticket Spike",
            message=f"Received {count} new support issues in last hour",
            severity="medium",
            component="support"
        )
