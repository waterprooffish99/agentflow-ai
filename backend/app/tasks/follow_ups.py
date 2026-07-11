import asyncio
import logging
from datetime import datetime, timezone

from app.core.celery import celery_app
from app.core.database import async_session_maker
from app.core.redis import redis_client
from app.core.redis_keys import tenant_key
from app.core.resilience import with_retry
from app.services.crm_service import ActivityTimelineService
from app.models import FollowUpTask, FollowUpStatus

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.follow_ups.process_reminders")
def process_reminders():
    """Check for overdue or upcoming follow-up tasks and send notifications."""
    # Celery tasks are usually sync, but we use an async bridge
    return asyncio.run(_process_reminders_async())

async def _process_reminders_async():
    async with async_session_maker() as db:
        # 1. Find pending tasks due now or in the past
        from sqlalchemy import select
        result = await db.execute(
            select(FollowUpTask).where(
                FollowUpTask.status == FollowUpStatus.PENDING,
                FollowUpTask.due_at <= datetime.now(timezone.utc)
            )
        )
        tasks = result.scalars().all()
        
        for task in tasks:
            logger.info(f"Processing reminder for task: {task.id}")
            lock_key = tenant_key(task.tenant_id, "tasks", "followup", str(task.id))
            # Dedupe protection in case of worker retries/duplicates.
            try:
                acquired = await redis_client.set(lock_key, "1", ex=900, nx=True)
            except Exception:
                acquired = True
            if not acquired:
                continue
            # 2. Send notification to assigned staff
            # ... notification logic ...
            
            # 3. Log activity
            timeline = ActivityTimelineService(db)
            await with_retry(
                lambda: timeline.log_activity(
                    tenant_id=task.tenant_id,
                    customer_id=task.customer_id,
                    activity_type="follow_up_reminder",
                    description=f"Automated reminder triggered for: {task.title}",
                ),
                attempts=2,
                timeout_seconds=8.0,
            )
            
            # 4. Mark as overdue if needed or just leave as pending
            
        await db.commit()
