"""API v1 endpoints.

REQ-WL-001-005: Waitlist management
REQ-NOTIF-001: SMS notifications
REQ-NOTIF-002: Automated reminders
REQ-SEC-004: Authentication
REQ-MENU-001: Menu browsing
REQ-MENU-005: Guest token-based access
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth_router,
    guest_router,
    menu_admin_router,
    menu_router,
    notifications_router,
    reminders_router,
    waitlist_router,
)

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(guest_router)
router.include_router(menu_router)
router.include_router(menu_admin_router)
router.include_router(notifications_router)
router.include_router(reminders_router)
router.include_router(waitlist_router)
