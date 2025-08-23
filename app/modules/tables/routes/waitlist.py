from typing import List, Optional
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.database.session import get_session
from app.shared.auth.deps import get_tenant_context, TenantContext, require_staff
import uuid
from app.modules.tables.models.waitlist import (
    WaitlistCreate,
    WaitlistUpdate,
    WaitlistRead,
    WaitlistNotify,
)
from app.modules.tables.services.waitlist import WaitlistService

router = APIRouter(prefix="/waitlist", tags=["Waitlist Management"])


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


@router.get("/", response_model=List[WaitlistRead])
async def get_waitlist(
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = Query(None, description="Filter by status"),
    preferred_date: Optional[date] = Query(None, description="Filter by preferred date"),
):
    """Get current waitlist for the restaurant."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    waitlist_entries = await WaitlistService.get_waitlist(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
        skip=skip,
        limit=limit,
        status=status,
        preferred_date=preferred_date,
    )
    
    return [
        WaitlistRead(
            id=str(entry.id),
            customer_name=entry.customer_name,
            customer_phone=entry.customer_phone,
            customer_email=entry.customer_email,
            party_size=entry.party_size,
            preferred_date=entry.preferred_date,
            preferred_time=entry.preferred_time,
            status=entry.status,
            priority_score=entry.priority_score,
            notes=entry.notes,
            organization_id=str(entry.organization_id),
            restaurant_id=str(entry.restaurant_id),
            created_at=entry.created_at.isoformat(),
            updated_at=entry.updated_at.isoformat(),
        )
        for entry in waitlist_entries
    ]


@router.post("/", response_model=WaitlistRead)
async def add_to_waitlist(
    waitlist_data: WaitlistCreate,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_staff),
):
    """Add a customer to the waitlist."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    waitlist_entry = await WaitlistService.add_to_waitlist(
        session=session,
        waitlist_data=waitlist_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return WaitlistRead(
        id=str(waitlist_entry.id),
        customer_name=waitlist_entry.customer_name,
        customer_phone=waitlist_entry.customer_phone,
        customer_email=waitlist_entry.customer_email,
        party_size=waitlist_entry.party_size,
        preferred_date=waitlist_entry.preferred_date,
        preferred_time=waitlist_entry.preferred_time,
        status=waitlist_entry.status,
        priority_score=waitlist_entry.priority_score,
        notes=waitlist_entry.notes,
        organization_id=str(waitlist_entry.organization_id),
        restaurant_id=str(waitlist_entry.restaurant_id),
        created_at=waitlist_entry.created_at.isoformat(),
        updated_at=waitlist_entry.updated_at.isoformat(),
    )


