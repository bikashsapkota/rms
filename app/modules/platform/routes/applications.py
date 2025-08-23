"""
Platform application management API routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.shared.auth.deps import get_current_active_user
from app.shared.database.session import get_session
from app.shared.models.user import User
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.platform.models.application import (
    RestaurantApplicationCreate,
    RestaurantApplicationUpdate,
    RestaurantApplicationRead,
    RestaurantApplicationApproval,
    RestaurantApplicationRejection,
    ApplicationStats,
)
from app.modules.platform.services.application import PlatformApplicationService

router = APIRouter(prefix="/platform", tags=["Platform Management"])


def verify_platform_admin(current_user: User = Depends(get_current_active_user)):
    """Verify user has platform admin role."""
    if current_user.role != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform admin access required"
        )
    return current_user


def verify_admin_access(current_user: User = Depends(get_current_active_user)):
    """Verify user has admin or platform_admin role (Phase 1 compatible)."""
    if current_user.role not in ["admin", "platform_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/applications", response_model=List[RestaurantApplicationRead])
async def list_applications(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of records to return"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(verify_admin_access),
):
    """List restaurant applications (platform admin only)."""
    applications = await PlatformApplicationService.get_applications(
        session=session,
        skip=skip,
        limit=limit,
        status=status_filter,
    )
    return [RestaurantApplicationRead.model_validate(app) for app in applications]


@router.get("/applications/{application_id}", response_model=RestaurantApplicationRead)
async def get_application(
    application_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(verify_admin_access),
):
    """Get a restaurant application by ID (platform admin only)."""
    application = await PlatformApplicationService.get_application_by_id(
        session=session,
        application_id=application_id,
    )
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    return RestaurantApplicationRead.model_validate(application)


@router.put("/applications/{application_id}", response_model=RestaurantApplicationRead)
async def update_application(
    application_id: str,
    update_data: RestaurantApplicationUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(verify_admin_access),
):
    """Update a restaurant application (admin access)."""
    application = await PlatformApplicationService.update_application(
        session=session,
        application_id=application_id,
        update_data=update_data,
    )
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found"
        )
    return RestaurantApplicationRead.model_validate(application)


@router.post("/applications/{application_id}/approve")
async def approve_application(
    application_id: str,
    approval_data: RestaurantApplicationApproval,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(verify_platform_admin),
):
    """Approve a restaurant application (platform admin only)."""
    success = await PlatformApplicationService.approve_application(
        session=session,
        application_id=application_id,
        admin_notes=approval_data.admin_notes,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found or already processed"
        )
    return {
        "message": "Application approved successfully",
        "application_id": application_id,
        "status": "approved"
    }


@router.post("/applications/{application_id}/reject")
async def reject_application(
    application_id: str,
    rejection_data: RestaurantApplicationRejection,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(verify_platform_admin),
):
    """Reject a restaurant application (platform admin only)."""
    success = await PlatformApplicationService.reject_application(
        session=session,
        application_id=application_id,
        admin_notes=rejection_data.admin_notes,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found or already processed"
        )
    return {
        "message": "Application rejected",
        "application_id": application_id,
        "status": "rejected",
        "reason": rejection_data.admin_notes
    }


@router.get("/applications/stats/summary", response_model=ApplicationStats)
async def get_application_stats(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(verify_platform_admin),
):
    """Get application statistics (platform admin only)."""
    return await PlatformApplicationService.get_application_stats(session=session)


# Phase 1: Admin endpoint for creating applications
@router.post("/applications", response_model=RestaurantApplicationRead)
async def create_application(
    application_data: RestaurantApplicationCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(verify_admin_access),
):
    """Create a new application (admin access)."""
    application = await PlatformApplicationService.create_application(
        session=session,
        application_data=application_data,
    )
    return RestaurantApplicationRead.model_validate(application)


# Public endpoint for submitting applications
@router.post("/applications/submit", response_model=RestaurantApplicationRead)
async def submit_application(
    application_data: RestaurantApplicationCreate,
    session: AsyncSession = Depends(get_session),
):
    """Submit a new restaurant application (public endpoint)."""
    application = await PlatformApplicationService.create_application(
        session=session,
        application_data=application_data,
    )
    return RestaurantApplicationRead.model_validate(application)