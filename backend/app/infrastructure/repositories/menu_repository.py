"""Menu repository for database operations.

REQ-MENU-001: Menu browsing
AC-MENU-005: Data model access for menu_items
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities import MenuCategory, MenuItem


class MenuRepository:
    """Repository for menu-related database operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ==================== Categories ====================

    async def get_categories(self, active_only: bool = True) -> list[MenuCategory]:
        """Get all menu categories.

        Args:
            active_only: If True, only return active categories

        Returns:
            List of categories ordered by display_order
        """
        stmt = select(MenuCategory).order_by(MenuCategory.display_order)
        if active_only:
            stmt = stmt.where(MenuCategory.is_active == True)  # noqa: E712

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_category_by_id(self, category_id: int) -> MenuCategory | None:
        """Get a category by ID."""
        stmt = select(MenuCategory).where(MenuCategory.id == category_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_categories_with_items(
        self, active_only: bool = True
    ) -> list[MenuCategory]:
        """Get categories with their items pre-loaded.

        REQ-MENU-001: Support menu browsing by category
        """
        stmt = (
            select(MenuCategory)
            .options(selectinload(MenuCategory.items))
            .order_by(MenuCategory.display_order)
        )
        if active_only:
            stmt = stmt.where(MenuCategory.is_active == True)  # noqa: E712

        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def create_category(self, category: MenuCategory) -> MenuCategory:
        """Create a new category."""
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def update_category(self, category: MenuCategory) -> MenuCategory:
        """Update an existing category."""
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def delete_category(self, category: MenuCategory) -> None:
        """Delete a category (soft delete by setting is_active=False)."""
        category.is_active = False
        await self.session.flush()

    # ==================== Menu Items ====================

    async def get_items(
        self,
        category_id: int | None = None,
        active_only: bool = True,
        available_only: bool = False,
    ) -> list[MenuItem]:
        """Get menu items with optional filters.

        Args:
            category_id: Filter by category
            active_only: Only return active items
            available_only: Only return available items

        Returns:
            List of items ordered by display_order
        """
        stmt = select(MenuItem).order_by(MenuItem.display_order)

        if category_id is not None:
            stmt = stmt.where(MenuItem.category_id == category_id)
        if active_only:
            stmt = stmt.where(MenuItem.is_active == True)  # noqa: E712
        if available_only:
            stmt = stmt.where(MenuItem.is_available == True)  # noqa: E712

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_item_by_id(self, item_id: int) -> MenuItem | None:
        """Get a menu item by ID."""
        stmt = select(MenuItem).where(MenuItem.id == item_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_items_by_ids(self, item_ids: list[int]) -> list[MenuItem]:
        """Get multiple items by their IDs."""
        if not item_ids:
            return []
        stmt = select(MenuItem).where(MenuItem.id.in_(item_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create_item(self, item: MenuItem) -> MenuItem:
        """Create a new menu item."""
        self.session.add(item)
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def update_item(self, item: MenuItem) -> MenuItem:
        """Update an existing menu item."""
        await self.session.flush()
        await self.session.refresh(item)
        return item

    async def delete_item(self, item: MenuItem) -> None:
        """Delete an item (soft delete by setting is_active=False)."""
        item.is_active = False
        await self.session.flush()

    async def set_item_availability(
        self, item_id: int, is_available: bool
    ) -> MenuItem | None:
        """Toggle item availability (e.g., sold out)."""
        item = await self.get_item_by_id(item_id)
        if item:
            item.is_available = is_available
            await self.session.flush()
            await self.session.refresh(item)
        return item
