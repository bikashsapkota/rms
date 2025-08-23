from typing import List, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from fastapi import HTTPException, status
from app.modules.menu.models.category import (
    MenuCategory,
    MenuCategoryCreate,
    MenuCategoryUpdate,
)
from app.modules.menu.models.item import MenuItem


class MenuCategoryService:
    """Service for menu category operations."""
    
    @staticmethod
    async def create_category(
        session: AsyncSession,
        category_data: MenuCategoryCreate,
        organization_id: str,
        restaurant_id: str,
    ) -> MenuCategory:
        """Create a new menu category."""
        category = MenuCategory(
            **category_data.model_dump(),
            organization_id=organization_id,
            restaurant_id=restaurant_id,
        )
        
        session.add(category)
        await session.commit()
        await session.refresh(category)
        
        return category
    
    @staticmethod
    async def get_categories(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
        skip: int = 0,
        limit: int = 100,
        include_inactive: bool = False,
    ) -> List[MenuCategory]:
        """Get menu categories for a restaurant."""
        statement = select(MenuCategory).where(
            MenuCategory.organization_id == organization_id,
            MenuCategory.restaurant_id == restaurant_id,
        )
        
        if not include_inactive:
            statement = statement.where(MenuCategory.is_active == True)
        
        statement = statement.order_by(MenuCategory.sort_order, MenuCategory.name)
        statement = statement.offset(skip).limit(limit)
        
        result = await session.exec(statement)
        return result.all()
    
    @staticmethod
    async def get_category_by_id(
        session: AsyncSession,
        category_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> Optional[MenuCategory]:
        """Get a menu category by ID."""
        statement = select(MenuCategory).where(
            MenuCategory.id == category_id,
            MenuCategory.organization_id == organization_id,
            MenuCategory.restaurant_id == restaurant_id,
        )
        
        result = await session.exec(statement)
        return result.first()
    
    @staticmethod
    async def update_category(
        session: AsyncSession,
        category_id: str,
        category_data: MenuCategoryUpdate,
        organization_id: str,
        restaurant_id: str,
    ) -> MenuCategory:
        """Update a menu category."""
        category = await MenuCategoryService.get_category_by_id(
            session, category_id, organization_id, restaurant_id
        )
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu category not found",
            )
        
        # Update fields
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)
        
        session.add(category)
        await session.commit()
        await session.refresh(category)
        
        return category
    
    @staticmethod
    async def delete_category(
        session: AsyncSession,
        category_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> bool:
        """Delete a menu category."""
        category = await MenuCategoryService.get_category_by_id(
            session, category_id, organization_id, restaurant_id
        )
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu category not found",
            )
        
        # Check if category has menu items
        items_statement = select(func.count(MenuItem.id)).where(
            MenuItem.category_id == category_id
        )
        items_result = await session.exec(items_statement)
        item_count = items_result.one()
        
        if item_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete category with menu items. Remove items first.",
            )
        
        await session.delete(category)
        await session.commit()
        
        return True
    
    @staticmethod
    async def get_category_with_stats(
        session: AsyncSession,
        category_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> Optional[dict]:
        """Get category with item statistics."""
        category = await MenuCategoryService.get_category_by_id(
            session, category_id, organization_id, restaurant_id
        )
        
        if not category:
            return None
        
        # Get item counts
        total_items_stmt = select(func.count(MenuItem.id)).where(
            MenuItem.category_id == category_id
        )
        active_items_stmt = select(func.count(MenuItem.id)).where(
            MenuItem.category_id == category_id,
            MenuItem.is_available == True,
        )
        
        total_items_result = await session.exec(total_items_stmt)
        active_items_result = await session.exec(active_items_stmt)
        
        total_items = total_items_result.one()
        active_items = active_items_result.one()
        
        return {
            "id": str(category.id),
            "name": category.name,
            "description": category.description,
            "sort_order": category.sort_order,
            "is_active": category.is_active,
            "organization_id": str(category.organization_id),
            "restaurant_id": str(category.restaurant_id),
            "created_at": category.created_at.isoformat(),
            "updated_at": category.updated_at.isoformat(),
            "item_count": total_items,
            "active_item_count": active_items,
        }
    
    @staticmethod
    async def set_cover_image(
        session: AsyncSession,
        category_id: str,
        image_url: str,
        organization_id: str,
        restaurant_id: str,
    ) -> bool:
        """Set the cover image for a category."""
        category = await MenuCategoryService.get_category_by_id(
            session, category_id, organization_id, restaurant_id
        )
        
        if not category:
            return False
        
        category.cover_image_url = image_url
        session.add(category)
        await session.commit()
        
        return True