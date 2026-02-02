"""Domain enums for waitlist system.

REQ-WL-005: Status tracking (waiting, seated, canceled, no-show)
REQ-WL-001, REQ-DEV-001: Source tracking (KIOSK, ADMIN)
"""

from enum import Enum


class WaitlistStatus(str, Enum):
    """Waitlist entry status.

    AC-WL-003: Status transitions supported
    - waiting -> seated, canceled, no_show
    """

    WAITING = "waiting"
    SEATED = "seated"
    CANCELED = "canceled"
    NO_SHOW = "no_show"


class EntrySource(str, Enum):
    """Source of waitlist entry creation.

    AC-WL-008: Source is captured (KIOSK or ADMIN minimum)
    """

    KIOSK = "kiosk"
    ADMIN = "admin"
