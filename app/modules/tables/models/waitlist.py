from typing import Optional
from datetime import date, time
from sqlmodel import SQLModel, Field
from app.shared.database.base import RestaurantTenantBaseModel


class WaitlistBase(SQLModel):
    """Base waitlist model for shared fields."""
    customer_name: str = Field(max_length=255, nullable=False)
    customer_phone: Optional[str] = Field(default=None, max_length=20)
    customer_email: Optional[str] = Field(default=None, max_length=255)
    party_size: int = Field(nullable=False, description="Number of guests")
    preferred_date: Optional[date] = Field(default=None)
    preferred_time: Optional[time] = Field(default=None)
    status: str = Field(
        default="active",
        max_length=50,
        description="Status: 'active', 'notified', 'seated', 'cancelled'"
    )
    priority_score: int = Field(
        default=0,
        description="Priority score for waitlist ordering"
    )
    notes: Optional[str] = Field(default=None)


class ReservationWaitlist(WaitlistBase, RestaurantTenantBaseModel, table=True):
    """Waitlist for reservations when fully booked."""
    __tablename__ = "reservation_waitlist"


class WaitlistCreate(WaitlistBase):
    """Schema for creating waitlist entries."""
    pass


class WaitlistUpdate(SQLModel):
    """Schema for updating waitlist entries."""
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    party_size: Optional[int] = None
    preferred_date: Optional[date] = None
    preferred_time: Optional[time] = None
    status: Optional[str] = None
    priority_score: Optional[int] = None
    notes: Optional[str] = None


class WaitlistRead(WaitlistBase):
    """Schema for reading waitlist entries."""
    id: str
    organization_id: str
    restaurant_id: str
    created_at: str
    updated_at: str


class WaitlistNotify(SQLModel):
    """Schema for notifying waitlist customers."""
    message: Optional[str] = Field(
        default=None,
        description="Custom notification message"
    )
    available_time: Optional[time] = Field(
        default=None,
        description="Available time slot to offer"
    )