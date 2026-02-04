"""Unit tests for Menu entities.

REQ-MENU-001: Menu browsing
REQ-MENU-002: Star items
AC-MENU-005: Data model for menu_items, guest_interests
"""

from decimal import Decimal

import pytest

from app.domain.entities import (
    GuestInterest,
    MenuCategory,
    MenuItem,
)


class TestMenuCategory:
    """Tests for MenuCategory entity."""

    def test_create_category(self) -> None:
        """Should create category with required fields."""
        category = MenuCategory(name="Appetizers")

        assert category.name == "Appetizers"
        assert category.description is None
        assert category.display_order == 0
        assert category.is_active is True

    def test_create_category_with_all_fields(self) -> None:
        """Should create category with all fields."""
        category = MenuCategory(
            name="Main Courses",
            description="Our signature dishes",
            display_order=2,
            is_active=True,
        )

        assert category.name == "Main Courses"
        assert category.description == "Our signature dishes"
        assert category.display_order == 2
        assert category.is_active is True

    def test_category_repr(self) -> None:
        """Should have readable repr."""
        category = MenuCategory(name="Desserts")
        category.id = 1

        assert "MenuCategory" in repr(category)
        assert "Desserts" in repr(category)


class TestMenuItem:
    """Tests for MenuItem entity."""

    def test_create_item_minimal(self) -> None:
        """Should create item with required fields."""
        item = MenuItem(
            category_id=1,
            name="Burger",
            price=Decimal("12.99"),
        )

        assert item.category_id == 1
        assert item.name == "Burger"
        assert item.price == Decimal("12.99")
        assert item.description is None
        assert item.image_url is None
        assert item.display_order == 0
        assert item.is_available is True
        assert item.is_active is True

    def test_create_item_with_all_fields(self) -> None:
        """Should create item with all fields."""
        item = MenuItem(
            category_id=1,
            name="Classic Cheeseburger",
            price=Decimal("14.99"),
            description="Angus beef patty with aged cheddar",
            image_url="https://example.com/burger.jpg",
            display_order=1,
            is_available=True,
            is_active=True,
            calories=850,
            allergens="dairy,gluten",
            tags="popular,chef-special",
        )

        assert item.name == "Classic Cheeseburger"
        assert item.price == Decimal("14.99")
        assert item.description == "Angus beef patty with aged cheddar"
        assert item.image_url == "https://example.com/burger.jpg"
        assert item.calories == 850
        assert item.allergens == "dairy,gluten"
        assert item.tags == "popular,chef-special"

    def test_tags_list_property(self) -> None:
        """Should parse tags into list."""
        item = MenuItem(
            category_id=1,
            name="Salad",
            price=Decimal("9.99"),
            tags="vegan, gluten-free, healthy",
        )

        assert item.tags_list == ["vegan", "gluten-free", "healthy"]

    def test_tags_list_empty(self) -> None:
        """Should return empty list when no tags."""
        item = MenuItem(
            category_id=1,
            name="Salad",
            price=Decimal("9.99"),
        )

        assert item.tags_list == []

    def test_item_repr(self) -> None:
        """Should have readable repr."""
        item = MenuItem(
            category_id=1,
            name="Pizza",
            price=Decimal("15.99"),
        )
        item.id = 1

        assert "MenuItem" in repr(item)
        assert "Pizza" in repr(item)
        assert "15.99" in repr(item)


class TestGuestInterest:
    """Tests for GuestInterest entity.

    AC-MENU-002: Star items stores to guest/waitlist entry
    AC-MENU-003: Soft pre-order stored
    """

    def test_create_interest_starred(self) -> None:
        """AC-MENU-002: Should create starred interest."""
        interest = GuestInterest(
            waitlist_entry_id=1,
            menu_item_id=5,
            is_starred=True,
        )

        assert interest.waitlist_entry_id == 1
        assert interest.menu_item_id == 5
        assert interest.is_starred is True
        assert interest.is_preorder is False
        assert interest.quantity == 1

    def test_create_interest_preorder(self) -> None:
        """AC-MENU-003: Should create pre-order interest."""
        interest = GuestInterest(
            waitlist_entry_id=1,
            menu_item_id=5,
            is_starred=True,
            is_preorder=True,
            quantity=2,
        )

        assert interest.is_starred is True
        assert interest.is_preorder is True
        assert interest.quantity == 2

    def test_interest_defaults(self) -> None:
        """Should have sensible defaults."""
        interest = GuestInterest(
            waitlist_entry_id=1,
            menu_item_id=5,
        )

        assert interest.is_starred is False
        assert interest.is_preorder is False
        assert interest.quantity == 1

    def test_interest_repr(self) -> None:
        """Should have readable repr."""
        interest = GuestInterest(
            waitlist_entry_id=10,
            menu_item_id=20,
            is_starred=True,
            is_preorder=False,
        )
        interest.id = 1

        repr_str = repr(interest)
        assert "GuestInterest" in repr_str
        assert "entry=10" in repr_str
        assert "item=20" in repr_str
        assert "starred=True" in repr_str
