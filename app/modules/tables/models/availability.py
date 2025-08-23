from typing import List, Optional, Dict, Any
from datetime import date, time
from sqlmodel import SQLModel, Field


class AvailabilitySlot(SQLModel):
    """Available time slot for reservations."""
    time: time
    available_tables: int
    total_capacity: int
    is_available: bool = True


class DayAvailability(SQLModel):
    """Availability for a specific date."""
    date: date
    slots: List[AvailabilitySlot]
    is_open: bool = True
    special_hours: Optional[Dict[str, Any]] = None


class AvailabilityCalendar(SQLModel):
    """Monthly availability calendar."""
    year: int
    month: int
    days: List[DayAvailability]


class AvailabilityQuery(SQLModel):
    """Query parameters for availability check."""
    date: date
    party_size: int
    time_preference: Optional[time] = None
    duration_minutes: int = Field(default=90)


class AvailabilityResponse(SQLModel):
    """Response for availability check."""
    date: date
    available_slots: List[AvailabilitySlot]
    recommendations: List[AvailabilitySlot] = Field(default_factory=list)
    is_fully_booked: bool = False


class BlackoutPeriod(SQLModel):
    """Schema for blocking time periods."""
    start_date: date
    end_date: date
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    reason: str = Field(description="Reason for blackout")
    affects_all_tables: bool = Field(default=True)
    specific_tables: List[str] = Field(default_factory=list)


class AvailabilityRules(SQLModel):
    """Rules for availability management."""
    min_advance_booking_hours: int = Field(default=1)
    max_advance_booking_days: int = Field(default=30)
    default_duration_minutes: int = Field(default=90)
    buffer_time_minutes: int = Field(default=15)
    max_party_size: int = Field(default=8)
    operating_hours: Dict[str, Dict[str, str]] = Field(
        default_factory=dict,
        description="Operating hours by day: {'monday': {'open': '11:00', 'close': '22:00'}}"
    )


class CapacityOptimization(SQLModel):
    """Capacity optimization suggestions."""
    date: date
    current_occupancy_rate: float
    suggested_improvements: List[str]
    peak_hours: List[time]
    recommended_actions: List[str]