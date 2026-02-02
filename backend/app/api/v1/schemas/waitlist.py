"""Waitlist API schemas.

REQ-WL-001: Guest data (name, phone, party_size)
REQ-WL-005: Status tracking
AC-WL-002: All fields required
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.entities import EntrySource, WaitlistStatus


class GuestCreate(BaseModel):
    """Schema for creating a guest with waitlist entry.

    AC-WL-002: All fields required.
    """

    name: str = Field(..., min_length=1, max_length=255, description="Guest name")
    phone_number: str = Field(
        ..., min_length=1, max_length=20, description="Contact phone number"
    )
    party_size: int = Field(..., ge=1, description="Number of people in party")
    source: EntrySource = Field(
        default=EntrySource.ADMIN, description="Entry source (kiosk or admin)"
    )


class GuestResponse(BaseModel):
    """Schema for guest response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone_number: str
    created_at: datetime


class WaitlistEntryCreate(BaseModel):
    """Schema for creating a waitlist entry (internal use)."""

    guest_id: int
    party_size: int = Field(..., ge=1)
    source: EntrySource


class WaitlistEntryUpdate(BaseModel):
    """Schema for updating a waitlist entry status.

    AC-WL-003: Status transition validation.
    """

    status: WaitlistStatus = Field(..., description="New status for the entry")


class WaitlistEntryResponse(BaseModel):
    """Schema for waitlist entry response.

    AC-WL-001: Entry includes status, position, timestamps.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    guest_id: int
    party_size: int
    status: str
    position: int
    vip_flag: bool
    source: str
    created_at: datetime
    updated_at: datetime
    eta_minutes: int | None = Field(None, description="Estimated wait time in minutes")

    # Nested guest info for display
    guest_name: str | None = None
    guest_phone: str | None = None


class WaitlistReorderRequest(BaseModel):
    """Schema for reordering waitlist entries.

    REQ-WL-004: Ability to reorder.
    AC-WL-006: Manual reorder only.
    """

    entry_ids: list[int] = Field(
        ..., min_length=1, description="Ordered list of entry IDs (first = position 1)"
    )
