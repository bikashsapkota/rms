"""
Pytest configuration for the Restaurant Management System.
Provides shared fixtures and test configuration.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """Test client for FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_organization_data():
    """Sample organization data for testing."""
    return {
        "name": "Test Restaurant Corp",
        "organization_type": "chain",
        "subscription_tier": "professional",
        "billing_email": "billing@testcorp.com"
    }


@pytest.fixture
def sample_restaurant_data():
    """Sample restaurant data for testing."""
    return {
        "name": "Downtown Pizzeria",
        "address": {
            "street": "123 Main St",
            "city": "Downtown",
            "state": "CA",
            "zip": "90210"
        },
        "phone": "+1-555-0123",
        "email": "info@downtown.com",
        "settings": {"timezone": "America/Los_Angeles"}
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "email": "admin@restaurant.com",
        "full_name": "John Smith",
        "role": "admin",
        "password": "securepassword123"
    }


@pytest.fixture
def sample_menu_category_data():
    """Sample menu category data for testing."""
    return {
        "name": "Appetizers",
        "description": "Start your meal right",
        "sort_order": 1,
        "is_active": True
    }


@pytest.fixture
def sample_menu_item_data():
    """Sample menu item data for testing."""
    return {
        "name": "Margherita Pizza",
        "description": "Fresh mozzarella and basil",
        "price": "15.99",
        "is_available": True,
        "image_url": "https://example.com/pizza.jpg"
    }