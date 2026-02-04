"""Notification service for SMS messaging.

REQ-NOTIF-001: SMS/text alerts when table is ready
REQ-NOTIF-002: Automated reminders or status updates
AC-NOTIF-001: Send "Table Ready" SMS on ready condition
AC-NOTIF-002: Avoid duplicate ready messages
AC-NOTIF-003: Automated reminder / status updates
"""

import logging
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import (
    Notification,
    NotificationStatus,
    NotificationType,
    WaitlistEntry,
)
from app.domain.exceptions import EntryNotFoundError
from app.infrastructure.sms.base import SMSAdapter

logger = logging.getLogger(__name__)

# Default message template
# REQ-NOTIF-001: Include location/venue name and next action guidance
DEFAULT_TABLE_READY_TEMPLATE = (
    "Hi {guest_name}! Your table at {restaurant_name} is ready. "
    "Please check in with the host."
)

# REQ-NOTIF-002: Automated reminder template
# AC-NOTIF-003: Reminder message sent before estimated seating
DEFAULT_REMINDER_TEMPLATE = (
    "Hi {guest_name}! Reminder: Your table at {restaurant_name} should be ready "
    "in about {minutes} minutes. Please stay nearby!"
)


class DuplicateNotificationError(Exception):
    """Raised when attempting to send a duplicate notification.

    AC-NOTIF-002: Avoid duplicate ready messages.
    """

    def __init__(self, entry_id: int, notification_type: str) -> None:
        self.entry_id = entry_id
        self.notification_type = notification_type
        super().__init__(
            f"A {notification_type} notification has already been sent for entry {entry_id}"
        )


