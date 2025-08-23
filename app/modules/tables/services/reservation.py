from typing import List, Optional, Dict, Any
from datetime import date, time, datetime, timedelta
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, and_, or_
from fastapi import HTTPException, status
from app.modules.tables.models.reservation import (
    Reservation,
    ReservationCreate,
    ReservationUpdate,
    ReservationCheckIn,
    ReservationAssignTable,
    ReservationNoShow,
)
from app.modules.tables.models.table import Table
from app.shared.cache import cached, cache_invalidate_pattern
from app.core.config import settings


class ReservationService:
    """Service for reservation management operations."""
    
    @staticmethod
    @cache_invalidate_pattern("reservations:*")
    @cache_invalidate_pattern("availability:*")
    async def create_reservation(
        session: AsyncSession,
        reservation_data: ReservationCreate,
        organization_id: str,
        restaurant_id: str,
    ) -> Reservation:
        """Create a new reservation."""
        # Convert string UUIDs to UUID objects
        org_uuid = UUID(organization_id) if isinstance(organization_id, str) else organization_id
        rest_uuid = UUID(restaurant_id) if isinstance(restaurant_id, str) else restaurant_id
        
        # Validate table if specified
        if reservation_data.table_id:
            table_id_uuid = UUID(reservation_data.table_id) if isinstance(reservation_data.table_id, str) else reservation_data.table_id
            table_stmt = select(Table).where(
                Table.id == table_id_uuid,
                Table.organization_id == org_uuid,
                Table.restaurant_id == rest_uuid,
                Table.is_active == True,
            )
            table_result = await session.exec(table_stmt)
            table = table_result.first()
            
            if not table:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid table ID or table not available",
                )
            
            # Check table capacity
            if reservation_data.party_size > table.capacity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Party size ({reservation_data.party_size}) exceeds table capacity ({table.capacity})",
                )
        
        # Check for conflicting reservations if table is assigned
        if reservation_data.table_id:
            await ReservationService._check_table_availability(
                session=session,
                table_id=reservation_data.table_id,
                reservation_date=reservation_data.reservation_date,
                reservation_time=reservation_data.reservation_time,
                duration_minutes=reservation_data.duration_minutes,
            )
        
        reservation = Reservation(
            **reservation_data.model_dump(),
            organization_id=org_uuid,
            restaurant_id=rest_uuid,
        )
        
        session.add(reservation)
        await session.commit()
        await session.refresh(reservation)
        
        return reservation
    
    @staticmethod
    @cached(ttl=settings.REDIS_TTL_RESERVATIONS, key_prefix="reservations")
    async def get_reservations(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
        skip: int = 0,
        limit: int = 100,
        reservation_date: Optional[date] = None,
        status: Optional[str] = None,
        table_id: Optional[str] = None,
    ) -> List[Reservation]:
        """Get reservations for a restaurant with optional filters."""
        # Convert string UUIDs to UUID objects
        org_uuid = UUID(organization_id) if isinstance(organization_id, str) else organization_id
        rest_uuid = UUID(restaurant_id) if isinstance(restaurant_id, str) else restaurant_id
        
        statement = select(Reservation).where(
            Reservation.organization_id == org_uuid,
            Reservation.restaurant_id == rest_uuid,
        )
        
        if reservation_date:
            statement = statement.where(Reservation.reservation_date == reservation_date)
        
        if status:
            statement = statement.where(Reservation.status == status)
        
        if table_id:
            table_id_uuid = UUID(table_id) if isinstance(table_id, str) else table_id
            statement = statement.where(Reservation.table_id == table_id_uuid)
        
        statement = statement.order_by(
            Reservation.reservation_date.desc(),
            Reservation.reservation_time
        )
        statement = statement.offset(skip).limit(limit)
        
        result = await session.exec(statement)
        return result.all()
    
    @staticmethod
    async def get_reservation_by_id(
        session: AsyncSession,
        reservation_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> Optional[Reservation]:
        """Get a reservation by ID."""
        # Convert string UUIDs to UUID objects
        res_uuid = UUID(reservation_id) if isinstance(reservation_id, str) else reservation_id
        org_uuid = UUID(organization_id) if isinstance(organization_id, str) else organization_id
        rest_uuid = UUID(restaurant_id) if isinstance(restaurant_id, str) else restaurant_id
        
        statement = select(Reservation).where(
            Reservation.id == res_uuid,
            Reservation.organization_id == org_uuid,
            Reservation.restaurant_id == rest_uuid,
        )
        
        result = await session.exec(statement)
        return result.first()
    
    @staticmethod
    @cache_invalidate_pattern("reservations:*")
    @cache_invalidate_pattern("availability:*")
    async def update_reservation(
        session: AsyncSession,
        reservation_id: str,
        reservation_data: ReservationUpdate,
        organization_id: str,
        restaurant_id: str,
    ) -> Reservation:
        """Update a reservation."""
        reservation = await ReservationService.get_reservation_by_id(
            session, reservation_id, organization_id, restaurant_id
        )
        
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found",
            )
        
        update_data = reservation_data.model_dump(exclude_unset=True)
        
        # Convert string UUIDs to UUID objects
        org_uuid = UUID(organization_id) if isinstance(organization_id, str) else organization_id
        rest_uuid = UUID(restaurant_id) if isinstance(restaurant_id, str) else restaurant_id
        
        # Validate table if being updated
        if "table_id" in update_data and update_data["table_id"]:
            table_id_uuid = UUID(update_data["table_id"]) if isinstance(update_data["table_id"], str) else update_data["table_id"]
            table_stmt = select(Table).where(
                Table.id == table_id_uuid,
                Table.organization_id == org_uuid,
                Table.restaurant_id == rest_uuid,
                Table.is_active == True,
            )
            table_result = await session.exec(table_stmt)
            table = table_result.first()
            
            if not table:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid table ID or table not available",
                )
            
            # Check capacity with updated party size
            party_size = update_data.get("party_size", reservation.party_size)
            if party_size > table.capacity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Party size ({party_size}) exceeds table capacity ({table.capacity})",
                )
        
        # Check for conflicts if time/date/table is being updated
        if any(key in update_data for key in ["table_id", "reservation_date", "reservation_time", "duration_minutes"]):
            new_table_id = update_data.get("table_id", reservation.table_id)
            new_date = update_data.get("reservation_date", reservation.reservation_date)
            new_time = update_data.get("reservation_time", reservation.reservation_time)
            new_duration = update_data.get("duration_minutes", reservation.duration_minutes)
            
            if new_table_id:
                res_uuid = UUID(reservation_id) if isinstance(reservation_id, str) else reservation_id
                await ReservationService._check_table_availability(
                    session=session,
                    table_id=new_table_id,
                    reservation_date=new_date,
                    reservation_time=new_time,
                    duration_minutes=new_duration,
                    exclude_reservation_id=res_uuid,
                )
        
        # Update fields
        for field, value in update_data.items():
            setattr(reservation, field, value)
        
        session.add(reservation)
        await session.commit()
        await session.refresh(reservation)
        
        return reservation
    
    @staticmethod
    @cache_invalidate_pattern("reservations:*")
    @cache_invalidate_pattern("availability:*")
    async def cancel_reservation(
        session: AsyncSession,
        reservation_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> Reservation:
        """Cancel a reservation."""
        reservation = await ReservationService.get_reservation_by_id(
            session, reservation_id, organization_id, restaurant_id
        )
        
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found",
            )
        
        if reservation.status in ["completed", "cancelled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel reservation with status '{reservation.status}'",
            )
        
        reservation.status = "cancelled"
        session.add(reservation)
        await session.commit()
        await session.refresh(reservation)
        
        return reservation
    
    @staticmethod
    async def check_in_reservation(
        session: AsyncSession,
        reservation_id: str,
        checkin_data: ReservationCheckIn,
        organization_id: str,
        restaurant_id: str,
    ) -> Reservation:
        """Check in a customer for their reservation."""
        reservation = await ReservationService.get_reservation_by_id(
            session, reservation_id, organization_id, restaurant_id
        )
        
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found",
            )
        
        if reservation.status != "confirmed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot check in reservation with status '{reservation.status}'",
            )
        
        # Convert string UUIDs to UUID objects
        org_uuid = UUID(organization_id) if isinstance(organization_id, str) else organization_id
        rest_uuid = UUID(restaurant_id) if isinstance(restaurant_id, str) else restaurant_id
        
        # Assign table if specified and not already assigned
        if checkin_data.table_id and reservation.table_id != checkin_data.table_id:
            table_id_uuid = UUID(checkin_data.table_id) if isinstance(checkin_data.table_id, str) else checkin_data.table_id
            table_stmt = select(Table).where(
                Table.id == table_id_uuid,
                Table.organization_id == org_uuid,
                Table.restaurant_id == rest_uuid,
                Table.is_active == True,
            )
            table_result = await session.exec(table_stmt)
            table = table_result.first()
            
            if not table:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid table ID or table not available",
                )
            
            # Check capacity
            if reservation.party_size > table.capacity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Party size ({reservation.party_size}) exceeds table capacity ({table.capacity})",
                )
            
            reservation.table_id = checkin_data.table_id
        
        reservation.status = "seated"
        session.add(reservation)
        await session.commit()
        await session.refresh(reservation)
        
        return reservation
    
    @staticmethod
    async def assign_table(
        session: AsyncSession,
        reservation_id: str,
        table_data: ReservationAssignTable,
        organization_id: str,
        restaurant_id: str,
    ) -> Reservation:
        """Assign a table to a reservation."""
        reservation = await ReservationService.get_reservation_by_id(
            session, reservation_id, organization_id, restaurant_id
        )
        
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found",
            )
        
        # Convert string UUIDs to UUID objects
        org_uuid = UUID(organization_id) if isinstance(organization_id, str) else organization_id
        rest_uuid = UUID(restaurant_id) if isinstance(restaurant_id, str) else restaurant_id
        
        # Validate table
        table_id_uuid = UUID(table_data.table_id) if isinstance(table_data.table_id, str) else table_data.table_id
        table_stmt = select(Table).where(
            Table.id == table_id_uuid,
            Table.organization_id == org_uuid,
            Table.restaurant_id == rest_uuid,
            Table.is_active == True,
        )
        table_result = await session.exec(table_stmt)
        table = table_result.first()
        
        if not table:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid table ID or table not available",
            )
        
        # Check capacity
        if reservation.party_size > table.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Party size ({reservation.party_size}) exceeds table capacity ({table.capacity})",
            )
        
        # Check availability
        res_uuid = UUID(reservation_id) if isinstance(reservation_id, str) else reservation_id
        await ReservationService._check_table_availability(
            session=session,
            table_id=table_data.table_id,
            reservation_date=reservation.reservation_date,
            reservation_time=reservation.reservation_time,
            duration_minutes=reservation.duration_minutes,
            exclude_reservation_id=res_uuid,
        )
        
        reservation.table_id = table_data.table_id
        session.add(reservation)
        await session.commit()
        await session.refresh(reservation)
        
        return reservation
    
    @staticmethod
    async def mark_no_show(
        session: AsyncSession,
        reservation_id: str,
        no_show_data: ReservationNoShow,
        organization_id: str,
        restaurant_id: str,
    ) -> Reservation:
        """Mark a reservation as no-show."""
        reservation = await ReservationService.get_reservation_by_id(
            session, reservation_id, organization_id, restaurant_id
        )
        
        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found",
            )
        
        if reservation.status not in ["confirmed", "seated"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot mark reservation with status '{reservation.status}' as no-show",
            )
        
        reservation.status = "no_show"
        session.add(reservation)
        await session.commit()
        await session.refresh(reservation)
        
        return reservation
    
    @staticmethod
    @cached(ttl=settings.REDIS_TTL_RESERVATIONS, key_prefix="reservations")
    async def get_today_reservations(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
    ) -> List[Dict[str, Any]]:
        """Get today's reservations with table details."""
        # Convert string UUIDs to UUID objects
        org_uuid = UUID(organization_id) if isinstance(organization_id, str) else organization_id
        rest_uuid = UUID(restaurant_id) if isinstance(restaurant_id, str) else restaurant_id
        
        today = date.today()
        
        statement = select(Reservation, Table).join(
            Table,
            Reservation.table_id == Table.id,
            isouter=True,
        ).where(
            Reservation.organization_id == org_uuid,
            Reservation.restaurant_id == rest_uuid,
            Reservation.reservation_date == today,
        ).order_by(Reservation.reservation_time)
        
        result = await session.exec(statement)
        reservations_with_tables = result.all()
        
        today_reservations = []
        for reservation, table in reservations_with_tables:
            reservation_data = {
                "id": str(reservation.id),
                "customer_name": reservation.customer_name,
                "customer_phone": reservation.customer_phone,
                "customer_email": reservation.customer_email,
                "party_size": reservation.party_size,
                "reservation_date": reservation.reservation_date.isoformat(),
                "reservation_time": reservation.reservation_time.isoformat(),
                "duration_minutes": reservation.duration_minutes,
                "status": reservation.status,
                "special_requests": reservation.special_requests,
                "customer_preferences": reservation.customer_preferences,
                "table_id": str(reservation.table_id) if reservation.table_id else None,
                "table_number": table.table_number if table else None,
                "table_capacity": table.capacity if table else None,
                "created_at": reservation.created_at.isoformat(),
                "updated_at": reservation.updated_at.isoformat(),
            }
            today_reservations.append(reservation_data)
        
        return today_reservations
    
    @staticmethod
    async def get_reservation_calendar(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """Get reservations for a date range (calendar view)."""
        # Convert string UUIDs to UUID objects
        org_uuid = UUID(organization_id) if isinstance(organization_id, str) else organization_id
        rest_uuid = UUID(restaurant_id) if isinstance(restaurant_id, str) else restaurant_id
        
        statement = select(Reservation).where(
            Reservation.organization_id == org_uuid,
            Reservation.restaurant_id == rest_uuid,
            Reservation.reservation_date.between(start_date, end_date),
        ).order_by(Reservation.reservation_date, Reservation.reservation_time)
        
        result = await session.exec(statement)
        reservations = result.all()
        
        # Group by date
        calendar_data = {}
        for reservation in reservations:
            date_str = reservation.reservation_date.isoformat()
            if date_str not in calendar_data:
                calendar_data[date_str] = []
            
            calendar_data[date_str].append({
                "id": str(reservation.id),
                "customer_name": reservation.customer_name,
                "party_size": reservation.party_size,
                "reservation_time": reservation.reservation_time.isoformat(),
                "status": reservation.status,
                "table_id": str(reservation.table_id) if reservation.table_id else None,
            })
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "reservations_by_date": calendar_data,
        }
    
    @staticmethod
    async def get_reservation_analytics(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """Get reservation analytics for a date range."""
        # Convert string UUIDs to UUID objects
        org_uuid = UUID(organization_id) if isinstance(organization_id, str) else organization_id
        rest_uuid = UUID(restaurant_id) if isinstance(restaurant_id, str) else restaurant_id
        
        statement = select(Reservation).where(
            Reservation.organization_id == org_uuid,
            Reservation.restaurant_id == rest_uuid,
            Reservation.reservation_date.between(start_date, end_date),
        )
        
        result = await session.exec(statement)
        reservations = result.all()
        
        # Calculate analytics
        total_reservations = len(reservations)
        status_counts = {}
        party_sizes = []
        time_slots = {}
        
        for reservation in reservations:
            # Status breakdown
            status = reservation.status
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Party sizes
            party_sizes.append(reservation.party_size)
            
            # Time slot popularity
            hour = reservation.reservation_time.hour
            time_slot = f"{hour:02d}:00"
            time_slots[time_slot] = time_slots.get(time_slot, 0) + 1
        
        # Calculate averages
        avg_party_size = sum(party_sizes) / len(party_sizes) if party_sizes else 0
        
        # Calculate rates
        confirmed_count = status_counts.get("confirmed", 0)
        completed_count = status_counts.get("completed", 0)
        no_show_count = status_counts.get("no_show", 0)
        cancelled_count = status_counts.get("cancelled", 0)
        
        completion_rate = (completed_count / total_reservations * 100) if total_reservations > 0 else 0
        no_show_rate = (no_show_count / total_reservations * 100) if total_reservations > 0 else 0
        cancellation_rate = (cancelled_count / total_reservations * 100) if total_reservations > 0 else 0
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "total_reservations": total_reservations,
            "status_breakdown": status_counts,
            "average_party_size": round(avg_party_size, 2),
            "completion_rate": round(completion_rate, 2),
            "no_show_rate": round(no_show_rate, 2),
            "cancellation_rate": round(cancellation_rate, 2),
            "peak_hours": dict(sorted(time_slots.items(), key=lambda x: x[1], reverse=True)[:5]),
        }
    
    @staticmethod
    async def _check_table_availability(
        session: AsyncSession,
        table_id: str,
        reservation_date: date,
        reservation_time: time,
        duration_minutes: int,
        exclude_reservation_id: Optional[str] = None,
    ) -> None:
        """Check if a table is available for the given time slot."""
        # Convert string UUIDs to UUID objects
        table_id_uuid = UUID(table_id) if isinstance(table_id, str) else table_id
        
        # Calculate time range
        start_datetime = datetime.combine(reservation_date, reservation_time)
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        
        # Check for overlapping reservations - simplified approach
        overlapping_stmt = select(Reservation).where(
            Reservation.table_id == table_id_uuid,
            Reservation.reservation_date == reservation_date,
            Reservation.status.in_(["confirmed", "seated"]),
        )
        
        if exclude_reservation_id:
            exclude_uuid = UUID(exclude_reservation_id) if isinstance(exclude_reservation_id, str) else exclude_reservation_id
            overlapping_stmt = overlapping_stmt.where(Reservation.id != exclude_uuid)
        
        overlapping_result = await session.exec(overlapping_stmt)
        overlapping_reservations = overlapping_result.all()
        
        # Check for time conflicts in Python (more reliable than complex SQL)
        for existing_reservation in overlapping_reservations:
            existing_start = datetime.combine(
                existing_reservation.reservation_date, 
                existing_reservation.reservation_time
            )
            existing_end = existing_start + timedelta(minutes=existing_reservation.duration_minutes)
            
            # Check if times overlap
            if (start_datetime < existing_end and end_datetime > existing_start):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Table is not available at the requested time. Conflicts with existing reservation at {existing_reservation.reservation_time}.",
                )