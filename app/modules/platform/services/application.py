"""
Platform application service for restaurant approval workflow.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.platform.models.application import (
    RestaurantApplication,
    RestaurantApplicationCreate,
    RestaurantApplicationUpdate,
    ApplicationStats,
)
from app.shared.models.organization import Organization, OrganizationCreate
from app.shared.models.restaurant import Restaurant, RestaurantCreate
from app.shared.models.user import User, UserCreate
from app.shared.auth.security import get_password_hash


class PlatformApplicationService:
    """Service for managing restaurant applications."""

    @staticmethod
    async def create_application(
        session: AsyncSession,
        application_data: RestaurantApplicationCreate,
    ) -> RestaurantApplication:
        """Submit a new restaurant application."""
        application = RestaurantApplication(**application_data.model_dump())
        session.add(application)
        await session.commit()
        await session.refresh(application)
        return application

    @staticmethod
    async def get_applications(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
    ) -> List[RestaurantApplication]:
        """Get list of restaurant applications."""
        query = select(RestaurantApplication)
        
        if status:
            query = query.where(RestaurantApplication.status == status)
        
        query = query.order_by(RestaurantApplication.created_at.desc())
        query = query.offset(skip).limit(limit)

        result = await session.exec(query)
        return result.all()

    @staticmethod
    async def get_application_by_id(
        session: AsyncSession,
        application_id: str,
    ) -> Optional[RestaurantApplication]:
        """Get an application by ID."""
        query = select(RestaurantApplication).where(
            RestaurantApplication.id == application_id
        )
        result = await session.exec(query)
        return result.first()

    @staticmethod
    async def update_application(
        session: AsyncSession,
        application_id: str,
        update_data: RestaurantApplicationUpdate,
    ) -> Optional[RestaurantApplication]:
        """Update a restaurant application."""
        application = await PlatformApplicationService.get_application_by_id(
            session, application_id
        )
        if not application:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(application, field, value)

        session.add(application)
        await session.commit()
        await session.refresh(application)
        return application

    @staticmethod
    async def approve_application(
        session: AsyncSession,
        application_id: str,
        admin_notes: Optional[str] = None,
    ) -> bool:
        """Approve a restaurant application and create organization/restaurant."""
        application = await PlatformApplicationService.get_application_by_id(
            session, application_id
        )
        if not application or application.status != "pending":
            return False

        try:
            # Create organization
            org_data = OrganizationCreate(
                name=f"{application.restaurant_name} Organization",
                organization_type="independent",
            )
            organization = Organization(
                **org_data.model_dump()
            )
            session.add(organization)
            await session.flush()  # Get the ID

            # Create restaurant
            restaurant_data = RestaurantCreate(
                name=application.restaurant_name,
                address=application.restaurant_address,
                phone=application.restaurant_phone,
                email=application.restaurant_email,
            )
            restaurant = Restaurant(
                **restaurant_data.model_dump(),
                organization_id=str(organization.id),
            )
            session.add(restaurant)
            await session.flush()  # Get the ID

            # Create admin user
            user_data = UserCreate(
                email=application.applicant_email,
                full_name=application.applicant_name,
                password="change_me_123",  # Default password - should be changed
                role="admin",
            )
            user = User(
                email=user_data.email,
                full_name=user_data.full_name,
                password_hash=get_password_hash(user_data.password),
                role=user_data.role,
                organization_id=str(organization.id),
                restaurant_id=str(restaurant.id),
            )
            session.add(user)

            # Update application
            application.status = "approved"
            application.admin_notes = admin_notes
            application.organization_id = str(organization.id)
            session.add(application)

            await session.commit()
            return True

        except Exception as e:
            await session.rollback()
            raise e

    @staticmethod
    async def reject_application(
        session: AsyncSession,
        application_id: str,
        admin_notes: str,
    ) -> bool:
        """Reject a restaurant application."""
        application = await PlatformApplicationService.get_application_by_id(
            session, application_id
        )
        if not application or application.status != "pending":
            return False

        application.status = "rejected"
        application.admin_notes = admin_notes
        session.add(application)
        await session.commit()
        return True

    @staticmethod
    async def get_application_stats(
        session: AsyncSession,
    ) -> ApplicationStats:
        """Get application statistics."""
        # Total applications
        total_query = select(func.count(RestaurantApplication.id))
        total_result = await session.exec(total_query)
        total_applications = total_result.first() or 0

        # Pending applications
        pending_query = select(func.count(RestaurantApplication.id)).where(
            RestaurantApplication.status == "pending"
        )
        pending_result = await session.exec(pending_query)
        pending_applications = pending_result.first() or 0

        # Approved applications
        approved_query = select(func.count(RestaurantApplication.id)).where(
            RestaurantApplication.status == "approved"
        )
        approved_result = await session.exec(approved_query)
        approved_applications = approved_result.first() or 0

        # Rejected applications
        rejected_query = select(func.count(RestaurantApplication.id)).where(
            RestaurantApplication.status == "rejected"
        )
        rejected_result = await session.exec(rejected_query)
        rejected_applications = rejected_result.first() or 0

        # Recent applications (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_query = select(func.count(RestaurantApplication.id)).where(
            RestaurantApplication.created_at >= thirty_days_ago
        )
        recent_result = await session.exec(recent_query)
        recent_applications = recent_result.first() or 0

        return ApplicationStats(
            total_applications=total_applications,
            pending_applications=pending_applications,
            approved_applications=approved_applications,
            rejected_applications=rejected_applications,
            recent_applications=recent_applications,
        )