"""Waitlist repository interface (port).

Defines the contract for waitlist data access.
Following DIP - domain depends on abstraction, not implementation.
"""

from abc import ABC, abstractmethod

from app.domain.entities import WaitlistEntry


class WaitlistRepositoryInterface(ABC):
    """Abstract repository for waitlist operations."""

    @abstractmethod
    async def add(self, entry: WaitlistEntry) -> WaitlistEntry:
        """Add a new waitlist entry."""
        ...

    @abstractmethod
    async def get_by_id(self, entry_id: int) -> WaitlistEntry | None:
        """Get entry by ID."""
        ...

    @abstractmethod
    async def get_all_waiting(self) -> list[WaitlistEntry]:
        """Get all entries with status 'waiting', ordered by position."""
        ...

    @abstractmethod
    async def update(self, entry: WaitlistEntry) -> WaitlistEntry:
        """Update an existing entry."""
        ...

    @abstractmethod
    async def get_max_position(self) -> int:
        """Get the maximum position in the waitlist."""
        ...

    @abstractmethod
    async def update_positions(self, entries: list[WaitlistEntry]) -> None:
        """Bulk update positions for reordering."""
        ...
