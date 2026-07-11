import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Async email sending via SMTP (dev) or SendGrid (prod)."""

    def __init__(self):
        self.provider = settings.email_provider
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_address = settings.smtp_from

    async def send_email(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> bool:
        """Send an email. Mocks in development."""
        # 1. Check for Development/Local Mocking
        if settings.app_env == "development" or self.smtp_host == "localhost":
            print("\n" + "="*50)
            print(f"📧 MOCK EMAIL SENT")
            print(f"To: {to}")
            print(f"Subject: {subject}")
            print(f"Body: {text_body or 'HTML Body (truncated)'}")
            print("="*50 + "\n")
            return True

        try:
            if self.provider == "smtp":
                return await self._send_smtp(to, subject, html_body, text_body)
            elif self.provider == "sendgrid":
                return await self._send_sendgrid(to, subject, html_body, text_body)
            else:
                logger.warning(f"Unknown email provider: {self.provider}")
                return False
        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return False

    async def _send_smtp(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> bool:
        """Send via SMTP."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.from_address
        msg["To"] = to

        if text_body:
            msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                if self.smtp_user and self.smtp_password:
                    server.starttls()
                    server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.from_address, [to], msg.as_string())
            logger.info(f"Email sent to {to}: {subject}")
            return True
        except Exception as e:
            logger.error(f"SMTP send failed: {e}")
            return False

    async def _send_sendgrid(
        self,
        to: str,
        subject: str,
        html_body: str,
        text_body: str | None = None,
    ) -> bool:
        """Send via SendGrid API."""
        import httpx

        payload = {
            "personalizations": [{"to": [{"email": to}]}],
            "from": {"email": self.from_address},
            "subject": subject,
            "content": [
                {"type": "text/html", "value": html_body},
            ],
        }
        if text_body:
            payload["content"].insert(0, {"type": "text/plain", "value": text_body})

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.sendgrid.com/v3/mail/send",
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.sendgrid_api_key}",
                    "Content-Type": "application/json",
                },
                timeout=10.0,
            )
        return response.status_code in (200, 201, 202)

    async def send_verification_email(self, to: str, token: str) -> bool:
        """Send email verification."""
        verify_url = f"{settings.frontend_url}/verify-email?token={token}"
        subject = "Verify your AgentFlow AI account"
        html = f"""
        <h1>Welcome to AgentFlow AI</h1>
        <p>Click the link below to verify your email address:</p>
        <p><a href="{verify_url}">Verify Email</a></p>
        <p>This link expires in 24 hours.</p>
        """
        return await self.send_email(to, subject, html)

    async def send_password_reset_email(self, to: str, token: str) -> bool:
        """Send password reset email."""
        reset_url = f"{settings.frontend_url}/reset-password?token={token}"
        subject = "Reset your AgentFlow AI password"
        html = f"""
        <h1>Password Reset</h1>
        <p>Click the link below to reset your password:</p>
        <p><a href="{reset_url}">Reset Password</a></p>
        <p>This link expires in 1 hour. If you didn't request this, ignore this email.</p>
        """
        return await self.send_email(to, subject, html)

    async def send_booking_confirmation(
        self,
        to: str,
        customer_name: str,
        service: str,
        date_time: str,
    ) -> bool:
        """Send booking confirmation email."""
        subject = "Your appointment is confirmed"
        html = f"""
        <h1>Appointment Confirmed</h1>
        <p>Hi {customer_name},</p>
        <p>Your <strong>{service}</strong> appointment is confirmed for <strong>{date_time}</strong>.</p>
        <p>We look forward to seeing you!</p>
        """
        return await self.send_email(to, subject, html)


email_service = EmailService()