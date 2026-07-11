from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.api.deps import get_db
from app.schemas.auth import (
    UserRegisterRequest,
    UserRegisterResponse,
    EmailVerifyRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshRequest,
    RefreshResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.core.config import settings
from app.core.security_monitor import record_auth_failure

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegisterRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Register a new tenant and business admin user, and log them in."""
    auth_service = AuthService(db)
    tenant, user, _ = await auth_service.register_tenant(
        business_name=data.business_name,
        email=data.email,
        password=data.password,
        full_name=data.full_name,
        lead_source=data.lead_source,
        campaign_source=data.campaign_source,
        referral_source=data.referral_source,
        acquisition_channel=data.acquisition_channel,
    )
    
    # Auto-login after registration
    login_result = await auth_service.login(data.email, data.password)
    if not login_result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration successful but auto-login failed",
        )
    
    _, access_token, refresh_token = login_result

    # Set refresh token in httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )

    return UserRegisterResponse(
        tenant_id=tenant.id,
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/verify-email")
async def verify_email(
    data: EmailVerifyRequest,
    db: AsyncSession = Depends(get_db),
):
    """Verify email with token."""
    auth_service = AuthService(db)
    user = await auth_service.verify_email(data.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )
    return {"message": "Email verified successfully"}


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and return tokens."""
    auth_service = AuthService(db)
    result = await auth_service.login(data.email, data.password)
    if not result:
        await record_auth_failure(data.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user, access_token, refresh_token = result

    # Set refresh token in httpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Should be True in production
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )

    return TokenResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(deps.get_current_user)):
    """Get current authenticated user info."""
    return current_user


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Issue a new access token using a refresh token."""
    auth_service = AuthService(db)
    
    # Try getting refresh token from request body or cookie
    refresh_token = data.refresh_token
    # If not in body, we could check cookies here, but FastAPI makes it easier 
    # if we define it in the dependency. For now, let's stick to the schema.
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )

    result = await auth_service.refresh_access_token(refresh_token)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    access_token, expires_in = result
    return RefreshResponse(
        access_token=access_token,
        expires_in=expires_in,
    )


@router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing the refresh token cookie."""
    response.delete_cookie(key="refresh_token")
    return {"message": "Successfully logged out"}


@router.post("/reset-password-request")
async def reset_password_request(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request a password reset email."""
    auth_service = AuthService(db)
    # Always return success to avoid email enumeration
    await auth_service.request_password_reset(data.email)
    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password-confirm")
async def reset_password_confirm(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    """Reset password with token."""
    auth_service = AuthService(db)
    success = await auth_service.reset_password(data.token, data.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )
    return {"message": "Password reset successfully"}
