from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import date, time, datetime
from uuid import UUID
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from app.shared.database.base import RestaurantTenantBaseModel

if TYPE_CHECKING:
    from app.shared.models.restaurant import Restaurant
    from app.modules.tables.models.table import Table
    from app.modules.orders.models.order import Order


class ReservationBase(SQLModel):
    """Base reservation model for shared fields."""
    customer_name: str = Field(max_length=255, nullable=False)
    customer_phone: Optional[str] = Field(default=None, max_length=20)
    customer_email: Optional[str] = Field(default=None, max_length=255)
    party_size: int = Field(nullable=False, description="Number of guests")
    reservation_date: date = Field(nullable=False)
    reservation_time: time = Field(nullable=False)
    duration_minutes: int = Field(default=90, description="Expected duration in minutes")
    status: str = Field(
        default="confirmed",
        max_length=50,
        description="Status: 'confirmed', 'seated', 'completed', 'cancelled', 'no_show'"
    )
    special_requests: Optional[str] = Field(default=None)
    customer_preferences: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Customer preferences: seating, dietary, etc."
    )


class Reservation(ReservationBase, RestaurantTenantBaseModel, table=True):
    """Reservation model with multi-tenant support."""
    __tablename__ = "reservations"
    
    table_id: Optional[UUID] = Field(
        default=None,
        foreign_key="tables.id",
        index=True,
        description="Assigned table (NULL if not yet assigned)"
    )
    
    # Relationships
    restaurant: "Restaurant" = Relationship(back_populates="reservations")
    table: Optional["Table"] = Relationship(back_populates="reservations")
    # orders: List["Order"] = Relationship(back_populates="reservation")


class ReservationCreate(ReservationBase):
    """Schema for creating reservations."""
    table_id: Optional[UUID] = None


class ReservationUpdate(SQLModel):
    """Schema for updating reservations."""
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    party_size: Optional[int] = None
    reservation_date: Optional[date] = None
    reservation_time: Optional[time] = None
    duration_minutes: Optional[int] = None
    status: Optional[str] = None
    special_requests: Optional[str] = None
    customer_preferences: Optional[Dict[str, Any]] = None
    table_id: Optional[UUID] = None


class ReservationRead(ReservationBase):
    """Schema for reading reservations."""
    id: str
    organization_id: str
    restaurant_id: str
    table_id: Optional[str] = None
    created_at: str
    updated_at: str


class ReservationReadWithDetails(ReservationRead):
    """Schema for reading reservations with table details."""
    table_number: Optional[str] = None
    table_capacity: Optional[int] = None


class ReservationPublic(SQLModel):
    """Public schema for customer reservations."""
    customer_name: str
    party_size: int
    reservation_date: date
    reservation_time: time
    special_requests: Optional[str] = None


class ReservationCheckIn(SQLModel):
    """Schema for checking in customers."""
    table_id: Optional[UUID] = Field(default=None, description="Assign to specific table")
    notes: Optional[str] = Field(default=None, description="Check-in notes")


class ReservationAssignTable(SQLModel):
    """Schema for assigning table to reservation."""
    table_id: UUID = Field(description="Table to assign to reservation")


class ReservationNoShow(SQLModel):
    """Schema for marking reservation as no-show."""
    notes: Optional[str] = Field(default=None, description="No-show notes")


class ReservationCalendarView(SQLModel):
    """Schema for calendar view of reservations."""
    date: date
    reservations: List[ReservationRead]
    capacity_info: Dict[str, Any] = Field(default_factory=dict)


class ReservationAnalytics(SQLModel):
    """Schema for reservation analytics."""
    total_reservations: int
    confirmed_reservations: int
    completed_reservations: int
    no_shows: int
    cancellations: int
    average_party_size: float
    peak_hours: Dict[str, int] = Field(default_factory=dict)
    occupancy_rate: float