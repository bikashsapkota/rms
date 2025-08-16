from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.shared.database.base import BaseModel

if TYPE_CHECKING:
    from app.shared.models.restaurant import Restaurant
    from app.shared.models.user import User


class OrganizationBase(SQLModel):
    """Base organization model for shared fields."""
    name: str = Field(max_length=255, nullable=False)
    organization_type: str = Field(
        default="independent", 
        max_length=50,
        description="Type: 'franchise', 'chain', 'independent'"
    )
    subscription_tier: str = Field(
        default="basic",
        max_length=50,
        description="Subscription tier: 'basic', 'professional', 'enterprise'"
    )
    billing_email: Optional[str] = Field(default=None, max_length=255)
    is_active: bool = Field(default=True)


class Organization(OrganizationBase, BaseModel, table=True):
    """Organization model for multi-tenant support."""
    __tablename__ = "organizations"
    
    # Relationships
    restaurants: List["Restaurant"] = Relationship(back_populates="organization")
    users: List["User"] = Relationship(back_populates="organization")


class OrganizationCreate(OrganizationBase):
    """Schema for creating organizations."""
    pass


class OrganizationUpdate(SQLModel):
    """Schema for updating organizations."""
    name: Optional[str] = None
    organization_type: Optional[str] = None
    subscription_tier: Optional[str] = None
    billing_email: Optional[str] = None
    is_active: Optional[bool] = None


class OrganizationRead(OrganizationBase):
    """Schema for reading organizations."""
    id: str
    created_at: str
    updated_at: str


class OrganizationReadWithDetails(OrganizationRead):
    """Schema for reading organizations with related data."""
    restaurant_count: int = 0
    user_count: int = 0