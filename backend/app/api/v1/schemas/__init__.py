"""API v1 schemas (Pydantic models for request/response).

REQ-WL-001-005: Waitlist schemas
REQ-NOTIF-001: Notification schemas
REQ-SEC-004: Auth schemas
"""

from app.api.v1.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.api.v1.schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
    SendNotificationRequest,
)
from app.api.v1.schemas.waitlist import (
    GuestCreate,
    GuestResponse,
    WaitlistEntryCreate,
    WaitlistEntryResponse,
    WaitlistEntryUpdate,
    WaitlistReorderRequest,
)

__all__ = [
    "GuestCreate",
    "GuestResponse",
    "LoginRequest",
    "NotificationListResponse",
    "NotificationResponse",
    "RefreshTokenRequest",
    "SendNotificationRequest",
    "TokenResponse",
    "UserCreate",
    "UserResponse",
    "WaitlistEntryCreate",
    "WaitlistEntryResponse",
    "WaitlistEntryUpdate",
    "WaitlistReorderRequest",
]
