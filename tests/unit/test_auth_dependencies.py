"""
Unit tests for authentication dependencies and utilities.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from app.shared.auth.deps import (
    get_current_user_token,
    get_current_user,
    get_current_active_user,
    require_admin,
    require_staff,
    TenantContext,
)
from app.shared.models.user import User


class TestAuthDependencies:
    """Test authentication dependency functions."""

    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        """Test getting current user with valid token."""
        # Mock database session
        mock_session = AsyncMock()
        
        # Mock user
        mock_user = User(
            id="test-user-id",
            email="test@example.com",
            full_name="Test User",
            role="admin",
            password_hash="hashed_password",
            organization_id="test-org-id",
            restaurant_id="test-restaurant-id",
            is_active=True
        )
        
        # Mock session.get to return the user
        mock_session.get.return_value = mock_user
        
        # Mock the decode function
        with patch('app.shared.auth.deps.decode_user_token') as mock_decode:
            mock_decode.return_value = {
                "user_id": "test-user-id",
                "email": "test@example.com",
                "organization_id": "test-org-id",
                "restaurant_id": "test-restaurant-id",
                "role": "admin"
            }
            
            # Test the function
            result = await get_current_user("Bearer valid-token", mock_session)
            
            assert result == mock_user
            mock_decode.assert_called_once_with("valid-token")
            mock_session.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_token(self):
        """Test getting current user with invalid token."""
        mock_session = AsyncMock()
        
        with patch('app.shared.auth.deps.decode_user_token') as mock_decode:
            mock_decode.return_value = None
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("Bearer invalid-token", mock_session)
            
            assert exc_info.value.status_code == 401
            assert "Invalid authentication credentials" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_get_current_user_inactive_user(self):
        """Test getting current user when user is inactive."""
        mock_session = AsyncMock()
        
        # Mock inactive user
        mock_user = User(
            id="test-user-id",
            email="test@example.com",
            full_name="Test User",
            role="admin",
            password_hash="hashed_password",
            organization_id="test-org-id",
            restaurant_id="test-restaurant-id",
            is_active=False  # Inactive user
        )
        
        mock_session.get.return_value = mock_user
        
        with patch('app.shared.auth.deps.decode_user_token') as mock_decode:
            mock_decode.return_value = {
                "user_id": "test-user-id",
                "email": "test@example.com",
                "organization_id": "test-org-id",
                "restaurant_id": "test-restaurant-id",
                "role": "admin"
            }
            
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("Bearer valid-token", mock_session)
            
            assert exc_info.value.status_code == 401
            assert "Inactive user" in str(exc_info.value.detail)

    def test_require_admin_with_admin_user(self):
        """Test require_admin with admin user."""
        admin_user = User(
            id="admin-id",
            email="admin@test.com",
            full_name="Admin User",
            role="admin",
            password_hash="hashed",
            organization_id="org-id",
            restaurant_id="restaurant-id",
            is_active=True
        )
        
        # Should not raise exception
        result = require_admin(admin_user)
        assert result == admin_user

    def test_require_admin_with_non_admin_user(self):
        """Test require_admin with non-admin user."""
        staff_user = User(
            id="staff-id",
            email="staff@test.com",
            full_name="Staff User",
            role="staff",
            password_hash="hashed",
            organization_id="org-id",
            restaurant_id="restaurant-id",
            is_active=True
        )
        
        with pytest.raises(HTTPException) as exc_info:
            require_admin(staff_user)
        
        assert exc_info.value.status_code == 403
        assert "Admin access required" in str(exc_info.value.detail)

    def test_require_staff_with_admin(self):
        """Test require_staff with admin user."""
        admin_user = User(
            id="admin-id",
            email="admin@test.com",
            full_name="Admin User",
            role="admin",
            password_hash="hashed",
            organization_id="org-id",
            restaurant_id="restaurant-id",
            is_active=True
        )
        
        result = require_staff(admin_user)
        assert result == admin_user

    def test_require_staff_with_staff(self):
        """Test require_staff with staff user."""
        staff_user = User(
            id="staff-id",
            email="staff@test.com",
            full_name="Staff User",
            role="staff",
            password_hash="hashed",
            organization_id="org-id",
            restaurant_id="restaurant-id",
            is_active=True
        )
        
        result = require_staff(staff_user)
        assert result == staff_user

    def test_require_staff_with_customer(self):
        """Test require_staff with customer user."""
        customer_user = User(
            id="customer-id",
            email="customer@test.com",
            full_name="Customer User",
            role="customer",
            password_hash="hashed",
            organization_id="org-id",
            restaurant_id="restaurant-id",
            is_active=True
        )
        
        with pytest.raises(HTTPException) as exc_info:
            require_staff(customer_user)
        
        assert exc_info.value.status_code == 403
        assert "Insufficient permissions" in str(exc_info.value.detail)

    def test_tenant_context_creation(self):
        """Test creating tenant context."""
        from app.shared.models.organization import Organization
        from app.shared.models.restaurant import Restaurant
        
        user = User(
            id="user-id",
            email="user@test.com",
            full_name="Test User",
            role="admin",
            password_hash="hashed",
            organization_id="org-id",
            restaurant_id="restaurant-id",
            is_active=True
        )
        
        org = Organization(
            id="org-id",
            name="Test Org",
            organization_type="independent",
            subscription_tier="basic",
            is_active=True
        )
        
        restaurant = Restaurant(
            id="restaurant-id",
            name="Test Restaurant",
            organization_id="org-id",
            is_active=True
        )
        
        context = TenantContext(user=user, organization=org, restaurant=restaurant)
        
        assert context.organization_id == "org-id"
        assert context.restaurant_id == "restaurant-id"
        assert context.user == user

    def test_tenant_context_no_restaurant(self):
        """Test tenant context without restaurant."""
        from app.shared.models.organization import Organization
        
        user = User(
            id="user-id",
            email="user@test.com",
            full_name="Test User",
            role="admin",
            password_hash="hashed",
            organization_id="org-id",
            restaurant_id=None,
            is_active=True
        )
        
        org = Organization(
            id="org-id",
            name="Test Org",
            organization_type="independent",
            subscription_tier="basic",
            is_active=True
        )
        
        context = TenantContext(user=user, organization=org, restaurant=None)
        
        assert context.organization_id == "org-id"
        assert context.restaurant_id is None