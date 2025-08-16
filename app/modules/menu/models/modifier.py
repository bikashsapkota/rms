from typing import Optional
from decimal import Decimal
from sqlmodel import SQLModel, Field
from app.shared.database.base import RestaurantTenantBaseModel


class ModifierBase(SQLModel):
    """Base modifier model for shared fields."""
    name: str = Field(max_length=255, nullable=False)
    type: str = Field(
        max_length=50,
        description="Modifier type: 'size', 'addon', 'substitution'"
    )
    price_adjustment: Decimal = Field(
        default=Decimal("0.00"),
        max_digits=10,
        decimal_places=2,
        description="Price adjustment (can be negative)"
    )
    is_active: bool = Field(default=True)


class Modifier(ModifierBase, RestaurantTenantBaseModel, table=True):
    """Modifier model for menu item customizations."""
    __tablename__ = "modifiers"


class ModifierCreate(ModifierBase):
    """Schema for creating modifiers."""
    pass


class ModifierUpdate(SQLModel):
    """Schema for updating modifiers."""
    name: Optional[str] = None
    type: Optional[str] = None
    price_adjustment: Optional[Decimal] = None
    is_active: Optional[bool] = None


class ModifierRead(ModifierBase):
    """Schema for reading modifiers."""
    id: str
    organization_id: str
    restaurant_id: str
    created_at: str
    updated_at: str