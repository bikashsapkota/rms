from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from app.shared.database.session import get_session
from app.shared.auth.deps import get_current_active_user, get_tenant_context, TenantContext
from app.shared.models.user import User, UserCreate, UserRead, UserReadWithDetails
from app.modules.auth.schemas import (
    LoginRequest,
    LoginResponse,
    RefreshTokenResponse,
    LogoutResponse,
    CreateAdminRequest,
    CreateAdminResponse,
)
from app.modules.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    session: AsyncSession = Depends(get_session),
):
    """Authenticate user and return access token."""
    user = await AuthService.authenticate_user(
        session, login_data.email, login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token, expires_in = await AuthService.create_access_token_for_user(
        session, user
    )
    user_details = await AuthService.get_user_details(session, user)
    
    return LoginResponse(
        access_token=access_token,
        expires_in=expires_in,
        user=user_details,
    )


@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    """OAuth2 compatible token endpoint for Swagger UI authentication."""
    user = await AuthService.authenticate_user(
        session, form_data.username, form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token, expires_in = await AuthService.create_access_token_for_user(
        session, user
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": expires_in
    }


@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: User = Depends(get_current_active_user),
):
    """Logout user (client should discard token)."""
    return LogoutResponse()


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Refresh access token."""
    access_token, expires_in = await AuthService.create_access_token_for_user(
        session, current_user
    )
    
    return RefreshTokenResponse(
        access_token=access_token,
        expires_in=expires_in,
    )


@router.get("/me", response_model=UserReadWithDetails)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
):
    """Get current user information."""
    user_details = await AuthService.get_user_details(session, current_user)
    return UserReadWithDetails(**user_details)


@router.post("/create-admin", response_model=CreateAdminResponse)
async def create_admin_user(
    admin_data: CreateAdminRequest,
    session: AsyncSession = Depends(get_session),
):
    """Create admin user with organization. No authentication required for first admin."""
    result = await AuthService.create_admin_with_organization(
        session=session,
        email=admin_data.email,
        password=admin_data.password,
        full_name=admin_data.full_name,
        organization_name=admin_data.organization_name,
        restaurant_name=admin_data.restaurant_name,
    )
    
    return CreateAdminResponse(**result)


# User management endpoints (require appropriate permissions)
users_router = APIRouter(prefix="/users", tags=["User Management"])


@users_router.get("/", response_model=list[UserReadWithDetails])
async def list_users(
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
    skip: int = 0,
    limit: int = 100,
):
    """List users in the current organization/restaurant."""
    # Build query based on user's access level
    if tenant_context.user.role == "admin":
        # Admin can see all users in organization
        statement = select(User).where(
            User.organization_id == tenant_context.organization_id,
            User.is_active == True,
        )
    else:
        # Non-admin can only see users in their restaurant
        if not tenant_context.restaurant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        statement = select(User).where(
            User.restaurant_id == tenant_context.restaurant_id,
            User.is_active == True,
        )
    
    statement = statement.offset(skip).limit(limit)
    result = await session.exec(statement)
    users = result.all()
    
    # Get detailed info for each user
    detailed_users = []
    for user in users:
        user_details = await AuthService.get_user_details(session, user)
        detailed_users.append(UserReadWithDetails(**user_details))
    
    return detailed_users


@users_router.post("/", response_model=UserRead)
async def create_user(
    user_data: UserCreate,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Create a new user (admin only)."""
    if tenant_context.user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create users",
        )
    
    user = await AuthService.create_user(
        session=session,
        user_data=user_data,
        organization_id=tenant_context.organization_id,
        restaurant_id=tenant_context.restaurant_id,
    )
    
    return UserRead(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        organization_id=str(user.organization_id),
        restaurant_id=str(user.restaurant_id) if user.restaurant_id else None,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
    )


@users_router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    user_data: dict,
    tenant_context: TenantContext = Depends(get_tenant_context),
    session: AsyncSession = Depends(get_session),
):
    """Update user (admin only)."""
    if tenant_context.user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can update users",
        )
    
    # Get user
    statement = select(User).where(
        User.id == user_id,
        User.organization_id == tenant_context.organization_id,
    )
    result = await session.exec(statement)
    user = result.first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Update user fields
    for field, value in user_data.items():
        if hasattr(user, field) and field != "id":
            setattr(user, field, value)
    
    session.add(user)
    await session.commit()
    await session.refresh(user)
    
    return UserRead(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        role=user.role,
        organization_id=str(user.organization_id),
        restaurant_id=str(user.restaurant_id) if user.restaurant_id else None,
        created_at=user.created_at.isoformat(),
        updated_at=user.updated_at.isoformat(),
    )