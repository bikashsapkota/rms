from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.shared.database.session import get_session
from app.shared.models.user import User
from app.shared.models.organization import Organization
from app.shared.models.restaurant import Restaurant
from app.shared.auth.security import decode_user_token

# Bearer token security scheme
bearer_scheme = HTTPBearer()


async def get_current_user_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> Dict[str, Any]:
    """Extract and validate JWT token."""
    token = credentials.credentials
    payload = decode_user_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


async def get_current_user(
    token_payload: Dict[str, Any] = Depends(get_current_user_token),
    session: AsyncSession = Depends(get_session),
) -> User:
    """Get current authenticated user."""
    user_id = token_payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    statement = select(User).where(User.id == user_id, User.is_active == True)
    result = await session.exec(statement)
    user = result.first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


class TenantContext:
    """Tenant context for multi-tenant operations."""
    
    def __init__(
        self,
        user: User,
        organization: Organization,
        restaurant: Optional[Restaurant] = None,
    ):
        self.user = user
        self.organization = organization
        self.restaurant = restaurant
    
    @property
    def organization_id(self) -> str:
        return str(self.organization.id)
    
    @property
    def restaurant_id(self) -> Optional[str]:
        return str(self.restaurant.id) if self.restaurant else None


async def get_tenant_context(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> TenantContext:
    """Get tenant context for the current user."""
    # Get organization
    org_statement = select(Organization).where(
        Organization.id == current_user.organization_id,
        Organization.is_active == True,
    )
    org_result = await session.exec(org_statement)
    organization = org_result.first()
    
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Organization not found or inactive",
        )
    
    # Get restaurant if user has one
    restaurant = None
    if current_user.restaurant_id:
        rest_statement = select(Restaurant).where(
            Restaurant.id == current_user.restaurant_id,
            Restaurant.is_active == True,
        )
        rest_result = await session.exec(rest_statement)
        restaurant = rest_result.first()
        
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Restaurant not found or inactive",
            )
    
    return TenantContext(
        user=current_user,
        organization=organization,
        restaurant=restaurant,
    )


def require_role(*allowed_roles: str):
    """Dependency factory for role-based access control."""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}",
            )
        return current_user
    
    return role_checker


# Common role dependencies
require_admin = require_role("admin")
require_manager = require_role("admin", "manager")
require_staff = require_role("admin", "manager", "staff")