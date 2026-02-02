"""Domain exceptions.

REQ-WL-005: Status transition validation
AC-WL-003: Invalid status transitions raise errors
"""


class DomainError(Exception):
    """Base domain error."""

    pass


class InvalidStatusTransitionError(DomainError):
    """Raised when an invalid status transition is attempted.

    AC-WL-003: Only valid transitions allowed.
    """

    def __init__(self, current: str, target: str) -> None:
        self.current = current
        self.target = target
        super().__init__(f"Cannot transition from '{current}' to '{target}'")


class EntryNotFoundError(DomainError):
    """Raised when a waitlist entry is not found."""

    def __init__(self, entry_id: int) -> None:
        self.entry_id = entry_id
        super().__init__(f"Waitlist entry {entry_id} not found")


class GuestNotFoundError(DomainError):
    """Raised when a guest is not found."""

    def __init__(self, guest_id: int) -> None:
        self.guest_id = guest_id
        super().__init__(f"Guest {guest_id} not found")


class InvalidPartySize(DomainError):
    """Raised when party size is invalid.

    AC-WL-002: party_size >= 1
    """

    def __init__(self, party_size: int) -> None:
        self.party_size = party_size
        super().__init__(f"Party size must be >= 1, got {party_size}")
