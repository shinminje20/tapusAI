"""Mock SMS adapter for testing.

REQ-NOTIF-001: SMS/text alerts when table is ready
AC-NOTIF-001: Send "Table Ready" SMS on ready condition

Provides a mock implementation for testing without sending real SMS.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime

from app.infrastructure.sms.base import SMSAdapter

logger = logging.getLogger(__name__)


@dataclass
class SentMessage:
    """Record of a sent message for test assertions."""

    to: str
    message: str
    sent_at: datetime = field(default_factory=datetime.utcnow)


class MockSMSAdapter(SMSAdapter):
    """Mock implementation of SMSAdapter for testing.

    REQ-NOTIF-001: SMS/text alerts when table is ready

    Features:
    - Logs messages instead of sending
    - Stores sent messages for test assertions
    - Can simulate failures for testing error handling
    """

    def __init__(self, should_fail: bool = False) -> None:
        """Initialize mock adapter.

        Args:
            should_fail: If True, send() will return False (simulate failure)
        """
        self._should_fail = should_fail
        self._sent_messages: list[SentMessage] = []

    @property
    def sent_messages(self) -> list[SentMessage]:
        """Get list of sent messages for assertions."""
        return self._sent_messages.copy()

    def clear_messages(self) -> None:
        """Clear sent messages (useful between tests)."""
        self._sent_messages.clear()

    async def send(self, to: str, message: str) -> bool:
        """Mock send SMS - logs and stores message.

        REQ-NOTIF-001: SMS/text alerts when table is ready

        Args:
            to: Phone number to send to
            message: Message content

        Returns:
            True if should_fail is False, False otherwise
        """
        if self._should_fail:
            logger.warning(f"[MOCK SMS] Simulated failure sending to {to}")
            return False

        sent = SentMessage(to=to, message=message)
        self._sent_messages.append(sent)
        logger.info(f"[MOCK SMS] Message sent to {to}: {message}")
        return True

    def get_last_message(self) -> SentMessage | None:
        """Get the last sent message, if any."""
        return self._sent_messages[-1] if self._sent_messages else None

    def get_messages_to(self, phone_number: str) -> list[SentMessage]:
        """Get all messages sent to a specific phone number."""
        return [m for m in self._sent_messages if m.to == phone_number]
