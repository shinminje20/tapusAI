"""Guest API schemas for token-based access.

REQ-MENU-005: Guest receives SMS with a link
AC-MENU-001: Guest accesses menu from SMS link
AC-MENU-002: Star items stores to guest/waitlist entry
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.api.v1.schemas.menu import MenuItemResponse


class GuestContextResponse(BaseModel):
    """Response for guest context via token.

    AC-MENU-001: Guest accesses menu from SMS link
    Returns guest info and waitlist status.
    """

    model_config = ConfigDict(from_attributes=True)

    entry_id: int
    guest_name: str
    party_size: int
    status: str
    position: int
    eta_minutes: int | None = None
    created_at: datetime


class StarItemRequest(BaseModel):
    """Request to star/unstar a menu item.

    AC-MENU-002: Star items for interest capture
    """

    menu_item_id: int
    starred: bool = True


class PreorderItemRequest(BaseModel):
    """Request to add item to pre-order.

    AC-MENU-003: Soft pre-order capture
    """

    menu_item_id: int
    quantity: int = Field(default=1, ge=1, le=99)


class GuestInterestResponse(BaseModel):
    """Response for a single guest interest."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    menu_item_id: int
    is_starred: bool
    is_preorder: bool
    quantity: int
    menu_item: MenuItemResponse | None = None


class GuestInterestsListResponse(BaseModel):
    """Response with all guest interests.

    AC-MENU-002: Starred items tied to waitlist entry
    AC-MENU-003: Pre-order selections stored
    """

    starred_items: list[GuestInterestResponse]
    preorder_items: list[GuestInterestResponse]
    total_starred: int
    total_preorder: int


class PreorderSummary(BaseModel):
    """Summary of guest's pre-order for admin view.

    AC-MENU-004: "Likely to order" visibility
    """

    item_name: str
    quantity: int


class GuestInterestsSummaryResponse(BaseModel):
    """Summary response for admin view.

    AC-MENU-004: Admin sees "Likely to order: 2 burgers, 1 salad"
    """

    entry_id: int
    guest_name: str
    starred_count: int
    preorder_count: int
    preorder_summary: list[PreorderSummary]
    starred_items: list[str]  # Just names for quick view
