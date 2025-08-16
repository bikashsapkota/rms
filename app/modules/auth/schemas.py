from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=1, description="User password")


class LoginResponse(BaseModel):
    """Login response schema."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: "UserInfo" = Field(..., description="User information")


class UserInfo(BaseModel):
    """User information in login response."""
    id: str = Field(..., description="User ID")
    email: str = Field(..., description="User email")
    full_name: str = Field(..., description="User full name")
    role: str = Field(..., description="User role")
    organization_id: str = Field(..., description="Organization ID")
    restaurant_id: Optional[str] = Field(None, description="Restaurant ID")
    organization_name: str = Field(..., description="Organization name")
    restaurant_name: Optional[str] = Field(None, description="Restaurant name")


class RefreshTokenResponse(BaseModel):
    """Refresh token response schema."""
    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")


class LogoutResponse(BaseModel):
    """Logout response schema."""
    message: str = Field(default="Successfully logged out", description="Logout message")


class TokenPayload(BaseModel):
    """Token payload schema for internal use."""
    user_id: str
    email: str
    organization_id: str
    restaurant_id: Optional[str] = None
    role: str = "staff"