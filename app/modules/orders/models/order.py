"""
Order models for restaurant order management.
"""

from typing import Optional, List, Dict, Any, TYPE_CHECKING
from enum import Enum
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship, Column, JSON, Enum as SQLEnum
from app.shared.database.base import RestaurantTenantBaseModel

if TYPE_CHECKING:
    from app.shared.models.restaurant import Restaurant
    from app.modules.tables.models.table import Table
    from app.modules.tables.models.reservation import Reservation
    from .order_item import OrderItem
    from .payment import Payment


class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"          # Just placed, awaiting payment
    CONFIRMED = "confirmed"      # Payment confirmed, sent to kitchen
    PREPARING = "preparing"      # Kitchen is preparing
    READY = "ready"             # Ready for pickup/delivery
    DELIVERED = "delivered"      # Delivered to customer
    CANCELLED = "cancelled"      # Cancelled by customer/restaurant
    REFUNDED = "refunded"       # Payment refunded


class OrderType(str, Enum):
    """Order type enumeration."""
    DINE_IN = "dine_in"         # Customer dining in restaurant
    TAKEOUT = "takeout"         # Customer pickup
    DELIVERY = "delivery"       # Delivered to customer
    QR_ORDER = "qr_order"       # Ordered via QR code at table


class OrderBase(SQLModel):
    """Base order model for shared fields."""
    order_number: str = Field(max_length=50, nullable=False, unique=True)
    order_type: OrderType = Field(sa_column=Column(SQLEnum(OrderType)))
    status: OrderStatus = Field(default=OrderStatus.PENDING, sa_column=Column(SQLEnum(OrderStatus)))
    
    # Customer information
    customer_name: Optional[str] = Field(default=None, max_length=255)
    customer_phone: Optional[str] = Field(default=None, max_length=20)
    customer_email: Optional[str] = Field(default=None, max_length=255)
    
    # Pricing
    subtotal: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    tax_amount: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    tip_amount: Decimal = Field(default=0, max_digits=10, decimal_places=2)
    total_amount: Decimal = Field(max_digits=10, decimal_places=2)
    
    # Delivery information
    delivery_address: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON))
    delivery_instructions: Optional[str] = Field(default=None, max_length=500)
    
    # Timing
    requested_time: Optional[datetime] = Field(default=None)
    estimated_ready_time: Optional[datetime] = Field(default=None)
    actual_ready_time: Optional[datetime] = Field(default=None)
    prep_time_minutes: Optional[int] = Field(default=None)
    
    # Special instructions and notes
    special_instructions: Optional[str] = Field(default=None, max_length=1000)
    kitchen_notes: Optional[str] = Field(default=None, max_length=1000)
    
    # Table/reservation linking
    table_id: Optional[UUID] = Field(default=None, foreign_key="tables.id")
    reservation_id: Optional[UUID] = Field(default=None, foreign_key="reservations.id")
    
    # QR code ordering
    qr_session_id: Optional[str] = Field(default=None, max_length=100)
    
    # Metadata
    order_metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))


class Order(OrderBase, RestaurantTenantBaseModel, table=True):
    """Order model."""
    __tablename__ = "orders"
    
    # Relationships
    order_items: List["OrderItem"] = Relationship(back_populates="order")
    payments: List["Payment"] = Relationship(back_populates="order")


class OrderCreate(OrderBase):
    """Schema for creating orders."""
    pass


class OrderUpdate(SQLModel):
    """Schema for updating orders."""
    status: Optional[OrderStatus] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    delivery_address: Optional[Dict[str, Any]] = None
    delivery_instructions: Optional[str] = None
    requested_time: Optional[datetime] = None
    estimated_ready_time: Optional[datetime] = None
    actual_ready_time: Optional[datetime] = None
    prep_time_minutes: Optional[int] = None
    special_instructions: Optional[str] = None
    kitchen_notes: Optional[str] = None
    order_metadata: Optional[Dict[str, Any]] = None


class OrderRead(OrderBase):
    """Schema for reading orders."""
    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    created_at: datetime
    updated_at: datetime


class OrderReadWithItems(OrderRead):
    """Schema for reading orders with items."""
    order_items: List = []
    payments: List = []


class OrderSummary(SQLModel):
    """Summary schema for order lists."""
    id: UUID
    order_number: str
    order_type: OrderType
    status: OrderStatus
    customer_name: Optional[str]
    total_amount: Decimal
    requested_time: Optional[datetime]
    estimated_ready_time: Optional[datetime]
    table_number: Optional[str] = None
    created_at: datetime