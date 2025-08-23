"""
Order management schemas for API operations.
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from .models.order import OrderType, OrderStatus
from .models.order_item import OrderItemCreate, OrderItemModifierCreate
from .models.payment import PaymentMethod, PaymentCreate


class QROrderSessionCreate(BaseModel):
    """Schema for creating QR order sessions."""
    table_id: str = Field(..., description="Table ID for QR ordering")
    customer_name: Optional[str] = Field(None, description="Customer name")


class QROrderSessionInfo(BaseModel):
    """Schema for QR order session information."""
    session_id: str
    table_number: str
    restaurant_name: str
    menu_url: str
    active_until: datetime


class OrderCreateRequest(BaseModel):
    """Schema for creating orders with items."""
    order_type: OrderType = Field(..., description="Type of order")
    
    # Customer information
    customer_name: Optional[str] = Field(None, max_length=255)
    customer_phone: Optional[str] = Field(None, max_length=20)
    customer_email: Optional[str] = Field(None)
    
    # Order items
    items: List[OrderItemCreate] = Field(..., description="Order items")
    
    # Delivery information (for delivery orders)
    delivery_address: Optional[Dict[str, Any]] = Field(None)
    delivery_instructions: Optional[str] = Field(None, max_length=500)
    
    # Timing
    requested_time: Optional[datetime] = Field(None, description="Requested ready time")
    
    # Special instructions
    special_instructions: Optional[str] = Field(None, max_length=1000)
    
    # Table/reservation linking
    table_id: Optional[str] = Field(None, description="Table ID for dine-in orders")
    reservation_id: Optional[str] = Field(None, description="Reservation ID")
    
    # QR ordering
    qr_session_id: Optional[str] = Field(None, description="QR session ID")
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v:
            raise ValueError('Order must contain at least one item')
        return v


class OrderUpdateRequest(BaseModel):
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


class OrderStatusUpdate(BaseModel):
    """Schema for order status updates."""
    status: OrderStatus = Field(..., description="New order status")
    kitchen_notes: Optional[str] = Field(None, description="Kitchen notes")
    estimated_ready_time: Optional[datetime] = Field(None)


class OrderKitchenUpdate(BaseModel):
    """Schema for kitchen order updates."""
    prep_start_time: Optional[datetime] = Field(None)
    prep_complete_time: Optional[datetime] = Field(None)
    kitchen_notes: Optional[str] = Field(None, max_length=500)
    estimated_ready_time: Optional[datetime] = Field(None)


class OrderItemKitchenUpdate(BaseModel):
    """Schema for updating individual order items in kitchen."""
    prep_start_time: Optional[datetime] = Field(None)
    prep_complete_time: Optional[datetime] = Field(None)
    kitchen_notes: Optional[str] = Field(None, max_length=500)


class OrderSearchFilters(BaseModel):
    """Schema for order search filters."""
    status: Optional[List[OrderStatus]] = Field(None, description="Filter by status")
    order_type: Optional[List[OrderType]] = Field(None, description="Filter by type")
    customer_name: Optional[str] = Field(None, description="Filter by customer name")
    table_id: Optional[str] = Field(None, description="Filter by table")
    date_from: Optional[datetime] = Field(None, description="Filter from date")
    date_to: Optional[datetime] = Field(None, description="Filter to date")
    
    # Kitchen filters
    prep_status: Optional[str] = Field(None, description="Filter by prep status: 'not_started', 'in_progress', 'completed'")


class OrderAnalytics(BaseModel):
    """Schema for order analytics."""
    total_orders: int
    orders_by_status: Dict[str, int]
    orders_by_type: Dict[str, int]
    total_revenue: Decimal
    average_order_value: Decimal
    average_prep_time: Optional[float]
    peak_hours: List[Dict[str, Any]]


class SplitPaymentRequest(BaseModel):
    """Schema for split payment requests."""
    payments: List[PaymentCreate] = Field(..., description="Individual payments")
    split_method: str = Field(..., description="Split method: 'equal', 'custom', 'by_item'")
    customer_payments: Optional[List[Dict[str, Any]]] = Field(None, description="Customer payment assignments")
    
    @field_validator('payments')
    @classmethod
    def validate_payments(cls, v):
        if not v:
            raise ValueError('At least one payment required')
        return v


class OrderReceiptData(BaseModel):
    """Schema for order receipt data."""
    order_number: str
    restaurant_name: str
    restaurant_address: Optional[Dict[str, Any]]
    customer_name: Optional[str]
    order_date: datetime
    items: List[Dict[str, Any]]
    subtotal: Decimal
    tax_amount: Decimal
    tip_amount: Decimal
    total_amount: Decimal
    payment_method: str
    transaction_id: Optional[str]


class QRMenuAccess(BaseModel):
    """Schema for QR menu access."""
    table_id: str
    session_id: Optional[str] = None


class CustomerOrderPlacement(BaseModel):
    """Schema for customer order placement via QR."""
    session_id: str
    items: List[OrderItemCreate]
    customer_name: Optional[str] = None
    special_instructions: Optional[str] = None