"""
Restaurant application models for platform management.
"""

from typing import Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from app.shared.database.base import BaseModel

if TYPE_CHECKING:
    from app.shared.models.organization import Organization


class RestaurantApplicationBase(SQLModel):
    """Base restaurant application model."""
    applicant_name: str = Field(max_length=255, description="Name of the applicant")
    applicant_email: str = Field(max_length=255, description="Email of the applicant")
    restaurant_name: str = Field(max_length=255, description="Proposed restaurant name")
    restaurant_address: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    restaurant_phone: Optional[str] = Field(default=None, max_length=20)
    restaurant_email: Optional[str] = Field(default=None, max_length=255)
    business_description: Optional[str] = Field(default=None, description="Business description")
    status: str = Field(
        default="pending",
        description="Application status: pending, approved, rejected"
    )
    admin_notes: Optional[str] = Field(default=None, description="Admin review notes")


class RestaurantApplication(RestaurantApplicationBase, BaseModel, table=True):
    """Restaurant application model."""
    __tablename__ = "restaurant_applications"
    
    # Foreign key to organization (will be set when approved)
    organization_id: Optional[UUID] = Field(
        default=None,
        foreign_key="organizations.id",
        index=True
    )
    
    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="applications")


class RestaurantApplicationCreate(RestaurantApplicationBase):
    """Schema for creating restaurant applications."""
    pass


class RestaurantApplicationUpdate(SQLModel):
    """Schema for updating restaurant applications."""
    status: Optional[str] = None
    admin_notes: Optional[str] = None


class RestaurantApplicationRead(RestaurantApplicationBase):
    """Schema for reading restaurant applications."""
    id: UUID
    organization_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime


class RestaurantApplicationApproval(SQLModel):
    """Schema for approving applications."""
    admin_notes: Optional[str] = Field(default=None, description="Admin approval notes")


class RestaurantApplicationRejection(SQLModel):
    """Schema for rejecting applications."""
    admin_notes: str = Field(description="Reason for rejection")


class ApplicationStats(SQLModel):
    """Schema for application statistics."""
    total_applications: int
    pending_applications: int
    approved_applications: int
    rejected_applications: int
    recent_applications: int  # Last 30 days