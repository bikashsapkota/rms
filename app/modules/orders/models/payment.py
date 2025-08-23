"""
Payment models for order payment processing.
"""

from typing import Optional, Dict, Any, TYPE_CHECKING
from enum import Enum
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship, Column, JSON, Enum as SQLEnum
from app.shared.database.base import RestaurantTenantBaseModel

if TYPE_CHECKING:
    from .order import Order


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    PENDING = "pending"          # Payment initiated but not completed
    PROCESSING = "processing"    # Payment being processed
    COMPLETED = "completed"      # Payment successful
    FAILED = "failed"           # Payment failed
    REFUNDED = "refunded"       # Payment refunded
    PARTIALLY_REFUNDED = "partially_refunded"  # Partial refund


class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    MOBILE_PAYMENT = "mobile_payment"  # Apple Pay, Google Pay, etc.
    DIGITAL_WALLET = "digital_wallet"  # PayPal, Venmo, etc.
    GIFT_CARD = "gift_card"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"


class PaymentBase(SQLModel):
    """Base payment model for shared fields."""
    amount: Decimal = Field(max_digits=10, decimal_places=2)
    payment_method: PaymentMethod = Field(sa_column=Column(SQLEnum(PaymentMethod)))
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, sa_column=Column(SQLEnum(PaymentStatus)))
    
    # Payment processing
    transaction_id: Optional[str] = Field(default=None, max_length=255)
    external_payment_id: Optional[str] = Field(default=None, max_length=255)  # Stripe, PayPal, etc.
    processor: Optional[str] = Field(default=None, max_length=100)  # "stripe", "square", etc.
    
    # Card/account details (masked for security)
    card_last_four: Optional[str] = Field(default=None, max_length=4)
    card_brand: Optional[str] = Field(default=None, max_length=50)
    
    # Timing
    processed_at: Optional[datetime] = Field(default=None)
    refunded_at: Optional[datetime] = Field(default=None)
    
    # Split payments
    is_split_payment: bool = Field(default=False)
    split_payment_group_id: Optional[str] = Field(default=None, max_length=100)
    
    # Refund information
    refund_amount: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    refund_reason: Optional[str] = Field(default=None, max_length=500)
    
    # Tips
    tip_amount: Optional[Decimal] = Field(default=None, max_digits=10, decimal_places=2)
    
    # Notes and metadata
    notes: Optional[str] = Field(default=None, max_length=1000)
    payment_metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Order reference
    order_id: UUID = Field(foreign_key="orders.id")


class Payment(PaymentBase, RestaurantTenantBaseModel, table=True):
    """Payment model."""
    __tablename__ = "payments"
    
    # Relationships
    order: "Order" = Relationship(back_populates="payments")


class PaymentCreate(SQLModel):
    """Schema for creating payments."""
    amount: Decimal
    payment_method: PaymentMethod
    tip_amount: Optional[Decimal] = None
    is_split_payment: bool = False
    split_payment_group_id: Optional[str] = None
    notes: Optional[str] = None
    payment_metadata: Optional[Dict[str, Any]] = None


class PaymentUpdate(SQLModel):
    """Schema for updating payments."""
    status: Optional[PaymentStatus] = None
    transaction_id: Optional[str] = None
    external_payment_id: Optional[str] = None
    processor: Optional[str] = None
    card_last_four: Optional[str] = None
    card_brand: Optional[str] = None
    processed_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    refund_amount: Optional[Decimal] = None
    refund_reason: Optional[str] = None
    notes: Optional[str] = None
    payment_metadata: Optional[Dict[str, Any]] = None


class PaymentRead(PaymentBase):
    """Schema for reading payments."""
    id: UUID
    organization_id: UUID
    restaurant_id: UUID
    created_at: datetime
    updated_at: datetime


class PaymentRefundRequest(SQLModel):
    """Schema for payment refund requests."""
    refund_amount: Decimal
    refund_reason: str
    notes: Optional[str] = None


class PaymentSummary(SQLModel):
    """Summary schema for payment lists."""
    id: UUID
    amount: Decimal
    payment_method: PaymentMethod
    status: PaymentStatus
    transaction_id: Optional[str]
    tip_amount: Optional[Decimal]
    processed_at: Optional[datetime]
    created_at: datetime