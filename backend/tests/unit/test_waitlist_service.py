"""Unit tests for WaitlistService.

REQ-WL-001-005: Waitlist management business logic
Tests use mock repositories to isolate service logic.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.entities import EntrySource, Guest, WaitlistEntry, WaitlistStatus
from app.domain.exceptions import (
    EntryNotFoundError,
    InvalidPartySize,
    InvalidStatusTransitionError,
)
from app.domain.interfaces import GuestRepositoryInterface, WaitlistRepositoryInterface
from app.domain.services import WaitlistService


@pytest.fixture
def mock_guest_repo() -> AsyncMock:
    """Create mock guest repository."""
    repo = AsyncMock(spec=GuestRepositoryInterface)
    return repo


@pytest.fixture
def mock_waitlist_repo() -> AsyncMock:
    """Create mock waitlist repository."""
    repo = AsyncMock(spec=WaitlistRepositoryInterface)
    return repo


@pytest.fixture
def waitlist_service(
    mock_waitlist_repo: AsyncMock, mock_guest_repo: AsyncMock
) -> WaitlistService:
    """Create WaitlistService with mock repositories."""
    return WaitlistService(
        waitlist_repo=mock_waitlist_repo,
        guest_repo=mock_guest_repo,
        avg_turn_time_minutes=15,
    )


class TestAddGuest:
    """Tests for add_guest method - REQ-WL-001, AC-WL-001, AC-WL-002."""

    @pytest.mark.asyncio
    async def test_add_guest_creates_new_guest_and_entry(
        self,
        waitlist_service: WaitlistService,
        mock_guest_repo: AsyncMock,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """AC-WL-001: Entry appears immediately with status 'waiting'."""
        # Arrange
        mock_guest_repo.get_by_phone.return_value = None
        mock_guest = MagicMock(spec=Guest)
        mock_guest.id = 1
        mock_guest_repo.add.return_value = mock_guest
        mock_waitlist_repo.get_max_position.return_value = 0

        mock_entry = MagicMock(spec=WaitlistEntry)
        mock_entry.id = 1
        mock_entry.status = WaitlistStatus.WAITING.value
        mock_waitlist_repo.add.return_value = mock_entry

        # Act
        result = await waitlist_service.add_guest(
            name="John Doe",
            party_size=4,
            phone_number="555-1234",
            source=EntrySource.KIOSK,
        )

        # Assert
        mock_guest_repo.get_by_phone.assert_called_once_with("555-1234")
        mock_guest_repo.add.assert_called_once()
        mock_waitlist_repo.add.assert_called_once()
        assert result.status == WaitlistStatus.WAITING.value

    @pytest.mark.asyncio
    async def test_add_guest_uses_existing_guest(
        self,
        waitlist_service: WaitlistService,
        mock_guest_repo: AsyncMock,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """Should reuse existing guest by phone number."""
        # Arrange
        existing_guest = MagicMock(spec=Guest)
        existing_guest.id = 42
        mock_guest_repo.get_by_phone.return_value = existing_guest
        mock_waitlist_repo.get_max_position.return_value = 5

        mock_entry = MagicMock(spec=WaitlistEntry)
        mock_waitlist_repo.add.return_value = mock_entry

        # Act
        await waitlist_service.add_guest(
            name="John Doe",
            party_size=2,
            phone_number="555-1234",
            source=EntrySource.ADMIN,
        )

        # Assert
        mock_guest_repo.add.assert_not_called()
        call_args = mock_waitlist_repo.add.call_args[0][0]
        assert call_args.guest_id == 42
        assert call_args.position == 6  # max_position + 1

    @pytest.mark.asyncio
    async def test_add_guest_invalid_party_size_raises_error(
        self, waitlist_service: WaitlistService
    ) -> None:
        """AC-WL-002: party_size must be >= 1."""
        with pytest.raises(InvalidPartySize) as exc_info:
            await waitlist_service.add_guest(
                name="John",
                party_size=0,
                phone_number="555-1234",
                source=EntrySource.KIOSK,
            )

        assert exc_info.value.party_size == 0

    @pytest.mark.asyncio
    async def test_add_guest_captures_source(
        self,
        waitlist_service: WaitlistService,
        mock_guest_repo: AsyncMock,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """AC-WL-008: Source is captured."""
        mock_guest_repo.get_by_phone.return_value = MagicMock(id=1)
        mock_waitlist_repo.get_max_position.return_value = 0
        mock_waitlist_repo.add.return_value = MagicMock()

        await waitlist_service.add_guest(
            name="John",
            party_size=2,
            phone_number="555-1234",
            source=EntrySource.ADMIN,
        )

        call_args = mock_waitlist_repo.add.call_args[0][0]
        assert call_args.source == EntrySource.ADMIN.value


class TestUpdateStatus:
    """Tests for update_status method - REQ-WL-005, AC-WL-003."""

    @pytest.mark.asyncio
    async def test_update_status_valid_transition_waiting_to_seated(
        self,
        waitlist_service: WaitlistService,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """AC-WL-003: waiting -> seated is valid."""
        mock_entry = WaitlistEntry(
            guest_id=1, party_size=2, source=EntrySource.KIOSK
        )
        mock_entry.id = 1
        mock_waitlist_repo.get_by_id.return_value = mock_entry
        mock_waitlist_repo.update.return_value = mock_entry

        result = await waitlist_service.update_status(1, WaitlistStatus.SEATED)

        assert result.status == WaitlistStatus.SEATED.value

    @pytest.mark.asyncio
    async def test_update_status_valid_transition_waiting_to_canceled(
        self,
        waitlist_service: WaitlistService,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """AC-WL-003: waiting -> canceled is valid."""
        mock_entry = WaitlistEntry(
            guest_id=1, party_size=2, source=EntrySource.KIOSK
        )
        mock_entry.id = 1
        mock_waitlist_repo.get_by_id.return_value = mock_entry
        mock_waitlist_repo.update.return_value = mock_entry

        result = await waitlist_service.update_status(1, WaitlistStatus.CANCELED)

        assert result.status == WaitlistStatus.CANCELED.value

    @pytest.mark.asyncio
    async def test_update_status_valid_transition_waiting_to_no_show(
        self,
        waitlist_service: WaitlistService,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """AC-WL-003: waiting -> no_show is valid."""
        mock_entry = WaitlistEntry(
            guest_id=1, party_size=2, source=EntrySource.KIOSK
        )
        mock_entry.id = 1
        mock_waitlist_repo.get_by_id.return_value = mock_entry
        mock_waitlist_repo.update.return_value = mock_entry

        result = await waitlist_service.update_status(1, WaitlistStatus.NO_SHOW)

        assert result.status == WaitlistStatus.NO_SHOW.value

    @pytest.mark.asyncio
    async def test_update_status_invalid_transition_raises_error(
        self,
        waitlist_service: WaitlistService,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """AC-WL-003: seated -> waiting is invalid."""
        mock_entry = WaitlistEntry(
            guest_id=1,
            party_size=2,
            source=EntrySource.KIOSK,
            status=WaitlistStatus.SEATED,
        )
        mock_entry.id = 1
        mock_waitlist_repo.get_by_id.return_value = mock_entry

        with pytest.raises(InvalidStatusTransitionError) as exc_info:
            await waitlist_service.update_status(1, WaitlistStatus.WAITING)

        assert exc_info.value.current == "seated"
        assert exc_info.value.target == "waiting"

    @pytest.mark.asyncio
    async def test_update_status_entry_not_found_raises_error(
        self,
        waitlist_service: WaitlistService,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """Should raise EntryNotFoundError for missing entry."""
        mock_waitlist_repo.get_by_id.return_value = None

        with pytest.raises(EntryNotFoundError) as exc_info:
            await waitlist_service.update_status(999, WaitlistStatus.SEATED)

        assert exc_info.value.entry_id == 999


class TestReorderEntries:
    """Tests for reorder_entries method - REQ-WL-004, AC-WL-006."""

    @pytest.mark.asyncio
    async def test_reorder_entries_updates_positions(
        self,
        waitlist_service: WaitlistService,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """REQ-WL-004: Ability to reorder."""
        entry1 = WaitlistEntry(guest_id=1, party_size=2, source=EntrySource.KIOSK)
        entry1.id = 1
        entry1.position = 2
        entry2 = WaitlistEntry(guest_id=2, party_size=3, source=EntrySource.KIOSK)
        entry2.id = 2
        entry2.position = 1

        mock_waitlist_repo.get_by_id.side_effect = lambda id: {1: entry1, 2: entry2}[id]

        # Reorder: entry2 first, then entry1
        result = await waitlist_service.reorder_entries([2, 1])

        assert result[0].position == 1
        assert result[0].id == 2
        assert result[1].position == 2
        assert result[1].id == 1
        mock_waitlist_repo.update_positions.assert_called_once()

    @pytest.mark.asyncio
    async def test_reorder_entries_not_found_raises_error(
        self,
        waitlist_service: WaitlistService,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """Should raise EntryNotFoundError if entry doesn't exist."""
        mock_waitlist_repo.get_by_id.return_value = None

        with pytest.raises(EntryNotFoundError) as exc_info:
            await waitlist_service.reorder_entries([999])

        assert exc_info.value.entry_id == 999


