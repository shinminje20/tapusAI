"""API dependencies (Dependency Injection).

Provides service instances with proper repository injection.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.services import WaitlistService
from app.infrastructure.database import get_db
from app.infrastructure.repositories import GuestRepository, WaitlistRepository


async def get_waitlist_service(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[WaitlistService, None]:
    """Provide WaitlistService with repository dependencies."""
    guest_repo = GuestRepository(db)
    waitlist_repo = WaitlistRepository(db)
    yield WaitlistService(waitlist_repo=waitlist_repo, guest_repo=guest_repo)
