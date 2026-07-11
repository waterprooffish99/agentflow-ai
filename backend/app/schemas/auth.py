import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegisterRequest(BaseModel):
    business_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=100)
    
    # Lead Attribution
    lead_source: str | None = Field(None, max_length=50)
    campaign_source: str | None = Field(None, max_length=50)
    referral_source: str | None = Field(None, max_length=255)
    acquisition_channel: str | None = Field(None, max_length=50)


class UserRegisterResponse(BaseModel):
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    access_token: str
    refresh_token: str
    message: str = "Account created and logged in."


class EmailVerifyRequest(BaseModel):
    token: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: "UserResponse"


class RefreshRequest(BaseModel):
    refresh_token: str | None = None


class RefreshResponse(BaseModel):
    access_token: str
    expires_in: int


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    role: str
    full_name: str
    tenant_id: uuid.UUID | None
    status: str
    email_verified: bool
    last_login: datetime | None = None

    model_config = {"from_attributes": True}


class UserUpdateRequest(BaseModel):
    role: str | None = None
    status: str | None = None
    full_name: str | None = None


class UserInviteRequest(BaseModel):
    email: EmailStr
    role: str = Field(..., pattern="^(business_admin|staff)$")
    full_name: str | None = None


TokenResponse.model_rebuild()