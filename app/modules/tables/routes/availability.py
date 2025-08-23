from typing import List
from datetime import date, time, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.database.session import get_session
from app.shared.auth.deps import get_tenant_context, TenantContext
from app.modules.tables.models.availability import (
    AvailabilityQuery,
    AvailabilityResponse,
    AvailabilityCalendar,
    AvailabilitySlot,
    CapacityOptimization,
)
from app.modules.tables.services.availability import AvailabilityService

router = APIRouter(prefix="/availability", tags=["Availability Management"])


@router.get("/slots", response_model=AvailabilityResponse)
async def get_available_slots(
    date: date = Query(..., description="Date to check availability"),
    party_size: int = Query(..., ge=1, le=20, description="Number of guests"),
    time_preference: time = Query(None, description="Preferred time (optional)"),
    duration_minutes: int = Query(90, ge=30, le=300, description="Expected duration"),
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Get available time slots for a specific date and party size."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    query = AvailabilityQuery(
        date=date,
        party_size=party_size,
        time_preference=time_preference,
        duration_minutes=duration_minutes,
    )
    
    availability = await AvailabilityService.get_available_slots(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
        query=query,
    )
    
    return availability


@router.get("/calendar", response_model=AvailabilityCalendar)
async def get_availability_calendar(
    year: int = Query(..., ge=2020, le=2030),
    month: int = Query(..., ge=1, le=12),
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Get monthly availability calendar."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    calendar = await AvailabilityService.get_monthly_availability(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
        year=year,
        month=month,
    )
    
    return calendar


@router.get("/alternatives", response_model=List[AvailabilitySlot])
async def get_alternative_slots(
    preferred_date: date = Query(default_factory=lambda: date.today() + timedelta(days=1), description="Preferred date"),
    preferred_time: time = Query(default=time(19, 0), description="Preferred time"),
    party_size: int = Query(default=4, ge=1, le=20, description="Number of guests"),
    duration_minutes: int = Query(90, ge=30, le=300, description="Expected duration"),
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Find alternative time slots if preferred time is not available."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    alternatives = await AvailabilityService.find_alternative_slots(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
        preferred_date=preferred_date,
        preferred_time=preferred_time,
        party_size=party_size,
        duration_minutes=duration_minutes,
    )
    
    return alternatives


@router.get("/capacity/optimization", response_model=CapacityOptimization)
async def get_capacity_optimization(
    target_date: date = Query(default_factory=lambda: date.today() + timedelta(days=1), description="Date to analyze"),
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Get capacity optimization suggestions for a specific date."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    optimization = await AvailabilityService.get_capacity_optimization(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
        target_date=target_date,
    )
    
    return optimization


@router.get("/overview")
async def get_availability_overview(
    start_date: date = Query(default_factory=lambda: date.today(), description="Start date for overview"),
    end_date: date = Query(default_factory=lambda: date.today() + timedelta(days=7), description="End date for overview"),
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Get availability overview for a date range."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    # Validate date range
    if end_date < start_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End date must be after start date",
        )
    
    if (end_date - start_date).days > 31:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Date range cannot exceed 31 days",
        )
    
    overview_data = []
    current_date = start_date
    
    while current_date <= end_date:
        query = AvailabilityQuery(
            date=current_date,
            party_size=2,  # Default party size for overview
            duration_minutes=90,
        )
        
        availability = await AvailabilityService.get_available_slots(
            session=session,
            organization_id=tenant_context.organization_id,
            restaurant_id=tenant_context.restaurant_id,
            query=query,
        )
        
        overview_data.append({
            "date": current_date.isoformat(),
            "is_available": not availability.is_fully_booked,
            "available_slots_count": len(availability.available_slots),
            "peak_capacity": max(
                (slot.total_capacity for slot in availability.available_slots),
                default=0
            ),
        })
        
        current_date += timedelta(days=1)
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
        },
        "daily_availability": overview_data,
        "summary": {
            "total_days": len(overview_data),
            "available_days": len([d for d in overview_data if d["is_available"]]),
            "fully_booked_days": len([d for d in overview_data if not d["is_available"]]),
        }
    }