from typing import Optional, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship
from pydantic import field_validator
from app.shared.database.base import RestaurantTenantBaseModel

if TYPE_CHECKING:
    from app.shared.models.restaurant import Restaurant
    from app.modules.menu.models.item import MenuItem


class MenuCategoryBase(SQLModel):
    """Base menu category model for shared fields."""
    name: str = Field(min_length=1, max_length=255, nullable=False, description="Category name (required)")
    description: Optional[str] = Field(default=None)
    sort_order: int = Field(default=0, description="Display order")
    cover_image_url: Optional[str] = Field(default=None, max_length=500, description="Category cover image URL")
    is_active: bool = Field(default=True)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate category name is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError('Category name cannot be empty or whitespace only')
        return v.strip()


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
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    sort_order: Optional[int] = None
    cover_image_url: Optional[str] = None
    is_active: Optional[bool] = None
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate category name is not empty or whitespace only."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Category name cannot be empty or whitespace only')
            return v.strip()
        return v


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