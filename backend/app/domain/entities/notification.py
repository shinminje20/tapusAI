"""Notification entity model.

REQ-NOTIF-001: SMS/text alerts when table is ready
AC-NOTIF-001: Send "Table Ready" SMS on ready condition
AC-NOTIF-002: Avoid duplicate ready messages

Tracks all notifications sent to guests.
"""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base

if TYPE_CHECKING:
    from app.domain.entities.waitlist_entry import WaitlistEntry


class NotificationType(str, Enum):
    """Type of notification sent.

    REQ-NOTIF-001: table_ready
    REQ-NOTIF-002: reminder (future)
    """

    TABLE_READY = "table_ready"
    REMINDER = "reminder"
    CUSTOM = "custom"


class NotificationStatus(str, Enum):
    """Status of notification delivery.

    AC-NOTIF-002: Track status for duplicate prevention.
    """

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Notification(Base):
    """Notification entity representing a message sent to a guest.

    REQ-NOTIF-001: SMS/text alerts when table is ready
    AC-NOTIF-001: Send "Table Ready" SMS on ready condition
    AC-NOTIF-002: Avoid duplicate ready messages

    Tracks:
    - What notification was sent
    - To which waitlist entry
    - Delivery status
    - Timestamps for audit
    """

    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    waitlist_entry_id: Mapped[int] = mapped_column(
        ForeignKey("waitlist_entries.id"), nullable=False
    )
    notification_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=NotificationType.TABLE_READY.value
    )
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=NotificationStatus.PENDING.value
    )
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # Relationships
    waitlist_entry: Mapped["WaitlistEntry"] = relationship(
        "WaitlistEntry", back_populates="notifications"
    )

    def __init__(
        self,
        waitlist_entry_id: int,
        phone_number: str,
        message: str,
        notification_type: NotificationType = NotificationType.TABLE_READY,
        status: NotificationStatus = NotificationStatus.PENDING,
        sent_at: datetime | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            waitlist_entry_id=waitlist_entry_id,
            phone_number=phone_number,
            message=message,
            notification_type=(
                notification_type.value
                if isinstance(notification_type, NotificationType)
                else notification_type
            ),
            status=(
                status.value if isinstance(status, NotificationStatus) else status
            ),
            sent_at=sent_at,
            **kwargs,
        )

    @property
    def notification_type_enum(self) -> NotificationType:
        """Get notification_type as enum."""
        return NotificationType(self.notification_type)

    @property
    def status_enum(self) -> NotificationStatus:
        """Get status as enum."""
        return NotificationStatus(self.status)

    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type={self.notification_type}, status={self.status})>"
