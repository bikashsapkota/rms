"""
Integration tests for authentication API endpoints with mocked data.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


class TestAuthAPIMocked:
    """Test authentication API endpoints with mocked services."""

    def test_health_endpoint(self, client: TestClient):
        """Test health endpoint (no auth required)."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint (no auth required)."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "Restaurant Management System" in data["message"]

    @patch('app.modules.auth.service.AuthService.authenticate_user')
    def test_login_success_mocked(self, mock_authenticate, client: TestClient):
        """Test successful login with mocked service."""
        # Mock the authentication service response
        mock_user = {
            "id": "test-user-id",
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "admin",
            "organization_id": "test-org-id",
            "restaurant_id": "test-restaurant-id",
            "is_active": True
        }
        
        mock_authenticate.return_value = {
            "access_token": "test-access-token",
            "token_type": "bearer",
            "expires_in": 3600,
            "user": mock_user
        }
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["email"] == "test@example.com"

    @patch('app.modules.auth.service.AuthService.authenticate_user')
    def test_login_invalid_credentials_mocked(self, mock_authenticate, client: TestClient):
        """Test login with invalid credentials."""
        from fastapi import HTTPException
        
        # Mock authentication failure
        mock_authenticate.side_effect = HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
        
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "wrong@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_login_missing_fields(self, client: TestClient):
        """Test login with missing fields."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com"
                # Missing password
            }
        )
        
        assert response.status_code == 422  # Validation error

    def test_login_invalid_email_format(self, client: TestClient):
        """Test login with invalid email format."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "invalid-email-format",
                "password": "password123"
            }
        )
        
        assert response.status_code == 422  # Validation error

    @patch('app.shared.auth.deps.get_current_user')
    def test_get_current_user_mocked(self, mock_get_user, client: TestClient):
        """Test getting current user with mocked dependency."""
        # Mock the current user
        mock_user = {
            "id": "test-user-id",
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "admin",
            "organization_id": "test-org-id",
            "restaurant_id": "test-restaurant-id",
            "is_active": True
        }
        
        mock_get_user.return_value = mock_user
        
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["role"] == "admin"

    def test_get_current_user_no_token(self, client: TestClient):
        """Test getting current user without token."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client: TestClient):
        """Test getting current user with invalid token."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401

    @patch('app.shared.auth.deps.get_current_user')
    @patch('app.shared.auth.security.create_user_access_token')
    def test_refresh_token_mocked(self, mock_create_token, mock_get_user, client: TestClient):
        """Test token refresh with mocked dependencies."""
        # Mock current user
        mock_user = {
            "id": "test-user-id",
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "admin",
            "organization_id": "test-org-id",
            "restaurant_id": "test-restaurant-id",
            "is_active": True
        }
        
        mock_get_user.return_value = mock_user
        mock_create_token.return_value = "new-access-token"
        
        response = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": "Bearer old-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @patch('app.shared.auth.deps.get_current_user')
    def test_logout_mocked(self, mock_get_user, client: TestClient):
        """Test logout with mocked user."""
        mock_user = {"id": "test-user-id", "email": "test@example.com"}
        mock_get_user.return_value = mock_user
        
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data

    def test_protected_endpoint_requires_auth(self, client: TestClient):
        """Test that protected endpoints require authentication."""
        # Try to access user management without auth
        response = client.get("/api/v1/users/")
        assert response.status_code == 401

    @patch('app.shared.auth.deps.get_current_user')
    @patch('app.shared.auth.deps.require_admin')
    @patch('app.modules.auth.service.AuthService.get_users')
    def test_list_users_admin_mocked(self, mock_get_users, mock_require_admin, mock_get_user, client: TestClient):
        """Test listing users as admin with mocked services."""
        # Mock admin user
        admin_user = {
            "id": "admin-id",
            "email": "admin@example.com",
            "role": "admin",
            "organization_id": "org-id",
            "restaurant_id": "restaurant-id"
        }
        
        mock_get_user.return_value = admin_user
        mock_require_admin.return_value = admin_user
        mock_get_users.return_value = [admin_user]
        
        response = client.get(
            "/api/v1/users/",
            headers={"Authorization": "Bearer admin-token"}
        )
        
        assert response.status_code == 200
        users = response.json()
        assert isinstance(users, list)

    @patch('app.shared.auth.deps.get_current_user')
    @patch('app.shared.auth.deps.require_admin')
    @patch('app.modules.auth.service.AuthService.create_user')
    def test_create_user_admin_mocked(self, mock_create_user, mock_require_admin, mock_get_user, client: TestClient):
        """Test creating user as admin with mocked services."""
        # Mock admin user
        admin_user = {
            "id": "admin-id",
            "email": "admin@example.com",
            "role": "admin"
        }
        
        # Mock created user
        created_user = {
            "id": "new-user-id",
            "email": "newuser@example.com",
            "full_name": "New User",
            "role": "staff",
            "organization_id": "org-id",
            "restaurant_id": "restaurant-id",
            "is_active": True
        }
        
        mock_get_user.return_value = admin_user
        mock_require_admin.return_value = admin_user
        mock_create_user.return_value = created_user
        
        response = client.post(
            "/api/v1/users/",
            headers={"Authorization": "Bearer admin-token"},
            json={
                "email": "newuser@example.com",
                "full_name": "New User",
                "role": "staff",
                "password": "password123"
            }
        )
        
        assert response.status_code == 200
        user_data = response.json()
        assert user_data["email"] == "newuser@example.com"
        assert user_data["role"] == "staff"