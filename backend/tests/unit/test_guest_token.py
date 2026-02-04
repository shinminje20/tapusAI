"""Unit tests for guest token functionality.

REQ-MENU-005: Guest receives SMS with a link
AC-MENU-001: Guest accesses menu from SMS link
"""

from datetime import datetime, timedelta

import pytest

from app.domain.entities import WaitlistEntry
from app.domain.entities.enums import EntrySource


class TestGuestToken:
    """Tests for guest token generation and validation."""

    def test_generate_guest_token(self) -> None:
        """Should generate a secure token."""
        entry = WaitlistEntry(
            guest_id=1,
            party_size=2,
            source=EntrySource.KIOSK,
        )

        token = entry.generate_guest_token()

        assert token is not None
        assert len(token) > 20  # URL-safe token should be reasonably long
        assert entry.guest_token == token
        assert entry.token_expires_at is not None

    def test_token_is_unique_per_generation(self) -> None:
        """Should generate different tokens each time."""
        entry = WaitlistEntry(
            guest_id=1,
            party_size=2,
            source=EntrySource.KIOSK,
        )

        token1 = entry.generate_guest_token()
        token2 = entry.generate_guest_token()

        assert token1 != token2
        assert entry.guest_token == token2  # Latest token stored

    def test_token_expiry_default(self) -> None:
        """Should expire after default 24 hours."""
        entry = WaitlistEntry(
            guest_id=1,
            party_size=2,
            source=EntrySource.KIOSK,
        )

        entry.generate_guest_token()

        # Should expire in ~24 hours
        expected_expiry = datetime.utcnow() + timedelta(hours=24)
        assert entry.token_expires_at is not None
        # Allow 1 minute tolerance
        diff = abs((entry.token_expires_at - expected_expiry).total_seconds())
        assert diff < 60

    def test_token_expiry_custom(self) -> None:
        """Should use custom expiry hours."""
        entry = WaitlistEntry(
            guest_id=1,
            party_size=2,
            source=EntrySource.KIOSK,
        )

        entry.generate_guest_token(expiry_hours=48)

        expected_expiry = datetime.utcnow() + timedelta(hours=48)
        diff = abs((entry.token_expires_at - expected_expiry).total_seconds())
        assert diff < 60

    def test_is_token_valid_when_valid(self) -> None:
        """Should return True when token is valid and not expired."""
        entry = WaitlistEntry(
            guest_id=1,
            party_size=2,
            source=EntrySource.KIOSK,
        )

        entry.generate_guest_token()

        assert entry.is_token_valid() is True

    def test_is_token_valid_when_no_token(self) -> None:
        """Should return False when no token exists."""
        entry = WaitlistEntry(
            guest_id=1,
            party_size=2,
            source=EntrySource.KIOSK,
        )

        assert entry.is_token_valid() is False

    def test_is_token_valid_when_expired(self) -> None:
        """Should return False when token is expired."""
        entry = WaitlistEntry(
            guest_id=1,
            party_size=2,
            source=EntrySource.KIOSK,
        )

        entry.generate_guest_token()
        # Manually set expiry to past
        entry.token_expires_at = datetime.utcnow() - timedelta(hours=1)

        assert entry.is_token_valid() is False

    def test_token_regeneration_updates_expiry(self) -> None:
        """Regenerating token should update expiry."""
        entry = WaitlistEntry(
            guest_id=1,
            party_size=2,
            source=EntrySource.KIOSK,
        )

        entry.generate_guest_token()
        old_expiry = entry.token_expires_at

        # Manually expire it
        entry.token_expires_at = datetime.utcnow() - timedelta(hours=1)
        assert entry.is_token_valid() is False

        # Regenerate
        entry.generate_guest_token()

        assert entry.is_token_valid() is True
        assert entry.token_expires_at > old_expiry
