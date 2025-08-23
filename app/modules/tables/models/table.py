from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from app.shared.database.base import RestaurantTenantBaseModel

if TYPE_CHECKING:
    from app.shared.models.restaurant import Restaurant
    from app.modules.tables.models.reservation import Reservation
    from app.modules.orders.models.order import Order


class TableBase(SQLModel):
    """Base table model for shared fields."""
    table_number: str = Field(max_length=10, nullable=False)
    capacity: int = Field(nullable=False, description="Maximum seating capacity")
    location: Optional[str] = Field(
        default=None, 
        max_length=100,
        description="Location: 'main_dining', 'patio', 'private', etc."
    )
    status: str = Field(
        default="available",
        max_length=50,
        description="Status: 'available', 'occupied', 'reserved', 'maintenance'"
    )
    coordinates: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON),
        description="Floor plan coordinates: {x: 100, y: 200}"
    )
    is_active: bool = Field(default=True)


class Table(TableBase, RestaurantTenantBaseModel, table=True):
    """Restaurant table model with multi-tenant support."""
    __tablename__ = "tables"
    
    # Relationships
    restaurant: "Restaurant" = Relationship(back_populates="tables")
    reservations: List["Reservation"] = Relationship(back_populates="table")
    # orders: List["Order"] = Relationship(back_populates="table")
    
    # Ensure unique table numbers per restaurant
    __table_args__ = (
        {"extend_existing": True},
    )


class TableCreate(TableBase):
    """Schema for creating tables."""
    pass


class TableUpdate(SQLModel):
    """Schema for updating tables."""
    table_number: Optional[str] = None
    capacity: Optional[int] = None
    location: Optional[str] = None
    status: Optional[str] = None
    coordinates: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class TableRead(TableBase):
    """Schema for reading tables."""
    id: str
    organization_id: str
    restaurant_id: str
    created_at: str
    updated_at: str


class TableReadWithDetails(TableRead):
    """Schema for reading tables with reservation details."""
    active_reservations: int = 0
    upcoming_reservations: int = 0


class TableLayout(SQLModel):
    """Schema for restaurant floor plan layout."""
    tables: List[TableRead]
    layout_settings: Dict[str, Any] = Field(default_factory=dict)


class TableStatusUpdate(SQLModel):
    """Schema for updating table status."""
    status: str = Field(description="New status for the table")
    notes: Optional[str] = Field(default=None, description="Optional status change notes")