"""GuestInterest entity model.

REQ-MENU-002: Guests can "star" items they are interested in
REQ-MENU-003: Soft pre-order (fast casual)
REQ-MENU-004: Server sees predicted interests (full service)
AC-MENU-002: Star items stores to guest/waitlist entry
AC-MENU-003: Soft pre-order stored, hidden until seated
AC-MENU-005: Data model for guest_interests and preorders
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base

if TYPE_CHECKING:
    from app.domain.entities.menu_item import MenuItem
    from app.domain.entities.waitlist_entry import WaitlistEntry


class GuestInterest(Base):
    """Guest interest in a menu item (starred or pre-ordered).

    REQ-MENU-002: Star items for interest capture
    REQ-MENU-003: Soft pre-order with quantity
    AC-MENU-002: Stores starred items tied to waitlist entry
    AC-MENU-003: Pre-order not exposed to kitchen until seated

    Fields:
    - is_starred: Guest marked interest (star)
    - is_preorder: Guest wants to pre-order (fast casual)
    - quantity: For pre-orders, how many to order
    """

    __tablename__ = "guest_interests"

    # Unique constraint: one record per entry + menu item
    __table_args__ = (
        UniqueConstraint("waitlist_entry_id", "menu_item_id", name="uq_entry_item"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    waitlist_entry_id: Mapped[int] = mapped_column(
        ForeignKey("waitlist_entries.id"), nullable=False
    )
    menu_item_id: Mapped[int] = mapped_column(
        ForeignKey("menu_items.id"), nullable=False
    )

    # Interest tracking
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Pre-order tracking (AC-MENU-003)
    is_preorder: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    waitlist_entry: Mapped["WaitlistEntry"] = relationship(
        "WaitlistEntry", back_populates="guest_interests"
    )
    menu_item: Mapped["MenuItem"] = relationship(
        "MenuItem", back_populates="guest_interests"
    )

    def __init__(
        self,
        waitlist_entry_id: int,
        menu_item_id: int,
        is_starred: bool = False,
        is_preorder: bool = False,
        quantity: int = 1,
        **kwargs,
    ) -> None:
        super().__init__(
            waitlist_entry_id=waitlist_entry_id,
            menu_item_id=menu_item_id,
            is_starred=is_starred,
            is_preorder=is_preorder,
            quantity=quantity,
            **kwargs,
        )

    def __repr__(self) -> str:
        return (
            f"<GuestInterest(id={self.id}, entry={self.waitlist_entry_id}, "
            f"item={self.menu_item_id}, starred={self.is_starred}, preorder={self.is_preorder})>"
        )
