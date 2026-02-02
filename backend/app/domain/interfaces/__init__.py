"""Domain interfaces (ports).

Repository interfaces following DIP - domain depends on abstractions.
"""

from app.domain.interfaces.guest_repository import GuestRepositoryInterface
from app.domain.interfaces.waitlist_repository import WaitlistRepositoryInterface

__all__ = [
    "GuestRepositoryInterface",
    "WaitlistRepositoryInterface",
]
