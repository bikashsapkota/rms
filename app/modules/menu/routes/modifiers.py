"""
Menu modifier API routes.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query

from app.shared.auth.deps import get_current_active_user
from app.shared.database.session import get_session
from app.shared.models.user import User
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.menu.models.modifier import (
    ModifierCreate,
    ModifierUpdate,
    ModifierRead,
    ModifierReadWithItems,
    MenuItemModifierAssignment,
    MenuItemModifierRead,
)
from app.modules.menu.services.modifier import ModifierService

router = APIRouter(prefix="/menu/modifiers", tags=["Menu Modifiers"])


@router.get("/", response_model=List[ModifierReadWithItems])
async def list_modifiers(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Number of records to return"),
    modifier_type: Optional[str] = Query(None, description="Filter by modifier type"),
    include_inactive: bool = Query(False, description="Include inactive modifiers"),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """List menu modifiers for the restaurant."""
    return await ModifierService.get_modifiers(
        session=session,
        organization_id=current_user.organization_id,
        restaurant_id=current_user.restaurant_id,
        skip=skip,
        limit=limit,
        modifier_type=modifier_type,
        include_inactive=include_inactive,
    )


@router.post("/", response_model=ModifierRead, status_code=status.HTTP_201_CREATED)
async def create_modifier(
    modifier_data: ModifierCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new menu modifier."""
    modifier = await ModifierService.create_modifier(
        session=session,
        modifier_data=modifier_data,
        organization_id=current_user.organization_id,
        restaurant_id=current_user.restaurant_id,
    )
    
    return ModifierRead(
        id=modifier.id,
        name=modifier.name,
        description=modifier.description,
        modifier_type=modifier.modifier_type,
        price_adjustment=modifier.price_adjustment,
        is_required=modifier.is_required,
        sort_order=modifier.sort_order,
        is_active=modifier.is_active,
        organization_id=modifier.organization_id,
        restaurant_id=modifier.restaurant_id,
        created_at=modifier.created_at.isoformat(),
        updated_at=modifier.updated_at.isoformat(),
    )


@router.get("/{modifier_id}", response_model=ModifierRead)
async def get_modifier(
    modifier_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Get a menu modifier by ID."""
    modifier = await ModifierService.get_modifier_by_id(
        session=session,
        modifier_id=modifier_id,
        organization_id=current_user.organization_id,
        restaurant_id=current_user.restaurant_id,
    )
    if not modifier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modifier not found"
        )
    return ModifierRead(
        id=modifier.id,
        name=modifier.name,
        description=modifier.description,
        modifier_type=modifier.modifier_type,
        price_adjustment=modifier.price_adjustment,
        is_required=modifier.is_required,
        sort_order=modifier.sort_order,
        is_active=modifier.is_active,
        organization_id=modifier.organization_id,
        restaurant_id=modifier.restaurant_id,
        created_at=modifier.created_at.isoformat(),
        updated_at=modifier.updated_at.isoformat(),
    )


@router.put("/{modifier_id}", response_model=ModifierRead)
async def update_modifier(
    modifier_id: str,
    modifier_data: ModifierUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Update a menu modifier."""
    modifier = await ModifierService.update_modifier(
        session=session,
        modifier_id=modifier_id,
        modifier_data=modifier_data,
        organization_id=current_user.organization_id,
        restaurant_id=current_user.restaurant_id,
    )
    if not modifier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modifier not found"
        )
    return ModifierRead(
        id=modifier.id,
        name=modifier.name,
        description=modifier.description,
        modifier_type=modifier.modifier_type,
        price_adjustment=modifier.price_adjustment,
        is_required=modifier.is_required,
        sort_order=modifier.sort_order,
        is_active=modifier.is_active,
        organization_id=modifier.organization_id,
        restaurant_id=modifier.restaurant_id,
        created_at=modifier.created_at.isoformat(),
        updated_at=modifier.updated_at.isoformat(),
    )


@router.delete("/{modifier_id}")
async def delete_modifier(
    modifier_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a menu modifier."""
    success = await ModifierService.delete_modifier(
        session=session,
        modifier_id=modifier_id,
        organization_id=current_user.organization_id,
        restaurant_id=current_user.restaurant_id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Modifier not found"
        )
    return {"message": "Modifier deleted successfully"}


@router.post("/items/{item_id}/modifiers")
async def assign_modifier_to_item(
    item_id: str,
    assignment: MenuItemModifierAssignment,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Assign a modifier to a menu item."""
    success = await ModifierService.assign_modifier_to_item(
        session=session,
        item_id=item_id,
        modifier_id=assignment.modifier_id,
        organization_id=current_user.organization_id,
        restaurant_id=current_user.restaurant_id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item or modifier not found"
        )
    return {"message": "Modifier assigned to item successfully"}


@router.delete("/items/{item_id}/modifiers/{modifier_id}")
async def remove_modifier_from_item(
    item_id: str,
    modifier_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Remove a modifier from a menu item."""
    success = await ModifierService.remove_modifier_from_item(
        session=session,
        item_id=item_id,
        modifier_id=modifier_id,
        organization_id=current_user.organization_id,
        restaurant_id=current_user.restaurant_id,
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item or modifier not found"
        )
    return {"message": "Modifier removed from item successfully"}


@router.get("/items/{item_id}/modifiers", response_model=List[ModifierRead])
async def get_item_modifiers(
    item_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_active_user),
):
    """Get all modifiers for a menu item."""
    modifiers = await ModifierService.get_item_modifiers(
        session=session,
        item_id=item_id,
        organization_id=current_user.organization_id,
        restaurant_id=current_user.restaurant_id,
    )
    return [ModifierRead(
        id=modifier.id,
        name=modifier.name,
        description=modifier.description,
        modifier_type=modifier.modifier_type,
        price_adjustment=modifier.price_adjustment,
        is_required=modifier.is_required,
        sort_order=modifier.sort_order,
        is_active=modifier.is_active,
        organization_id=modifier.organization_id,
        restaurant_id=modifier.restaurant_id,
        created_at=modifier.created_at.isoformat(),
        updated_at=modifier.updated_at.isoformat(),
    ) for modifier in modifiers]