import logging
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification, NotificationChannel, NotificationStatus
from app.core.email import email_service

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for handling notifications and email dispatch with retry logic."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_notification(
        self,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID | None,
        channel: NotificationChannel,
        subject: str,
        content: str,
        recipient: str,
        metadata: dict[str, Any] | None = None,
    ) -> Notification:
        """Create a notification record in the database."""
        notification = Notification(
            tenant_id=tenant_id,
            user_id=user_id,
            channel=channel,
            status=NotificationStatus.PENDING,
            recipient=recipient,
            subject=subject,
            content=content,
            metadata=metadata or {},
        )
        self.db.add(notification)
        await self.db.flush()
        return notification

    async def send_notification(self, notification_id: uuid.UUID) -> bool:
        """Send a notification by its ID with retry logic."""
        result = await self.db.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return False

        if notification.status == NotificationStatus.SENT:
            return True

        success = False
        if notification.channel == NotificationChannel.EMAIL:
            # For now, we use a simple HTML body. In the future, this could use templates.
            success = await email_service.send_email(
                to=notification.recipient,
                subject=notification.subject,
                html_body=notification.content,
            )

        if success:
            notification.status = NotificationStatus.SENT
            notification.sent_at = datetime.now(timezone.utc)
        else:
            notification.retry_count += 1
            if notification.retry_count >= 3:  # Max 3 retries
                notification.status = NotificationStatus.FAILED
            else:
                notification.status = NotificationStatus.PENDING
        
        await self.db.commit()
        return success

    async def send_email_notification(
        self,
        tenant_id: uuid.UUID,
        recipient: str,
        subject: str,
        content: str,
        user_id: uuid.UUID | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Notification:
        """Helper to create and immediately attempt to send an email notification."""
        notification = await self.create_notification(
            tenant_id=tenant_id,
            user_id=user_id,
            channel=NotificationChannel.EMAIL,
            recipient=recipient,
            subject=subject,
            content=content,
            metadata=metadata,
        )
        await self.db.commit() # Commit to ensure notification exists before sending
        
        # We can send this in the background in a real app, but here we'll do it 
        # as part of the service call or via a background task in the route.
        # For simplicity in this task, we'll trigger it here.
        await self.send_notification(notification.id)
        return notification

    async def retry_failed_notifications(self, tenant_id: uuid.UUID | None = None):
        """Retry all pending or failed notifications that haven't reached max retries."""
        query = select(Notification).where(
            Notification.status.in_([NotificationStatus.PENDING, NotificationStatus.FAILED]),
            Notification.retry_count < 3
        )
        if tenant_id:
            query = query.where(Notification.tenant_id == tenant_id)

        result = await self.db.execute(query)
        notifications = result.scalars().all()

        for notification in notifications:
            await self.send_notification(notification.id)
            # Add a small delay to avoid overwhelming the provider
            await asyncio.sleep(0.5)
