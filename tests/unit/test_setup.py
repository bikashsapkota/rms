"""
Unit tests for restaurant setup functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch
from app.core.setup import RestaurantSetupService, TenantContextManager
from app.modules.setup.schemas import RestaurantSetupRequest, AdminUserCreate


class TestRestaurantSetupService:
    """Test restaurant setup service."""

    @pytest.mark.asyncio
    async def test_create_restaurant_setup_success(self):
        """Test successful restaurant setup."""
        # Mock database session
        mock_session = AsyncMock()
        
        # Mock models
        with patch('app.core.setup.Organization') as mock_org, \
             patch('app.core.setup.Restaurant') as mock_restaurant, \
             patch('app.core.setup.User') as mock_user:
            
            # Set up mock instances
            mock_org_instance = AsyncMock()
            mock_org_instance.id = "org-123"
            mock_org_instance.name = "Test Restaurant Organization"
            mock_org.return_value = mock_org_instance
            
            mock_restaurant_instance = AsyncMock()
            mock_restaurant_instance.id = "rest-123"
            mock_restaurant_instance.name = "Test Restaurant"
            mock_restaurant_instance.organization_id = "org-123"
            mock_restaurant.return_value = mock_restaurant_instance
            
            mock_user_instance = AsyncMock()
            mock_user_instance.id = "user-123"
            mock_user_instance.email = "admin@test.com"
            mock_user_instance.full_name = "Test Admin"
            mock_user_instance.role = "admin"
            mock_user.return_value = mock_user_instance
            
            # Test data
            restaurant_data = {
                "name": "Test Restaurant",
                "address": {"street": "123 Main St"},
                "phone": "+1-555-0123",
                "email": "info@test.com",
                "settings": {"timezone": "UTC"}
            }
            
            admin_user_data = {
                "email": "admin@test.com",
                "full_name": "Test Admin",
                "password": "password123"
            }
            
            # Execute setup
            setup_service = RestaurantSetupService(mock_session)
            result = await setup_service.create_restaurant_setup(
                restaurant_data, admin_user_data
            )
            
            # Verify result structure
            assert "organization" in result
            assert "restaurant" in result
            assert "admin_user" in result
            
            assert result["organization"]["name"] == "Test Restaurant Organization"
            assert result["restaurant"]["name"] == "Test Restaurant"
            assert result["admin_user"]["email"] == "admin@test.com"
            assert result["admin_user"]["role"] == "admin"
            
            # Verify database operations
            assert mock_session.add.call_count == 3  # org, restaurant, user
            assert mock_session.commit.call_count == 3
            assert mock_session.refresh.call_count == 3


class TestTenantContextManager:
    """Test tenant context management."""

    def test_set_and_get_context(self):
        """Test setting and getting tenant context."""
        context_manager = TenantContextManager()
        
        org_id = "org-123"
        restaurant_id = "rest-123"
        
        context_manager.set_context(org_id, restaurant_id)
        
        assert str(context_manager.get_organization_id()) == org_id
        assert str(context_manager.get_restaurant_id()) == restaurant_id

    def test_clear_context(self):
        """Test clearing tenant context."""
        context_manager = TenantContextManager()
        
        context_manager.set_context("org-123", "rest-123")
        context_manager.clear_context()
        
        # Should return default values after clearing
        assert context_manager.get_organization_id() is not None
        assert context_manager.get_restaurant_id() is not None

    def test_default_context(self):
        """Test default context values."""
        context_manager = TenantContextManager()
        
        # Should have default values when no context is set
        org_id = context_manager.get_organization_id()
        restaurant_id = context_manager.get_restaurant_id()
        
        assert org_id is not None
        assert restaurant_id is not None


class TestSetupSchemas:
    """Test setup request/response schemas."""

    def test_admin_user_create_valid(self):
        """Test valid admin user creation data."""
        admin_data = AdminUserCreate(
            email="admin@test.com",
            full_name="Test Administrator",
            password="securepassword123"
        )
        
        assert admin_data.email == "admin@test.com"
        assert admin_data.full_name == "Test Administrator"
        assert admin_data.password == "securepassword123"

    def test_admin_user_create_invalid_email(self):
        """Test admin user creation with invalid email."""
        with pytest.raises(ValueError):
            AdminUserCreate(
                email="invalid-email",
                full_name="Test Admin",
                password="password123"
            )

    def test_admin_user_create_short_password(self):
        """Test admin user creation with short password."""
        with pytest.raises(ValueError):
            AdminUserCreate(
                email="admin@test.com",
                full_name="Test Admin",
                password="short"  # Too short
            )

    def test_restaurant_setup_request_valid(self):
        """Test valid restaurant setup request."""
        admin_user = AdminUserCreate(
            email="admin@test.com",
            full_name="Test Admin",
            password="password123"
        )
        
        setup_request = RestaurantSetupRequest(
            restaurant_name="Test Restaurant",
            address={
                "street": "123 Main St",
                "city": "Test City",
                "state": "TS",
                "zip": "12345"
            },
            phone="+1-555-0123",
            email="info@test.com",
            settings={"timezone": "America/New_York"},
            admin_user=admin_user
        )
        
        assert setup_request.restaurant_name == "Test Restaurant"
        assert setup_request.address["street"] == "123 Main St"
        assert setup_request.phone == "+1-555-0123"
        assert setup_request.email == "info@test.com"
        assert setup_request.settings["timezone"] == "America/New_York"
        assert setup_request.admin_user.email == "admin@test.com"

    def test_restaurant_setup_request_minimal(self):
        """Test minimal restaurant setup request."""
        admin_user = AdminUserCreate(
            email="admin@test.com",
            full_name="Test Admin",
            password="password123"
        )
        
        setup_request = RestaurantSetupRequest(
            restaurant_name="Minimal Restaurant",
            admin_user=admin_user
        )
        
        assert setup_request.restaurant_name == "Minimal Restaurant"
        assert setup_request.address is None
        assert setup_request.phone is None
        assert setup_request.email is None
        assert setup_request.settings == {}
        assert setup_request.admin_user.email == "admin@test.com"