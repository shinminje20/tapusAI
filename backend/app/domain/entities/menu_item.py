"""MenuItem entity model.

REQ-MENU-001: Guests can browse an interactive menu
REQ-MENU-002: Guests can "star" items they are interested in
AC-MENU-005: Data model exists for menu (menu_items)
"""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base

if TYPE_CHECKING:
    from app.domain.entities.menu_category import MenuCategory
    from app.domain.entities.guest_interest import GuestInterest


class MenuItem(Base):
    """Menu item representing a dish or beverage.

    REQ-MENU-001: Interactive menu browsing
    AC-MENU-005: Data model for menu items
    - name, description, price for display
    - category for organization
    - image_url for visual presentation
    - is_available for real-time availability
    """

    __tablename__ = "menu_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("menu_categories.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    image_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Optional fields for enhanced display
    calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    allergens: Mapped[str | None] = mapped_column(String(500), nullable=True)
    tags: Mapped[str | None] = mapped_column(String(200), nullable=True)  # e.g., "vegan,gluten-free"

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    category: Mapped["MenuCategory"] = relationship(
        "MenuCategory", back_populates="items"
    )
    guest_interests: Mapped[list["GuestInterest"]] = relationship(
        "GuestInterest", back_populates="menu_item"
    )

    def __init__(
        self,
        category_id: int,
        name: str,
        price: Decimal,
        description: str | None = None,
        image_url: str | None = None,
        display_order: int = 0,
        is_available: bool = True,
        is_active: bool = True,
        calories: int | None = None,
        allergens: str | None = None,
        tags: str | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            category_id=category_id,
            name=name,
            price=price,
            description=description,
            image_url=image_url,
            display_order=display_order,
            is_available=is_available,
            is_active=is_active,
            calories=calories,
            allergens=allergens,
            tags=tags,
            **kwargs,
        )

    @property
    def tags_list(self) -> list[str]:
        """Get tags as a list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",")]

    def __repr__(self) -> str:
        return f"<MenuItem(id={self.id}, name={self.name}, price={self.price})>"
