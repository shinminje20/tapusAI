"""Unit tests for domain entities.

Tests cover:
- AC-WL-001: Entry creation with correct defaults
- AC-WL-002: Required fields validation
- AC-WL-003: Status values
- AC-WL-006: VIP flag
- AC-WL-008: Source tracking
"""

import pytest

from app.domain.entities import (
    EntrySource,
    Guest,
    Table,
    WaitlistEntry,
    WaitlistStatus,
)


class TestWaitlistStatus:
    """Tests for WaitlistStatus enum. AC-WL-003."""

    def test_status_values_exist(self) -> None:
        """AC-WL-003: Status transitions supported."""
        assert WaitlistStatus.WAITING == "waiting"
        assert WaitlistStatus.SEATED == "seated"
        assert WaitlistStatus.CANCELED == "canceled"
        assert WaitlistStatus.NO_SHOW == "no_show"

    def test_status_count(self) -> None:
        """Verify all expected statuses exist."""
        assert len(WaitlistStatus) == 4


class TestEntrySource:
    """Tests for EntrySource enum. AC-WL-008."""

    def test_source_values_exist(self) -> None:
        """AC-WL-008: Source is captured (KIOSK or ADMIN)."""
        assert EntrySource.KIOSK == "kiosk"
        assert EntrySource.ADMIN == "admin"


class TestGuest:
    """Tests for Guest entity. REQ-WL-001, AC-WL-002."""

    def test_guest_creation(self) -> None:
        """AC-WL-002: Guest with required fields."""
        guest = Guest(name="John Doe", phone_number="+1234567890")
        assert guest.name == "John Doe"
        assert guest.phone_number == "+1234567890"

    def test_guest_repr(self) -> None:
        """Guest string representation."""
        guest = Guest(id=1, name="John Doe", phone_number="+1234567890")
        assert "John Doe" in repr(guest)


class TestWaitlistEntry:
    """Tests for WaitlistEntry entity. REQ-WL-001, AC-WL-001."""

    def test_entry_defaults(self) -> None:
        """AC-WL-001: Entry has status 'waiting' by default."""
        entry = WaitlistEntry(
            guest_id=1,
            party_size=4,
            source=EntrySource.KIOSK,
        )
        assert entry.status == WaitlistStatus.WAITING.value
        assert entry.status_enum == WaitlistStatus.WAITING
        assert entry.vip_flag is False
        assert entry.position == 0
        assert entry.version == 1

    def test_entry_with_vip(self) -> None:
        """AC-WL-006: VIP flagging."""
        entry = WaitlistEntry(
            guest_id=1,
            party_size=2,
            source=EntrySource.ADMIN,
            vip_flag=True,
        )
        assert entry.vip_flag is True

    def test_entry_source_kiosk(self) -> None:
        """AC-WL-008: Source captured as KIOSK."""
        entry = WaitlistEntry(
            guest_id=1,
            party_size=3,
            source=EntrySource.KIOSK,
        )
        assert entry.source == EntrySource.KIOSK.value
        assert entry.source_enum == EntrySource.KIOSK

    def test_entry_source_admin(self) -> None:
        """AC-WL-008: Source captured as ADMIN."""
        entry = WaitlistEntry(
            guest_id=1,
            party_size=3,
            source=EntrySource.ADMIN,
        )
        assert entry.source == EntrySource.ADMIN.value
        assert entry.source_enum == EntrySource.ADMIN

    def test_entry_party_size(self) -> None:
        """AC-WL-002: Party size captured."""
        entry = WaitlistEntry(
            guest_id=1,
            party_size=6,
            source=EntrySource.KIOSK,
        )
        assert entry.party_size == 6


class TestTable:
    """Tests for Table entity."""

    def test_table_creation(self) -> None:
        """Table with number and capacity."""
        table = Table(number="A1", capacity=4)
        assert table.number == "A1"
        assert table.capacity == 4

    def test_table_default_capacity(self) -> None:
        """Table default capacity is 4."""
        table = Table(number="B2")
        assert table.capacity == 4
