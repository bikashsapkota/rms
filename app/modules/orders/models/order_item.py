"""
Order item models for individual items within orders.
"""

from typing import Optional, List, Dict, Any, TYPE_CHECKING
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from app.shared.database.base import RestaurantTenantBaseModel

if TYPE_CHECKING:
    from .order import Order
    from app.modules.menu.models.item import MenuItem
    from app.modules.menu.models.modifier import Modifier


class OrderItemBase(SQLModel):
    """Base order item model for shared fields."""
    quantity: int = Field(default=1, ge=1)
    unit_price: Decimal = Field(max_digits=10, decimal_places=2)
    total_price: Decimal = Field(max_digits=10, decimal_places=2)
    
    # Menu item reference
    menu_item_id: UUID = Field(foreign_key="menu_items.id")
    menu_item_name: str = Field(max_length=255)  # Snapshot for historical accuracy
    menu_item_description: Optional[str] = Field(default=None, max_length=1000)
    
    # Special instructions for this item
    special_instructions: Optional[str] = Field(default=None, max_length=500)
    
    # Kitchen tracking
    kitchen_notes: Optional[str] = Field(default=None, max_length=500)
    prep_start_time: Optional[datetime] = Field(default=None)  # When kitchen started this item
    prep_complete_time: Optional[datetime] = Field(default=None)  # When item was ready
    
    # Order reference
    order_id: UUID = Field(foreign_key="orders.id")


class OrderItem(OrderItemBase, RestaurantTenantBaseModel, table=True):
    """Order item model."""
    __tablename__ = "order_items"
    
    # Relationships
    order: "Order" = Relationship(back_populates="order_items")
    menu_item: "MenuItem" = Relationship()
    modifiers: List["OrderItemModifier"] = Relationship(back_populates="order_item")


class OrderItemModifierBase(SQLModel):
    """Base order item modifier model."""
    modifier_id: UUID = Field(foreign_key="modifiers.id")
    modifier_name: str = Field(max_length=255)  # Snapshot for historical accuracy
    modifier_price: Decimal = Field(max_digits=10, decimal_places=2)
    quantity: int = Field(default=1, ge=1)
    total_price: Decimal = Field(max_digits=10, decimal_places=2)
    
    # Order item reference
    order_item_id: UUID = Field(foreign_key="order_items.id")


class OrderItemModifier(OrderItemModifierBase, RestaurantTenantBaseModel, table=True):
    """Order item modifier model."""
    __tablename__ = "order_item_modifiers"
    
    # Relationships
    order_item: "OrderItem" = Relationship(back_populates="modifiers")
    modifier: "Modifier" = Relationship()


# Pydantic schemas for API
class OrderItemModifierCreate(SQLModel):
    """Schema for creating order item modifiers."""
    modifier_id: UUID
    quantity: int = 1


class OrderItemModifierRead(OrderItemModifierBase):
    """Schema for reading order item modifiers."""
    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    created_at: datetime
    updated_at: datetime


class OrderItemCreate(SQLModel):
    """Schema for creating order items."""
    menu_item_id: UUID
    quantity: int = 1
    special_instructions: Optional[str] = None
    modifiers: List[OrderItemModifierCreate] = []


class OrderItemUpdate(SQLModel):
    """Schema for updating order items."""
    quantity: Optional[int] = None
    special_instructions: Optional[str] = None
    kitchen_notes: Optional[str] = None


class OrderItemRead(OrderItemBase):
    """Schema for reading order items."""
    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    created_at: datetime
    updated_at: datetime


class OrderItemReadWithModifiers(OrderItemRead):
    """Schema for reading order items with modifiers."""
    modifiers: List = []


class OrderItemKitchenView(SQLModel):
    """Kitchen-focused view of order items."""
    id: UUID
    menu_item_name: str
    quantity: int
    special_instructions: Optional[str]
    kitchen_notes: Optional[str]
    modifiers: List = []
    prep_start_time: Optional[datetime]
    prep_complete_time: Optional[datetime]