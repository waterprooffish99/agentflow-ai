import uuid
from typing import Annotated, AsyncGenerator

from fastapi import Depends, Header, HTTPException, status, Cookie
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session_maker
from app.core.security import decode_token
from app.models import User, UserRole


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async with async_session_maker() as session:
        yield session


async def get_current_user(
    authorization: Annotated[str | None, Header()] = None,
    auth_token: Annotated[str | None, Cookie()] = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get the current authenticated user from JWT token (Header or Cookie)."""
    token = None
    
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
    elif auth_token:
        token = auth_token

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header or cookie",
        )

    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    user_id = uuid.UUID(payload["sub"])
    from sqlalchemy import select

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    status_val = user.status.value if hasattr(user.status, "value") else user.status
    if status_val != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    return user


def require_role(*roles: UserRole):
    """Dependency factory: require specific roles."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of: {[r.value for r in roles]}",
            )
        return current_user

    return role_checker


def get_tenant_id(current_user: User = Depends(get_current_user)) -> uuid.UUID | None:
    """Get tenant_id from current user."""
    if current_user.tenant_id is None and current_user.role != UserRole.SUPER_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant context is required for this action",
        )
    return current_user.tenant_id


# Type aliases for cleaner dependency injection
CurrentUser = Annotated[User, Depends(get_current_user)]
DBSession = Annotated[AsyncSession, Depends(get_db)]
