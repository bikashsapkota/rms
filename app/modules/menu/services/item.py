from typing import List, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, and_
from fastapi import HTTPException, status
from app.modules.menu.models.item import (
    MenuItem,
    MenuItemCreate,
    MenuItemUpdate,
    MenuItemPublic,
)
from app.modules.menu.models.category import MenuCategory


class MenuItemService:
    """Service for menu item operations."""
    
    @staticmethod
    async def create_item(
        session: AsyncSession,
        item_data: MenuItemCreate,
        organization_id: str,
        restaurant_id: str,
    ) -> MenuItem:
        """Create a new menu item."""
        # Validate category exists if provided
        if item_data.category_id:
            category_stmt = select(MenuCategory).where(
                MenuCategory.id == item_data.category_id,
                MenuCategory.organization_id == organization_id,
                MenuCategory.restaurant_id == restaurant_id,
            )
            category_result = await session.exec(category_stmt)
            if not category_result.first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid category ID",
                )
        
        item = MenuItem(
            **item_data.model_dump(),
            organization_id=organization_id,
            restaurant_id=restaurant_id,
        )
        
        session.add(item)
        await session.commit()
        await session.refresh(item)
        
        return item
    
    @staticmethod
    async def get_items(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
        category_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        include_unavailable: bool = False,
    ) -> List[MenuItem]:
        """Get menu items for a restaurant."""
        statement = select(MenuItem).where(
            MenuItem.organization_id == organization_id,
            MenuItem.restaurant_id == restaurant_id,
        )
        
        if category_id:
            statement = statement.where(MenuItem.category_id == category_id)
        
        if not include_unavailable:
            statement = statement.where(MenuItem.is_available == True)
        
        statement = statement.order_by(MenuItem.name)
        statement = statement.offset(skip).limit(limit)
        
        result = await session.exec(statement)
        return result.all()
    
    @staticmethod
    async def get_item_by_id(
        session: AsyncSession,
        item_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> Optional[MenuItem]:
        """Get a menu item by ID."""
        statement = select(MenuItem).where(
            MenuItem.id == item_id,
            MenuItem.organization_id == organization_id,
            MenuItem.restaurant_id == restaurant_id,
        )
        
        result = await session.exec(statement)
        return result.first()
    
    @staticmethod
    async def update_item(
        session: AsyncSession,
        item_id: str,
        item_data: MenuItemUpdate,
        organization_id: str,
        restaurant_id: str,
    ) -> MenuItem:
        """Update a menu item."""
        item = await MenuItemService.get_item_by_id(
            session, item_id, organization_id, restaurant_id
        )
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found",
            )
        
        # Validate category if being updated
        update_data = item_data.model_dump(exclude_unset=True)
        if "category_id" in update_data and update_data["category_id"]:
            category_stmt = select(MenuCategory).where(
                MenuCategory.id == update_data["category_id"],
                MenuCategory.organization_id == organization_id,
                MenuCategory.restaurant_id == restaurant_id,
            )
            category_result = await session.exec(category_stmt)
            if not category_result.first():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid category ID",
                )
        
        # Update fields
        for field, value in update_data.items():
            setattr(item, field, value)
        
        session.add(item)
        await session.commit()
        await session.refresh(item)
        
        return item
    
    @staticmethod
    async def delete_item(
        session: AsyncSession,
        item_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> bool:
        """Delete a menu item."""
        item = await MenuItemService.get_item_by_id(
            session, item_id, organization_id, restaurant_id
        )
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found",
            )
        
        await session.delete(item)
        await session.commit()
        
        return True
    
    @staticmethod
    async def toggle_availability(
        session: AsyncSession,
        item_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> MenuItem:
        """Toggle menu item availability."""
        item = await MenuItemService.get_item_by_id(
            session, item_id, organization_id, restaurant_id
        )
        
        if not item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu item not found",
            )
        
        item.is_available = not item.is_available
        session.add(item)
        await session.commit()
        await session.refresh(item)
        
        return item
    
    @staticmethod
    async def get_public_menu(
        session: AsyncSession,
        restaurant_id: str,
    ) -> List[MenuItemPublic]:
        """Get public menu for customers."""
        statement = select(MenuItem, MenuCategory).join(
            MenuCategory,
            and_(
                MenuItem.category_id == MenuCategory.id,
                MenuCategory.is_active == True,
            ),
            isouter=True,
        ).where(
            MenuItem.restaurant_id == restaurant_id,
            MenuItem.is_available == True,
        ).order_by(MenuCategory.sort_order, MenuItem.name)
        
        result = await session.exec(statement)
        items_with_categories = result.all()
        
        public_items = []
        for item, category in items_with_categories:
            public_items.append(
                MenuItemPublic(
                    id=str(item.id),
                    name=item.name,
                    description=item.description,
                    price=item.price,
                    image_url=item.image_url,
                    category_name=category.name if category else None,
                )
            )
        
        return public_items
    
    @staticmethod
    async def get_item_with_category(
        session: AsyncSession,
        item_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> Optional[dict]:
        """Get menu item with category details."""
        statement = select(MenuItem, MenuCategory).join(
            MenuCategory,
            MenuItem.category_id == MenuCategory.id,
            isouter=True,
        ).where(
            MenuItem.id == item_id,
            MenuItem.organization_id == organization_id,
            MenuItem.restaurant_id == restaurant_id,
        )
        
        result = await session.exec(statement)
        item_with_category = result.first()
        
        if not item_with_category:
            return None
        
        item, category = item_with_category
        
        return {
            "id": str(item.id),
            "name": item.name,
            "description": item.description,
            "price": float(item.price),
            "is_available": item.is_available,
            "image_url": item.image_url,
            "category_id": str(item.category_id) if item.category_id else None,
            "category_name": category.name if category else None,
            "organization_id": str(item.organization_id),
            "restaurant_id": str(item.restaurant_id),
            "created_at": item.created_at.isoformat(),
            "updated_at": item.updated_at.isoformat(),
        }