from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from app.shared.database.base import TenantBaseModel

if TYPE_CHECKING:
    from app.shared.models.organization import Organization
    from app.shared.models.user import User
    from app.modules.menu.models.category import MenuCategory
    from app.modules.menu.models.item import MenuItem


class RestaurantBase(SQLModel):
    """Base restaurant model for shared fields."""
    name: str = Field(max_length=255, nullable=False)
    address: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=255)
    settings: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    is_active: bool = Field(default=True)


class Restaurant(RestaurantBase, TenantBaseModel, table=True):
    """Restaurant model."""
    __tablename__ = "restaurants"
    
    # Relationships
    organization: "Organization" = Relationship(back_populates="restaurants")
    users: List["User"] = Relationship(back_populates="restaurant")
    menu_categories: List["MenuCategory"] = Relationship(back_populates="restaurant")
    menu_items: List["MenuItem"] = Relationship(back_populates="restaurant")


class RestaurantCreate(RestaurantBase):
    """Schema for creating restaurants."""
    pass


class RestaurantUpdate(SQLModel):
    """Schema for updating restaurants."""
    name: Optional[str] = None
    address: Optional[Dict[str, Any]] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class RestaurantRead(RestaurantBase):
    """Schema for reading restaurants."""
    id: str
    organization_id: str
    created_at: str
    updated_at: str


class RestaurantReadWithDetails(RestaurantRead):
    """Schema for reading restaurants with related data."""
    user_count: int = 0
    category_count: int = 0
    menu_item_count: int = 0