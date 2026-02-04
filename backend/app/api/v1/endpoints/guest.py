"""Guest API endpoints for token-based menu access.

REQ-MENU-005: Guest receives SMS with a link, opens menu page
AC-MENU-001: Guest accesses menu from SMS link
AC-MENU-002: Guests can star items
AC-MENU-003: Soft pre-order capture
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.guest import (
    GuestContextResponse,
    GuestInterestResponse,
    GuestInterestsListResponse,
    PreorderItemRequest,
    StarItemRequest,
)
from app.api.v1.schemas.menu import MenuItemResponse, MenuResponse, MenuCategoryWithItemsResponse
from app.infrastructure.database import get_db
from app.infrastructure.repositories.guest_interest_repository import GuestInterestRepository
from app.infrastructure.repositories.menu_repository import MenuRepository

router = APIRouter(prefix="/guest", tags=["guest"])


# ==================== Dependencies ====================


async def get_guest_interest_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> GuestInterestRepository:
    """Get guest interest repository instance."""
    return GuestInterestRepository(session)


async def get_menu_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> MenuRepository:
    """Get menu repository instance."""
    return MenuRepository(session)


# ==================== Guest Context ====================


@router.get(
    "/{token}",
    response_model=GuestContextResponse,
    summary="Get guest context by token",
    description="AC-MENU-001: Guest accesses their waitlist status via SMS link",
)
async def get_guest_context(
    token: str,
    repo: Annotated[GuestInterestRepository, Depends(get_guest_interest_repository)],
) -> GuestContextResponse:
    """Get guest waitlist context using token from SMS link."""
    entry = await repo.get_entry_by_token(token)

    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired link",
        )

    if not entry.is_token_valid():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="This link has expired",
        )

    # Calculate ETA (simple: position * 15 min average)
    eta_minutes = None
    if entry.status == "waiting" and entry.position > 0:
        eta_minutes = entry.position * 15

    return GuestContextResponse(
        entry_id=entry.id,
        guest_name=entry.guest.name if entry.guest else "Guest",
        party_size=entry.party_size,
        status=entry.status,
        position=entry.position,
        eta_minutes=eta_minutes,
        created_at=entry.created_at,
    )


# ==================== Menu Access ====================


@router.get(
    "/{token}/menu",
    response_model=MenuResponse,
    summary="Get menu for guest",
    description="REQ-MENU-001: Guest browses interactive menu",
)
async def get_guest_menu(
    token: str,
    interest_repo: Annotated[GuestInterestRepository, Depends(get_guest_interest_repository)],
    menu_repo: Annotated[MenuRepository, Depends(get_menu_repository)],
    available_only: bool = True,
) -> MenuResponse:
    """Get menu for guest. Validates token first."""
    entry = await interest_repo.get_entry_by_token(token)

    if not entry or not entry.is_token_valid():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired link",
        )

    # Get menu (same as public endpoint but validates token first)
    categories = await menu_repo.get_categories_with_items(active_only=True)

    category_responses = []
    total_items = 0

    for category in categories:
        items = [
            item
            for item in category.items
            if item.is_active and (not available_only or item.is_available)
        ]
        total_items += len(items)

        category_responses.append(
            MenuCategoryWithItemsResponse(
                id=category.id,
                name=category.name,
                description=category.description,
                display_order=category.display_order,
                is_active=category.is_active,
                items=[
                    MenuItemResponse(
                        id=item.id,
                        category_id=item.category_id,
                        name=item.name,
                        description=item.description,
                        price=item.price,
                        image_url=item.image_url,
                        display_order=item.display_order,
                        is_available=item.is_available,
                        is_active=item.is_active,
                        calories=item.calories,
                        allergens=item.allergens,
                        tags=item.tags,
                        tags_list=item.tags_list,
                    )
                    for item in items
                ],
            )
        )

    return MenuResponse(categories=category_responses, total_items=total_items)


# ==================== Interests (Star) ====================


@router.get(
    "/{token}/interests",
    response_model=GuestInterestsListResponse,
    summary="Get guest's interests",
    description="AC-MENU-002: Get starred and pre-order items",
)
async def get_guest_interests(
    token: str,
    repo: Annotated[GuestInterestRepository, Depends(get_guest_interest_repository)],
) -> GuestInterestsListResponse:
    """Get all starred and pre-order items for the guest."""
    entry = await repo.get_entry_by_token(token)

    if not entry or not entry.is_token_valid():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired link",
        )

    starred = await repo.get_starred_items(entry.id)
    preorders = await repo.get_preorder_items(entry.id)

    def to_response(interest) -> GuestInterestResponse:
        item_response = None
        if interest.menu_item:
            item_response = MenuItemResponse(
                id=interest.menu_item.id,
                category_id=interest.menu_item.category_id,
                name=interest.menu_item.name,
                description=interest.menu_item.description,
                price=interest.menu_item.price,
                image_url=interest.menu_item.image_url,
                display_order=interest.menu_item.display_order,
                is_available=interest.menu_item.is_available,
                is_active=interest.menu_item.is_active,
                calories=interest.menu_item.calories,
                allergens=interest.menu_item.allergens,
                tags=interest.menu_item.tags,
                tags_list=interest.menu_item.tags_list,
            )
        return GuestInterestResponse(
            id=interest.id,
            menu_item_id=interest.menu_item_id,
            is_starred=interest.is_starred,
            is_preorder=interest.is_preorder,
            quantity=interest.quantity,
            menu_item=item_response,
        )

    return GuestInterestsListResponse(
        starred_items=[to_response(i) for i in starred],
        preorder_items=[to_response(i) for i in preorders],
        total_starred=len(starred),
        total_preorder=len(preorders),
    )


@router.post(
    "/{token}/interests/star",
    response_model=GuestInterestResponse,
    summary="Star/unstar a menu item",
    description="AC-MENU-002: Guest can star items for interest capture",
)
async def star_item(
    token: str,
    data: StarItemRequest,
    repo: Annotated[GuestInterestRepository, Depends(get_guest_interest_repository)],
    menu_repo: Annotated[MenuRepository, Depends(get_menu_repository)],
) -> GuestInterestResponse:
    """Star or unstar a menu item."""
    entry = await repo.get_entry_by_token(token)

    if not entry or not entry.is_token_valid():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired link",
        )

    # Verify menu item exists
    item = await menu_repo.get_item_by_id(data.menu_item_id)
    if not item or not item.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    interest = await repo.star_item(entry.id, data.menu_item_id, data.starred)

    return GuestInterestResponse(
        id=interest.id,
        menu_item_id=interest.menu_item_id,
        is_starred=interest.is_starred,
        is_preorder=interest.is_preorder,
        quantity=interest.quantity,
        menu_item=None,  # Don't include full item in response
    )


# ==================== Pre-Order ====================


@router.post(
    "/{token}/preorder",
    response_model=GuestInterestResponse,
    summary="Add item to pre-order",
    description="AC-MENU-003: Soft pre-order capture",
)
async def add_preorder(
    token: str,
    data: PreorderItemRequest,
    repo: Annotated[GuestInterestRepository, Depends(get_guest_interest_repository)],
    menu_repo: Annotated[MenuRepository, Depends(get_menu_repository)],
) -> GuestInterestResponse:
    """Add a menu item to pre-order."""
    entry = await repo.get_entry_by_token(token)

    if not entry or not entry.is_token_valid():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired link",
        )

    # Verify menu item exists and is available
    item = await menu_repo.get_item_by_id(data.menu_item_id)
    if not item or not item.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    if not item.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This item is currently unavailable",
        )

    interest = await repo.add_preorder(entry.id, data.menu_item_id, data.quantity)

    return GuestInterestResponse(
        id=interest.id,
        menu_item_id=interest.menu_item_id,
        is_starred=interest.is_starred,
        is_preorder=interest.is_preorder,
        quantity=interest.quantity,
        menu_item=None,
    )


@router.delete(
    "/{token}/preorder/{menu_item_id}",
    response_model=GuestInterestResponse,
    summary="Remove item from pre-order",
)
async def remove_preorder(
    token: str,
    menu_item_id: int,
    repo: Annotated[GuestInterestRepository, Depends(get_guest_interest_repository)],
) -> GuestInterestResponse:
    """Remove a menu item from pre-order."""
    entry = await repo.get_entry_by_token(token)

    if not entry or not entry.is_token_valid():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid or expired link",
        )

    interest = await repo.remove_preorder(entry.id, menu_item_id)

    if not interest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not in pre-order",
        )

    return GuestInterestResponse(
        id=interest.id,
        menu_item_id=interest.menu_item_id,
        is_starred=interest.is_starred,
        is_preorder=interest.is_preorder,
        quantity=interest.quantity,
        menu_item=None,
    )
