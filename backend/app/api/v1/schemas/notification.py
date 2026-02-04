"""Notification API schemas.

REQ-NOTIF-001: SMS/text alerts when table is ready
AC-NOTIF-001: Send "Table Ready" SMS on ready condition
AC-NOTIF-002: Avoid duplicate ready messages
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SendNotificationRequest(BaseModel):
    """Request schema for sending a notification.

    AC-NOTIF-001: Send "Table Ready" SMS on ready condition
    """

    message: str | None = Field(
        None,
        max_length=500,
        description="Custom message (optional, overrides default template)",
    )


class NotificationResponse(BaseModel):
    """Response schema for notification records.

    REQ-NOTIF-001: SMS/text alerts when table is ready
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Notification ID")
    waitlist_entry_id: int = Field(..., description="Associated waitlist entry ID")
    notification_type: str = Field(
        ..., description="Type of notification (table_ready, reminder, custom)"
    )
    phone_number: str = Field(..., description="Phone number message was sent to")
    message: str = Field(..., description="Message content")
    status: str = Field(..., description="Delivery status (pending, sent, failed)")
    sent_at: datetime | None = Field(None, description="Timestamp when sent")
    created_at: datetime = Field(..., description="Timestamp when created")


class NotificationListResponse(BaseModel):
    """Response schema for list of notifications."""

    notifications: list[NotificationResponse] = Field(
        ..., description="List of notifications"
    )
    total: int = Field(..., description="Total count")
