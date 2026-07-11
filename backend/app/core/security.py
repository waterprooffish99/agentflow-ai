import secrets
import uuid
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt

from app.core.config import settings

ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash a password using argon2."""
    return ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against a hash."""
    try:
        return ph.verify(password_hash, password)
    except VerifyMismatchError:
        return False


def create_access_token(user_id: uuid.UUID, tenant_id: uuid.UUID | None, role: str) -> str:
    """Create a JWT access token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id) if tenant_id else None,
        "role": role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.access_token_expire_minutes)).timestamp()),
        "jti": secrets.token_hex(16),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
        headers={"kid": settings.jwt_kid_current},
    )


def create_refresh_token(user_id: uuid.UUID) -> str:
    """Create a JWT refresh token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(days=settings.refresh_token_expire_days)).timestamp()),
        "jti": secrets.token_hex(24),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
        headers={"kid": settings.jwt_kid_current},
    )


def decode_token(token: str) -> dict | None:
    """Decode and validate a JWT token."""
    keys: list[str] = [settings.jwt_secret]
    if settings.jwt_previous_secret:
        keys.append(settings.jwt_previous_secret)

    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    if kid == settings.jwt_kid_previous and settings.jwt_previous_secret:
        keys = [settings.jwt_previous_secret, settings.jwt_secret]

    try:
        for key in keys:
            try:
                payload = jwt.decode(token, key, algorithms=[settings.jwt_algorithm])
                return payload
            except JWTError:
                continue
        return None
    except JWTError:
        return None


def create_email_verify_token(user_id: uuid.UUID) -> str:
    """Create an email verification token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "verify",
        "iat": now,
        "exp": now + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_password_reset_token(user_id: uuid.UUID) -> str:
    """Create a password reset token."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "reset",
        "iat": now,
        "exp": now + timedelta(hours=1),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_email_token(token: str) -> uuid.UUID | None:
    """Verify email token and return user_id."""
    payload = decode_token(token)
    if payload and payload.get("type") == "verify":
        return uuid.UUID(payload["sub"])
    return None


def verify_reset_token(token: str) -> tuple[uuid.UUID, datetime] | None:
    """Verify reset token and return user_id + expiry."""
    payload = decode_token(token)
    if payload and payload.get("type") == "reset":
        user_id = uuid.UUID(payload["sub"])
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        return user_id, exp
    return None
