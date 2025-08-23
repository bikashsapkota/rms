from typing import List, Optional, Dict, Any
from datetime import date, time
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from fastapi import HTTPException, status
from app.modules.tables.models.reservation import (
    Reservation,
    ReservationCreate,
    ReservationPublic,
)
from app.modules.tables.models.waitlist import (
    ReservationWaitlist,
    WaitlistCreate,
)
from app.modules.tables.models.availability import AvailabilityQuery
from app.modules.tables.services.availability import AvailabilityService
from app.modules.tables.services.reservation import ReservationService
from app.modules.tables.services.waitlist import WaitlistService
from app.shared.cache import cached, cache_invalidate_pattern
from app.core.config import settings


class CustomerService:
    """Service for customer-facing reservation operations."""
    
    @staticmethod
    @cached(ttl=settings.REDIS_TTL_AVAILABILITY, key_prefix="public_availability")
    async def get_availability(
        session: AsyncSession,
        restaurant_id: str,
        reservation_date: date,
        party_size: int,
        time_preference: Optional[time] = None,
        duration_minutes: int = 90,
    ) -> Dict[str, Any]:
        """Get availability for customers (public endpoint)."""
        # Get restaurant info for organization_id
        from app.shared.models.restaurant import Restaurant
        restaurant_stmt = select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.is_active == True,
        )
        restaurant_result = await session.exec(restaurant_stmt)
        restaurant = restaurant_result.first()
        
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )
        
        # Check availability
        query = AvailabilityQuery(
            date=reservation_date,
            party_size=party_size,
            time_preference=time_preference,
            duration_minutes=duration_minutes,
        )
        
        availability = await AvailabilityService.get_available_slots(
            session=session,
            organization_id=str(restaurant.organization_id),
            restaurant_id=restaurant_id,
            query=query,
        )
        
        # If fully booked, suggest alternatives
        alternatives = []
        if availability.is_fully_booked:
            alternatives = await AvailabilityService.find_alternative_slots(
                session=session,
                organization_id=str(restaurant.organization_id),
                restaurant_id=restaurant_id,
                preferred_date=reservation_date,
                preferred_time=time_preference or time(19, 0),  # Default to 7 PM
                party_size=party_size,
                duration_minutes=duration_minutes,
            )
        
        return {
            "restaurant_id": restaurant_id,
            "restaurant_name": restaurant.name,
            "date": reservation_date.isoformat(),
            "party_size": party_size,
            "available_slots": [
                {
                    "time": slot.time.isoformat(),
                    "available_tables": slot.available_tables,
                    "total_capacity": slot.total_capacity,
                }
                for slot in availability.available_slots
            ],
            "recommendations": [
                {
                    "time": slot.time.isoformat(),
                    "available_tables": slot.available_tables,
                    "total_capacity": slot.total_capacity,
                }
                for slot in availability.recommendations
            ],
            "is_fully_booked": availability.is_fully_booked,
            "alternatives": [
                {
                    "time": slot.time.isoformat(),
                    "available_tables": slot.available_tables,
                    "total_capacity": slot.total_capacity,
                }
                for slot in alternatives
            ] if alternatives else [],
        }
    
    @staticmethod
    async def create_reservation(
        session: AsyncSession,
        restaurant_id: str,
        reservation_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Create a reservation for a customer (public endpoint)."""
        # Get restaurant info
        from app.shared.models.restaurant import Restaurant
        restaurant_stmt = select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.is_active == True,
        )
        restaurant_result = await session.exec(restaurant_stmt)
        restaurant = restaurant_result.first()
        
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )
        
        # Validate required fields
        required_fields = ["customer_name", "party_size", "reservation_date", "reservation_time"]
        for field in required_fields:
            if field not in reservation_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}",
                )
        
        # Create reservation data
        create_data = ReservationCreate(
            customer_name=reservation_data["customer_name"],
            customer_phone=reservation_data.get("customer_phone"),
            customer_email=reservation_data.get("customer_email"),
            party_size=reservation_data["party_size"],
            reservation_date=reservation_data["reservation_date"],
            reservation_time=reservation_data["reservation_time"],
            duration_minutes=reservation_data.get("duration_minutes", 90),
            special_requests=reservation_data.get("special_requests"),
            customer_preferences=reservation_data.get("customer_preferences", {}),
        )
        
        # Create the reservation
        reservation = await ReservationService.create_reservation(
            session=session,
            reservation_data=create_data,
            organization_id=str(restaurant.organization_id),
            restaurant_id=restaurant_id,
        )
        
        return {
            "reservation_id": str(reservation.id),
            "customer_name": reservation.customer_name,
            "party_size": reservation.party_size,
            "reservation_date": reservation.reservation_date.isoformat(),
            "reservation_time": reservation.reservation_time.isoformat(),
            "status": reservation.status,
            "restaurant_name": restaurant.name,
            "confirmation_message": f"Reservation confirmed for {reservation.customer_name} on {reservation.reservation_date} at {reservation.reservation_time}",
        }
    
    @staticmethod
    async def join_waitlist(
        session: AsyncSession,
        restaurant_id: str,
        waitlist_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Add customer to waitlist (public endpoint)."""
        # Get restaurant info
        from app.shared.models.restaurant import Restaurant
        restaurant_stmt = select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.is_active == True,
        )
        restaurant_result = await session.exec(restaurant_stmt)
        restaurant = restaurant_result.first()
        
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )
        
        # Validate required fields
        required_fields = ["customer_name", "party_size"]
        for field in required_fields:
            if field not in waitlist_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required field: {field}",
                )
        
        # Create waitlist data
        create_data = WaitlistCreate(
            customer_name=waitlist_data["customer_name"],
            customer_phone=waitlist_data.get("customer_phone"),
            customer_email=waitlist_data.get("customer_email"),
            party_size=waitlist_data["party_size"],
            preferred_date=waitlist_data.get("preferred_date"),
            preferred_time=waitlist_data.get("preferred_time"),
            notes=waitlist_data.get("notes"),
        )
        
        # Add to waitlist
        waitlist_entry = await WaitlistService.add_to_waitlist(
            session=session,
            waitlist_data=create_data,
            organization_id=str(restaurant.organization_id),
            restaurant_id=restaurant_id,
        )
        
        # Get current position in waitlist
        position = await CustomerService._get_waitlist_position(
            session=session,
            waitlist_entry_id=str(waitlist_entry.id),
            organization_id=str(restaurant.organization_id),
            restaurant_id=restaurant_id,
        )
        
        return {
            "waitlist_id": str(waitlist_entry.id),
            "customer_name": waitlist_entry.customer_name,
            "party_size": waitlist_entry.party_size,
            "position": position,
            "priority_score": waitlist_entry.priority_score,
            "restaurant_name": restaurant.name,
            "confirmation_message": f"Added to waitlist - you are currently position #{position}",
        }
    
    @staticmethod
    async def get_reservation_status(
        session: AsyncSession,
        restaurant_id: str,
        customer_phone: str,
        customer_name: str,
    ) -> List[Dict[str, Any]]:
        """Get reservation status for a customer (public endpoint)."""
        # Get restaurant info
        from app.shared.models.restaurant import Restaurant
        restaurant_stmt = select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.is_active == True,
        )
        restaurant_result = await session.exec(restaurant_stmt)
        restaurant = restaurant_result.first()
        
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )
        
        # Find reservations for this customer
        reservations_stmt = select(Reservation).where(
            Reservation.restaurant_id == restaurant_id,
            Reservation.customer_phone == customer_phone,
            Reservation.customer_name == customer_name,
            Reservation.status.in_(["confirmed", "seated"]),
        ).order_by(Reservation.reservation_date.desc(), Reservation.reservation_time.desc())
        
        reservations_result = await session.exec(reservations_stmt)
        reservations = reservations_result.all()
        
        reservation_list = []
        for reservation in reservations:
            reservation_list.append({
                "reservation_id": str(reservation.id),
                "customer_name": reservation.customer_name,
                "party_size": reservation.party_size,
                "reservation_date": reservation.reservation_date.isoformat(),
                "reservation_time": reservation.reservation_time.isoformat(),
                "status": reservation.status,
                "special_requests": reservation.special_requests,
            })
        
        return reservation_list
    
    @staticmethod
    async def cancel_reservation(
        session: AsyncSession,
        restaurant_id: str,
        reservation_id: str,
        customer_phone: str,
    ) -> Dict[str, Any]:
        """Cancel a reservation (public endpoint)."""
        # Get restaurant info
        from app.shared.models.restaurant import Restaurant
        restaurant_stmt = select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.is_active == True,
        )
        restaurant_result = await session.exec(restaurant_stmt)
        restaurant = restaurant_result.first()
        
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )
        
        # Find and validate reservation
        reservation_stmt = select(Reservation).where(
            Reservation.id == reservation_id,
            Reservation.restaurant_id == restaurant_id,
            Reservation.customer_phone == customer_phone,
        )
        reservation_result = await session.exec(reservation_stmt)
        reservation = reservation_result.first()
        
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found or phone number doesn't match",
            )
        
        if reservation.status in ["cancelled", "completed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel reservation with status '{reservation.status}'",
            )
        
        # Cancel the reservation
        cancelled_reservation = await ReservationService.cancel_reservation(
            session=session,
            reservation_id=reservation_id,
            organization_id=str(restaurant.organization_id),
            restaurant_id=restaurant_id,
        )
        
        return {
            "reservation_id": str(cancelled_reservation.id),
            "status": cancelled_reservation.status,
            "message": "Reservation cancelled successfully",
        }
    
    @staticmethod
    async def get_waitlist_status(
        session: AsyncSession,
        restaurant_id: str,
        customer_phone: str,
        customer_name: str,
    ) -> List[Dict[str, Any]]:
        """Get waitlist status for a customer (public endpoint)."""
        # Get restaurant info
        from app.shared.models.restaurant import Restaurant
        restaurant_stmt = select(Restaurant).where(
            Restaurant.id == restaurant_id,
            Restaurant.is_active == True,
        )
        restaurant_result = await session.exec(restaurant_stmt)
        restaurant = restaurant_result.first()
        
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found",
            )
        
        # Find waitlist entries for this customer
        waitlist_stmt = select(ReservationWaitlist).where(
            ReservationWaitlist.restaurant_id == restaurant_id,
            ReservationWaitlist.customer_phone == customer_phone,
            ReservationWaitlist.customer_name == customer_name,
            ReservationWaitlist.status.in_(["active", "notified"]),
        ).order_by(ReservationWaitlist.created_at.desc())
        
        waitlist_result = await session.exec(waitlist_stmt)
        waitlist_entries = waitlist_result.all()
        
        waitlist_list = []
        for entry in waitlist_entries:
            position = await CustomerService._get_waitlist_position(
                session=session,
                waitlist_entry_id=str(entry.id),
                organization_id=str(restaurant.organization_id),
                restaurant_id=restaurant_id,
            )
            
            waitlist_list.append({
                "waitlist_id": str(entry.id),
                "customer_name": entry.customer_name,
                "party_size": entry.party_size,
                "preferred_date": entry.preferred_date.isoformat() if entry.preferred_date else None,
                "preferred_time": entry.preferred_time.isoformat() if entry.preferred_time else None,
                "status": entry.status,
                "position": position,
                "priority_score": entry.priority_score,
            })
        
        return waitlist_list
    
    @staticmethod
    async def _get_waitlist_position(
        session: AsyncSession,
        waitlist_entry_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> int:
        """Get the position of a waitlist entry."""
        # Get all active waitlist entries ordered by priority
        waitlist_stmt = select(ReservationWaitlist).where(
            ReservationWaitlist.organization_id == organization_id,
            ReservationWaitlist.restaurant_id == restaurant_id,
            ReservationWaitlist.status == "active",
        ).order_by(
            ReservationWaitlist.priority_score.desc(),
            ReservationWaitlist.created_at
        )
        
        waitlist_result = await session.exec(waitlist_stmt)
        waitlist_entries = waitlist_result.all()
        
        # Find position
        for i, entry in enumerate(waitlist_entries):
            if str(entry.id) == waitlist_entry_id:
                return i + 1
        
        return 0  # Not found or not active