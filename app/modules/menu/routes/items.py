from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query, Path as PathParam
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.database.session import get_session
from app.shared.auth.deps import get_tenant_context, TenantContext, require_manager
from uuid import UUID
import uuid
from app.modules.menu.models.item import (
    MenuItemCreate,
    MenuItemUpdate,
    MenuItemRead,
    MenuItemReadWithCategory,
    MenuItemPublic,
)
from app.modules.menu.services.item import MenuItemService
from app.core.config import settings
import os
import uuid
from pathlib import Path

router = APIRouter(prefix="/menu/items", tags=["Menu Items"])
public_router = APIRouter(prefix="/menu", tags=["Public Menu"])


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


@router.get("/", response_model=List[MenuItemReadWithCategory])
async def list_items(
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    category_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    include_unavailable: bool = False,
):
    """List menu items for the restaurant."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    items = await MenuItemService.get_items(
        session=session,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
        category_id=category_id,
        skip=skip,
        limit=limit,
        include_unavailable=include_unavailable,
    )
    
    # Get items with category details
    detailed_items = []
    for item in items:
        item_data = await MenuItemService.get_item_with_category(
            session=session,
            item_id=str(item.id),
            organization_id=tenant_context.organization_id,
            restaurant_id=tenant_context.restaurant_id,
        )
        if item_data:
            detailed_items.append(MenuItemReadWithCategory(**item_data))
    
    return detailed_items


@router.post("/", response_model=MenuItemRead)
async def create_item(
    item_data: MenuItemCreate,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_manager),
):
    """Create a new menu item."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    item = await MenuItemService.create_item(
        session=session,
        item_data=item_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return MenuItemRead(
        id=str(item.id),
        name=item.name,
        description=item.description,
        price=item.price,
        is_available=item.is_available,
        image_url=item.image_url,
        category_id=str(item.category_id) if item.category_id else None,
        organization_id=str(item.organization_id),
        restaurant_id=str(item.restaurant_id),
        created_at=item.created_at.isoformat(),
        updated_at=item.updated_at.isoformat(),
    )


@router.get("/{item_id}", response_model=MenuItemReadWithCategory)
async def get_item(
    item_id: str = PathParam(..., description="Menu item ID"),
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Get a menu item by ID."""
    # Validate UUID format
    validate_uuid(item_id, "item ID")
    
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    item_data = await MenuItemService.get_item_with_category(
        session=session,
        item_id=item_id,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    if not item_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )
    
    return MenuItemReadWithCategory(**item_data)


@router.put("/{item_id}", response_model=MenuItemRead)
async def update_item(
    item_data: MenuItemUpdate,
    item_id: str = PathParam(..., description="Menu item ID"),
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_manager),
):
    """Update a menu item."""
    # Validate UUID format
    validate_uuid(item_id, "item ID")
    
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    item = await MenuItemService.update_item(
        session=session,
        item_id=item_id,
        item_data=item_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return MenuItemRead(
        id=str(item.id),
        name=item.name,
        description=item.description,
        price=item.price,
        is_available=item.is_available,
        image_url=item.image_url,
        category_id=str(item.category_id) if item.category_id else None,
        organization_id=str(item.organization_id),
        restaurant_id=str(item.restaurant_id),
        created_at=item.created_at.isoformat(),
        updated_at=item.updated_at.isoformat(),
    )


@router.delete("/{item_id}")
async def delete_item(
    item_id: str = PathParam(..., description="Menu item ID"),
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_manager),
):
    """Delete a menu item."""
    # Validate UUID format
    validate_uuid(item_id, "item ID")
    
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    await MenuItemService.delete_item(
        session=session,
        item_id=item_id,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return {"message": "Menu item deleted successfully"}


@router.put("/{item_id}/availability", response_model=MenuItemRead)
async def toggle_item_availability(
    item_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_manager),
):
    """Toggle menu item availability."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    item = await MenuItemService.toggle_availability(
        session=session,
        item_id=item_id,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return MenuItemRead(
        id=str(item.id),
        name=item.name,
        description=item.description,
        price=item.price,
        is_available=item.is_available,
        image_url=item.image_url,
        category_id=str(item.category_id) if item.category_id else None,
        organization_id=str(item.organization_id),
        restaurant_id=str(item.restaurant_id),
        created_at=item.created_at.isoformat(),
        updated_at=item.updated_at.isoformat(),
    )


@router.post("/{item_id}/image")
async def upload_item_image(
    item_id: str,
    image: UploadFile = File(...),
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_manager),
):
    """Upload an image for a menu item."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    # Validate file type
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image",
        )
    
    # Validate file size
    if image.size and image.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size must be less than {settings.MAX_FILE_SIZE} bytes",
        )
    
    # Get the item first
    item = await MenuItemService.get_item_by_id(
        session=session,
        item_id=item_id,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )
    
    # Generate unique filename
    file_extension = Path(image.filename).suffix.lower()
    if file_extension not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_IMAGE_EXTENSIONS)}",
        )
    
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = settings.upload_path / "menu_items" / unique_filename
    
    # Create directory if it doesn't exist
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save file
    try:
        with open(file_path, "wb") as buffer:
            content = await image.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save image",
        )
    
    # Update item with image URL
    image_url = f"/uploads/menu_items/{unique_filename}"
    item.image_url = image_url
    session.add(item)
    await session.commit()
    
    return {"message": "Image uploaded successfully", "image_url": image_url}


@router.put("/{item_id}/set-as-category-cover")
async def set_item_as_category_cover(
    item_id: str,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    current_user=Depends(require_manager),
):
    """Set an item's image as the category cover image."""
    if not tenant_context.restaurant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Restaurant context required",
        )
    
    # Get the item first
    item = await MenuItemService.get_item_by_id(
        session=session,
        item_id=item_id,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu item not found",
        )
    
    if not item.image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Menu item must have an image to set as category cover",
        )
    
    if not item.category_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Menu item must belong to a category",
        )
    
    # Update the category with the item's image
    from app.modules.menu.services.category import MenuCategoryService
    
    success = await MenuCategoryService.set_cover_image(
        session=session,
        category_id=str(item.category_id),
        image_url=item.image_url,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    return {
        "message": "Item image set as category cover successfully",
        "category_id": str(item.category_id),
        "cover_image_url": item.image_url
    }


# Public menu endpoint (no authentication required)
@public_router.get("/public", response_model=List[MenuItemPublic])
async def get_public_menu(
    restaurant_id: str = Query(..., description="Restaurant ID to get menu for"),
    session: AsyncSession = Depends(get_session),
):
    """Get public menu for customers."""
    items = await MenuItemService.get_public_menu(
        session=session,
        restaurant_id=restaurant_id,
    )
    
    return items