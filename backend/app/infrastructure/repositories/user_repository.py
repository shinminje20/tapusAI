"""User repository implementation.

REQ-SEC-004: Role-based access control - user data access.
Infrastructure adapter for User entity persistence.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User


class UserRepository:
    """SQLAlchemy implementation for User repository.

    REQ-SEC-004: Provides user data access for authentication and authorization.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session.
        """
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        """Get user by email address.

        NFR-SEC-010: Used for authentication lookup.

        Args:
            email: User email address.

        Returns:
            User if found, None otherwise.
        """
        result = await self._session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: int) -> User | None:
        """Get user by ID.

        Args:
            user_id: User ID.

        Returns:
            User if found, None otherwise.
        """
        result = await self._session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Create a new user.

        Args:
            user: User entity to persist.

        Returns:
            Created user with ID populated.
        """
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def update(self, user: User) -> User:
        """Update an existing user.

        Args:
            user: User entity with updated fields.

        Returns:
            Updated user.
        """
        await self._session.merge(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user

    async def get_all_by_restaurant(self, restaurant_id: int) -> list[User]:
        """Get all users for a restaurant.

        Args:
            restaurant_id: Restaurant ID.

        Returns:
            List of users for the restaurant.
        """
        result = await self._session.execute(
            select(User).where(User.restaurant_id == restaurant_id)
        )
        return list(result.scalars().all())
