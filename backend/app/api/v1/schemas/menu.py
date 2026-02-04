"""Menu API schemas.

REQ-MENU-001: Menu browsing
AC-MENU-001: Guest accesses menu from SMS link
"""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


# ==================== Menu Item Schemas ====================


class MenuItemBase(BaseModel):
    """Base schema for menu item data."""

    name: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=2000)
    price: Decimal = Field(..., ge=0, decimal_places=2)
    image_url: str | None = Field(None, max_length=500)
    display_order: int = Field(default=0)
    is_available: bool = Field(default=True)
    calories: int | None = Field(None, ge=0)
    allergens: str | None = Field(None, max_length=500)
    tags: str | None = Field(None, max_length=200)


class MenuItemCreate(MenuItemBase):
    """Schema for creating a menu item."""

    category_id: int


class MenuItemUpdate(BaseModel):
    """Schema for updating a menu item."""

    name: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = None
    price: Decimal | None = Field(None, ge=0)
    image_url: str | None = None
    display_order: int | None = None
    is_available: bool | None = None
    calories: int | None = None
    allergens: str | None = None
    tags: str | None = None
    category_id: int | None = None


class MenuItemResponse(MenuItemBase):
    """Schema for menu item response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    category_id: int
    is_active: bool
    tags_list: list[str] = Field(default_factory=list)


# ==================== Category Schemas ====================


class MenuCategoryBase(BaseModel):
    """Base schema for menu category."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    display_order: int = Field(default=0)


class MenuCategoryCreate(MenuCategoryBase):
    """Schema for creating a category."""

    pass


class MenuCategoryUpdate(BaseModel):
    """Schema for updating a category."""

    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = None
    display_order: int | None = None


class MenuCategoryResponse(MenuCategoryBase):
    """Schema for category response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool


class MenuCategoryWithItemsResponse(MenuCategoryResponse):
    """Schema for category with nested items.

    REQ-MENU-001: Browse menu by category
    """

    items: list[MenuItemResponse] = Field(default_factory=list)


# ==================== Full Menu Response ====================


class MenuResponse(BaseModel):
    """Full menu response with categories and items.

    AC-MENU-001: Guest accesses menu from SMS link
    """

    categories: list[MenuCategoryWithItemsResponse]
    total_items: int
