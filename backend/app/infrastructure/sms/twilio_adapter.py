"""Twilio SMS adapter implementation.

REQ-NOTIF-001: SMS/text alerts when table is ready
AC-NOTIF-001: Send "Table Ready" SMS on ready condition

Uses Twilio API for production SMS delivery.
"""

import logging
from functools import lru_cache

from app.infrastructure.sms.base import SMSAdapter

logger = logging.getLogger(__name__)


class TwilioAdapter(SMSAdapter):
    """Twilio implementation of SMSAdapter.

    REQ-NOTIF-001: SMS/text alerts when table is ready

    Environment variables required:
    - TWILIO_ACCOUNT_SID: Twilio account SID
    - TWILIO_AUTH_TOKEN: Twilio auth token
    - TWILIO_FROM_NUMBER: Twilio phone number to send from
    """

    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        from_number: str,
    ) -> None:
        """Initialize Twilio adapter.

        Args:
            account_sid: Twilio account SID
            auth_token: Twilio auth token
            from_number: Phone number to send from
        """
        self._account_sid = account_sid
        self._auth_token = auth_token
        self._from_number = from_number
        self._client = None

    def _get_client(self):
        """Get or create Twilio client (lazy initialization)."""
        if self._client is None:
            try:
                from twilio.rest import Client

                self._client = Client(self._account_sid, self._auth_token)
            except ImportError:
                logger.error("Twilio library not installed. Run: pip install twilio")
                raise RuntimeError("Twilio library not installed")
        return self._client

    async def send(self, to: str, message: str) -> bool:
        """Send an SMS via Twilio.

        REQ-NOTIF-001: SMS/text alerts when table is ready

        Args:
            to: Phone number to send to
            message: Message content

        Returns:
            True if message was sent successfully, False otherwise
        """
        try:
            client = self._get_client()
            # Twilio's Python library is synchronous, but we can call it from async
            # In production, consider using run_in_executor for true async
            twilio_message = client.messages.create(
                body=message,
                from_=self._from_number,
                to=to,
            )
            logger.info(
                f"SMS sent successfully via Twilio. SID: {twilio_message.sid}, To: {to}"
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send SMS via Twilio to {to}: {e}")
            return False


@lru_cache
def get_twilio_adapter(
    account_sid: str,
    auth_token: str,
    from_number: str,
) -> TwilioAdapter:
    """Get cached TwilioAdapter instance."""
    return TwilioAdapter(
        account_sid=account_sid,
        auth_token=auth_token,
        from_number=from_number,
    )
