from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.database.session import get_session
from app.shared.auth.deps import get_tenant_context, TenantContext, require_manager
import uuid
from app.modules.tables.models.table import (
    TableCreate,
    TableUpdate,
    TableRead,
    TableReadWithDetails,
    TableLayout,
    TableStatusUpdate,
)
from app.modules.tables.services.table import TableService

router = APIRouter(prefix="/tables", tags=["Table Management"])


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


@router.get("/", response_model=List[TableRead])
async def list_tables(
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    location: Optional[str] = Query(None, description="Filter by location"),
    status: Optional[str] = Query(None, description="Filter by status"),
    include_inactive: bool = Query(False, description="Include inactive tables"),
):
    """List all tables for the restaurant."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    tables = await TableService.get_tables(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
        skip=skip,
        limit=limit,
        location=location,
        status=status,
        include_inactive=include_inactive,
    )
    
    return [
        TableRead(
            id=str(table.id),
            table_number=table.table_number,
            capacity=table.capacity,
            location=table.location,
            status=table.status,
            coordinates=table.coordinates,
            is_active=table.is_active,
            organization_id=str(table.organization_id),
            restaurant_id=str(table.restaurant_id),
            created_at=table.created_at.isoformat(),
            updated_at=table.updated_at.isoformat(),
        )
        for table in tables
    ]


@router.post("/", response_model=TableRead)
async def create_table(
    table_data: TableCreate,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_manager),
):
    """Create a new table."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    table = await TableService.create_table(
        session=session,
        table_data=table_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return TableRead(
        id=str(table.id),
        table_number=table.table_number,
        capacity=table.capacity,
        location=table.location,
        status=table.status,
        coordinates=table.coordinates,
        is_active=table.is_active,
        organization_id=str(table.organization_id),
        restaurant_id=str(table.restaurant_id),
        created_at=table.created_at.isoformat(),
        updated_at=table.updated_at.isoformat(),
    )


@router.get("/{table_id}", response_model=TableReadWithDetails)
async def get_table(
    table_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Get a table by ID with details."""
    # Validate UUID format
    validate_uuid(table_id, "table ID")
    
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    table_data = await TableService.get_table_with_details(
        session=session,
        table_id=table_id,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    if not table_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found",
        )
    
    return TableReadWithDetails(**table_data)


@router.put("/{table_id}", response_model=TableRead)
async def update_table(
    table_id: str,
    table_data: TableUpdate,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_manager),
):
    """Update a table."""
    # Validate UUID format
    validate_uuid(table_id, "table ID")
    
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    table = await TableService.update_table(
        session=session,
        table_id=table_id,
        table_data=table_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return TableRead(
        id=str(table.id),
        table_number=table.table_number,
        capacity=table.capacity,
        location=table.location,
        status=table.status,
        coordinates=table.coordinates,
        is_active=table.is_active,
        organization_id=str(table.organization_id),
        restaurant_id=str(table.restaurant_id),
        created_at=table.created_at.isoformat(),
        updated_at=table.updated_at.isoformat(),
    )


@router.delete("/{table_id}")
async def delete_table(
    table_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_manager),
):
    """Delete a table."""
    # Validate UUID format
    validate_uuid(table_id, "table ID")
    
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    await TableService.delete_table(
        session=session,
        table_id=table_id,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return {"message": "Table deleted successfully"}


@router.put("/{table_id}/status", response_model=TableRead)
async def update_table_status(
    table_id: str,
    status_data: TableStatusUpdate,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_manager),
):
    """Update table status."""
    # Validate UUID format
    validate_uuid(table_id, "table ID")
    
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    table = await TableService.update_table_status(
        session=session,
        table_id=table_id,
        status_data=status_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return TableRead(
        id=str(table.id),
        table_number=table.table_number,
        capacity=table.capacity,
        location=table.location,
        status=table.status,
        coordinates=table.coordinates,
        is_active=table.is_active,
        organization_id=str(table.organization_id),
        restaurant_id=str(table.restaurant_id),
        created_at=table.created_at.isoformat(),
        updated_at=table.updated_at.isoformat(),
    )


@router.get("/layout/restaurant", response_model=TableLayout)
async def get_restaurant_layout(
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Get restaurant floor plan layout."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    layout_data = await TableService.get_restaurant_layout(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return TableLayout(
        tables=[TableRead(**table) for table in layout_data["tables"]],
        layout_settings=layout_data["layout_settings"],
    )


@router.get("/availability/overview")
async def get_availability_overview(
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Get real-time table availability overview."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    availability = await TableService.get_availability_overview(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return availability


@router.get("/analytics/utilization")
async def get_table_analytics(
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    days_back: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
):
    """Get table utilization analytics."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    analytics = await TableService.get_table_analytics(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
        days_back=days_back,
    )
    
    return analytics