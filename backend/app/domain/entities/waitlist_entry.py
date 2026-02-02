"""WaitlistEntry entity model.

REQ-WL-001: Add guests quickly
REQ-WL-004: Ability to reorder, prioritize, or mark VIP guests
REQ-WL-005: Status tracking
AC-WL-001: Entry appears immediately with status 'waiting'
AC-WL-006: VIP flagging (manual move only)
"""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.entities.enums import EntrySource, WaitlistStatus
from app.infrastructure.database import Base

if TYPE_CHECKING:
    from app.domain.entities.guest import Guest


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

    # Relationships
    guest: Mapped["Guest"] = relationship("Guest", back_populates="waitlist_entries")

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

    def __repr__(self) -> str:
        return f"<WaitlistEntry(id={self.id}, status={self.status}, party_size={self.party_size})>"
