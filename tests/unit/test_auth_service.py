"""
Unit tests for authentication service functionality.
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
from app.modules.auth.service import AuthService
from app.shared.models.user import User
from uuid import uuid4


class TestAuthService:
    """Test authentication service functionality."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock()
        self.auth_service = AuthService(self.mock_session)
        self.test_user_id = uuid4()
        self.test_org_id = uuid4()
        self.test_restaurant_id = uuid4()

    @pytest.mark.asyncio
    async def test_create_user_success(self):
        """Test successful user creation."""
        user_data = {
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "password123",
            "role": "staff"
        }
        
        with patch('app.modules.auth.service.get_password_hash') as mock_hash:
            mock_hash.return_value = "hashed_password"
            
            # Mock session operations
            self.mock_session.add = AsyncMock()
            self.mock_session.commit = AsyncMock()
            self.mock_session.refresh = AsyncMock()
            
            created_user = await self.auth_service.create_user(
                user_data, self.test_org_id, self.test_restaurant_id
            )
            
            # Verify user creation process
            self.mock_session.add.assert_called_once()
            self.mock_session.commit.assert_called_once()
            mock_hash.assert_called_once_with("password123")

    @pytest.mark.asyncio
    async def test_authenticate_user_success(self):
        """Test successful user authentication."""
        mock_user = User(
            id=self.test_user_id,
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password",
            role="staff",
            organization_id=self.test_org_id,
            restaurant_id=self.test_restaurant_id,
            is_active=True
        )
        
        with patch('app.modules.auth.service.verify_password') as mock_verify:
            mock_verify.return_value = True
            
            # Mock database query
            mock_result = AsyncMock()
            mock_result.first.return_value = mock_user
            self.mock_session.exec.return_value = mock_result
            
            authenticated_user = await self.auth_service.authenticate_user(
                "test@example.com", "password123"
            )
            
            assert authenticated_user == mock_user
            mock_verify.assert_called_once_with("password123", "hashed_password")

    @pytest.mark.asyncio
    async def test_authenticate_user_invalid_password(self):
        """Test authentication with invalid password."""
        mock_user = User(
            id=self.test_user_id,
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password",
            role="staff",
            organization_id=self.test_org_id,
            restaurant_id=self.test_restaurant_id,
            is_active=True
        )
        
        with patch('app.modules.auth.service.verify_password') as mock_verify:
            mock_verify.return_value = False
            
            # Mock database query
            mock_result = AsyncMock()
            mock_result.first.return_value = mock_user
            self.mock_session.exec.return_value = mock_result
            
            authenticated_user = await self.auth_service.authenticate_user(
                "test@example.com", "wrong_password"
            )
            
            assert authenticated_user is None
            mock_verify.assert_called_once_with("wrong_password", "hashed_password")

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self):
        """Test authentication with non-existent user."""
        # Mock database query returning no user
        mock_result = AsyncMock()
        mock_result.first.return_value = None
        self.mock_session.exec.return_value = mock_result
        
        authenticated_user = await self.auth_service.authenticate_user(
            "nonexistent@example.com", "password123"
        )
        
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_authenticate_user_inactive(self):
        """Test authentication with inactive user."""
        mock_user = User(
            id=self.test_user_id,
            email="test@example.com",
            full_name="Test User",
            hashed_password="hashed_password",
            role="staff",
            organization_id=self.test_org_id,
            restaurant_id=self.test_restaurant_id,
            is_active=False  # Inactive user
        )
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.first.return_value = mock_user
        self.mock_session.exec.return_value = mock_result
        
        authenticated_user = await self.auth_service.authenticate_user(
            "test@example.com", "password123"
        )
        
        assert authenticated_user is None

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self):
        """Test successful user retrieval by ID."""
        mock_user = User(
            id=self.test_user_id,
            email="test@example.com",
            full_name="Test User",
            role="staff",
            organization_id=self.test_org_id,
            restaurant_id=self.test_restaurant_id,
            is_active=True
        )
        
        # Mock database query
        mock_result = AsyncMock()
        mock_result.first.return_value = mock_user
        self.mock_session.exec.return_value = mock_result
        
        user = await self.auth_service.get_user_by_id(str(self.test_user_id))
        
        assert user == mock_user

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        """Test user retrieval with non-existent ID."""
        # Mock database query returning no user
        mock_result = AsyncMock()
        mock_result.first.return_value = None
        self.mock_session.exec.return_value = mock_result
        
        user = await self.auth_service.get_user_by_id(str(uuid4()))
        
        assert user is None