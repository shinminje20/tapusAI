"""Guest repository interface (port).

Defines the contract for guest data access.
"""

from abc import ABC, abstractmethod

from app.domain.entities import Guest


class GuestRepositoryInterface(ABC):
    """Abstract repository for guest operations."""

    @abstractmethod
    async def add(self, guest: Guest) -> Guest:
        """Add a new guest."""
        ...

    @abstractmethod
    async def get_by_id(self, guest_id: int) -> Guest | None:
        """Get guest by ID."""
        ...

    @abstractmethod
    async def get_by_phone(self, phone_number: str) -> Guest | None:
        """Get guest by phone number."""
        ...
