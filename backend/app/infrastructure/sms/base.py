"""Abstract SMS adapter interface.

REQ-NOTIF-001: SMS/text alerts when table is ready
AC-NOTIF-001: Send "Table Ready" SMS on ready condition

Defines the contract for SMS providers.
"""

from abc import ABC, abstractmethod


class SMSAdapter(ABC):
    """Abstract base class for SMS adapters.

    REQ-NOTIF-001: SMS/text alerts when table is ready

    All SMS providers must implement this interface to support:
    - Sending SMS messages to phone numbers
    - Returning success/failure status
    """

    @abstractmethod
    async def send(self, to: str, message: str) -> bool:
        """Send an SMS message.

        Args:
            to: Phone number to send to (E.164 format preferred)
            message: Message content

        Returns:
            True if message was sent successfully, False otherwise
        """
        pass