class TestMarkVip:
    """Tests for mark_vip method - REQ-WL-004, AC-WL-006."""

    @pytest.mark.asyncio
    async def test_mark_vip_sets_flag(
        self,
        waitlist_service: WaitlistService,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """AC-WL-006: VIP flagging (informational only)."""
        mock_entry = WaitlistEntry(
            guest_id=1, party_size=2, source=EntrySource.KIOSK
        )
        mock_entry.id = 1
        mock_waitlist_repo.get_by_id.return_value = mock_entry
        mock_waitlist_repo.update.return_value = mock_entry

        result = await waitlist_service.mark_vip(1, vip=True)

        assert result.vip_flag is True
        mock_waitlist_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_unmark_vip_clears_flag(
        self,
        waitlist_service: WaitlistService,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """Should be able to unmark VIP."""
        mock_entry = WaitlistEntry(
            guest_id=1, party_size=2, source=EntrySource.KIOSK, vip_flag=True
        )
        mock_entry.id = 1
        mock_waitlist_repo.get_by_id.return_value = mock_entry
        mock_waitlist_repo.update.return_value = mock_entry

        result = await waitlist_service.mark_vip(1, vip=False)

        assert result.vip_flag is False

    @pytest.mark.asyncio
    async def test_mark_vip_not_found_raises_error(
        self,
        waitlist_service: WaitlistService,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """Should raise EntryNotFoundError for missing entry."""
        mock_waitlist_repo.get_by_id.return_value = None

        with pytest.raises(EntryNotFoundError) as exc_info:
            await waitlist_service.mark_vip(999)

        assert exc_info.value.entry_id == 999


class TestCalculateEta:
    """Tests for calculate_eta method - REQ-WL-003, AC-WL-007."""

    @pytest.mark.asyncio
    async def test_calculate_eta_position_1(
        self,
        waitlist_service: WaitlistService,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """AC-WL-007: Position 1 = 0 wait (next to be seated)."""
        mock_entry = WaitlistEntry(
            guest_id=1, party_size=2, source=EntrySource.KIOSK, position=1
        )
        mock_entry.id = 1
        mock_waitlist_repo.get_by_id.return_value = mock_entry

        eta = await waitlist_service.calculate_eta(1)

        assert eta == 0  # Position 1 means next up

    @pytest.mark.asyncio
    async def test_calculate_eta_position_5(
        self,
        waitlist_service: WaitlistService,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """AC-WL-007: Simple algorithm (position × avg_turn_time)."""
        mock_entry = WaitlistEntry(
            guest_id=1, party_size=2, source=EntrySource.KIOSK, position=5
        )
        mock_entry.id = 1
        mock_waitlist_repo.get_by_id.return_value = mock_entry

        eta = await waitlist_service.calculate_eta(1)

        # Position 5 = 4 parties ahead × 15 min = 60 min
        assert eta == 60

    @pytest.mark.asyncio
    async def test_calculate_eta_not_found_raises_error(
        self,
        waitlist_service: WaitlistService,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """Should raise EntryNotFoundError for missing entry."""
        mock_waitlist_repo.get_by_id.return_value = None

        with pytest.raises(EntryNotFoundError) as exc_info:
            await waitlist_service.calculate_eta(999)

        assert exc_info.value.entry_id == 999


class TestGetAllWaiting:
    """Tests for get_all_waiting method - REQ-WL-002."""

    @pytest.mark.asyncio
    async def test_get_all_waiting_returns_ordered_entries(
        self,
        waitlist_service: WaitlistService,
        mock_waitlist_repo: AsyncMock,
    ) -> None:
        """REQ-WL-002: Real-time queue display."""
        entry1 = WaitlistEntry(
            guest_id=1, party_size=2, source=EntrySource.KIOSK, position=1
        )
        entry2 = WaitlistEntry(
            guest_id=2, party_size=3, source=EntrySource.KIOSK, position=2
        )
        mock_waitlist_repo.get_all_waiting.return_value = [entry1, entry2]

        result = await waitlist_service.get_all_waiting()

        assert len(result) == 2
        assert result[0].position == 1
        assert result[1].position == 2
