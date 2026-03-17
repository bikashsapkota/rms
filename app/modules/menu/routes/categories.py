from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.database.session import get_session
from app.shared.auth.deps import get_tenant_context, TenantContext, require_manager
from app.modules.menu.models.category import (
    MenuCategory,
    MenuCategoryCreate,
    MenuCategoryUpdate,
    MenuCategoryRead,
    MenuCategoryReadWithItems,
)
from app.modules.menu.services.category import MenuCategoryService

router = APIRouter(prefix="/menu/categories", tags=["Menu Categories"])


@router.get("/", response_model=List[MenuCategoryRead])
async def list_categories(
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
):
    """List menu categories for the restaurant."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    try:
        # Direct query to debug the issue
        from sqlmodel import select
        statement = select(MenuCategory).where(
            MenuCategory.organization_id == tenant_context.organization_id,
            MenuCategory.restaurant_id == tenant_context.restaurant_id,
        )
        
        if not include_inactive:
            statement = statement.where(MenuCategory.is_active == True)
        
        statement = statement.order_by(MenuCategory.sort_order, MenuCategory.name)
        statement = statement.offset(skip).limit(limit)
        
        result = await session.exec(statement)
        categories = result.all()
        
        # Filter out any categories with empty names as a safety measure
        valid_categories = []
        for cat in categories:
            if cat.name and cat.name.strip():
                valid_categories.append(cat)
        
        return valid_categories
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error in categories route: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve categories: {str(e)}",
        )


@router.post("/", response_model=MenuCategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: MenuCategoryCreate,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_manager),
):
    """Create a new menu category."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    category = await MenuCategoryService.create_category(
        session=session,
        category_data=category_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return category


@router.get("/{category_id}", response_model=MenuCategoryReadWithItems)
async def get_category(
    category_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Get a menu category by ID."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    category_data = await MenuCategoryService.get_category_with_stats(
        session=session,
        category_id=category_id,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    if not category_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu category not found",
        )
    
    return MenuCategoryReadWithItems(**category_data)


@router.put("/{category_id}", response_model=MenuCategoryRead)
async def update_category(
    category_id: str,
    category_data: MenuCategoryUpdate,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_manager),
):
    """Update a menu category."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    category = await MenuCategoryService.update_category(
        session=session,
        category_id=category_id,
        category_data=category_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return category


@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_manager),
):
    """Delete a menu category."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    await MenuCategoryService.delete_category(
        session=session,
        category_id=category_id,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return {"message": "Category deleted successfully"}