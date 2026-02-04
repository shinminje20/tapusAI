"""Background task for automated reminders.

REQ-NOTIF-002: Automated reminders or status updates
AC-NOTIF-003: Send reminder X minutes before estimated seating
    - reminders can be sent based on defined rules
    - the system logs that reminder was sent
    - reminders must respect opt-out

This module provides:
1. Function to find entries due for reminder
2. Function to send reminders for those entries
3. Background task class for continuous checking
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.domain.entities import (
    Notification,
    NotificationStatus,
    NotificationType,
    WaitlistEntry,
    WaitlistStatus,
)

if TYPE_CHECKING:
    from app.services.notification_service import NotificationService

logger = logging.getLogger(__name__)


async def get_entries_due_for_reminder(
    session: AsyncSession,
    reminder_minutes_before: int,
    avg_turn_time_minutes: int,
) -> list[WaitlistEntry]:
    """Get waitlist entries that are due for a reminder notification.

    REQ-NOTIF-002: Automated reminders
    AC-NOTIF-003: Send reminder X minutes before estimated seating

    Logic:
    - Entry must be in 'waiting' status
    - Estimated seat time = check_in_time + (position * avg_turn_time)
    - Reminder due when: now >= estimated_seat_time - reminder_minutes_before
    - Entry must NOT already have a REMINDER notification sent

    Args:
        session: Database session
        reminder_minutes_before: Minutes before estimated seating to send reminder
        avg_turn_time_minutes: Average time per party in minutes

    Returns:
        List of WaitlistEntry objects due for reminder
    """
    now = datetime.utcnow()

    # First, get all waiting entries
    waiting_result = await session.execute(
        select(WaitlistEntry).where(
            WaitlistEntry.status == WaitlistStatus.WAITING.value
        )
    )
    waiting_entries = list(waiting_result.scalars().all())

    entries_due = []

    for entry in waiting_entries:
        # Calculate estimated seat time
        # estimated_seat_time = created_at + (position * avg_turn_time)
        estimated_seat_time = entry.created_at + timedelta(
            minutes=entry.position * avg_turn_time_minutes
        )

        # Calculate reminder threshold time
        reminder_threshold = estimated_seat_time - timedelta(
            minutes=reminder_minutes_before
        )

        # Check if reminder is due (current time >= reminder threshold)
        if now >= reminder_threshold:
            # Check if reminder already sent for this entry
            existing_reminder = await session.execute(
                select(Notification).where(
                    and_(
                        Notification.waitlist_entry_id == entry.id,
                        Notification.notification_type == NotificationType.REMINDER.value,
                        Notification.status.in_([
                            NotificationStatus.SENT.value,
                            NotificationStatus.PENDING.value,
                        ]),
                    )
                )
            )

            if existing_reminder.scalar_one_or_none() is None:
                # No reminder sent yet, add to list
                entries_due.append(entry)
                logger.debug(
                    f"Entry {entry.id} due for reminder. "
                    f"Estimated seat: {estimated_seat_time}, "
                    f"Reminder threshold: {reminder_threshold}"
                )

    logger.info(f"Found {len(entries_due)} entries due for reminder")
    return entries_due


async def check_and_send_reminders(
    session: AsyncSession,
    notification_service: "NotificationService",
    settings: Settings | None = None,
) -> list[int]:
    """Check for entries due for reminder and send notifications.

    REQ-NOTIF-002: Automated reminders
    AC-NOTIF-003: Automated reminder / status updates

    Args:
        session: Database session
        notification_service: Service for sending notifications
        settings: Application settings (defaults to get_settings())

    Returns:
        List of entry IDs that received reminders
    """
    if settings is None:
        settings = get_settings()

    # Get entries due for reminder
    entries = await get_entries_due_for_reminder(
        session=session,
        reminder_minutes_before=settings.reminder_minutes_before,
        avg_turn_time_minutes=settings.default_avg_turn_time_minutes,
    )

    sent_entry_ids = []

    for entry in entries:
        try:
            await notification_service.send_reminder(entry_id=entry.id)
            sent_entry_ids.append(entry.id)
            logger.info(f"Reminder sent for entry {entry.id}")
        except Exception as e:
            # Log error but continue processing other entries
            logger.error(f"Failed to send reminder for entry {entry.id}: {e}")

    return sent_entry_ids


class ReminderTask:
    """Background task for continuous reminder checking.

    REQ-NOTIF-002: Automated reminders
    AC-NOTIF-003: Automated reminder / status updates

    This class manages the background loop that periodically checks
    for entries due for reminders and sends them.

    Usage (MVP - Simple polling via FastAPI lifespan):
        task = ReminderTask(session_factory, notification_service_factory)
        asyncio.create_task(task.run())
    """

    def __init__(
        self,
        session_factory,
        notification_service_factory,
        settings: Settings | None = None,
    ) -> None:
        """Initialize the reminder task.

        Args:
            session_factory: Async callable that returns an AsyncSession
            notification_service_factory: Callable(session) that returns NotificationService
            settings: Application settings
        """
        self._session_factory = session_factory
        self._notification_service_factory = notification_service_factory
        self._settings = settings or get_settings()
        self._running = False
        self._task: asyncio.Task | None = None

    async def run(self) -> None:
        """Run the reminder check loop.

        Continuously checks for due reminders at the configured interval.
        """
        self._running = True
        logger.info(
            f"Starting reminder task. "
            f"Check interval: {self._settings.reminder_check_interval_seconds}s, "
            f"Reminder window: {self._settings.reminder_minutes_before} minutes before seating"
        )

        while self._running:
            try:
                async with self._session_factory() as session:
                    notification_service = self._notification_service_factory(session)
                    sent_ids = await check_and_send_reminders(
                        session=session,
                        notification_service=notification_service,
                        settings=self._settings,
                    )
                    if sent_ids:
                        logger.info(f"Sent reminders for entries: {sent_ids}")
                        await session.commit()
            except Exception as e:
                logger.error(f"Error in reminder task loop: {e}")

            # Wait for next check interval
            await asyncio.sleep(self._settings.reminder_check_interval_seconds)

    def stop(self) -> None:
        """Stop the reminder task."""
        self._running = False
        logger.info("Reminder task stopped")

    def start_background(self) -> asyncio.Task:
        """Start the task in the background.

        Returns:
            The asyncio Task object
        """
        self._task = asyncio.create_task(self.run())
        return self._task
