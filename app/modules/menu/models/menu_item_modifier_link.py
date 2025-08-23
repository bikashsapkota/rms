"""
Link table for menu items and modifiers many-to-many relationship.
"""

from typing import Optional
from uuid import UUID
from sqlmodel import SQLModel, Field


class MenuItemModifierLink(SQLModel, table=True):
    """Link table for menu items and modifiers."""
    __tablename__ = "menu_item_modifiers"

    menu_item_id: UUID = Field(
        foreign_key="menu_items.id",
        primary_key=True,
    )
    modifier_id: UUID = Field(
        foreign_key="modifiers.id", 
        primary_key=True,
    )
    
    # Optional override fields for this specific assignment
    is_required: Optional[bool] = Field(default=None, description="Override modifier required setting")
    sort_order: Optional[int] = Field(default=None, description="Override sort order for this item")