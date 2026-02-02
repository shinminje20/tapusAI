"""Guest repository implementation.

Infrastructure adapter implementing GuestRepositoryInterface.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import Guest
from app.domain.interfaces import GuestRepositoryInterface


class GuestRepository(GuestRepositoryInterface):
    """SQLAlchemy implementation of GuestRepositoryInterface."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, guest: Guest) -> Guest:
        """Add a new guest."""
        self._session.add(guest)
        await self._session.flush()
        await self._session.refresh(guest)
        return guest

    async def get_by_id(self, guest_id: int) -> Guest | None:
        """Get guest by ID."""
        result = await self._session.execute(
            select(Guest).where(Guest.id == guest_id)
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone_number: str) -> Guest | None:
        """Get guest by phone number."""
        result = await self._session.execute(
            select(Guest).where(Guest.phone_number == phone_number)
        )
        return result.scalar_one_or_none()
