from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from app.shared.database.base import RestaurantTenantBaseModel

if TYPE_CHECKING:
    from app.shared.models.restaurant import Restaurant
    from app.modules.menu.models.item import MenuItem


class MenuCategoryBase(SQLModel):
    """Base menu category model for shared fields."""
    name: str = Field(max_length=255, nullable=False)
    description: Optional[str] = Field(default=None)
    sort_order: int = Field(default=0, description="Display order")
    is_active: bool = Field(default=True)


class MenuCategory(MenuCategoryBase, RestaurantTenantBaseModel, table=True):
    """Menu category model."""
    __tablename__ = "menu_categories"
    
    # Relationships
    restaurant: "Restaurant" = Relationship(back_populates="menu_categories")
    menu_items: List["MenuItem"] = Relationship(back_populates="category")


class MenuCategoryCreate(MenuCategoryBase):
    """Schema for creating menu categories."""
    pass


class MenuCategoryUpdate(SQLModel):
    """Schema for updating menu categories."""
    name: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class MenuCategoryRead(MenuCategoryBase):
    """Schema for reading menu categories."""
    id: str
    organization_id: str
    restaurant_id: str
    created_at: str
    updated_at: str


class MenuCategoryReadWithItems(MenuCategoryRead):
    """Schema for reading menu categories with items."""
    item_count: int = 0
    active_item_count: int = 0