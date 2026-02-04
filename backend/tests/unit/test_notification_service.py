"""Unit tests for NotificationService.

REQ-NOTIF-001: SMS/text alerts when table is ready
AC-NOTIF-001: Send "Table Ready" SMS on ready condition
AC-NOTIF-002: Avoid duplicate ready messages

Tests use MockSMSAdapter to isolate service logic from actual SMS sending.
"""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import (
    EntrySource,
    Guest,
    Notification,
    NotificationStatus,
    NotificationType,
    WaitlistEntry,
)
from app.domain.exceptions import EntryNotFoundError
from app.infrastructure.sms.mock_adapter import MockSMSAdapter
from app.services.notification_service import (
    DEFAULT_TABLE_READY_TEMPLATE,
    DuplicateNotificationError,
    NotificationService,
)


class MockSession:
    """Mock AsyncSession for unit tests."""

    def __init__(self):
        self._entries: dict[int, WaitlistEntry] = {}
        self._guests: dict[int, Guest] = {}
        self._notifications: list[Notification] = []
        self._notification_id_counter = 1

    async def execute(self, stmt):
        """Mock execute that handles both entry and notification queries."""
        # This is a simplified mock - in real tests we'd use actual async session
        mock_result = MagicMock()

        # Detect query type by checking the statement
        stmt_str = str(stmt)

        if "notifications" in stmt_str.lower():
            # Notification query - check for existing
            if hasattr(stmt, "_where_criteria"):
                # Return None for no duplicates (simplified)
                mock_result.scalar_one_or_none.return_value = None
            else:
                mock_result.scalars.return_value.all.return_value = []
        elif "waitlist_entries" in stmt_str.lower():
            # Extract entry_id from where clause
            entry_id = None
            for entry in self._entries.values():
                entry_id = entry.id
                break
            mock_result.scalar_one_or_none.return_value = self._entries.get(entry_id)

        return mock_result

    async def refresh(self, obj, attrs=None):
        """Mock refresh."""
        if isinstance(obj, WaitlistEntry) and attrs and "guest" in attrs:
            # Set the guest relationship
            obj.guest = self._guests.get(obj.guest_id)
        elif isinstance(obj, Notification):
            # Set ID if not set
            if obj.id is None:
                obj.id = self._notification_id_counter
                self._notification_id_counter += 1

    async def flush(self):
        """Mock flush."""
        pass

    def add(self, obj):
        """Mock add."""
        if isinstance(obj, Notification):
            self._notifications.append(obj)


@pytest.fixture
def mock_sms_adapter() -> MockSMSAdapter:
    """Create mock SMS adapter."""
    return MockSMSAdapter(should_fail=False)


@pytest.fixture
def mock_session() -> MockSession:
    """Create mock database session."""
    return MockSession()


@pytest.fixture
def notification_service(
    mock_session: MockSession,
    mock_sms_adapter: MockSMSAdapter,
) -> NotificationService:
    """Create NotificationService with mock dependencies."""
    return NotificationService(
        session=mock_session,  # type: ignore
        sms_adapter=mock_sms_adapter,
        restaurant_name="Test Restaurant",
    )


