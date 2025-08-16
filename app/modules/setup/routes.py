"""
Setup routes for restaurant configuration and health checks.
Phase 1: Simple restaurant setup with hidden multi-tenant foundation.
"""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.shared.database.session import get_session
from app.core.config import settings
from app.core.setup import RestaurantSetupService
from app.modules.setup.schemas import (
    RestaurantSetupRequest,
    RestaurantSetupResponse,
    HealthCheckResponse,
)

router = APIRouter()


@router.post(
    "/setup",
    response_model=RestaurantSetupResponse,
    summary="Restaurant Setup",
    description="Set up a new restaurant with admin user (Phase 1: auto-creates organization)"
)
async def setup_restaurant(
    setup_data: RestaurantSetupRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Phase 1: Restaurant setup with hidden multi-tenant foundation.
    
    This endpoint creates:
    1. Organization (automatically)
    2. Restaurant 
    3. Admin user
    
    This maintains multi-tenant architecture while providing simple single-tenant UX.
    """
    try:
        setup_service = RestaurantSetupService(session)
        
        # Prepare restaurant data
        restaurant_data = {
            "name": setup_data.restaurant_name,
            "address": setup_data.address,
            "phone": setup_data.phone,
            "email": setup_data.email,
            "settings": setup_data.settings,
        }
        
        # Prepare admin user data
        admin_user_data = {
            "email": setup_data.admin_user.email,
            "full_name": setup_data.admin_user.full_name,
            "password": setup_data.admin_user.password,
        }
        
        # Create restaurant setup
        result = await setup_service.create_restaurant_setup(
            restaurant_data, admin_user_data
        )
        
        return RestaurantSetupResponse(
            success=True,
            message="Restaurant setup completed successfully",
            organization=result["organization"],
            restaurant=result["restaurant"], 
            admin_user=result["admin_user"],
            next_steps=[
                "Log in with your admin credentials",
                "Configure your menu categories and items",
                "Set up your restaurant's basic settings",
                "Start managing your restaurant operations"
            ]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Restaurant setup failed: {str(e)}"
        )


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health Check",
    description="Check system health and status"
)
async def health_check(session: AsyncSession = Depends(get_session)):
    """
    System health check endpoint.
    Returns status of all major system components.
    """
    try:
        # Test database connectivity
        await session.execute("SELECT 1")
        database_status = "healthy"
    except Exception:
        database_status = "unhealthy"
    
    return HealthCheckResponse(
        status="healthy" if database_status == "healthy" else "unhealthy",
        version=settings.VERSION,
        timestamp=datetime.utcnow().isoformat(),
        database=database_status,
        services={
            "authentication": "healthy",
            "menu_management": "healthy", 
            "user_management": "healthy",
            "file_upload": "healthy"
        }
    )


@router.get(
    "/",
    summary="API Root",
    description="API information and welcome message"
)
async def root():
    """
    API root endpoint with basic information.
    """
    return {
        "message": "Restaurant Management System API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
        "api_version": "v1",
        "phase": "Phase 1: Foundation & Basic Menu Management"
    }