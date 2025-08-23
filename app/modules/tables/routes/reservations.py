from typing import List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.database.session import get_session
from app.shared.auth.deps import get_tenant_context, TenantContext, require_manager, require_staff
import uuid
from app.modules.tables.models.reservation import (
    ReservationCreate,
    ReservationUpdate,
    ReservationRead,
    ReservationReadWithDetails,
    ReservationCheckIn,
    ReservationAssignTable,
    ReservationNoShow,
    ReservationCalendarView,
    ReservationAnalytics,
)
from app.modules.tables.services.reservation import ReservationService

router = APIRouter(prefix="/reservations", tags=["Reservation Management"])


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


@router.get("/", response_model=List[ReservationReadWithDetails])
async def list_reservations(
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    reservation_date: Optional[date] = Query(None, description="Filter by date"),
    status: Optional[str] = Query(None, description="Filter by status"),
    table_id: Optional[str] = Query(None, description="Filter by table"),
):
    """List reservations for the restaurant."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    reservations = await ReservationService.get_reservations(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
        skip=skip,
        limit=limit,
        reservation_date=reservation_date,
        status=status,
        table_id=table_id,
    )
    
    # Get detailed information for each reservation
    detailed_reservations = []
    for reservation in reservations:
        # Get table info if assigned
        table_number = None
        table_capacity = None
        if reservation.table_id:
            from app.modules.tables.services.table import TableService
            table = await TableService.get_table_by_id(
                session=session,
                table_id=str(reservation.table_id),
                organization_id=tenant_context.organization_id,
                restaurant_id=tenant_context.restaurant_id,
            )
            if table:
                table_number = table.table_number
                table_capacity = table.capacity
        
        detailed_reservations.append(
            ReservationReadWithDetails(
                id=str(reservation.id),
                customer_name=reservation.customer_name,
                customer_phone=reservation.customer_phone,
                customer_email=reservation.customer_email,
                party_size=reservation.party_size,
                reservation_date=reservation.reservation_date,
                reservation_time=reservation.reservation_time,
                duration_minutes=reservation.duration_minutes,
                status=reservation.status,
                special_requests=reservation.special_requests,
                customer_preferences=reservation.customer_preferences,
                organization_id=str(reservation.organization_id),
                restaurant_id=str(reservation.restaurant_id),
                table_id=str(reservation.table_id) if reservation.table_id else None,
                table_number=table_number,
                table_capacity=table_capacity,
                created_at=reservation.created_at.isoformat(),
                updated_at=reservation.updated_at.isoformat(),
            )
        )
    
    return detailed_reservations


@router.post("/", response_model=ReservationRead)
async def create_reservation(
    reservation_data: ReservationCreate,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_staff),
):
    """Create a new reservation."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    reservation = await ReservationService.create_reservation(
        session=session,
        reservation_data=reservation_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return ReservationRead(
        id=str(reservation.id),
        customer_name=reservation.customer_name,
        customer_phone=reservation.customer_phone,
        customer_email=reservation.customer_email,
        party_size=reservation.party_size,
        reservation_date=reservation.reservation_date,
        reservation_time=reservation.reservation_time,
        duration_minutes=reservation.duration_minutes,
        status=reservation.status,
        special_requests=reservation.special_requests,
        customer_preferences=reservation.customer_preferences,
        organization_id=str(reservation.organization_id),
        restaurant_id=str(reservation.restaurant_id),
        table_id=str(reservation.table_id) if reservation.table_id else None,
        created_at=reservation.created_at.isoformat(),
        updated_at=reservation.updated_at.isoformat(),
    )