class TestSendTableReady:
    """Tests for send_table_ready method.

    REQ-NOTIF-001: SMS/text alerts when table is ready
    AC-NOTIF-001: Send "Table Ready" SMS on ready condition
    """

    @pytest.mark.asyncio
    async def test_send_table_ready_success(
        self,
        mock_sms_adapter: MockSMSAdapter,
    ) -> None:
        """AC-NOTIF-001: Successfully send table ready SMS."""
        # Create real mock session with proper async behavior
        session = AsyncMock(spec=AsyncSession)

        # Create test data
        guest = MagicMock(spec=Guest)
        guest.id = 1
        guest.name = "John Doe"
        guest.phone_number = "+1555123456"

        entry = MagicMock(spec=WaitlistEntry)
        entry.id = 1
        entry.guest_id = 1
        entry.guest = guest

        # Setup session mocks - need to use a shared result mock
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [
            entry,  # First call: get waitlist entry
            None,   # Second call: check for existing notification (none)
        ]
        session.execute.return_value = mock_result

        # Track notifications added
        added_notifications = []

        def track_add(obj):
            added_notifications.append(obj)

        session.add.side_effect = track_add

        async def mock_refresh(obj, attrs=None):
            if isinstance(obj, WaitlistEntry) and attrs:
                obj.guest = guest
            elif hasattr(obj, "id") and obj.id is None:
                obj.id = 1

        session.refresh.side_effect = mock_refresh

        # Create service
        service = NotificationService(
            session=session,
            sms_adapter=mock_sms_adapter,
            restaurant_name="Test Restaurant",
        )

        # Act
        result = await service.send_table_ready(entry_id=1)

        # Assert
        assert result is not None
        assert result.notification_type == NotificationType.TABLE_READY.value
        assert result.status == NotificationStatus.SENT.value
        assert result.sent_at is not None
        assert result.phone_number == "+1555123456"

        # Verify SMS was sent
        assert len(mock_sms_adapter.sent_messages) == 1
        sent_msg = mock_sms_adapter.sent_messages[0]
        assert sent_msg.to == "+1555123456"
        assert "John Doe" in sent_msg.message
        assert "Test Restaurant" in sent_msg.message

    @pytest.mark.asyncio
    async def test_send_table_ready_entry_not_found(
        self,
        mock_sms_adapter: MockSMSAdapter,
    ) -> None:
        """Should raise EntryNotFoundError when entry doesn't exist."""
        session = AsyncMock(spec=AsyncSession)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        session.execute.return_value = mock_result

        service = NotificationService(
            session=session,
            sms_adapter=mock_sms_adapter,
            restaurant_name="Test Restaurant",
        )

        # Act & Assert
        with pytest.raises(EntryNotFoundError) as exc_info:
            await service.send_table_ready(entry_id=999)

        assert exc_info.value.entry_id == 999

    @pytest.mark.asyncio
    async def test_send_table_ready_with_custom_message(
        self,
        mock_sms_adapter: MockSMSAdapter,
    ) -> None:
        """Should use custom message when provided."""
        session = AsyncMock(spec=AsyncSession)

        guest = MagicMock(spec=Guest)
        guest.id = 1
        guest.name = "Jane"
        guest.phone_number = "+1555999888"

        entry = MagicMock(spec=WaitlistEntry)
        entry.id = 2
        entry.guest_id = 1
        entry.guest = guest

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [
            entry,
            None,
        ]
        session.execute.return_value = mock_result

        async def mock_refresh(obj, attrs=None):
            if isinstance(obj, WaitlistEntry) and attrs:
                obj.guest = guest
            elif hasattr(obj, "id") and obj.id is None:
                obj.id = 1

        session.refresh.side_effect = mock_refresh

        service = NotificationService(
            session=session,
            sms_adapter=mock_sms_adapter,
            restaurant_name="Test Restaurant",
        )

        custom_msg = "VIP table ready! Please come to the front."

        # Act
        result = await service.send_table_ready(
            entry_id=2,
            custom_message=custom_msg,
        )

        # Assert
        assert result.message == custom_msg
        sent_msg = mock_sms_adapter.get_last_message()
        assert sent_msg is not None
        assert sent_msg.message == custom_msg


