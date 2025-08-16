"""
Restaurant setup service for Phase 1 - Single tenant with multi-tenant foundation.
Implements the Phase 1 strategy: auto-create organization for each restaurant.
"""

from typing import Dict, Any
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.models.organization import Organization, OrganizationCreate
from app.shared.models.restaurant import Restaurant, RestaurantCreate
from app.shared.models.user import User, UserCreate
from app.shared.auth.security import get_password_hash


class RestaurantSetupService:
    """Service for setting up new restaurants with multi-tenant foundation."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_restaurant_setup(
        self, 
        restaurant_data: Dict[str, Any],
        admin_user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Phase 1: Auto-create organization + restaurant for simple setup.
        This maintains multi-tenant architecture while providing single-tenant UX.
        """
        
        # 1. Create organization automatically
        organization = Organization(
            name=f"{restaurant_data['name']} Organization",
            organization_type="independent",
            subscription_tier="basic"
        )
        self.session.add(organization)
        await self.session.commit()
        await self.session.refresh(organization)
        
        # 2. Create restaurant
        restaurant = Restaurant(
            organization_id=organization.id,
            name=restaurant_data["name"],
            address=restaurant_data.get("address"),
            phone=restaurant_data.get("phone"),
            email=restaurant_data.get("email"),
            settings=restaurant_data.get("settings", {})
        )
        self.session.add(restaurant)
        await self.session.commit()
        await self.session.refresh(restaurant)
        
        # 3. Create admin user
        admin_user = User(
            organization_id=organization.id,
            restaurant_id=restaurant.id,
            email=admin_user_data["email"],
            full_name=admin_user_data["full_name"],
            role="admin",
            password_hash=get_password_hash(admin_user_data["password"]),
            is_active=True
        )
        self.session.add(admin_user)
        await self.session.commit()
        await self.session.refresh(admin_user)
        
        return {
            "organization": {
                "id": str(organization.id),
                "name": organization.name,
                "type": organization.organization_type
            },
            "restaurant": {
                "id": str(restaurant.id),
                "name": restaurant.name,
                "organization_id": str(restaurant.organization_id)
            },
            "admin_user": {
                "id": str(admin_user.id),
                "email": admin_user.email,
                "full_name": admin_user.full_name,
                "role": admin_user.role
            }
        }


def get_default_organization_id() -> UUID:
    """
    Get default organization ID for Phase 1 single-tenant usage.
    In Phase 1, we use a single organization for simplicity.
    """
    # This would be configured during initial setup
    # For now, we'll use a placeholder that should be set during deployment
    return UUID("00000000-0000-0000-0000-000000000001")


def get_default_restaurant_id() -> UUID:
    """
    Get default restaurant ID for Phase 1 single-tenant usage.
    In Phase 1, we use a single restaurant for simplicity.
    """
    # This would be configured during initial setup
    # For now, we'll use a placeholder that should be set during deployment
    return UUID("00000000-0000-0000-0000-000000000002")


class TenantContextManager:
    """
    Manages tenant context for multi-tenant operations.
    Phase 1: Simple context (single tenant)
    Phase 4: Full multi-tenant context switching
    """
    
    def __init__(self):
        self._current_organization_id: UUID = None
        self._current_restaurant_id: UUID = None
    
    def set_context(self, organization_id: UUID, restaurant_id: UUID = None):
        """Set current tenant context."""
        self._current_organization_id = organization_id
        self._current_restaurant_id = restaurant_id
    
    def get_organization_id(self) -> UUID:
        """Get current organization ID."""
        return self._current_organization_id or get_default_organization_id()
    
    def get_restaurant_id(self) -> UUID:
        """Get current restaurant ID."""
        return self._current_restaurant_id or get_default_restaurant_id()
    
    def clear_context(self):
        """Clear tenant context."""
        self._current_organization_id = None
        self._current_restaurant_id = None


# Global tenant context manager (Phase 1 simplification)
tenant_context = TenantContextManager()