"""Menu API endpoints.

REQ-MENU-001: Guests can browse an interactive menu
AC-MENU-001: Guest accesses menu from SMS link

Public endpoints for menu browsing.
Admin endpoints for menu management (protected).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas.menu import (
    MenuCategoryCreate,
    MenuCategoryResponse,
    MenuCategoryUpdate,
    MenuCategoryWithItemsResponse,
    MenuItemCreate,
    MenuItemResponse,
    MenuItemUpdate,
    MenuResponse,
)
from app.core.deps import HostUser, ManagerUser
from app.domain.entities import MenuCategory, MenuItem
from app.infrastructure.database import get_db
from app.infrastructure.repositories.menu_repository import MenuRepository

router = APIRouter(prefix="/menu", tags=["menu"])
admin_router = APIRouter(prefix="/admin/menu", tags=["admin-menu"])


# ==================== Dependencies ====================


async def get_menu_repository(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> MenuRepository:
    """Get menu repository instance."""
    return MenuRepository(session)


# ==================== Public Endpoints ====================


@router.get(
    "",
    response_model=MenuResponse,
    summary="Get full menu",
    description="REQ-MENU-001: Browse interactive menu with categories and items",
)
async def get_menu(
    repo: Annotated[MenuRepository, Depends(get_menu_repository)],
    available_only: bool = False,
) -> MenuResponse:
    """Get the complete menu with categories and items.

    AC-MENU-001: Guest accesses menu from SMS link
    """
    categories = await repo.get_categories_with_items(active_only=True)

    # Filter items if available_only
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


@router.get(
    "/categories",
    response_model=list[MenuCategoryResponse],
    summary="List menu categories",
)
async def list_categories(
    repo: Annotated[MenuRepository, Depends(get_menu_repository)],
) -> list[MenuCategoryResponse]:
    """Get all active menu categories."""
    categories = await repo.get_categories(active_only=True)
    return [
        MenuCategoryResponse(
            id=c.id,
            name=c.name,
            description=c.description,
            display_order=c.display_order,
            is_active=c.is_active,
        )
        for c in categories
    ]


@router.get(
    "/categories/{category_id}",
    response_model=MenuCategoryWithItemsResponse,
    summary="Get category with items",
)
async def get_category(
    category_id: int,
    repo: Annotated[MenuRepository, Depends(get_menu_repository)],
) -> MenuCategoryWithItemsResponse:
    """Get a category with its menu items."""
    category = await repo.get_category_by_id(category_id)
    if not category or not category.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    items = await repo.get_items(category_id=category_id, active_only=True)

    return MenuCategoryWithItemsResponse(
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


@router.get(
    "/items/{item_id}",
    response_model=MenuItemResponse,
    summary="Get menu item details",
)
async def get_item(
    item_id: int,
    repo: Annotated[MenuRepository, Depends(get_menu_repository)],
) -> MenuItemResponse:
    """Get a single menu item by ID."""
    item = await repo.get_item_by_id(item_id)
    if not item or not item.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    return MenuItemResponse(
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


# ==================== Admin Endpoints ====================


@admin_router.post(
    "/categories",
    response_model=MenuCategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create menu category",
)
async def create_category(
    data: MenuCategoryCreate,
    repo: Annotated[MenuRepository, Depends(get_menu_repository)],
    current_user: ManagerUser,
) -> MenuCategoryResponse:
    """Create a new menu category. Requires manager or owner role."""
    category = MenuCategory(
        name=data.name,
        description=data.description,
        display_order=data.display_order,
    )
    category = await repo.create_category(category)

    return MenuCategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        display_order=category.display_order,
        is_active=category.is_active,
    )


@admin_router.put(
    "/categories/{category_id}",
    response_model=MenuCategoryResponse,
    summary="Update menu category",
)
async def update_category(
    category_id: int,
    data: MenuCategoryUpdate,
    repo: Annotated[MenuRepository, Depends(get_menu_repository)],
    current_user: ManagerUser,
) -> MenuCategoryResponse:
    """Update a menu category. Requires manager or owner role."""
    category = await repo.get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    # Update fields
    if data.name is not None:
        category.name = data.name
    if data.description is not None:
        category.description = data.description
    if data.display_order is not None:
        category.display_order = data.display_order

    category = await repo.update_category(category)

    return MenuCategoryResponse(
        id=category.id,
        name=category.name,
        description=category.description,
        display_order=category.display_order,
        is_active=category.is_active,
    )


@admin_router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete menu category",
)
async def delete_category(
    category_id: int,
    repo: Annotated[MenuRepository, Depends(get_menu_repository)],
    current_user: ManagerUser,
) -> None:
    """Soft delete a menu category. Requires manager or owner role."""
    category = await repo.get_category_by_id(category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )

    await repo.delete_category(category)


@admin_router.post(
    "/items",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create menu item",
)
async def create_item(
    data: MenuItemCreate,
    repo: Annotated[MenuRepository, Depends(get_menu_repository)],
    current_user: ManagerUser,
) -> MenuItemResponse:
    """Create a new menu item. Requires manager or owner role."""
    # Verify category exists
    category = await repo.get_category_by_id(data.category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category not found",
        )

    item = MenuItem(
        category_id=data.category_id,
        name=data.name,
        description=data.description,
        price=data.price,
        image_url=data.image_url,
        display_order=data.display_order,
        is_available=data.is_available,
        calories=data.calories,
        allergens=data.allergens,
        tags=data.tags,
    )
    item = await repo.create_item(item)

    return MenuItemResponse(
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


@admin_router.put(
    "/items/{item_id}",
    response_model=MenuItemResponse,
    summary="Update menu item",
)
async def update_item(
    item_id: int,
    data: MenuItemUpdate,
    repo: Annotated[MenuRepository, Depends(get_menu_repository)],
    current_user: ManagerUser,
) -> MenuItemResponse:
    """Update a menu item. Requires manager or owner role."""
    item = await repo.get_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    # Update fields
    if data.name is not None:
        item.name = data.name
    if data.description is not None:
        item.description = data.description
    if data.price is not None:
        item.price = data.price
    if data.image_url is not None:
        item.image_url = data.image_url
    if data.display_order is not None:
        item.display_order = data.display_order
    if data.is_available is not None:
        item.is_available = data.is_available
    if data.calories is not None:
        item.calories = data.calories
    if data.allergens is not None:
        item.allergens = data.allergens
    if data.tags is not None:
        item.tags = data.tags
    if data.category_id is not None:
        # Verify new category exists
        category = await repo.get_category_by_id(data.category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category not found",
            )
        item.category_id = data.category_id

    item = await repo.update_item(item)

    return MenuItemResponse(
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


@admin_router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete menu item",
)
async def delete_item(
    item_id: int,
    repo: Annotated[MenuRepository, Depends(get_menu_repository)],
    current_user: ManagerUser,
) -> None:
    """Soft delete a menu item. Requires manager or owner role."""
    item = await repo.get_item_by_id(item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    await repo.delete_item(item)


@admin_router.patch(
    "/items/{item_id}/availability",
    response_model=MenuItemResponse,
    summary="Toggle item availability",
)
async def toggle_availability(
    item_id: int,
    is_available: bool,
    repo: Annotated[MenuRepository, Depends(get_menu_repository)],
    current_user: HostUser,
) -> MenuItemResponse:
    """Toggle item availability (e.g., sold out). Hosts can do this."""
    item = await repo.set_item_availability(item_id, is_available)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )

    return MenuItemResponse(
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
