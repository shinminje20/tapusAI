"""Waitlist repository implementation.

Infrastructure adapter implementing WaitlistRepositoryInterface.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import WaitlistEntry, WaitlistStatus
from app.domain.interfaces import WaitlistRepositoryInterface


class WaitlistRepository(WaitlistRepositoryInterface):
    """SQLAlchemy implementation of WaitlistRepositoryInterface."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, entry: WaitlistEntry) -> WaitlistEntry:
        """Add a new waitlist entry."""
        self._session.add(entry)
        await self._session.flush()
        await self._session.refresh(entry)
        return entry

    async def get_by_id(self, entry_id: int) -> WaitlistEntry | None:
        """Get entry by ID."""
        result = await self._session.execute(
            select(WaitlistEntry).where(WaitlistEntry.id == entry_id)
        )
        return result.scalar_one_or_none()

    async def get_all_waiting(self) -> list[WaitlistEntry]:
        """Get all entries with status 'waiting', ordered by position."""
        result = await self._session.execute(
            select(WaitlistEntry)
            .where(WaitlistEntry.status == WaitlistStatus.WAITING.value)
            .order_by(WaitlistEntry.position)
        )
        return list(result.scalars().all())

    async def update(self, entry: WaitlistEntry) -> WaitlistEntry:
        """Update an existing entry."""
        await self._session.flush()
        await self._session.refresh(entry)
        return entry

    async def get_max_position(self) -> int:
        """Get the maximum position in the waitlist."""
        result = await self._session.execute(
            select(func.max(WaitlistEntry.position)).where(
                WaitlistEntry.status == WaitlistStatus.WAITING.value
            )
        )
        max_pos = result.scalar()
        return max_pos if max_pos is not None else 0

    async def update_positions(self, entries: list[WaitlistEntry]) -> None:
        """Bulk update positions for reordering."""
        await self._session.flush()
