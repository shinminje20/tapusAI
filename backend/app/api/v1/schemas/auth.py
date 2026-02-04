"""Authentication API schemas.

REQ-SEC-004: Role-based access control
NFR-SEC-010: Authentication required for admin access
NFR-SEC-012: Session security - token handling
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LoginRequest(BaseModel):
    """Schema for login request.

    NFR-SEC-010: Authentication required for admin access.
    """

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class TokenResponse(BaseModel):
    """Schema for token response.

    NFR-SEC-012: Token/session handling.
    """

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request.

    NFR-SEC-012: Refresh mechanism must be secure.
    """

    refresh_token: str = Field(..., description="JWT refresh token")


class UserResponse(BaseModel):
    """Schema for user response.

    REQ-SEC-004: Role-based access control - expose role info.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="User ID")
    email: str = Field(..., description="User email address")
    role: str = Field(..., description="User role (guest, host, manager, owner)")
    restaurant_id: int | None = Field(None, description="Associated restaurant ID")
    is_active: bool = Field(..., description="Whether user is active")
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class UserCreate(BaseModel):
    """Schema for creating a new user (internal/admin use).

    REQ-SEC-004: Role-based access control.
    """

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 chars)")
    role: str = Field(default="host", description="User role")
    restaurant_id: int | None = Field(None, description="Associated restaurant ID")
