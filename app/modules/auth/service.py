from typing import Optional, Tuple
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status
from app.shared.models.user import User, UserCreate
from app.shared.models.organization import Organization
from app.shared.models.restaurant import Restaurant
from app.shared.auth.security import (
    verify_password,
    get_password_hash,
    create_user_access_token,
)
from app.core.config import settings


class AuthService:
    """Authentication service."""
    
    @staticmethod
    async def authenticate_user(
        session: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """Authenticate user by email and password."""
        statement = select(User).where(
            User.email == email,
            User.is_active == True,
        )
        result = await session.exec(statement)
        user = result.first()
        
        if not user:
            return None
        
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    
    @staticmethod
    async def create_access_token_for_user(
        session: AsyncSession, user: User
    ) -> Tuple[str, int]:
        """Create access token for user with tenant context."""
        # Get organization
        org_statement = select(Organization).where(Organization.id == user.organization_id)
        org_result = await session.exec(org_statement)
        organization = org_result.first()
        
        if not organization:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="User organization not found",
            )
        
        # Get restaurant if user has one
        restaurant_id = None
        if user.restaurant_id:
            rest_statement = select(Restaurant).where(Restaurant.id == user.restaurant_id)
            rest_result = await session.exec(rest_statement)
            restaurant = rest_result.first()
            if restaurant:
                restaurant_id = str(restaurant.id)
        
        # Create token
        access_token = create_user_access_token(
            user_id=str(user.id),
            email=user.email,
            organization_id=str(user.organization_id),
            restaurant_id=restaurant_id,
            role=user.role,
        )
        
        return access_token, settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    
    @staticmethod
    async def get_user_details(session: AsyncSession, user: User) -> dict:
        """Get detailed user information for login response."""
        # Get organization
        org_statement = select(Organization).where(Organization.id == user.organization_id)
        org_result = await session.exec(org_statement)
        organization = org_result.first()
        
        # Get restaurant if user has one
        restaurant = None
        if user.restaurant_id:
            rest_statement = select(Restaurant).where(Restaurant.id == user.restaurant_id)
            rest_result = await session.exec(rest_statement)
            restaurant = rest_result.first()
        
        return {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "organization_id": str(user.organization_id),
            "restaurant_id": str(user.restaurant_id) if user.restaurant_id else None,
            "organization_name": organization.name if organization else "Unknown",
            "restaurant_name": restaurant.name if restaurant else None,
        }
    
    @staticmethod
    async def create_user(
        session: AsyncSession,
        user_data: UserCreate,
        organization_id: str,
        restaurant_id: Optional[str] = None,
    ) -> User:
        """Create a new user."""
        # Check if user already exists
        statement = select(User).where(User.email == user_data.email)
        result = await session.exec(statement)
        existing_user = result.first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists",
            )
        
        # Create user
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            role=user_data.role,
            password_hash=get_password_hash(user_data.password),
            organization_id=organization_id,
            restaurant_id=restaurant_id or user_data.restaurant_id,
            is_active=True,
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return user