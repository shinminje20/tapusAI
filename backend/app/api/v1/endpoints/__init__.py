"""API v1 endpoints.

REQ-WL-001-005: Waitlist management
REQ-NOTIF-001: SMS notifications
REQ-NOTIF-002: Automated reminders
REQ-SEC-004: Authentication
REQ-MENU-001: Menu browsing
REQ-MENU-005: Guest token-based access
"""

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.guest import router as guest_router
from app.api.v1.endpoints.menu import admin_router as menu_admin_router
from app.api.v1.endpoints.menu import router as menu_router
from app.api.v1.endpoints.notifications import router as notifications_router
from app.api.v1.endpoints.reminders import router as reminders_router
from app.api.v1.endpoints.waitlist import router as waitlist_router

__all__ = [
    "auth_router",
    "guest_router",
    "menu_admin_router",
    "menu_router",
    "notifications_router",
    "reminders_router",
    "waitlist_router",
]
