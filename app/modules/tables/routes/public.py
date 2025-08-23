from typing import List, Optional, Dict, Any
from datetime import date, time
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.database.session import get_session
import uuid
from app.modules.tables.services.customer import CustomerService
from app.shared.cache import cached
from app.core.config import settings

router = APIRouter(prefix="/public/reservations", tags=["Public Reservations"])


def validate_uuid(uuid_string: str, field_name: str = "ID") -> str:
    """Validate UUID format and return the string."""
    try:
        uuid.UUID(uuid_string)
        return uuid_string
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name} format"
        )


@router.get("/{restaurant_id}/availability")
async def check_availability(
    restaurant_id: str,
    date: date = Query(..., description="Date to check availability"),
    party_size: int = Query(..., ge=1, le=20, description="Number of guests"),
    time_preference: Optional[time] = Query(None, description="Preferred time"),
    duration_minutes: int = Query(90, ge=30, le=300, description="Expected duration"),
    session: AsyncSession = Depends(get_session),
):
    """Check availability for a restaurant (public endpoint)."""
    # Validate UUID format
    validate_uuid(restaurant_id, "restaurant ID")
    
    availability = await CustomerService.get_availability(
        session=session,
        restaurant_id=restaurant_id,
        reservation_date=date,
        party_size=party_size,
        time_preference=time_preference,
        duration_minutes=duration_minutes,
    )
    
    return availability


@router.post("/{restaurant_id}/book")
async def create_reservation(
    restaurant_id: str,
    reservation_data: Dict[str, Any] = Body(...),
    session: AsyncSession = Depends(get_session),
):
    """Create a new reservation (public endpoint)."""
    reservation = await CustomerService.create_reservation(
        session=session,
        restaurant_id=restaurant_id,
        reservation_data=reservation_data,
    )
    
    return reservation


@router.post("/{restaurant_id}/waitlist")
async def join_waitlist(
    restaurant_id: str,
    waitlist_data: Dict[str, Any] = Body(...),
    session: AsyncSession = Depends(get_session),
):
    """Join the restaurant waitlist (public endpoint)."""
    waitlist_entry = await CustomerService.join_waitlist(
        session=session,
        restaurant_id=restaurant_id,
        waitlist_data=waitlist_data,
    )
    
    return waitlist_entry


@router.get("/{restaurant_id}/status")
async def get_reservation_status(
    restaurant_id: str,
    customer_phone: str = Query(..., description="Customer phone number"),
    customer_name: str = Query(..., description="Customer name"),
    session: AsyncSession = Depends(get_session),
):
    """Get reservation status for a customer (public endpoint)."""
    reservations = await CustomerService.get_reservation_status(
        session=session,
        restaurant_id=restaurant_id,
        customer_phone=customer_phone,
        customer_name=customer_name,
    )
    
    return {
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "reservations": reservations,
    }


@router.delete("/{restaurant_id}/cancel/{reservation_id}")
async def cancel_reservation(
    restaurant_id: str,
    reservation_id: str,
    customer_phone: str = Query(..., description="Customer phone number for verification"),
    session: AsyncSession = Depends(get_session),
):
    """Cancel a reservation (public endpoint)."""
    result = await CustomerService.cancel_reservation(
        session=session,
        restaurant_id=restaurant_id,
        reservation_id=reservation_id,
        customer_phone=customer_phone,
    )
    
    return result


@router.get("/{restaurant_id}/waitlist/status")
async def get_waitlist_status(
    restaurant_id: str,
    customer_phone: str = Query(..., description="Customer phone number"),
    customer_name: str = Query(..., description="Customer name"),
    session: AsyncSession = Depends(get_session),
):
    """Get waitlist status for a customer (public endpoint)."""
    waitlist_entries = await CustomerService.get_waitlist_status(
        session=session,
        restaurant_id=restaurant_id,
        customer_phone=customer_phone,
        customer_name=customer_name,
    )
    
    return {
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "waitlist_entries": waitlist_entries,
    }


@router.get("/{restaurant_id}/info")
@cached(ttl=settings.REDIS_TTL_RESTAURANT_INFO, key_prefix="public_restaurant_info")
async def get_restaurant_info(
    restaurant_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get basic restaurant information (public endpoint)."""
    from app.shared.models.restaurant import Restaurant
    from sqlmodel import select
    
    restaurant_stmt = select(Restaurant).where(
        Restaurant.id == restaurant_id,
        Restaurant.is_active == True,
    )
    restaurant_result = await session.exec(restaurant_stmt)
    restaurant = restaurant_result.first()
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found",
        )
    
    return {
        "restaurant_id": str(restaurant.id),
        "name": restaurant.name,
        "address": restaurant.address,
        "phone": restaurant.phone,
        "email": restaurant.email,
        "settings": restaurant.settings,
    }