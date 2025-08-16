from typing import Optional, TYPE_CHECKING
from decimal import Decimal
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship
from app.shared.database.base import RestaurantTenantBaseModel

if TYPE_CHECKING:
    from app.shared.models.restaurant import Restaurant
    from app.modules.menu.models.category import MenuCategory


class MenuItemBase(SQLModel):
    """Base menu item model for shared fields."""
    name: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None)
    price: Decimal = Field(max_digits=10, decimal_places=2, nullable=False)
    is_available: bool = Field(default=True)
    image_url: Optional[str] = Field(default=None, max_length=500)


class MenuItem(MenuItemBase, RestaurantTenantBaseModel, table=True):
    """Menu item model."""
    __tablename__ = "menu_items"
    
    category_id: Optional[UUID] = Field(
        default=None, 
        foreign_key="menu_categories.id", 
        index=True
    )
    
    # Relationships
    restaurant: "Restaurant" = Relationship(back_populates="menu_items")
    category: Optional["MenuCategory"] = Relationship(back_populates="menu_items")


class MenuItemCreate(MenuItemBase):
    """Schema for creating menu items."""
    category_id: Optional[UUID] = None


class MenuItemUpdate(SQLModel):
    """Schema for updating menu items."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[Decimal] = None
    is_available: Optional[bool] = None
    image_url: Optional[str] = None
    category_id: Optional[UUID] = None


class MenuItemRead(MenuItemBase):
    """Schema for reading menu items."""
    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    category_id: Optional[UUID] = None
    created_at: str
    updated_at: str


class MenuItemReadWithCategory(MenuItemRead):
    """Schema for reading menu items with category details."""
    category_name: Optional[str] = None


class MenuItemPublic(SQLModel):
    """Public schema for menu items (customer-facing)."""
    id: UUID
    name: str
    description: Optional[str] = None
    price: Decimal
    image_url: Optional[str] = None
    category_name: Optional[str] = None