@router.get("/{reservation_id}", response_model=ReservationReadWithDetails)
async def get_reservation(
    reservation_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Get a reservation by ID."""
    # Validate UUID format
    validate_uuid(reservation_id, "reservation ID")
    
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    reservation = await ReservationService.get_reservation_by_id(
        session=session,
        reservation_id=reservation_id,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    if not reservation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reservation not found",
        )
    
    # Get table info if assigned
    table_number = None
    table_capacity = None
    if reservation.table_id:
        from app.modules.tables.services.table import TableService
        table = await TableService.get_table_by_id(
            session=session,
            table_id=str(reservation.table_id),
            organization_id=tenant_context.organization_id,
            restaurant_id=tenant_context.restaurant_id,
        )
        if table:
            table_number = table.table_number
            table_capacity = table.capacity
    
    return ReservationReadWithDetails(
        id=str(reservation.id),
        customer_name=reservation.customer_name,
        customer_phone=reservation.customer_phone,
        customer_email=reservation.customer_email,
        party_size=reservation.party_size,
        reservation_date=reservation.reservation_date,
        reservation_time=reservation.reservation_time,
        duration_minutes=reservation.duration_minutes,
        status=reservation.status,
        special_requests=reservation.special_requests,
        customer_preferences=reservation.customer_preferences,
        organization_id=str(reservation.organization_id),
        restaurant_id=str(reservation.restaurant_id),
        table_id=str(reservation.table_id) if reservation.table_id else None,
        table_number=table_number,
        table_capacity=table_capacity,
        created_at=reservation.created_at.isoformat(),
        updated_at=reservation.updated_at.isoformat(),
    )


@router.put("/{reservation_id}", response_model=ReservationRead)
@router.patch("/{reservation_id}", response_model=ReservationRead)
async def update_reservation(
    reservation_id: str,
    reservation_data: ReservationUpdate,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_staff),
):
    """Update a reservation (supports both PUT and PATCH)."""
    # Validate UUID format
    validate_uuid(reservation_id, "reservation ID")
    
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    reservation = await ReservationService.update_reservation(
        session=session,
        reservation_id=reservation_id,
        reservation_data=reservation_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return ReservationRead(
        id=str(reservation.id),
        customer_name=reservation.customer_name,
        customer_phone=reservation.customer_phone,
        customer_email=reservation.customer_email,
        party_size=reservation.party_size,
        reservation_date=reservation.reservation_date,
        reservation_time=reservation.reservation_time,
        duration_minutes=reservation.duration_minutes,
        status=reservation.status,
        special_requests=reservation.special_requests,
        customer_preferences=reservation.customer_preferences,
        organization_id=str(reservation.organization_id),
        restaurant_id=str(reservation.restaurant_id),
        table_id=str(reservation.table_id) if reservation.table_id else None,
        created_at=reservation.created_at.isoformat(),
        updated_at=reservation.updated_at.isoformat(),
    )


@router.delete("/{reservation_id}")
async def cancel_reservation(
    reservation_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_staff),
):
    """Cancel a reservation."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    await ReservationService.cancel_reservation(
        session=session,
        reservation_id=reservation_id,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return {"message": "Reservation cancelled successfully"}


@router.post("/{reservation_id}/checkin", response_model=ReservationRead)
async def checkin_reservation(
    reservation_id: str,
    checkin_data: ReservationCheckIn = ReservationCheckIn(),
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_staff),
):
    """Check in a customer for their reservation."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    reservation = await ReservationService.check_in_reservation(
        session=session,
        reservation_id=reservation_id,
        checkin_data=checkin_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return ReservationRead(
        id=str(reservation.id),
        customer_name=reservation.customer_name,
        customer_phone=reservation.customer_phone,
        customer_email=reservation.customer_email,
        party_size=reservation.party_size,
        reservation_date=reservation.reservation_date,
        reservation_time=reservation.reservation_time,
        duration_minutes=reservation.duration_minutes,
        status=reservation.status,
        special_requests=reservation.special_requests,
        customer_preferences=reservation.customer_preferences,
        organization_id=str(reservation.organization_id),
        restaurant_id=str(reservation.restaurant_id),
        table_id=str(reservation.table_id) if reservation.table_id else None,
        created_at=reservation.created_at.isoformat(),
        updated_at=reservation.updated_at.isoformat(),
    )


@router.post("/{reservation_id}/seat", response_model=ReservationRead)
async def assign_table_to_reservation(
    reservation_id: str,
    table_data: ReservationAssignTable,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_staff),
):
    """Assign a table to a reservation."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    reservation = await ReservationService.assign_table(
        session=session,
        reservation_id=reservation_id,
        table_data=table_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return ReservationRead(
        id=str(reservation.id),
        customer_name=reservation.customer_name,
        customer_phone=reservation.customer_phone,
        customer_email=reservation.customer_email,
        party_size=reservation.party_size,
        reservation_date=reservation.reservation_date,
        reservation_time=reservation.reservation_time,
        duration_minutes=reservation.duration_minutes,
        status=reservation.status,
        special_requests=reservation.special_requests,
        customer_preferences=reservation.customer_preferences,
        organization_id=str(reservation.organization_id),
        restaurant_id=str(reservation.restaurant_id),
        table_id=str(reservation.table_id) if reservation.table_id else None,
        created_at=reservation.created_at.isoformat(),
        updated_at=reservation.updated_at.isoformat(),
    )


@router.post("/{reservation_id}/no-show", response_model=ReservationRead)
async def mark_reservation_no_show(
    reservation_id: str,
    no_show_data: ReservationNoShow,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_staff),
):
    """Mark a reservation as no-show."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    reservation = await ReservationService.mark_no_show(
        session=session,
        reservation_id=reservation_id,
        no_show_data=no_show_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return ReservationRead(
        id=str(reservation.id),
        customer_name=reservation.customer_name,
        customer_phone=reservation.customer_phone,
        customer_email=reservation.customer_email,
        party_size=reservation.party_size,
        reservation_date=reservation.reservation_date,
        reservation_time=reservation.reservation_time,
        duration_minutes=reservation.duration_minutes,
        status=reservation.status,
        special_requests=reservation.special_requests,
        customer_preferences=reservation.customer_preferences,
        organization_id=str(reservation.organization_id),
        restaurant_id=str(reservation.restaurant_id),
        table_id=str(reservation.table_id) if reservation.table_id else None,
        created_at=reservation.created_at.isoformat(),
        updated_at=reservation.updated_at.isoformat(),
    )


@router.get("/today/overview")
async def get_today_reservations(
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Get today's reservations overview."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    today_reservations = await ReservationService.get_today_reservations(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return {
        "date": date.today().isoformat(),
        "total_reservations": len(today_reservations),
        "reservations": today_reservations,
    }


@router.get("/calendar/view")
async def get_reservation_calendar(
    start_date: date = Query(default_factory=lambda: date.today(), description="Start date for calendar"),
    end_date: date = Query(default_factory=lambda: date.today() + timedelta(days=30), description="End date for calendar"),
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Get reservation calendar view for date range."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    calendar_data = await ReservationService.get_reservation_calendar(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
        start_date=start_date,
        end_date=end_date,
    )
    
    return calendar_data


@router.get("/analytics/summary")
async def get_reservation_analytics(
    start_date: date = Query(default_factory=lambda: date.today() - timedelta(days=30), description="Start date for analytics"),
    end_date: date = Query(default_factory=lambda: date.today(), description="End date for analytics"),
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Get reservation analytics for date range."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    analytics = await ReservationService.get_reservation_analytics(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
        start_date=start_date,
        end_date=end_date,
    )
    
    return analytics