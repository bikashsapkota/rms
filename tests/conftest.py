"""
Test configuration and fixtures.
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from httpx import AsyncClient
from fastapi.testclient import TestClient
from app.main import app
from app.shared.database.session import get_session
from app.shared.models.organization import Organization
from app.shared.models.restaurant import Restaurant
from app.shared.models.user import User
from app.modules.menu.models.category import MenuCategory
from app.modules.menu.models.item import MenuItem
from app.shared.auth.security import get_password_hash, create_user_access_token
from decimal import Decimal


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Create FastAPI test client without database dependency."""
    return TestClient(app)


@pytest.fixture
def mock_session():
    """Mock database session for testing without actual database."""
    return AsyncMock(spec=AsyncSession)


def auth_headers(token: str) -> dict:
    """Helper function to create auth headers."""
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture 
def sample_auth_headers():
    """Sample authentication headers."""
    return {
        "Authorization": "Bearer test-token",
        "Content-Type": "application/json"
    }


@pytest.fixture
def sample_jwt_payload():
    """Sample JWT payload for testing."""
    return {
        "user_id": "test-user-id",
        "email": "test@example.com", 
        "organization_id": "test-org-id",
        "restaurant_id": "test-restaurant-id",
        "role": "admin"
    }


# Database-dependent fixtures for integration tests
@pytest.fixture
async def test_organization():
    """Mock test organization for integration tests."""
    from app.shared.models.organization import Organization
    return Organization(
        id="test-org-id",
        name="Test Pizza Restaurant",
        organization_type="independent",
        subscription_tier="basic",
        billing_email="billing@testpizza.com",
        is_active=True,
    )


@pytest.fixture
async def test_restaurant(test_organization):
    """Mock test restaurant for integration tests."""
    from app.shared.models.restaurant import Restaurant
    return Restaurant(
        id="test-restaurant-id",
        name="Test Pizza Downtown",
        organization_id=test_organization.id,
        address={
            "street": "123 Main St",
            "city": "Downtown",
            "state": "CA",
            "zip": "90210",
            "country": "US"
        },
        phone="+1-555-0123",
        email="info@testpizza.com",
        settings={
            "timezone": "America/Los_Angeles",
            "currency": "USD",
            "tax_rate": 8.25
        },
        is_active=True,
    )


@pytest.fixture
async def test_admin_user(test_organization, test_restaurant):
    """Mock test admin user for integration tests."""
    from app.shared.models.user import User
    from app.shared.auth.security import get_password_hash
    return User(
        id="test-admin-id",
        email="admin@testpizza.com",
        full_name="Test Admin",
        role="admin",
        password_hash=get_password_hash("testpassword123"),
        organization_id=test_organization.id,
        restaurant_id=test_restaurant.id,
        is_active=True,
    )


@pytest.fixture
async def test_staff_user(test_organization, test_restaurant):
    """Mock test staff user for integration tests."""
    from app.shared.models.user import User
    from app.shared.auth.security import get_password_hash
    return User(
        id="test-staff-id",
        email="staff@testpizza.com",
        full_name="Test Staff",
        role="staff",
        password_hash=get_password_hash("testpassword123"),
        organization_id=test_organization.id,
        restaurant_id=test_restaurant.id,
        is_active=True,
    )


@pytest.fixture
async def admin_token(test_admin_user):
    """Create admin access token."""
    from app.shared.auth.security import create_user_access_token
    return create_user_access_token(
        user_id=str(test_admin_user.id),
        email=test_admin_user.email,
        organization_id=str(test_admin_user.organization_id),
        restaurant_id=str(test_admin_user.restaurant_id),
        role=test_admin_user.role,
    )


@pytest.fixture
async def staff_token(test_staff_user):
    """Create staff access token."""
    from app.shared.auth.security import create_user_access_token
    return create_user_access_token(
        user_id=str(test_staff_user.id),
        email=test_staff_user.email,
        organization_id=str(test_staff_user.organization_id),
        restaurant_id=str(test_staff_user.restaurant_id),
        role=test_staff_user.role,
    )


@pytest.fixture
async def test_menu_category(test_organization, test_restaurant):
    """Mock test menu category for integration tests."""
    from app.modules.menu.models.category import MenuCategory
    return MenuCategory(
        id="test-category-id",
        name="Pizza",
        description="Delicious wood-fired pizzas",
        sort_order=1,
        organization_id=test_organization.id,
        restaurant_id=test_restaurant.id,
        is_active=True,
    )


@pytest.fixture
async def test_menu_item(test_organization, test_restaurant, test_menu_category):
    """Mock test menu item for integration tests."""
    from app.modules.menu.models.item import MenuItem
    from decimal import Decimal
    return MenuItem(
        id="test-item-id",
        name="Margherita Pizza",
        description="Fresh mozzarella, tomato sauce, and basil",
        price=Decimal("15.99"),
        category_id=test_menu_category.id,
        organization_id=test_organization.id,
        restaurant_id=test_restaurant.id,
        is_available=True,
    )