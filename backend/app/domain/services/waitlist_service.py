"""Waitlist service - core business logic.

REQ-WL-001: Add guests quickly
REQ-WL-002: Real-time queue display
REQ-WL-003: Estimated wait time
REQ-WL-004: Reorder, prioritize, mark VIP
REQ-WL-005: Status tracking
"""

from app.domain.entities import EntrySource, Guest, WaitlistEntry, WaitlistStatus
from app.domain.exceptions import (
    EntryNotFoundError,
    InvalidPartySize,
    InvalidStatusTransitionError,
)
from app.domain.interfaces import GuestRepositoryInterface, WaitlistRepositoryInterface

# Valid status transitions per AC-WL-003
VALID_TRANSITIONS: dict[WaitlistStatus, set[WaitlistStatus]] = {
    WaitlistStatus.WAITING: {
        WaitlistStatus.SEATED,
        WaitlistStatus.CANCELED,
        WaitlistStatus.NO_SHOW,
    },
    WaitlistStatus.SEATED: set(),
    WaitlistStatus.CANCELED: set(),
    WaitlistStatus.NO_SHOW: set(),
}

# Default average turn time in minutes for ETA calculation
DEFAULT_AVG_TURN_TIME_MINUTES = 15


class WaitlistService:
    """Service for waitlist business operations.

    AC-WL-001: Add guest and display immediately
    AC-WL-002: Validate input
    AC-WL-003: Status transitions
    AC-WL-006: VIP flagging (manual move only)
    AC-WL-007: ETA calculation (simple: position × avg_turn_time)
    """

    def __init__(
        self,
        waitlist_repo: WaitlistRepositoryInterface,
        guest_repo: GuestRepositoryInterface,
        avg_turn_time_minutes: int = DEFAULT_AVG_TURN_TIME_MINUTES,
    ) -> None:
        self._waitlist_repo = waitlist_repo
        self._guest_repo = guest_repo
        self._avg_turn_time = avg_turn_time_minutes

    async def add_guest(
        self,
        name: str,
        party_size: int,
        phone_number: str,
        source: EntrySource,
    ) -> WaitlistEntry:
        """Add a new guest to the waitlist.

        REQ-WL-001: Add guests quickly
        AC-WL-001: Entry appears immediately with status 'waiting'
        AC-WL-002: Validate all fields (name, phone, party_size required)
        AC-WL-008: Source is captured

        Args:
            name: Guest name (required)
            party_size: Number of people (required, >= 1)
            phone_number: Contact phone (required)
            source: Entry source (KIOSK or ADMIN)

        Returns:
            Created WaitlistEntry

        Raises:
            InvalidPartySize: If party_size < 1
        """
        if party_size < 1:
            raise InvalidPartySize(party_size)

        # Check for existing guest by phone or create new
        guest = await self._guest_repo.get_by_phone(phone_number)
        if guest is None:
            guest = Guest(name=name, phone_number=phone_number)
            guest = await self._guest_repo.add(guest)

        # Get next position (end of queue)
        max_position = await self._waitlist_repo.get_max_position()
        next_position = max_position + 1

        # Create waitlist entry (status defaults to WAITING per AC-WL-001)
        entry = WaitlistEntry(
            guest_id=guest.id,
            party_size=party_size,
            source=source,
            position=next_position,
        )
        return await self._waitlist_repo.add(entry)

    async def update_status(
        self,
        entry_id: int,
        new_status: WaitlistStatus,
    ) -> WaitlistEntry:
        """Update the status of a waitlist entry.

        REQ-WL-005: Status tracking
        AC-WL-003: Validate status transitions

        Args:
            entry_id: Entry to update
            new_status: Target status

        Returns:
            Updated WaitlistEntry

        Raises:
            EntryNotFoundError: If entry doesn't exist
            InvalidStatusTransitionError: If transition is not allowed
        """
        entry = await self._waitlist_repo.get_by_id(entry_id)
        if entry is None:
            raise EntryNotFoundError(entry_id)

        current_status = entry.status_enum
        if new_status not in VALID_TRANSITIONS.get(current_status, set()):
            raise InvalidStatusTransitionError(current_status.value, new_status.value)

        entry.status = new_status.value
        return await self._waitlist_repo.update(entry)

    async def reorder_entries(self, entry_ids: list[int]) -> list[WaitlistEntry]:
        """Reorder waitlist entries by specifying new order.

        REQ-WL-004: Ability to reorder
        AC-WL-006: VIP is manual move only (no auto policy)

        Args:
            entry_ids: Ordered list of entry IDs (first = position 1)

        Returns:
            List of updated entries in new order

        Raises:
            EntryNotFoundError: If any entry doesn't exist
        """
        entries = []
        for idx, entry_id in enumerate(entry_ids, start=1):
            entry = await self._waitlist_repo.get_by_id(entry_id)
            if entry is None:
                raise EntryNotFoundError(entry_id)
            entry.position = idx
            entries.append(entry)

        await self._waitlist_repo.update_positions(entries)
        return entries

    async def mark_vip(self, entry_id: int, vip: bool = True) -> WaitlistEntry:
        """Mark or unmark an entry as VIP.

        REQ-WL-004: Mark VIP guests
        AC-WL-006: VIP is informational flag only (manual move)

        Args:
            entry_id: Entry to update
            vip: VIP status (default True)

        Returns:
            Updated WaitlistEntry

        Raises:
            EntryNotFoundError: If entry doesn't exist
        """
        entry = await self._waitlist_repo.get_by_id(entry_id)
        if entry is None:
            raise EntryNotFoundError(entry_id)

        entry.vip_flag = vip
        return await self._waitlist_repo.update(entry)

    async def calculate_eta(self, entry_id: int) -> int:
        """Calculate estimated wait time in minutes.

        REQ-WL-003: Estimated wait time
        AC-WL-007: Simple algorithm (position × avg_turn_time)

        Args:
            entry_id: Entry to calculate ETA for

        Returns:
            Estimated wait time in minutes

        Raises:
            EntryNotFoundError: If entry doesn't exist
        """
        entry = await self._waitlist_repo.get_by_id(entry_id)
        if entry is None:
            raise EntryNotFoundError(entry_id)

        # Simple ETA: position × average turn time
        # Position 1 = next to be seated, so position - 1 parties ahead
        parties_ahead = max(0, entry.position - 1)
        return parties_ahead * self._avg_turn_time

    async def get_all_waiting(self) -> list[WaitlistEntry]:
        """Get all entries with status 'waiting', ordered by position.

        REQ-WL-002: Real-time queue display

        Returns:
            List of waiting entries ordered by position
        """
        return await self._waitlist_repo.get_all_waiting()
