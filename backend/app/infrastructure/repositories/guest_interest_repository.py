"""Guest interest repository for database operations.

REQ-MENU-002: Guests can "star" items
AC-MENU-002: Star items stores to guest/waitlist entry
AC-MENU-003: Soft pre-order capture
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities import GuestInterest, MenuItem, WaitlistEntry


class GuestInterestRepository:
    """Repository for guest interest database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_entry_by_token(self, token: str) -> WaitlistEntry | None:
        """Get waitlist entry by guest token.

        AC-MENU-001: Validate token for menu access
        """
        stmt = (
            select(WaitlistEntry)
            .where(WaitlistEntry.guest_token == token)
            .options(selectinload(WaitlistEntry.guest))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_interests_for_entry(
        self, entry_id: int, include_items: bool = False
    ) -> list[GuestInterest]:
        """Get all interests for a waitlist entry.

        Args:
            entry_id: Waitlist entry ID
            include_items: If True, eagerly load menu items

        Returns:
            List of guest interests
        """
        stmt = select(GuestInterest).where(GuestInterest.waitlist_entry_id == entry_id)
        if include_items:
            stmt = stmt.options(selectinload(GuestInterest.menu_item))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_interest(
        self, entry_id: int, menu_item_id: int
    ) -> GuestInterest | None:
        """Get a specific interest record."""
        stmt = select(GuestInterest).where(
            GuestInterest.waitlist_entry_id == entry_id,
            GuestInterest.menu_item_id == menu_item_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def star_item(
        self, entry_id: int, menu_item_id: int, starred: bool = True
    ) -> GuestInterest:
        """Star or unstar a menu item.

        AC-MENU-002: Star items for interest capture
        """
        interest = await self.get_interest(entry_id, menu_item_id)

        if interest:
            interest.is_starred = starred
        else:
            interest = GuestInterest(
                waitlist_entry_id=entry_id,
                menu_item_id=menu_item_id,
                is_starred=starred,
            )
            self.session.add(interest)

        await self.session.flush()
        await self.session.refresh(interest)
        return interest

    async def add_preorder(
        self, entry_id: int, menu_item_id: int, quantity: int = 1
    ) -> GuestInterest:
        """Add item to pre-order.

        AC-MENU-003: Soft pre-order capture
        """
        interest = await self.get_interest(entry_id, menu_item_id)

        if interest:
            interest.is_preorder = True
            interest.quantity = quantity
        else:
            interest = GuestInterest(
                waitlist_entry_id=entry_id,
                menu_item_id=menu_item_id,
                is_starred=True,  # Pre-order implies interest
                is_preorder=True,
                quantity=quantity,
            )
            self.session.add(interest)

        await self.session.flush()
        await self.session.refresh(interest)
        return interest

    async def remove_preorder(self, entry_id: int, menu_item_id: int) -> GuestInterest | None:
        """Remove item from pre-order (keeps starred if was starred)."""
        interest = await self.get_interest(entry_id, menu_item_id)
        if interest:
            interest.is_preorder = False
            interest.quantity = 1
            await self.session.flush()
            await self.session.refresh(interest)
        return interest

    async def clear_interests(self, entry_id: int) -> int:
        """Clear all interests for an entry. Returns count deleted."""
        interests = await self.get_interests_for_entry(entry_id)
        count = len(interests)
        for interest in interests:
            await self.session.delete(interest)
        await self.session.flush()
        return count

    async def get_starred_items(self, entry_id: int) -> list[GuestInterest]:
        """Get only starred items for an entry."""
        stmt = (
            select(GuestInterest)
            .where(
                GuestInterest.waitlist_entry_id == entry_id,
                GuestInterest.is_starred == True,  # noqa: E712
            )
            .options(selectinload(GuestInterest.menu_item))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_preorder_items(self, entry_id: int) -> list[GuestInterest]:
        """Get only pre-order items for an entry."""
        stmt = (
            select(GuestInterest)
            .where(
                GuestInterest.waitlist_entry_id == entry_id,
                GuestInterest.is_preorder == True,  # noqa: E712
            )
            .options(selectinload(GuestInterest.menu_item))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
