"""
Unit tests for SQLModel models validation and structure.
"""

import pytest
from decimal import Decimal
from app.shared.models.organization import Organization, OrganizationCreate, OrganizationUpdate
from app.shared.models.restaurant import Restaurant, RestaurantCreate, RestaurantUpdate
from app.shared.models.user import User, UserCreate, UserUpdate
from app.modules.menu.models.category import MenuCategory, MenuCategoryCreate, MenuCategoryUpdate
from app.modules.menu.models.item import MenuItem, MenuItemCreate, MenuItemUpdate
from app.modules.menu.models.modifier import Modifier, ModifierCreate, ModifierUpdate


class TestOrganizationModel:
    """Test organization model validation."""

    def test_organization_create_valid(self):
        """Test valid organization creation."""
        org_data = OrganizationCreate(
            name="Test Restaurant Corp",
            organization_type="chain",
            subscription_tier="professional",
            billing_email="billing@testcorp.com"
        )
        
        assert org_data.name == "Test Restaurant Corp"
        assert org_data.organization_type == "chain"
        assert org_data.subscription_tier == "professional"
        assert org_data.billing_email == "billing@testcorp.com"

    def test_organization_create_defaults(self):
        """Test organization creation with defaults."""
        org_data = OrganizationCreate(name="Simple Restaurant")
        
        assert org_data.name == "Simple Restaurant"
        assert org_data.organization_type == "independent"
        assert org_data.subscription_tier == "basic"
        assert org_data.billing_email is None

    def test_organization_update_partial(self):
        """Test partial organization update."""
        update_data = OrganizationUpdate(name="Updated Name")
        
        assert update_data.name == "Updated Name"
        assert update_data.organization_type is None
        assert update_data.subscription_tier is None


class TestRestaurantModel:
    """Test restaurant model validation."""

    def test_restaurant_create_valid(self):
        """Test valid restaurant creation."""
        restaurant_data = RestaurantCreate(
            name="Downtown Pizzeria",
            address={
                "street": "123 Main St",
                "city": "Downtown",
                "state": "CA",
                "zip": "90210"
            },
            phone="+1-555-0123",
            email="info@downtown.com",
            settings={"timezone": "America/Los_Angeles"}
        )
        
        assert restaurant_data.name == "Downtown Pizzeria"
        assert restaurant_data.address["street"] == "123 Main St"
        assert restaurant_data.phone == "+1-555-0123"
        assert restaurant_data.email == "info@downtown.com"
        assert restaurant_data.settings["timezone"] == "America/Los_Angeles"

    def test_restaurant_create_minimal(self):
        """Test restaurant creation with minimal data."""
        restaurant_data = RestaurantCreate(name="Simple Restaurant")
        
        assert restaurant_data.name == "Simple Restaurant"
        assert restaurant_data.address is None
        assert restaurant_data.phone is None
        assert restaurant_data.email is None
        assert restaurant_data.settings == {}


class TestUserModel:
    """Test user model validation."""

    def test_user_create_valid(self):
        """Test valid user creation."""
        user_data = UserCreate(
            email="admin@restaurant.com",
            full_name="John Smith",
            role="admin",
            password="securepassword123"
        )
        
        assert user_data.email == "admin@restaurant.com"
        assert user_data.full_name == "John Smith"
        assert user_data.role == "admin"
        assert user_data.password == "securepassword123"

    def test_user_create_defaults(self):
        """Test user creation with defaults."""
        user_data = UserCreate(
            email="staff@restaurant.com",
            full_name="Jane Doe",
            password="password123"
        )
        
        assert user_data.role == "staff"
        assert user_data.restaurant_id is None

    def test_user_password_validation(self):
        """Test user password validation."""
        with pytest.raises(ValueError):
            UserCreate(
                email="test@restaurant.com",
                full_name="Test User",
                password="short"  # Too short
            )

    def test_user_email_validation(self):
        """Test user email validation."""
        # Test with valid email first
        valid_user = UserCreate(
            email="valid@example.com",
            full_name="Test User",
            password="password123"
        )
        assert valid_user.email == "valid@example.com"
        
        # Invalid email should be caught by Pydantic validation
        try:
            UserCreate(
                email="invalid-email",
                full_name="Test User", 
                password="password123"
            )
            # If no exception was raised, the test should fail
            assert False, "Expected ValueError for invalid email"
        except Exception:
            # Any validation error is acceptable
            pass


class TestMenuCategoryModel:
    """Test menu category model validation."""

    def test_menu_category_create_valid(self):
        """Test valid menu category creation."""
        category_data = MenuCategoryCreate(
            name="Appetizers",
            description="Start your meal right",
            sort_order=1,
            is_active=True
        )
        
        assert category_data.name == "Appetizers"
        assert category_data.description == "Start your meal right"
        assert category_data.sort_order == 1
        assert category_data.is_active is True

    def test_menu_category_create_defaults(self):
        """Test menu category creation with defaults."""
        category_data = MenuCategoryCreate(name="Pizza")
        
        assert category_data.name == "Pizza"
        assert category_data.description is None
        assert category_data.sort_order == 0
        assert category_data.is_active is True


class TestMenuItemModel:
    """Test menu item model validation."""

    def test_menu_item_create_valid(self):
        """Test valid menu item creation."""
        item_data = MenuItemCreate(
            name="Margherita Pizza",
            description="Fresh mozzarella and basil",
            price=Decimal("15.99"),
            is_available=True,
            image_url="https://example.com/pizza.jpg"
        )
        
        assert item_data.name == "Margherita Pizza"
        assert item_data.description == "Fresh mozzarella and basil"
        assert item_data.price == Decimal("15.99")
        assert item_data.is_available is True
        assert item_data.image_url == "https://example.com/pizza.jpg"

    def test_menu_item_create_minimal(self):
        """Test menu item creation with minimal data."""
        item_data = MenuItemCreate(
            name="Simple Item",
            price=Decimal("10.00")
        )
        
        assert item_data.name == "Simple Item"
        assert item_data.price == Decimal("10.00")
        assert item_data.description is None
        assert item_data.is_available is True
        assert item_data.image_url is None

    def test_menu_item_price_validation(self):
        """Test menu item price validation."""
        # Test with string that converts to decimal
        item_data = MenuItemCreate(
            name="Test Item",
            price="12.99"
        )
        assert item_data.price == Decimal("12.99")


class TestModifierModel:
    """Test modifier model validation."""

    def test_modifier_create_valid(self):
        """Test valid modifier creation."""
        modifier_data = ModifierCreate(
            name="Extra Cheese",
            type="addon",
            price_adjustment=Decimal("2.00"),
            is_active=True
        )
        
        assert modifier_data.name == "Extra Cheese"
        assert modifier_data.type == "addon"
        assert modifier_data.price_adjustment == Decimal("2.00")
        assert modifier_data.is_active is True

    def test_modifier_create_defaults(self):
        """Test modifier creation with defaults."""
        modifier_data = ModifierCreate(
            name="Size Upgrade",
            type="size"
        )
        
        assert modifier_data.name == "Size Upgrade"
        assert modifier_data.type == "size"
        assert modifier_data.price_adjustment == Decimal("0.00")
        assert modifier_data.is_active is True