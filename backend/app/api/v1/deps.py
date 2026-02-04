"""API dependencies (Dependency Injection).

Provides service instances with proper repository injection.
REQ-NOTIF-001: SMS notification service dependency.
"""

from collections.abc import AsyncGenerator
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.domain.services import WaitlistService
from app.infrastructure.database import get_db
from app.infrastructure.repositories import GuestRepository, WaitlistRepository
from app.infrastructure.sms.base import SMSAdapter
from app.infrastructure.sms.mock_adapter import MockSMSAdapter
from app.infrastructure.sms.twilio_adapter import TwilioAdapter
from app.services.notification_service import NotificationService


async def get_waitlist_service(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[WaitlistService, None]:
    """Provide WaitlistService with repository dependencies."""
    guest_repo = GuestRepository(db)
    waitlist_repo = WaitlistRepository(db)
    yield WaitlistService(waitlist_repo=waitlist_repo, guest_repo=guest_repo)


@lru_cache
def get_sms_adapter() -> SMSAdapter:
    """Get SMS adapter based on configuration.

    REQ-NOTIF-001: SMS/text alerts when table is ready

    Returns:
        MockSMSAdapter for testing, TwilioAdapter for production
    """
    settings = get_settings()

    if settings.sms_adapter == "twilio":
        return TwilioAdapter(
            account_sid=settings.twilio_account_sid,
            auth_token=settings.twilio_auth_token,
            from_number=settings.twilio_from_number,
        )
    else:
        # Default to mock adapter
        return MockSMSAdapter()


async def get_notification_service(
    db: AsyncSession = Depends(get_db),
    sms_adapter: SMSAdapter = Depends(get_sms_adapter),
) -> AsyncGenerator[NotificationService, None]:
    """Provide NotificationService with dependencies.

    REQ-NOTIF-001: SMS/text alerts when table is ready
    """
    settings = get_settings()
    yield NotificationService(
        session=db,
        sms_adapter=sms_adapter,
        restaurant_name=settings.restaurant_name,
    )
