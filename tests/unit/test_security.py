"""
Unit tests for security and authentication functions.
"""

import pytest
from datetime import datetime, timedelta
from app.shared.auth.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    decode_access_token,
    create_user_access_token,
    decode_user_token,
    create_token_payload,
)


class TestPasswordSecurity:
    """Test password hashing and verification."""

    def test_password_hashing(self):
        """Test password hashing."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert isinstance(hashed, str)
        assert len(hashed) > 0

    def test_password_verification_success(self):
        """Test successful password verification."""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """Test failed password verification."""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False

    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        password1 = "password123"
        password2 = "password456"
        
        hash1 = get_password_hash(password1)
        hash2 = get_password_hash(password2)
        
        assert hash1 != hash2

    def test_same_password_different_hashes(self):
        """Test that same password produces different hashes (salt)."""
        password = "testpassword123"
        
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Due to salt, same password should produce different hashes
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWTTokens:
    """Test JWT token creation and validation."""

    def test_create_access_token(self):
        """Test basic access token creation."""
        subject = "test_user_id"
        token = create_access_token(subject)
        
        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # JWT tokens have dots

    def test_create_access_token_with_expiry(self):
        """Test access token creation with custom expiry."""
        subject = "test_user_id"
        expires_delta = timedelta(minutes=60)
        token = create_access_token(subject, expires_delta)
        
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_access_token_success(self):
        """Test successful token decoding."""
        subject = "test_user_id"
        token = create_access_token(subject)
        
        decoded_subject = decode_access_token(token)
        assert decoded_subject == subject

    def test_decode_access_token_invalid(self):
        """Test decoding invalid token."""
        invalid_token = "invalid.token.here"
        decoded_subject = decode_access_token(invalid_token)
        
        assert decoded_subject is None

    def test_decode_access_token_malformed(self):
        """Test decoding malformed token."""
        malformed_token = "not-a-jwt-token"
        decoded_subject = decode_access_token(malformed_token)
        
        assert decoded_subject is None


class TestUserTokens:
    """Test user-specific JWT token functionality."""

    def test_create_token_payload(self):
        """Test creating token payload."""
        payload = create_token_payload(
            user_id="user123",
            email="test@example.com",
            organization_id="org123",
            restaurant_id="rest123",
            role="admin"
        )
        
        assert payload["user_id"] == "user123"
        assert payload["email"] == "test@example.com"
        assert payload["organization_id"] == "org123"
        assert payload["restaurant_id"] == "rest123"
        assert payload["role"] == "admin"
        assert "iat" in payload

    def test_create_user_access_token(self):
        """Test creating user access token."""
        token = create_user_access_token(
            user_id="user123",
            email="test@example.com",
            organization_id="org123",
            restaurant_id="rest123",
            role="admin"
        )
        
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_user_token_success(self):
        """Test successful user token decoding."""
        user_id = "user123"
        email = "test@example.com"
        org_id = "org123"
        rest_id = "rest123"
        role = "admin"
        
        token = create_user_access_token(
            user_id=user_id,
            email=email,
            organization_id=org_id,
            restaurant_id=rest_id,
            role=role
        )
        
        payload = decode_user_token(token)
        
        assert payload is not None
        assert payload["user_id"] == user_id
        assert payload["email"] == email
        assert payload["organization_id"] == org_id
        assert payload["restaurant_id"] == rest_id
        assert payload["role"] == role

    def test_decode_user_token_invalid(self):
        """Test decoding invalid user token."""
        invalid_token = "invalid.token.here"
        payload = decode_user_token(invalid_token)
        
        assert payload is None

    def test_user_token_without_restaurant(self):
        """Test user token creation without restaurant."""
        token = create_user_access_token(
            user_id="user123",
            email="test@example.com",
            organization_id="org123",
            restaurant_id=None,  # No restaurant
            role="admin"
        )
        
        payload = decode_user_token(token)
        
        assert payload is not None
        assert payload["user_id"] == "user123"
        assert payload["restaurant_id"] is None

    def test_user_token_with_expiry(self):
        """Test user token creation with custom expiry."""
        expires_delta = timedelta(minutes=60)
        token = create_user_access_token(
            user_id="user123",
            email="test@example.com",
            organization_id="org123",
            expires_delta=expires_delta
        )
        
        payload = decode_user_token(token)
        assert payload is not None
        
        # Check that expiry is set (though we can't test exact value due to timing)
        assert "exp" in payload