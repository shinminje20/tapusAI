"""Domain entities.

REQ-WL-001: Guest and WaitlistEntry for waitlist management
REQ-WL-005: Status tracking via WaitlistStatus enum
REQ-NOTIF-001: Notification entity for SMS alerts
REQ-SEC-004: User entity for authentication and RBAC
"""

from app.domain.entities.enums import EntrySource, WaitlistStatus
from app.domain.entities.guest import Guest
from app.domain.entities.notification import (
    Notification,
    NotificationStatus,
    NotificationType,
)
from app.domain.entities.table import Table
from app.domain.entities.user import User, UserRole
from app.domain.entities.waitlist_entry import WaitlistEntry

__all__ = [
    "EntrySource",
    "Guest",
    "Notification",
    "NotificationStatus",
    "NotificationType",
    "Table",
    "User",
    "UserRole",
    "WaitlistEntry",
    "WaitlistStatus",
]
