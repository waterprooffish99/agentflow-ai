import uuid
from datetime import datetime, timezone, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Tenant,
    TenantStatus,
    User,
    UserRole,
    UserStatus,
    SubscriptionTier,
)
from app.core.security import (
    create_access_token,
    create_email_verify_token,
    create_password_reset_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_email_token,
    verify_reset_token,
    decode_token,
)
from app.core.email import email_service
from app.core.config import settings
from app.core.redis import redis_client
from app.core.redis_keys import tenant_key


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_tenant(
        self,
        business_name: str,
        email: str,
        password: str,
        full_name: str,
        lead_source: str | None = None,
        campaign_source: str | None = None,
        referral_source: str | None = None,
        acquisition_channel: str | None = None,
    ) -> tuple[Tenant, User, str]:
        """Create a new tenant with a business admin user."""
        # Create tenant
        tenant = Tenant(
            business_name=business_name,
            timezone="UTC",
            subscription_tier=SubscriptionTier.FREE,
            status=TenantStatus.TRIAL,
            lead_source=lead_source,
            campaign_source=campaign_source,
            referral_source=referral_source,
            acquisition_channel=acquisition_channel,
            settings={
                "business_hours": {"monday": {"start": "09:00", "end": "17:00"}},
                "services": [],
                "staff": [],
            },
        )
        self.db.add(tenant)
        await self.db.flush()

        # Create business admin user
        user = User(
            tenant_id=tenant.id,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.BUSINESS_ADMIN,
            full_name=full_name,
            email_verified=False,
        )
        self.db.add(user)
        await self.db.flush()

        # Create verification token with user_id
        verify_token = create_email_verify_token(user.id)
        user.email_verify_token = verify_token

        # Send verification email
        await email_service.send_verification_email(email, verify_token)

        await self.db.commit()
        return tenant, user, verify_token

    async def verify_email(self, token: str) -> User | None:
        """Verify email with token."""
        user_id = verify_email_token(token)
        if not user_id:
            return None

        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            return None

        user.email_verified = True
        user.email_verify_token = None
        user.status = UserStatus.ACTIVE
        await self.db.commit()
        return user

    async def login(self, email: str, password: str) -> tuple[User, str, str] | None:
        """Authenticate user and return tokens."""
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return None

        if not verify_password(password, user.password_hash):
            return None

        if user.status != UserStatus.ACTIVE:
            return None

        # Update last login
        user.last_login = datetime.now(timezone.utc)
        await self.db.commit()

        access_token = create_access_token(user.id, user.tenant_id, str(user.role))
        refresh_token = create_refresh_token(user.id)
        return user, access_token, refresh_token

    async def refresh_access_token(self, refresh_token: str) -> tuple[str, int] | None:
        """Issue new access token from refresh token."""
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        jti = payload.get("jti")
        exp = payload.get("exp")
        if not jti or not exp:
            return None

        now_ts = int(datetime.now(timezone.utc).timestamp())
        ttl = max(int(exp) - now_ts, 1)
        # Replay protection for refresh tokens.
        replay_key = tenant_key("global", "auth", "refresh_jti", jti)
        try:
            is_new = await redis_client.set(replay_key, "1", ex=ttl, nx=True)
            if not is_new:
                return None
        except Exception:
            # If Redis is down, do not hard-fail auth refresh path.
            pass

        user_id = uuid.UUID(payload["sub"])
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user or user.status != UserStatus.ACTIVE:
            return None

        access_token = create_access_token(user.id, user.tenant_id, str(user.role))
        return access_token, settings.access_token_expire_minutes * 60

    async def request_password_reset(self, email: str) -> bool:
        """Send password reset email."""
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            return False

        token = create_password_reset_token(user.id)
        user.password_reset_token = token
        user.password_reset_expires = datetime.now(timezone.utc) + timedelta(hours=1)
        await self.db.commit()

        return await email_service.send_password_reset_email(email, token)

    async def reset_password(self, token: str, new_password: str) -> bool:
        """Reset password with token."""
        result = verify_reset_token(token)
        if not result:
            return False

        user_id, expires = result
        if datetime.now(timezone.utc) > expires:
            return False

        db_result = await self.db.execute(select(User).where(User.id == user_id))
        user = db_result.scalar_one_or_none()
        if not user:
            return False

        user.password_hash = hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        await self.db.commit()
        return True
