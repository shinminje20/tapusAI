"""Reminder API endpoints.

REQ-NOTIF-002: Automated reminders or status updates
AC-NOTIF-003: Automated reminder / status updates
    - reminders can be sent based on defined rules
    - the system logs that reminder was sent
"""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_notification_service
from app.api.v1.schemas.notification import NotificationResponse
from app.core.config import get_settings
from app.domain.exceptions import EntryNotFoundError
from app.infrastructure.database import get_db
from app.services.notification_service import (
    DuplicateNotificationError,
    NotificationService,
)
from app.tasks.reminder_task import check_and_send_reminders, get_entries_due_for_reminder

router = APIRouter(prefix="/reminders", tags=["reminders"])


class PendingReminderEntry(BaseModel):
    """Schema for entries pending reminder."""

    entry_id: int = Field(..., description="Waitlist entry ID")
    guest_name: str = Field(..., description="Guest name")
    phone_number: str = Field(..., description="Guest phone number")
    position: int = Field(..., description="Queue position")
    estimated_seat_time: datetime = Field(..., description="Estimated seating time")
    reminder_threshold: datetime = Field(..., description="When reminder becomes due")
    created_at: datetime = Field(..., description="Entry creation time")


class PendingRemindersResponse(BaseModel):
    """Response schema for pending reminders."""

    pending: list[PendingReminderEntry] = Field(..., description="Entries due for reminder")
    total: int = Field(..., description="Total count")
    reminder_minutes_before: int = Field(..., description="Minutes before seating")
    avg_turn_time_minutes: int = Field(..., description="Average turn time in minutes")


class ReminderCheckResult(BaseModel):
    """Result of manual reminder check."""

    entries_processed: int = Field(..., description="Number of entries processed")
    reminders_sent: list[int] = Field(..., description="Entry IDs that received reminders")
    timestamp: datetime = Field(..., description="When check was performed")


@router.post(
    "/check",
    response_model=ReminderCheckResult,
    status_code=status.HTTP_200_OK,
    summary="Manually trigger reminder check",
    description=(
        "REQ-NOTIF-002: Manually check for entries due for reminder and send notifications. "
        "This endpoint is useful for testing or manual intervention. "
        "In production, reminders are sent automatically by the background task."
    ),
)
async def trigger_reminder_check(
    db: AsyncSession = Depends(get_db),
    service: NotificationService = Depends(get_notification_service),
) -> ReminderCheckResult:
    """Manually trigger a reminder check.

    REQ-NOTIF-002: Automated reminders or status updates
    AC-NOTIF-003: Automated reminder / status updates

    This endpoint allows staff to manually trigger a reminder check,
    useful for testing or when background task is not running.

    Returns:
        ReminderCheckResult with details of reminders sent
    """
    settings = get_settings()

    # Get entries due for reminder first (for count)
    entries = await get_entries_due_for_reminder(
        session=db,
        reminder_minutes_before=settings.reminder_minutes_before,
        avg_turn_time_minutes=settings.default_avg_turn_time_minutes,
    )

    # Send reminders
    sent_ids = await check_and_send_reminders(
        session=db,
        notification_service=service,
        settings=settings,
    )

    # Commit the changes
    await db.commit()

    return ReminderCheckResult(
        entries_processed=len(entries),
        reminders_sent=sent_ids,
        timestamp=datetime.utcnow(),
    )


@router.get(
    "/pending",
    response_model=PendingRemindersResponse,
    summary="Get entries due for reminder",
    description=(
        "REQ-NOTIF-002: Get list of entries that are due for a reminder notification. "
        "This shows entries where the current time is within the reminder window "
        "(default: 10 minutes before estimated seating) and no reminder has been sent."
    ),
)
async def get_pending_reminders(
    db: AsyncSession = Depends(get_db),
) -> PendingRemindersResponse:
    """Get entries that are due for a reminder.

    REQ-NOTIF-002: Automated reminders
    AC-NOTIF-003: Send reminder X minutes before estimated seating

    Returns:
        List of entries due for reminder with timing information
    """
    settings = get_settings()

    entries = await get_entries_due_for_reminder(
        session=db,
        reminder_minutes_before=settings.reminder_minutes_before,
        avg_turn_time_minutes=settings.default_avg_turn_time_minutes,
    )

    pending_list = []
    for entry in entries:
        # Load guest relationship
        await db.refresh(entry, ["guest"])

        estimated_seat_time = entry.created_at + timedelta(
            minutes=entry.position * settings.default_avg_turn_time_minutes
        )
        reminder_threshold = estimated_seat_time - timedelta(
            minutes=settings.reminder_minutes_before
        )

        guest_name = entry.guest.name if entry.guest else "Unknown"
        phone_number = entry.guest.phone_number if entry.guest else "Unknown"

        pending_list.append(
            PendingReminderEntry(
                entry_id=entry.id,
                guest_name=guest_name,
                phone_number=phone_number,
                position=entry.position,
                estimated_seat_time=estimated_seat_time,
                reminder_threshold=reminder_threshold,
                created_at=entry.created_at,
            )
        )

    return PendingRemindersResponse(
        pending=pending_list,
        total=len(pending_list),
        reminder_minutes_before=settings.reminder_minutes_before,
        avg_turn_time_minutes=settings.default_avg_turn_time_minutes,
    )


@router.post(
    "/send/{entry_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Send reminder for specific entry",
    description=(
        "REQ-NOTIF-002: Manually send a reminder notification for a specific entry. "
        "Useful for testing or when staff wants to manually remind a guest."
    ),
)
async def send_reminder_for_entry(
    entry_id: int,
    service: NotificationService = Depends(get_notification_service),
) -> NotificationResponse:
    """Send a reminder notification for a specific entry.

    REQ-NOTIF-002: Automated reminders
    AC-NOTIF-003: Automated reminder / status updates

    Args:
        entry_id: Waitlist entry ID to send reminder for

    Returns:
        NotificationResponse with notification details

    Raises:
        404: Entry not found
        409: Reminder already sent (duplicate prevention)
    """
    settings = get_settings()

    try:
        notification = await service.send_reminder(
            entry_id=entry_id,
            minutes_until_ready=settings.reminder_minutes_before,
        )
        return NotificationResponse(
            id=notification.id,
            waitlist_entry_id=notification.waitlist_entry_id,
            notification_type=notification.notification_type,
            phone_number=notification.phone_number,
            message=notification.message,
            status=notification.status,
            sent_at=notification.sent_at,
            created_at=notification.created_at,
        )
    except EntryNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Waitlist entry {entry_id} not found",
        )
    except DuplicateNotificationError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
