"""Notification API endpoints.

REQ-NOTIF-001: SMS/text alerts when table is ready
AC-NOTIF-001: Send "Table Ready" SMS on ready condition
AC-NOTIF-002: Avoid duplicate ready messages
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.deps import get_notification_service
from app.api.v1.schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
    SendNotificationRequest,
)
from app.domain.exceptions import EntryNotFoundError
from app.services.notification_service import (
    DuplicateNotificationError,
    NotificationService,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post(
    "/ready/{entry_id}",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
    summary="Send table ready notification",
    description="REQ-NOTIF-001: Send SMS alert when table is ready. AC-NOTIF-002: Prevents duplicate messages.",
)
async def send_table_ready(
    entry_id: int,
    request: SendNotificationRequest | None = None,
    service: NotificationService = Depends(get_notification_service),
) -> NotificationResponse:
    """Send a "table ready" SMS notification.

    REQ-NOTIF-001: SMS/text alerts when table is ready
    AC-NOTIF-001: Send "Table Ready" SMS on ready condition
    AC-NOTIF-002: Avoid duplicate ready messages

    Args:
        entry_id: Waitlist entry ID to notify
        request: Optional custom message

    Returns:
        NotificationResponse with notification details

    Raises:
        404: Entry not found
        409: Notification already sent (duplicate prevention)
    """
    try:
        custom_message = request.message if request else None
        notification = await service.send_table_ready(
            entry_id=entry_id,
            custom_message=custom_message,
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


@router.get(
    "/entry/{entry_id}",
    response_model=NotificationListResponse,
    summary="Get notifications for entry",
    description="Get all notifications sent for a waitlist entry.",
)
async def get_notifications_for_entry(
    entry_id: int,
    service: NotificationService = Depends(get_notification_service),
) -> NotificationListResponse:
    """Get all notifications for a waitlist entry.

    Args:
        entry_id: Waitlist entry ID

    Returns:
        List of notifications for the entry
    """
    notifications = await service.get_notifications_for_entry(entry_id)
    return NotificationListResponse(
        notifications=[
            NotificationResponse(
                id=n.id,
                waitlist_entry_id=n.waitlist_entry_id,
                notification_type=n.notification_type,
                phone_number=n.phone_number,
                message=n.message,
                status=n.status,
                sent_at=n.sent_at,
                created_at=n.created_at,
            )
            for n in notifications
        ],
        total=len(notifications),
    )


@router.get(
    "/{notification_id}",
    response_model=NotificationResponse,
    summary="Get notification by ID",
    description="Get a specific notification by its ID.",
)
async def get_notification(
    notification_id: int,
    service: NotificationService = Depends(get_notification_service),
) -> NotificationResponse:
    """Get a notification by ID.

    Args:
        notification_id: Notification ID

    Returns:
        Notification details

    Raises:
        404: Notification not found
    """
    notification = await service.get_notification_by_id(notification_id)
    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification {notification_id} not found",
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