class TestDuplicatePrevention:
    """Tests for duplicate notification prevention.

    AC-NOTIF-002: Avoid duplicate ready messages
    """

    @pytest.mark.asyncio
    async def test_duplicate_notification_raises_error(
        self,
        mock_sms_adapter: MockSMSAdapter,
    ) -> None:
        """AC-NOTIF-002: Should raise error when notification already sent."""
        session = AsyncMock(spec=AsyncSession)

        guest = MagicMock(spec=Guest)
        guest.id = 1
        guest.name = "Bob"
        guest.phone_number = "+1555111222"

        entry = MagicMock(spec=WaitlistEntry)
        entry.id = 3
        entry.guest_id = 1
        entry.guest = guest

        # Existing notification
        existing_notification = MagicMock(spec=Notification)
        existing_notification.id = 100
        existing_notification.notification_type = NotificationType.TABLE_READY.value
        existing_notification.status = NotificationStatus.SENT.value

        # First call returns entry, second returns existing notification
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [
            entry,
            existing_notification,
        ]
        session.execute.return_value = mock_result

        async def mock_refresh(obj, attrs=None):
            if isinstance(obj, WaitlistEntry) and attrs:
                obj.guest = guest

        session.refresh.side_effect = mock_refresh

        service = NotificationService(
            session=session,
            sms_adapter=mock_sms_adapter,
            restaurant_name="Test Restaurant",
        )

        # Act & Assert
        with pytest.raises(DuplicateNotificationError) as exc_info:
            await service.send_table_ready(entry_id=3)

        assert exc_info.value.entry_id == 3
        assert exc_info.value.notification_type == NotificationType.TABLE_READY.value

        # Verify no SMS was sent
        assert len(mock_sms_adapter.sent_messages) == 0


class TestMockSMSAdapter:
    """Tests for MockSMSAdapter itself.

    Verifies the mock adapter works correctly for testing.
    """

    @pytest.mark.asyncio
    async def test_mock_adapter_sends_successfully(self) -> None:
        """Mock adapter should return True and store message."""
        adapter = MockSMSAdapter(should_fail=False)

        result = await adapter.send(to="+1555000000", message="Test message")

        assert result is True
        assert len(adapter.sent_messages) == 1
        assert adapter.sent_messages[0].to == "+1555000000"
        assert adapter.sent_messages[0].message == "Test message"

    @pytest.mark.asyncio
    async def test_mock_adapter_simulates_failure(self) -> None:
        """Mock adapter should return False when should_fail is True."""
        adapter = MockSMSAdapter(should_fail=True)

        result = await adapter.send(to="+1555000000", message="Test message")

        assert result is False
        assert len(adapter.sent_messages) == 0

    @pytest.mark.asyncio
    async def test_mock_adapter_get_messages_to(self) -> None:
        """Should filter messages by phone number."""
        adapter = MockSMSAdapter()

        await adapter.send(to="+1555111111", message="First")
        await adapter.send(to="+1555222222", message="Second")
        await adapter.send(to="+1555111111", message="Third")

        messages_to_111 = adapter.get_messages_to("+1555111111")

        assert len(messages_to_111) == 2
        assert messages_to_111[0].message == "First"
        assert messages_to_111[1].message == "Third"

    def test_mock_adapter_clear_messages(self) -> None:
        """Should clear all stored messages."""
        adapter = MockSMSAdapter()
        adapter._sent_messages.append(MagicMock())

        adapter.clear_messages()

        assert len(adapter.sent_messages) == 0


class TestNotificationServiceFailure:
    """Tests for SMS send failure handling."""

    @pytest.mark.asyncio
    async def test_send_failure_marks_notification_failed(self) -> None:
        """Should mark notification as failed when SMS fails."""
        # Create failing adapter
        failing_adapter = MockSMSAdapter(should_fail=True)

        session = AsyncMock(spec=AsyncSession)

        guest = MagicMock(spec=Guest)
        guest.id = 1
        guest.name = "Test"
        guest.phone_number = "+1555333444"

        entry = MagicMock(spec=WaitlistEntry)
        entry.id = 5
        entry.guest_id = 1
        entry.guest = guest

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.side_effect = [
            entry,
            None,
        ]
        session.execute.return_value = mock_result

        async def mock_refresh(obj, attrs=None):
            if isinstance(obj, WaitlistEntry) and attrs:
                obj.guest = guest
            elif hasattr(obj, "id") and obj.id is None:
                obj.id = 1

        session.refresh.side_effect = mock_refresh

        service = NotificationService(
            session=session,
            sms_adapter=failing_adapter,
            restaurant_name="Test Restaurant",
        )

        # Act
        result = await service.send_table_ready(entry_id=5)

        # Assert
        assert result.status == NotificationStatus.FAILED.value
        assert result.sent_at is None
