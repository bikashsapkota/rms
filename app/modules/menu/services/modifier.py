"""
Menu modifier service for business logic.
"""

from typing import List, Optional
from uuid import UUID
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.menu.models.modifier import (
    Modifier,
    ModifierCreate,
    ModifierUpdate,
    ModifierRead,
    ModifierReadWithItems
)
from app.modules.menu.models.item import MenuItem


class ModifierService:
    """Service for managing menu modifiers."""

    @staticmethod
    async def create_modifier(
        session: AsyncSession,
        modifier_data: ModifierCreate,
        organization_id: UUID,
        restaurant_id: UUID,
    ) -> Modifier:
        """Create a new menu modifier."""
        modifier = Modifier(
            **modifier_data.model_dump(),
            organization_id=organization_id,
            restaurant_id=restaurant_id,
        )
        session.add(modifier)
        await session.commit()
        await session.refresh(modifier)
        return modifier

    @staticmethod
    async def get_modifiers(
        session: AsyncSession,
        organization_id: UUID,
        restaurant_id: UUID,
        skip: int = 0,
        limit: int = 100,
        modifier_type: Optional[str] = None,
        include_inactive: bool = False,
    ) -> List[ModifierReadWithItems]:
        """Get list of modifiers with item counts."""
        from app.modules.menu.models.menu_item_modifier_link import MenuItemModifierLink
        
        # Query modifiers with item counts using the link table
        query = select(
            Modifier,
            func.count(MenuItemModifierLink.menu_item_id).label("item_count")
        ).select_from(
            Modifier.__table__.outerjoin(
                MenuItemModifierLink.__table__,
                Modifier.id == MenuItemModifierLink.modifier_id
            )
        ).where(
            Modifier.organization_id == organization_id,
            Modifier.restaurant_id == restaurant_id,
        ).group_by(Modifier.id)

        if modifier_type:
            query = query.where(Modifier.modifier_type == modifier_type)
        
        if not include_inactive:
            query = query.where(Modifier.is_active == True)

        query = query.order_by(Modifier.sort_order, Modifier.name)
        query = query.offset(skip).limit(limit)

        result = await session.exec(query)
        rows = result.all()

        modifiers = []
        for row in rows:
            modifier_data = row[0]  # Modifier object
            item_count = row[1] or 0  # Item count
            
            modifier_dict = modifier_data.model_dump()
            modifier_dict["item_count"] = item_count
            # Convert datetime objects to strings for schema compatibility
            if modifier_dict.get("created_at"):
                modifier_dict["created_at"] = modifier_dict["created_at"].isoformat()
            if modifier_dict.get("updated_at"):
                modifier_dict["updated_at"] = modifier_dict["updated_at"].isoformat()
            modifiers.append(ModifierReadWithItems(**modifier_dict))

        return modifiers

    @staticmethod
    async def get_modifier_by_id(
        session: AsyncSession,
        modifier_id: str,
        organization_id: UUID,
        restaurant_id: UUID,
    ) -> Optional[Modifier]:
        """Get a modifier by ID."""
        query = select(Modifier).where(
            Modifier.id == modifier_id,
            Modifier.organization_id == organization_id,
            Modifier.restaurant_id == restaurant_id,
        )
        result = await session.exec(query)
        return result.first()

    @staticmethod
    async def update_modifier(
        session: AsyncSession,
        modifier_id: str,
        modifier_data: ModifierUpdate,
        organization_id: UUID,
        restaurant_id: UUID,
    ) -> Optional[Modifier]:
        """Update a modifier."""
        modifier = await ModifierService.get_modifier_by_id(
            session, modifier_id, organization_id, restaurant_id
        )
        if not modifier:
            return None

        update_data = modifier_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(modifier, field, value)

        session.add(modifier)
        await session.commit()
        await session.refresh(modifier)
        return modifier

    @staticmethod
    async def delete_modifier(
        session: AsyncSession,
        modifier_id: str,
        organization_id: UUID,
        restaurant_id: UUID,
    ) -> bool:
        """Delete a modifier."""
        modifier = await ModifierService.get_modifier_by_id(
            session, modifier_id, organization_id, restaurant_id
        )
        if not modifier:
            return False

        await session.delete(modifier)
        await session.commit()
        return True

    @staticmethod
    async def assign_modifier_to_item(
        session: AsyncSession,
        item_id: str,
        modifier_id: str,
        organization_id: UUID,
        restaurant_id: UUID,
    ) -> bool:
        """Assign a modifier to a menu item."""
        from app.modules.menu.models.menu_item_modifier_link import MenuItemModifierLink
        
        # Get the item
        item_query = select(MenuItem).where(
            MenuItem.id == item_id,
            MenuItem.organization_id == organization_id,
            MenuItem.restaurant_id == restaurant_id,
        )
        item_result = await session.exec(item_query)
        item = item_result.first()
        if not item:
            return False

        # Get the modifier
        modifier = await ModifierService.get_modifier_by_id(
            session, modifier_id, organization_id, restaurant_id
        )
        if not modifier:
            return False

        # Check if already assigned
        existing_link_query = select(MenuItemModifierLink).where(
            MenuItemModifierLink.menu_item_id == item_id,
            MenuItemModifierLink.modifier_id == modifier_id
        )
        existing_link_result = await session.exec(existing_link_query)
        existing_link = existing_link_result.first()
        
        if not existing_link:
            # Create the link
            link = MenuItemModifierLink(
                menu_item_id=item_id,
                modifier_id=modifier_id
            )
            session.add(link)
            await session.commit()

        return True

    @staticmethod
    async def remove_modifier_from_item(
        session: AsyncSession,
        item_id: str,
        modifier_id: str,
        organization_id: UUID,
        restaurant_id: UUID,
    ) -> bool:
        """Remove a modifier from a menu item."""
        from app.modules.menu.models.menu_item_modifier_link import MenuItemModifierLink
        
        # Get the item
        item_query = select(MenuItem).where(
            MenuItem.id == item_id,
            MenuItem.organization_id == organization_id,
            MenuItem.restaurant_id == restaurant_id,
        )
        item_result = await session.exec(item_query)
        item = item_result.first()
        if not item:
            return False

        # Get the modifier
        modifier = await ModifierService.get_modifier_by_id(
            session, modifier_id, organization_id, restaurant_id
        )
        if not modifier:
            return False

        # Find and remove the link if it exists
        link_query = select(MenuItemModifierLink).where(
            MenuItemModifierLink.menu_item_id == item_id,
            MenuItemModifierLink.modifier_id == modifier_id
        )
        link_result = await session.exec(link_query)
        link = link_result.first()
        
        if link:
            await session.delete(link)
            await session.commit()

        return True

    @staticmethod
    async def get_item_modifiers(
        session: AsyncSession,
        item_id: str,
        organization_id: UUID,
        restaurant_id: UUID,
    ) -> List[Modifier]:
        """Get all modifiers for a menu item."""
        from app.modules.menu.models.menu_item_modifier_link import MenuItemModifierLink
        
        # Get the item first to verify it exists
        item_query = select(MenuItem).where(
            MenuItem.id == item_id,
            MenuItem.organization_id == organization_id,
            MenuItem.restaurant_id == restaurant_id,
        )
        item_result = await session.exec(item_query)
        item = item_result.first()
        
        if not item:
            return []
        
        # Get modifiers through the link table
        query = select(Modifier).select_from(
            Modifier.__table__.join(
                MenuItemModifierLink.__table__,
                Modifier.id == MenuItemModifierLink.modifier_id
            )
        ).where(
            MenuItemModifierLink.menu_item_id == item_id,
            Modifier.organization_id == organization_id,
            Modifier.restaurant_id == restaurant_id,
        ).order_by(Modifier.sort_order, Modifier.name)
        
        result = await session.exec(query)
        return list(result.all())