@router.get("/{waitlist_id}", response_model=WaitlistRead)
async def get_waitlist_entry(
    waitlist_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Get a waitlist entry by ID."""
    # Validate UUID format
    validate_uuid(waitlist_id, "waitlist ID")
    
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    waitlist_entry = await WaitlistService.get_waitlist_entry_by_id(
        session=session,
        waitlist_id=waitlist_id,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    if not waitlist_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Waitlist entry not found",
        )
    
    return WaitlistRead(
        id=str(waitlist_entry.id),
        customer_name=waitlist_entry.customer_name,
        customer_phone=waitlist_entry.customer_phone,
        customer_email=waitlist_entry.customer_email,
        party_size=waitlist_entry.party_size,
        preferred_date=waitlist_entry.preferred_date,
        preferred_time=waitlist_entry.preferred_time,
        status=waitlist_entry.status,
        priority_score=waitlist_entry.priority_score,
        notes=waitlist_entry.notes,
        organization_id=str(waitlist_entry.organization_id),
        restaurant_id=str(waitlist_entry.restaurant_id),
        created_at=waitlist_entry.created_at.isoformat(),
        updated_at=waitlist_entry.updated_at.isoformat(),
    )


@router.put("/{waitlist_id}", response_model=WaitlistRead)
@router.patch("/{waitlist_id}", response_model=WaitlistRead)
async def update_waitlist_entry(
    waitlist_id: str,
    waitlist_data: WaitlistUpdate,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_staff),
):
    """Update a waitlist entry."""
    # Validate UUID format
    validate_uuid(waitlist_id, "waitlist ID")
    
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    waitlist_entry = await WaitlistService.update_waitlist_entry(
        session=session,
        waitlist_id=waitlist_id,
        waitlist_data=waitlist_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return WaitlistRead(
        id=str(waitlist_entry.id),
        customer_name=waitlist_entry.customer_name,
        customer_phone=waitlist_entry.customer_phone,
        customer_email=waitlist_entry.customer_email,
        party_size=waitlist_entry.party_size,
        preferred_date=waitlist_entry.preferred_date,
        preferred_time=waitlist_entry.preferred_time,
        status=waitlist_entry.status,
        priority_score=waitlist_entry.priority_score,
        notes=waitlist_entry.notes,
        organization_id=str(waitlist_entry.organization_id),
        restaurant_id=str(waitlist_entry.restaurant_id),
        created_at=waitlist_entry.created_at.isoformat(),
        updated_at=waitlist_entry.updated_at.isoformat(),
    )


@router.delete("/{waitlist_id}")
async def remove_from_waitlist(
    waitlist_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_staff),
):
    """Remove a customer from the waitlist."""
    # Validate UUID format
    validate_uuid(waitlist_id, "waitlist ID")
    
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    await WaitlistService.remove_from_waitlist(
        session=session,
        waitlist_id=waitlist_id,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return {"message": "Customer removed from waitlist successfully"}


@router.put("/{waitlist_id}/notify", response_model=WaitlistRead)
@router.patch("/{waitlist_id}/notify", response_model=WaitlistRead)
@router.post("/{waitlist_id}/notify", response_model=WaitlistRead)
async def notify_waitlist_customer(
    waitlist_id: str,
    notify_data: WaitlistNotify = WaitlistNotify(),
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_staff),
):
    """Notify a customer from the waitlist about availability."""
    # Validate UUID format
    validate_uuid(waitlist_id, "waitlist ID")
    
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    waitlist_entry = await WaitlistService.notify_customer(
        session=session,
        waitlist_id=waitlist_id,
        notify_data=notify_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return WaitlistRead(
        id=str(waitlist_entry.id),
        customer_name=waitlist_entry.customer_name,
        customer_phone=waitlist_entry.customer_phone,
        customer_email=waitlist_entry.customer_email,
        party_size=waitlist_entry.party_size,
        preferred_date=waitlist_entry.preferred_date,
        preferred_time=waitlist_entry.preferred_time,
        status=waitlist_entry.status,
        priority_score=waitlist_entry.priority_score,
        notes=waitlist_entry.notes,
        organization_id=str(waitlist_entry.organization_id),
        restaurant_id=str(waitlist_entry.restaurant_id),
        created_at=waitlist_entry.created_at.isoformat(),
        updated_at=waitlist_entry.updated_at.isoformat(),
    )


@router.put("/{waitlist_id}/seated", response_model=WaitlistRead)
@router.patch("/{waitlist_id}/seated", response_model=WaitlistRead)
@router.post("/{waitlist_id}/seated", response_model=WaitlistRead)
async def mark_waitlist_customer_seated(
    waitlist_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_staff),
):
    """Mark a waitlist customer as seated."""
    # Validate UUID format
    validate_uuid(waitlist_id, "waitlist ID")
    
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    waitlist_entry = await WaitlistService.mark_as_seated(
        session=session,
        waitlist_id=waitlist_id,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return WaitlistRead(
        id=str(waitlist_entry.id),
        customer_name=waitlist_entry.customer_name,
        customer_phone=waitlist_entry.customer_phone,
        customer_email=waitlist_entry.customer_email,
        party_size=waitlist_entry.party_size,
        preferred_date=waitlist_entry.preferred_date,
        preferred_time=waitlist_entry.preferred_time,
        status=waitlist_entry.status,
        priority_score=waitlist_entry.priority_score,
        notes=waitlist_entry.notes,
        organization_id=str(waitlist_entry.organization_id),
        restaurant_id=str(waitlist_entry.restaurant_id),
        created_at=waitlist_entry.created_at.isoformat(),
        updated_at=waitlist_entry.updated_at.isoformat(),
    )


@router.get("/analytics/summary")
async def get_waitlist_analytics(
    start_date: date = Query(default_factory=lambda: date.today() - timedelta(days=30), description="Start date for analytics"),
    end_date: date = Query(default_factory=lambda: date.today(), description="End date for analytics"),
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Get waitlist analytics for date range."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    analytics = await WaitlistService.get_waitlist_analytics(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
        start_date=start_date,
        end_date=end_date,
    )
    
    return analytics


@router.get("/availability/check")
async def check_waitlist_availability(
    target_date: Optional[date] = Query(None, description="Check availability for specific date"),
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Check availability for customers on waitlist and get notification suggestions."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    suggestions = await WaitlistService.check_availability_for_waitlist(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
        target_date=target_date,
    )
    
    return {
        "target_date": target_date.isoformat() if target_date else None,
        "notification_suggestions": suggestions,
        "total_suggestions": len(suggestions),
    }