"""WaitlistEntry entity model.

REQ-WL-001: Add guests quickly
REQ-WL-004: Ability to reorder, prioritize, or mark VIP guests
REQ-WL-005: Status tracking
REQ-MENU-005: Guest token for SMS link to menu
AC-WL-001: Entry appears immediately with status 'waiting'
AC-WL-006: VIP flagging (manual move only)
AC-MENU-001: Guest accesses menu from SMS link via token
"""

import secrets
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.enums import EntrySource, WaitlistStatus
from app.infrastructure.database import Base

# Token expiry in hours (24 hours default)
DEFAULT_TOKEN_EXPIRY_HOURS = 24

if TYPE_CHECKING:
    from app.domain.entities.guest import Guest
    from app.domain.entities.guest_interest import GuestInterest
    from app.domain.entities.notification import Notification


class WaitlistEntry(Base):
    """Waitlist entry representing a party waiting for a table.

    AC-WL-001: Add Guest and Display Immediately
    - status defaults to 'waiting'
    - includes created time and unique identifier

    AC-WL-002: Validate Input
    - party_size >= 1

    AC-WL-006: VIP Flagging
    - vip_flag is informational, manual move only

    AC-WL-008: Source is captured
    """

    __tablename__ = "waitlist_entries"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guest_id: Mapped[int] = mapped_column(ForeignKey("guests.id"), nullable=False)
    party_size: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), default=WaitlistStatus.WAITING.value, nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    vip_flag: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    source: Mapped[str] = mapped_column(String(20), nullable=False)

    # Timestamps for audit (AC-WL-003)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # For optimistic locking / conflict resolution
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    # Guest token for SMS link (REQ-MENU-005, AC-MENU-001)
    guest_token: Mapped[str | None] = mapped_column(
        String(64), unique=True, nullable=True, index=True
    )
    token_expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    guest: Mapped["Guest"] = relationship("Guest", back_populates="waitlist_entries")
    notifications: Mapped[list["Notification"]] = relationship(
        "Notification", back_populates="waitlist_entry"
    )
    guest_interests: Mapped[list["GuestInterest"]] = relationship(
        "GuestInterest", back_populates="waitlist_entry"
    )

    def __init__(
        self,
        guest_id: int,
        party_size: int,
        source: EntrySource,
        status: WaitlistStatus = WaitlistStatus.WAITING,
        position: int = 0,
        vip_flag: bool = False,
        version: int = 1,
        **kwargs,
    ) -> None:
        super().__init__(
            guest_id=guest_id,
            party_size=party_size,
            source=source.value if isinstance(source, EntrySource) else source,
            status=status.value if isinstance(status, WaitlistStatus) else status,
            position=position,
            vip_flag=vip_flag,
            version=version,
            **kwargs,
        )

    @property
    def status_enum(self) -> WaitlistStatus:
        """Get status as enum."""
        return WaitlistStatus(self.status)

    @property
    def source_enum(self) -> EntrySource:
        """Get source as enum."""
        return EntrySource(self.source)

    def generate_guest_token(self, expiry_hours: int = DEFAULT_TOKEN_EXPIRY_HOURS) -> str:
        """Generate a secure guest token for SMS link.

        REQ-MENU-005: Guest receives SMS with a link
        AC-MENU-001: Guest accesses menu from SMS link

        Args:
            expiry_hours: Hours until token expires (default 24)

        Returns:
            Generated token string
        """
        self.guest_token = secrets.token_urlsafe(32)
        self.token_expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
        return self.guest_token

    def is_token_valid(self) -> bool:
        """Check if the guest token is valid and not expired.

        Returns:
            True if token exists and is not expired
        """
        if not self.guest_token or not self.token_expires_at:
            return False
        return datetime.utcnow() < self.token_expires_at

    def __repr__(self) -> str:
        return f"<WaitlistEntry(id={self.id}, status={self.status}, party_size={self.party_size})>"
