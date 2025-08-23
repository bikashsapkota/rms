from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from app.shared.database.base import RestaurantTenantBaseModel
from app.modules.menu.models.menu_item_modifier_link import MenuItemModifierLink
import re

if TYPE_CHECKING:
    from app.shared.models.restaurant import Restaurant
    from app.modules.menu.models.category import MenuCategory
    from app.modules.menu.models.modifier import Modifier


class MenuItemBase(SQLModel):
    """Base menu item model for shared fields."""
    name: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None)
    price: Decimal = Field(max_digits=10, decimal_places=2, nullable=False, ge=0)  # Must be >= 0
    is_available: bool = Field(default=True)
    image_url: Optional[str] = Field(default=None, max_length=500)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        # Check for script tags and common XSS patterns
        if re.search(r'<script|javascript:|on\w+\s*=', v, re.IGNORECASE):
            raise ValueError('Invalid characters in name')
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls, v):
        if v is None:
            return v
        # Check for script tags and common XSS patterns  
        if re.search(r'<script|javascript:|on\w+\s*=', v, re.IGNORECASE):
            raise ValueError('Invalid characters in description')
        return v.strip()
    
    @field_validator('price')
    @classmethod
    def validate_price(cls, v):
        if v < 0:
            raise ValueError('Price cannot be negative')
        return v


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
    # modifiers: List["Modifier"] = Relationship(
    #     back_populates="menu_items",
    #     sa_relationship_kwargs={
    #         "secondary": MenuItemModifierLink.__table__,
    #     }
    # )


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