class NotificationService:
    """Service for sending and managing notifications.

    REQ-NOTIF-001: SMS/text alerts when table is ready
    REQ-NOTIF-002: Automated reminders or status updates
    AC-NOTIF-001: Send "Table Ready" SMS on ready condition
    AC-NOTIF-002: Avoid duplicate ready messages (duplicate prevention)
    AC-NOTIF-003: Automated reminder / status updates
    """

    def __init__(
        self,
        session: AsyncSession,
        sms_adapter: SMSAdapter,
        restaurant_name: str = "the restaurant",
    ) -> None:
        """Initialize notification service.

        Args:
            session: Database session for persistence
            sms_adapter: SMS adapter for sending messages
            restaurant_name: Restaurant name for message templates
        """
        self._session = session
        self._sms_adapter = sms_adapter
        self._restaurant_name = restaurant_name

    async def send_table_ready(
        self,
        entry_id: int,
        custom_message: str | None = None,
    ) -> Notification:
        """Send a "table ready" SMS notification.

        REQ-NOTIF-001: SMS/text alerts when table is ready
        AC-NOTIF-001: Send "Table Ready" SMS on ready condition
        AC-NOTIF-002: Avoid duplicate ready messages

        Args:
            entry_id: Waitlist entry ID
            custom_message: Optional custom message (overrides template)

        Returns:
            Created Notification record

        Raises:
            EntryNotFoundError: If entry doesn't exist
            DuplicateNotificationError: If table_ready already sent for this entry
        """
        # Get waitlist entry with guest info
        result = await self._session.execute(
            select(WaitlistEntry).where(WaitlistEntry.id == entry_id)
        )
        entry = result.scalar_one_or_none()

        if entry is None:
            raise EntryNotFoundError(entry_id)

        # Load the guest relationship
        await self._session.refresh(entry, ["guest"])

        # AC-NOTIF-002: Check for existing table_ready notification
        existing = await self._get_existing_notification(
            entry_id, NotificationType.TABLE_READY
        )
        if existing is not None:
            raise DuplicateNotificationError(entry_id, NotificationType.TABLE_READY.value)

        # Build message
        if custom_message:
            message = custom_message
        else:
            guest_name = entry.guest.name if entry.guest else "Guest"
            message = DEFAULT_TABLE_READY_TEMPLATE.format(
                guest_name=guest_name,
                restaurant_name=self._restaurant_name,
            )

        # Get phone number
        phone_number = entry.guest.phone_number if entry.guest else None
        if not phone_number:
            logger.error(f"No phone number for entry {entry_id}")
            raise ValueError(f"No phone number available for entry {entry_id}")

        # Create notification record (pending)
        notification = Notification(
            waitlist_entry_id=entry_id,
            phone_number=phone_number,
            message=message,
            notification_type=NotificationType.TABLE_READY,
            status=NotificationStatus.PENDING,
        )
        self._session.add(notification)
        await self._session.flush()
        await self._session.refresh(notification)

        # Send SMS
        success = await self._sms_adapter.send(to=phone_number, message=message)

        # Update status based on result
        if success:
            notification.status = NotificationStatus.SENT.value
            notification.sent_at = datetime.utcnow()
            logger.info(
                f"Table ready notification sent successfully for entry {entry_id}"
            )
        else:
            notification.status = NotificationStatus.FAILED.value
            logger.error(f"Failed to send table ready notification for entry {entry_id}")

        await self._session.flush()
        await self._session.refresh(notification)

        return notification

    async def send_reminder(
        self,
        entry_id: int,
        minutes_until_ready: int = 10,
        custom_message: str | None = None,
    ) -> Notification:
        """Send a reminder SMS notification before estimated seating.

        REQ-NOTIF-002: Automated reminders or status updates
        AC-NOTIF-003: Automated reminder / status updates
            - reminders can be sent based on defined rules
            - the system logs that reminder was sent

        Args:
            entry_id: Waitlist entry ID
            minutes_until_ready: Estimated minutes until table is ready
            custom_message: Optional custom message (overrides template)

        Returns:
            Created Notification record

        Raises:
            EntryNotFoundError: If entry doesn't exist
            DuplicateNotificationError: If reminder already sent for this entry
        """
        # Get waitlist entry with guest info
        result = await self._session.execute(
            select(WaitlistEntry).where(WaitlistEntry.id == entry_id)
        )
        entry = result.scalar_one_or_none()

        if entry is None:
            raise EntryNotFoundError(entry_id)

        # Load the guest relationship
        await self._session.refresh(entry, ["guest"])

        # Check for existing reminder notification (prevent duplicates)
        existing = await self._get_existing_notification(
            entry_id, NotificationType.REMINDER
        )
        if existing is not None:
            raise DuplicateNotificationError(entry_id, NotificationType.REMINDER.value)

        # Build message
        if custom_message:
            message = custom_message
        else:
            guest_name = entry.guest.name if entry.guest else "Guest"
            message = DEFAULT_REMINDER_TEMPLATE.format(
                guest_name=guest_name,
                restaurant_name=self._restaurant_name,
                minutes=minutes_until_ready,
            )

        # Get phone number
        phone_number = entry.guest.phone_number if entry.guest else None
        if not phone_number:
            logger.error(f"No phone number for entry {entry_id}")
            raise ValueError(f"No phone number available for entry {entry_id}")

        # Create notification record (pending)
        notification = Notification(
            waitlist_entry_id=entry_id,
            phone_number=phone_number,
            message=message,
            notification_type=NotificationType.REMINDER,
            status=NotificationStatus.PENDING,
        )
        self._session.add(notification)
        await self._session.flush()
        await self._session.refresh(notification)

        # Send SMS
        success = await self._sms_adapter.send(to=phone_number, message=message)

        # Update status based on result
        if success:
            notification.status = NotificationStatus.SENT.value
            notification.sent_at = datetime.utcnow()
            logger.info(
                f"Reminder notification sent successfully for entry {entry_id}"
            )
        else:
            notification.status = NotificationStatus.FAILED.value
            logger.error(f"Failed to send reminder notification for entry {entry_id}")

        await self._session.flush()
        await self._session.refresh(notification)

        return notification

    async def _get_existing_notification(
        self,
        entry_id: int,
        notification_type: NotificationType,
    ) -> Notification | None:
        """Check if a notification of given type already exists for entry.

        AC-NOTIF-002: Avoid duplicate ready messages

        Args:
            entry_id: Waitlist entry ID
            notification_type: Type of notification to check

        Returns:
            Existing notification if found, None otherwise
        """
        result = await self._session.execute(
            select(Notification).where(
                Notification.waitlist_entry_id == entry_id,
                Notification.notification_type == notification_type.value,
                Notification.status.in_([
                    NotificationStatus.SENT.value,
                    NotificationStatus.PENDING.value,
                ]),
            )
        )
        return result.scalar_one_or_none()

    async def get_notification_by_id(self, notification_id: int) -> Notification | None:
        """Get a notification by ID.

        Args:
            notification_id: Notification ID

        Returns:
            Notification if found, None otherwise
        """
        result = await self._session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_notifications_for_entry(
        self, entry_id: int
    ) -> list[Notification]:
        """Get all notifications for a waitlist entry.

        Args:
            entry_id: Waitlist entry ID

        Returns:
            List of notifications for the entry
        """
        result = await self._session.execute(
            select(Notification)
            .where(Notification.waitlist_entry_id == entry_id)
            .order_by(Notification.created_at.desc())
        )
        return list(result.scalars().all())
