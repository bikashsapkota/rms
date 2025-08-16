from typing import Optional, TYPE_CHECKING
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship
from app.shared.database.base import TenantBaseModel

if TYPE_CHECKING:
    from app.shared.models.organization import Organization
    from app.shared.models.restaurant import Restaurant


class UserBase(SQLModel):
    """Base user model for shared fields."""
    email: str = Field(max_length=255, unique=True, nullable=False)
    full_name: str = Field(max_length=255, nullable=False)
    role: str = Field(
        default="staff",
        max_length=50,
        description="User role: 'admin', 'manager', 'staff'"
    )
    is_active: bool = Field(default=True)


class User(UserBase, TenantBaseModel, table=True):
    """User model with multi-tenant support."""
    __tablename__ = "users"
    
    password_hash: str = Field(max_length=255, nullable=False)
    restaurant_id: Optional[UUID] = Field(
        default=None, 
        foreign_key="restaurants.id", 
        index=True,
        description="NULL for organization-level users"
    )
    
    # Relationships
    organization: "Organization" = Relationship(back_populates="users")
    restaurant: Optional["Restaurant"] = Relationship(back_populates="users")


class UserCreate(UserBase):
    """Schema for creating users."""
    password: str = Field(min_length=8, max_length=100)
    restaurant_id: Optional[UUID] = None


class UserUpdate(SQLModel):
    """Schema for updating users."""
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    restaurant_id: Optional[UUID] = None


class UserUpdatePassword(SQLModel):
    """Schema for updating user password."""
    current_password: str
    new_password: str = Field(min_length=8, max_length=100)


class UserRead(UserBase):
    """Schema for reading users."""
    id: UUID
    organization_id: UUID
    restaurant_id: Optional[UUID] = None
    created_at: str
    updated_at: str


class UserReadWithDetails(UserRead):
    """Schema for reading users with restaurant details."""
    restaurant_name: Optional[str] = None
    organization_name: str