"""
Unit tests for API schemas and validation.
"""

import pytest
from datetime import datetime
from app.modules.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshTokenResponse,
    UserInfo,
    TokenPayload,
)
from app.shared.models.user import UserCreate, UserUpdate


class TestAuthSchemas:
    """Test authentication-related schemas."""

    def test_login_request_valid(self):
        """Test valid login request."""
        login_data = LoginRequest(
            email="test@example.com",
            password="password123"
        )
        
        assert login_data.email == "test@example.com"
        assert login_data.password == "password123"

    def test_login_request_invalid_email(self):
        """Test login request with invalid email."""
        with pytest.raises(ValueError):
            LoginRequest(
                email="invalid-email",
                password="password123"
            )

    def test_login_response_structure(self):
        """Test login response structure."""
        user_data = UserInfo(
            id="test-id",
            email="test@example.com",
            full_name="Test User",
            role="admin",
            organization_id="org-id",
            restaurant_id="restaurant-id",
            organization_name="Test Org",
            restaurant_name="Test Restaurant"
        )
        
        login_response = LoginResponse(
            access_token="test-token",
            token_type="bearer",
            expires_in=3600,
            user=user_data
        )
        
        assert login_response.access_token == "test-token"
        assert login_response.token_type == "bearer"
        assert login_response.expires_in == 3600
        assert login_response.user.email == "test@example.com"

    def test_refresh_token_response(self):
        """Test refresh token response schema."""
        token_response = RefreshTokenResponse(
            access_token="new-token",
            token_type="bearer",
            expires_in=7200
        )
        
        assert token_response.access_token == "new-token"
        assert token_response.token_type == "bearer"
        assert token_response.expires_in == 7200

    def test_user_create_valid(self):
        """Test valid user creation schema."""
        user_create = UserCreate(
            email="newuser@example.com",
            full_name="New User",
            role="staff",
            password="securepassword123"
        )
        
        assert user_create.email == "newuser@example.com"
        assert user_create.full_name == "New User"
        assert user_create.role == "staff"
        assert user_create.password == "securepassword123"

    def test_user_create_defaults(self):
        """Test user creation with default values."""
        user_create = UserCreate(
            email="user@example.com",
            full_name="User Name",
            password="password123"
        )
        
        assert user_create.role == "staff"  # Default role
        assert user_create.restaurant_id is None

    def test_user_create_password_validation(self):
        """Test user creation password validation."""
        with pytest.raises(ValueError):
            UserCreate(
                email="user@example.com",
                full_name="User Name",
                password="short"  # Too short
            )

    def test_user_update_partial(self):
        """Test partial user update schema."""
        user_update = UserUpdate(
            full_name="Updated Name",
            role="admin"
        )
        
        assert user_update.full_name == "Updated Name"
        assert user_update.role == "admin"
        assert user_update.email is None
        assert user_update.password is None

    def test_user_info_structure(self):
        """Test user info schema structure."""
        user_info = UserInfo(
            id="user-id",
            email="user@example.com",
            full_name="User Name",
            role="staff",
            organization_id="org-id",
            restaurant_id="restaurant-id",
            organization_name="Test Org",
            restaurant_name="Test Restaurant"
        )
        
        assert user_info.id == "user-id"
        assert user_info.email == "user@example.com"
        assert user_info.role == "staff"
        assert user_info.organization_name == "Test Org"
        assert user_info.restaurant_name == "Test Restaurant"

    def test_token_payload_structure(self):
        """Test token payload schema."""
        payload = TokenPayload(
            user_id="user-id",
            email="user@example.com",
            organization_id="org-id",
            restaurant_id="restaurant-id",
            role="admin"
        )
        
        assert payload.user_id == "user-id"
        assert payload.email == "user@example.com"
        assert payload.role == "admin"
        assert payload.organization_id == "org-id"

    def test_user_info_no_password(self):
        """Test that user info doesn't expose password."""
        user_info = UserInfo(
            id="user-id",
            email="user@example.com",
            full_name="User Name",
            role="staff",
            organization_id="org-id",
            restaurant_id="restaurant-id",
            organization_name="Test Org",
            restaurant_name="Test Restaurant"
        )
        
        # Should not have password field
        assert not hasattr(user_info, 'password')
        assert not hasattr(user_info, 'password_hash')