"""Unit tests for reminder task.

REQ-NOTIF-002: Automated reminders or status updates
AC-NOTIF-003: Automated reminder / status updates
    - Send reminder X minutes before estimated seating
    - reminders can be sent based on defined rules
    - the system logs that reminder was sent

Tests:
- check_and_send_reminders finds correct entries
- Reminder sent only once (duplicate prevention)
- Reminder not sent if already notified
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.domain.entities import (
    EntrySource,
    Guest,
    Notification,
    NotificationStatus,
    NotificationType,
    WaitlistEntry,
    WaitlistStatus,
)
from app.infrastructure.sms.mock_adapter import MockSMSAdapter
from app.services.notification_service import (
    DuplicateNotificationError,
    NotificationService,
)
from app.tasks.reminder_task import (
    ReminderTask,
    check_and_send_reminders,
    get_entries_due_for_reminder,
)


class TestGetEntriesDueForReminder:
    """Tests for get_entries_due_for_reminder function.

    AC-NOTIF-003: Send reminder X minutes before estimated seating
    """

    @pytest.mark.asyncio
    async def test_finds_entry_due_for_reminder(self) -> None:
        """AC-NOTIF-003-1: Should find entries within the reminder window."""
        session = AsyncMock(spec=AsyncSession)

        # Create entry that is due for reminder
        # Position 1, avg turn time 15 min = estimated seat at created_at + 15 min
        # Reminder 10 min before = created_at + 5 min
        # If created_at was 6 minutes ago, reminder is due
        entry = MagicMock(spec=WaitlistEntry)
        entry.id = 1
        entry.status = WaitlistStatus.WAITING.value
        entry.position = 1
        entry.created_at = datetime.utcnow() - timedelta(minutes=6)

        # Mock waiting entries query
        waiting_result = MagicMock()
        waiting_result.scalars.return_value.all.return_value = [entry]

        # Mock notification check query (no existing reminder)
        notification_result = MagicMock()
        notification_result.scalar_one_or_none.return_value = None

        session.execute.side_effect = [waiting_result, notification_result]

        # Act
        entries = await get_entries_due_for_reminder(
            session=session,
            reminder_minutes_before=10,
            avg_turn_time_minutes=15,
        )

        # Assert
        assert len(entries) == 1
        assert entries[0].id == 1

    @pytest.mark.asyncio
    async def test_excludes_entry_not_yet_due(self) -> None:
        """AC-NOTIF-003-2: Should not include entries not yet in reminder window."""
        session = AsyncMock(spec=AsyncSession)

        # Create entry NOT yet due for reminder
        # Position 1, avg turn time 15 min = estimated seat at created_at + 15 min
        # Reminder 10 min before = created_at + 5 min
        # If created_at was just now (0 minutes ago), reminder is not yet due
        entry = MagicMock(spec=WaitlistEntry)
        entry.id = 1
        entry.status = WaitlistStatus.WAITING.value
        entry.position = 1
        entry.created_at = datetime.utcnow()  # Just created

        # Mock waiting entries query
        waiting_result = MagicMock()
        waiting_result.scalars.return_value.all.return_value = [entry]

        session.execute.return_value = waiting_result

        # Act
        entries = await get_entries_due_for_reminder(
            session=session,
            reminder_minutes_before=10,
            avg_turn_time_minutes=15,
        )

        # Assert - entry not in reminder window yet
        assert len(entries) == 0

    @pytest.mark.asyncio
    async def test_excludes_entry_with_existing_reminder(self) -> None:
        """AC-NOTIF-003-3: Should not include entries that already have a reminder sent."""
        session = AsyncMock(spec=AsyncSession)

        # Create entry due for reminder
        entry = MagicMock(spec=WaitlistEntry)
        entry.id = 1
        entry.status = WaitlistStatus.WAITING.value
        entry.position = 1
        entry.created_at = datetime.utcnow() - timedelta(minutes=10)

        # Existing reminder notification
        existing_reminder = MagicMock(spec=Notification)
        existing_reminder.notification_type = NotificationType.REMINDER.value
        existing_reminder.status = NotificationStatus.SENT.value

        # Mock waiting entries query
        waiting_result = MagicMock()
        waiting_result.scalars.return_value.all.return_value = [entry]

        # Mock notification check query (existing reminder found)
        notification_result = MagicMock()
        notification_result.scalar_one_or_none.return_value = existing_reminder

        session.execute.side_effect = [waiting_result, notification_result]

        # Act
        entries = await get_entries_due_for_reminder(
            session=session,
            reminder_minutes_before=10,
            avg_turn_time_minutes=15,
        )

        # Assert - entry excluded due to existing reminder
        assert len(entries) == 0

    @pytest.mark.asyncio
    async def test_excludes_non_waiting_entries(self) -> None:
        """Should only process entries with 'waiting' status."""
        session = AsyncMock(spec=AsyncSession)

        # Mock returns empty list (query filters by waiting status)
        waiting_result = MagicMock()
        waiting_result.scalars.return_value.all.return_value = []

        session.execute.return_value = waiting_result

        # Act
        entries = await get_entries_due_for_reminder(
            session=session,
            reminder_minutes_before=10,
            avg_turn_time_minutes=15,
        )

        # Assert
        assert len(entries) == 0

    @pytest.mark.asyncio
    async def test_multiple_entries_due(self) -> None:
        """Should find multiple entries when all are due."""
        session = AsyncMock(spec=AsyncSession)

        # Create multiple entries due for reminder
        entry1 = MagicMock(spec=WaitlistEntry)
        entry1.id = 1
        entry1.status = WaitlistStatus.WAITING.value
        entry1.position = 1
        entry1.created_at = datetime.utcnow() - timedelta(minutes=10)

        entry2 = MagicMock(spec=WaitlistEntry)
        entry2.id = 2
        entry2.status = WaitlistStatus.WAITING.value
        entry2.position = 2
        entry2.created_at = datetime.utcnow() - timedelta(minutes=20)

        # Mock waiting entries query
        waiting_result = MagicMock()
        waiting_result.scalars.return_value.all.return_value = [entry1, entry2]

        # Mock notification check queries (no existing reminders)
        notification_result1 = MagicMock()
        notification_result1.scalar_one_or_none.return_value = None
        notification_result2 = MagicMock()
        notification_result2.scalar_one_or_none.return_value = None

        session.execute.side_effect = [
            waiting_result,
            notification_result1,
            notification_result2,
        ]

        # Act
        entries = await get_entries_due_for_reminder(
            session=session,
            reminder_minutes_before=10,
            avg_turn_time_minutes=15,
        )

        # Assert
        assert len(entries) == 2


class TestCheckAndSendReminders:
    """Tests for check_and_send_reminders function.

    AC-NOTIF-003: Automated reminder / status updates
    """

    @pytest.mark.asyncio
    async def test_sends_reminders_for_due_entries(self) -> None:
        """AC-NOTIF-003-4: Should send reminders for all due entries."""
        session = AsyncMock(spec=AsyncSession)
        notification_service = AsyncMock(spec=NotificationService)

        # Create mock entry
        entry = MagicMock(spec=WaitlistEntry)
        entry.id = 1
        entry.status = WaitlistStatus.WAITING.value
        entry.position = 1
        entry.created_at = datetime.utcnow() - timedelta(minutes=10)

        settings = MagicMock(spec=Settings)
        settings.reminder_minutes_before = 10
        settings.default_avg_turn_time_minutes = 15

        # Mock the get_entries_due_for_reminder to return our entry
        with patch(
            "app.tasks.reminder_task.get_entries_due_for_reminder",
            return_value=[entry],
        ):
            # Act
            sent_ids = await check_and_send_reminders(
                session=session,
                notification_service=notification_service,
                settings=settings,
            )

        # Assert
        assert sent_ids == [1]
        notification_service.send_reminder.assert_called_once_with(entry_id=1)

    @pytest.mark.asyncio
    async def test_continues_on_send_failure(self) -> None:
        """Should continue processing other entries if one fails."""
        session = AsyncMock(spec=AsyncSession)
        notification_service = AsyncMock(spec=NotificationService)

        # Create mock entries
        entry1 = MagicMock(spec=WaitlistEntry)
        entry1.id = 1
        entry1.status = WaitlistStatus.WAITING.value
        entry1.position = 1
        entry1.created_at = datetime.utcnow() - timedelta(minutes=10)

        entry2 = MagicMock(spec=WaitlistEntry)
        entry2.id = 2
        entry2.status = WaitlistStatus.WAITING.value
        entry2.position = 2
        entry2.created_at = datetime.utcnow() - timedelta(minutes=20)

        # First call fails, second succeeds
        notification_service.send_reminder.side_effect = [
            Exception("SMS failed"),
            AsyncMock(),  # Success
        ]

        settings = MagicMock(spec=Settings)
        settings.reminder_minutes_before = 10
        settings.default_avg_turn_time_minutes = 15

        with patch(
            "app.tasks.reminder_task.get_entries_due_for_reminder",
            return_value=[entry1, entry2],
        ):
            # Act
            sent_ids = await check_and_send_reminders(
                session=session,
                notification_service=notification_service,
                settings=settings,
            )

        # Assert - only entry2 succeeded
        assert sent_ids == [2]
        assert notification_service.send_reminder.call_count == 2

    @pytest.mark.asyncio
    async def test_no_entries_due(self) -> None:
        """Should handle case with no entries due for reminder."""
        session = AsyncMock(spec=AsyncSession)
        notification_service = AsyncMock(spec=NotificationService)

        settings = MagicMock(spec=Settings)
        settings.reminder_minutes_before = 10
        settings.default_avg_turn_time_minutes = 15

        with patch(
            "app.tasks.reminder_task.get_entries_due_for_reminder",
            return_value=[],
        ):
            # Act
            sent_ids = await check_and_send_reminders(
                session=session,
                notification_service=notification_service,
                settings=settings,
            )

        # Assert
        assert sent_ids == []
        notification_service.send_reminder.assert_not_called()


class TestNotificationServiceSendReminder:
    """Tests for NotificationService.send_reminder method.

    REQ-NOTIF-002: Automated reminders
    AC-NOTIF-003: Automated reminder / status updates
    """

    @pytest.mark.asyncio
    async def test_send_reminder_success(self) -> None:
        """AC-NOTIF-003-5: Successfully send reminder SMS."""
        session = AsyncMock(spec=AsyncSession)
        sms_adapter = MockSMSAdapter(should_fail=False)

        # Create test data
        guest = MagicMock(spec=Guest)
        guest.id = 1
        guest.name = "John Doe"
        guest.phone_number = "+1555123456"

        entry = MagicMock(spec=WaitlistEntry)
        entry.id = 1
        entry.guest_id = 1
        entry.guest = guest

        # Setup session mocks
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [
            entry,  # First call: get waitlist entry
            None,   # Second call: check for existing notification (none)
        ]
        session.execute.return_value = mock_result

        async def mock_refresh(obj, attrs=None):
            if hasattr(obj, "guest_id") and attrs:
                obj.guest = guest
            elif hasattr(obj, "id") and obj.id is None:
                obj.id = 1

        session.refresh.side_effect = mock_refresh

        # Create service
        service = NotificationService(
            session=session,
            sms_adapter=sms_adapter,
            restaurant_name="Test Restaurant",
        )

        # Act
        result = await service.send_reminder(entry_id=1, minutes_until_ready=10)

        # Assert
        assert result is not None
        assert result.notification_type == NotificationType.REMINDER.value
        assert result.status == NotificationStatus.SENT.value
        assert result.sent_at is not None
        assert result.phone_number == "+1555123456"

        # Verify SMS was sent
        assert len(sms_adapter.sent_messages) == 1
        sent_msg = sms_adapter.sent_messages[0]
        assert sent_msg.to == "+1555123456"
        assert "John Doe" in sent_msg.message
        assert "Test Restaurant" in sent_msg.message
        assert "10 minutes" in sent_msg.message

    @pytest.mark.asyncio
    async def test_duplicate_reminder_raises_error(self) -> None:
        """AC-NOTIF-003-6: Should prevent duplicate reminders."""
        session = AsyncMock(spec=AsyncSession)
        sms_adapter = MockSMSAdapter()

        guest = MagicMock(spec=Guest)
        guest.id = 1
        guest.name = "Bob"
        guest.phone_number = "+1555111222"

        entry = MagicMock(spec=WaitlistEntry)
        entry.id = 3
        entry.guest_id = 1
        entry.guest = guest

        # Existing reminder notification
        existing_notification = MagicMock(spec=Notification)
        existing_notification.id = 100
        existing_notification.notification_type = NotificationType.REMINDER.value
        existing_notification.status = NotificationStatus.SENT.value

        # First call returns entry, second returns existing notification
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [
            entry,
            existing_notification,
        ]
        session.execute.return_value = mock_result

        async def mock_refresh(obj, attrs=None):
            if hasattr(obj, "guest_id") and attrs:
                obj.guest = guest

        session.refresh.side_effect = mock_refresh

        service = NotificationService(
            session=session,
            sms_adapter=sms_adapter,
            restaurant_name="Test Restaurant",
        )

        # Act & Assert
        with pytest.raises(DuplicateNotificationError) as exc_info:
            await service.send_reminder(entry_id=3)

        assert exc_info.value.entry_id == 3
        assert exc_info.value.notification_type == NotificationType.REMINDER.value

        # Verify no SMS was sent
        assert len(sms_adapter.sent_messages) == 0

    @pytest.mark.asyncio
    async def test_reminder_with_custom_message(self) -> None:
        """Should use custom message when provided."""
        session = AsyncMock(spec=AsyncSession)
        sms_adapter = MockSMSAdapter()

        guest = MagicMock(spec=Guest)
        guest.id = 1
        guest.name = "Jane"
        guest.phone_number = "+1555999888"

        entry = MagicMock(spec=WaitlistEntry)
        entry.id = 2
        entry.guest_id = 1
        entry.guest = guest

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [entry, None]
        session.execute.return_value = mock_result

        async def mock_refresh(obj, attrs=None):
            if hasattr(obj, "guest_id") and attrs:
                obj.guest = guest
            elif hasattr(obj, "id") and obj.id is None:
                obj.id = 1

        session.refresh.side_effect = mock_refresh

        service = NotificationService(
            session=session,
            sms_adapter=sms_adapter,
            restaurant_name="Test Restaurant",
        )

        custom_msg = "VIP reminder: Your table will be ready soon!"

        # Act
        result = await service.send_reminder(
            entry_id=2,
            custom_message=custom_msg,
        )

        # Assert
        assert result.message == custom_msg
        sent_msg = sms_adapter.get_last_message()
        assert sent_msg is not None
        assert sent_msg.message == custom_msg


class TestReminderTask:
    """Tests for ReminderTask background task class."""

    def test_task_initialization(self) -> None:
        """Should initialize with correct settings."""
        session_factory = AsyncMock()
        service_factory = MagicMock()
        settings = MagicMock(spec=Settings)
        settings.reminder_check_interval_seconds = 30
        settings.reminder_minutes_before = 5

        task = ReminderTask(
            session_factory=session_factory,
            notification_service_factory=service_factory,
            settings=settings,
        )

        assert task._settings.reminder_check_interval_seconds == 30
        assert task._settings.reminder_minutes_before == 5
        assert task._running is False

    def test_task_stop(self) -> None:
        """Should stop the running flag."""
        session_factory = AsyncMock()
        service_factory = MagicMock()

        task = ReminderTask(
            session_factory=session_factory,
            notification_service_factory=service_factory,
        )
        task._running = True

        task.stop()

        assert task._running is False
