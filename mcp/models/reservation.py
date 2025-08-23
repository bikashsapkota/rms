"""Reservation data models for MCP."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr
from datetime import date, time, datetime


class ReservationRequest(BaseModel):
    """Request model for creating a reservation."""
    restaurant_id: str
    customer_name: str
    customer_email: EmailStr
    customer_phone: str
    date: date
    time: time
    party_size: int
    special_requests: Optional[str] = None


class ReservationUpdate(BaseModel):
    """Request model for updating a reservation."""
    reservation_id: str
    customer_email: EmailStr
    date: Optional[date] = None
    time: Optional[time] = None
    party_size: Optional[int] = None
    special_requests: Optional[str] = None


class ReservationCancel(BaseModel):
    """Request model for canceling a reservation."""
    reservation_id: str
    customer_email: EmailStr
    reason: Optional[str] = None


class AvailabilityRequest(BaseModel):
    """Request model for checking availability."""
    restaurant_id: str
    date: date
    time: Optional[time] = None
    party_size: int


class ReservationDetails(BaseModel):
    """Reservation details response."""
    id: str
    customer_name: str
    customer_email: str
    customer_phone: str
    date: str
    time: str
    party_size: int
    status: str
    special_requests: Optional[str] = None
    created_at: str
    restaurant_name: Optional[str] = None
    table_number: Optional[str] = None


class AvailabilitySlot(BaseModel):
    """Available time slot."""
    time: str
    available_tables: int
    duration_minutes: int = 120


class AvailabilityResponse(BaseModel):
    """Availability check response."""
    date: str
    party_size: int
    available_slots: list[AvailabilitySlot]
    message: str


class ReservationConfirmation(BaseModel):
    """Reservation confirmation response."""
    reservation_id: str
    confirmation_number: str
    customer_name: str
    date: str
    time: str
    party_size: int
    restaurant_name: str
    status: str
    message: str
    special_requests: Optional[str] = None