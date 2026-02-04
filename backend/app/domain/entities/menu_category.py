"""MenuCategory entity model.

REQ-MENU-001: Guests can browse an interactive menu
AC-MENU-005: Data model exists for menu (menu_items organized by category)
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base

if TYPE_CHECKING:
    from app.domain.entities.menu_item import MenuItem


class MenuCategory(Base):
    """Menu category for organizing menu items.

    AC-MENU-005: Data model for menu organization
    - Categories group related menu items
    - Display order controls presentation sequence
    """

    __tablename__ = "menu_categories"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    items: Mapped[list["MenuItem"]] = relationship(
        "MenuItem", back_populates="category", order_by="MenuItem.display_order"
    )

    def __init__(
        self,
        name: str,
        description: str | None = None,
        display_order: int = 0,
        is_active: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(
            name=name,
            description=description,
            display_order=display_order,
            is_active=is_active,
            **kwargs,
        )

    def __repr__(self) -> str:
        return f"<MenuCategory(id={self.id}, name={self.name})>"
