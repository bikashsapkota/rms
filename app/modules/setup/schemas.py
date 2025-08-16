"""
Setup schemas for restaurant configuration.
"""

from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


class AdminUserCreate(BaseModel):
    """Schema for creating admin user during setup."""
    email: EmailStr = Field(..., description="Admin user email")
    full_name: str = Field(..., min_length=2, max_length=255, description="Admin user full name")
    password: str = Field(..., min_length=8, description="Admin user password")


class RestaurantSetupRequest(BaseModel):
    """Schema for restaurant setup request."""
    # Restaurant details
    restaurant_name: str = Field(..., min_length=2, max_length=255, description="Restaurant name")
    address: Optional[Dict[str, Any]] = Field(None, description="Restaurant address")
    phone: Optional[str] = Field(None, max_length=20, description="Restaurant phone")
    email: Optional[EmailStr] = Field(None, description="Restaurant email")
    settings: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Restaurant settings")
    
    # Admin user details
    admin_user: AdminUserCreate = Field(..., description="Admin user details")


class RestaurantSetupResponse(BaseModel):
    """Schema for restaurant setup response."""
    success: bool = Field(..., description="Setup success status")
    message: str = Field(..., description="Setup message")
    
    organization: Dict[str, Any] = Field(..., description="Created organization details")
    restaurant: Dict[str, Any] = Field(..., description="Created restaurant details")
    admin_user: Dict[str, Any] = Field(..., description="Created admin user details")
    
    next_steps: list[str] = Field(..., description="Next steps for the user")


class HealthCheckResponse(BaseModel):
    """Schema for health check response."""
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="Application version")
    timestamp: str = Field(..., description="Current timestamp")
    database: str = Field(..., description="Database status")
    services: Dict[str, str] = Field(..., description="Service statuses")