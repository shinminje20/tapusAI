"""Waitlist API endpoints.

REQ-WL-001: Add guests quickly
REQ-WL-002: Real-time queue display
REQ-WL-003: Estimated wait time
REQ-WL-004: Reorder, prioritize, mark VIP
REQ-WL-005: Status tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.deps import get_waitlist_service
from app.api.v1.schemas.waitlist import (
    GuestCreate,
    WaitlistEntryResponse,
    WaitlistEntryUpdate,
    WaitlistReorderRequest,
)
from app.domain.exceptions import (
    EntryNotFoundError,
    InvalidPartySize,
    InvalidStatusTransitionError,
)
from app.domain.services import WaitlistService

router = APIRouter(prefix="/waitlist", tags=["waitlist"])


@router.post(
    "/",
    response_model=WaitlistEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add guest to waitlist",
    description="REQ-WL-001: Add a new guest to the waitlist. AC-WL-001: Entry appears immediately with status 'waiting'.",
)
async def add_guest(
    guest_data: GuestCreate,
    service: WaitlistService = Depends(get_waitlist_service),
) -> WaitlistEntryResponse:
    """Add a new guest to the waitlist.

    AC-WL-001: Entry appears immediately with status 'waiting'
    AC-WL-002: Validates all required fields
    AC-WL-008: Source is captured
    """
    try:
        entry = await service.add_guest(
            name=guest_data.name,
            party_size=guest_data.party_size,
            phone_number=guest_data.phone_number,
            source=guest_data.source,
        )
        eta = await service.calculate_eta(entry.id)
        return WaitlistEntryResponse(
            id=entry.id,
            guest_id=entry.guest_id,
            party_size=entry.party_size,
            status=entry.status,
            position=entry.position,
            vip_flag=entry.vip_flag,
            source=entry.source,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            eta_minutes=eta,
            guest_name=guest_data.name,
            guest_phone=guest_data.phone_number,
        )
    except InvalidPartySize as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.get(
    "/",
    response_model=list[WaitlistEntryResponse],
    summary="Get all waiting entries",
    description="REQ-WL-002: Real-time queue display ordered by position.",
)
async def get_waitlist(
    service: WaitlistService = Depends(get_waitlist_service),
) -> list[WaitlistEntryResponse]:
    """Get all entries with status 'waiting', ordered by position.

    REQ-WL-002: Real-time queue display
    """
    entries = await service.get_all_waiting()
    result = []
    for entry in entries:
        eta = await service.calculate_eta(entry.id)
        result.append(
            WaitlistEntryResponse(
                id=entry.id,
                guest_id=entry.guest_id,
                party_size=entry.party_size,
                status=entry.status,
                position=entry.position,
                vip_flag=entry.vip_flag,
                source=entry.source,
                created_at=entry.created_at,
                updated_at=entry.updated_at,
                eta_minutes=eta,
                guest_name=entry.guest.name if entry.guest else None,
                guest_phone=entry.guest.phone_number if entry.guest else None,
            )
        )
    return result


@router.patch(
    "/{entry_id}/status",
    response_model=WaitlistEntryResponse,
    summary="Update entry status",
    description="REQ-WL-005: Status tracking. AC-WL-003: Validates status transitions.",
)
async def update_status(
    entry_id: int,
    update_data: WaitlistEntryUpdate,
    service: WaitlistService = Depends(get_waitlist_service),
) -> WaitlistEntryResponse:
    """Update the status of a waitlist entry.

    AC-WL-003: Validates status transitions (waiting -> seated/canceled/no_show)
    """
    try:
        entry = await service.update_status(entry_id, update_data.status)
        return WaitlistEntryResponse(
            id=entry.id,
            guest_id=entry.guest_id,
            party_size=entry.party_size,
            status=entry.status,
            position=entry.position,
            vip_flag=entry.vip_flag,
            source=entry.source,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            eta_minutes=None,  # No ETA for non-waiting entries
        )
    except EntryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Waitlist entry {entry_id} not found",
        )
    except InvalidStatusTransitionError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e),
        )


@router.post(
    "/reorder",
    response_model=list[WaitlistEntryResponse],
    summary="Reorder waitlist entries",
    description="REQ-WL-004: Reorder entries. AC-WL-006: Manual reorder only.",
)
async def reorder_entries(
    reorder_data: WaitlistReorderRequest,
    service: WaitlistService = Depends(get_waitlist_service),
) -> list[WaitlistEntryResponse]:
    """Reorder waitlist entries by specifying new order.

    REQ-WL-004: Ability to reorder
    AC-WL-006: VIP is manual move only (no auto policy)
    """
    try:
        entries = await service.reorder_entries(reorder_data.entry_ids)
        result = []
        for entry in entries:
            eta = await service.calculate_eta(entry.id)
            result.append(
                WaitlistEntryResponse(
                    id=entry.id,
                    guest_id=entry.guest_id,
                    party_size=entry.party_size,
                    status=entry.status,
                    position=entry.position,
                    vip_flag=entry.vip_flag,
                    source=entry.source,
                    created_at=entry.created_at,
                    updated_at=entry.updated_at,
                    eta_minutes=eta,
                )
            )
        return result
    except EntryNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch(
    "/{entry_id}/vip",
    response_model=WaitlistEntryResponse,
    summary="Toggle VIP flag",
    description="REQ-WL-004: Mark VIP guests. AC-WL-006: VIP is informational only.",
)
async def toggle_vip(
    entry_id: int,
    vip: bool = True,
    service: WaitlistService = Depends(get_waitlist_service),
) -> WaitlistEntryResponse:
    """Mark or unmark an entry as VIP.

    AC-WL-006: VIP is informational flag only (manual move for priority)
    """
    try:
        entry = await service.mark_vip(entry_id, vip=vip)
        eta = await service.calculate_eta(entry.id)
        return WaitlistEntryResponse(
            id=entry.id,
            guest_id=entry.guest_id,
            party_size=entry.party_size,
            status=entry.status,
            position=entry.position,
            vip_flag=entry.vip_flag,
            source=entry.source,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
            eta_minutes=eta,
        )
    except EntryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Waitlist entry {entry_id} not found",
        )


@router.get(
    "/{entry_id}/eta",
    summary="Get estimated wait time",
    description="REQ-WL-003: Estimated wait time. AC-WL-007: Simple algorithm.",
)
async def get_eta(
    entry_id: int,
    service: WaitlistService = Depends(get_waitlist_service),
) -> dict[str, int]:
    """Get estimated wait time for an entry.

    AC-WL-007: Simple algorithm (position × avg_turn_time)
    """
    try:
        eta = await service.calculate_eta(entry_id)
        return {"entry_id": entry_id, "eta_minutes": eta}
    except EntryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Waitlist entry {entry_id} not found",
        )
