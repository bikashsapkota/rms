from typing import Optional, List, TYPE_CHECKING
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship
from app.shared.database.base import RestaurantTenantBaseModel
from app.modules.menu.models.menu_item_modifier_link import MenuItemModifierLink

if TYPE_CHECKING:
    from app.shared.models.restaurant import Restaurant
    from app.modules.menu.models.item import MenuItem


class ModifierBase(SQLModel):
    """Base modifier model for shared fields."""
    name: str = Field(max_length=255, nullable=False, description="Modifier name")
    description: Optional[str] = Field(default=None, description="Modifier description")
    modifier_type: str = Field(
        max_length=50,
        description="Type: 'size', 'addon', 'substitution', 'required', 'optional'"
    )
    price_adjustment: Decimal = Field(
        default=Decimal("0.00"),
        max_digits=10,
        decimal_places=2,
        description="Price adjustment (can be negative for discounts)"
    )
    is_required: bool = Field(default=False, description="Whether this modifier is required")
    sort_order: int = Field(default=0, description="Display order")
    is_active: bool = Field(default=True, description="Whether modifier is active")


class Modifier(ModifierBase, RestaurantTenantBaseModel, table=True):
    """Menu modifier model with multi-tenant support."""
    __tablename__ = "modifiers"
    
    # Relationships
    restaurant: "Restaurant" = Relationship(back_populates="modifiers")
    # menu_items: List["MenuItem"] = Relationship(
    #     back_populates="modifiers",
    #     sa_relationship_kwargs={
    #         "secondary": MenuItemModifierLink.__table__,
    #     }
    # )


class ModifierCreate(ModifierBase):
    """Schema for creating modifiers."""
    pass


class ModifierUpdate(SQLModel):
    """Schema for updating modifiers."""
    name: Optional[str] = None
    description: Optional[str] = None
    modifier_type: Optional[str] = None
    price_adjustment: Optional[Decimal] = None
    is_required: Optional[bool] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ModifierRead(ModifierBase):
    """Schema for reading modifiers."""
    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    created_at: str
    updated_at: str


class ModifierReadWithItems(ModifierRead):
    """Schema for reading modifiers with associated menu items."""
    item_count: int = 0


class MenuItemModifierAssignment(SQLModel):
    """Schema for assigning modifiers to menu items."""
    modifier_id: str = Field(description="Modifier to assign")
    is_required: Optional[bool] = Field(default=None, description="Override modifier required setting")
    sort_order: Optional[int] = Field(default=None, description="Override sort order for this item")


class MenuItemModifierRead(SQLModel):
    """Schema for reading menu item modifier assignments."""
    modifier_id: str
    modifier_name: str
    modifier_type: str
    price_adjustment: Decimal
    is_required: bool
    sort_order: int
    description: Optional[str] = None