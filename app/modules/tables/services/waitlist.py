from typing import List, Optional, Dict, Any
from datetime import date, time, datetime
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func
from fastapi import HTTPException, status
from app.modules.tables.models.waitlist import (
    ReservationWaitlist,
    WaitlistCreate,
    WaitlistUpdate,
    WaitlistNotify,
)
from app.modules.tables.services.availability import AvailabilityService
from app.modules.tables.models.availability import AvailabilityQuery
from app.shared.cache import cached, cache_invalidate_pattern
from app.core.config import settings


class WaitlistService:
    """Service for waitlist management operations."""
    
    @staticmethod
    @cache_invalidate_pattern("waitlist:*")
    async def add_to_waitlist(
        session: AsyncSession,
        waitlist_data: WaitlistCreate,
        organization_id: str,
        restaurant_id: str,
    ) -> ReservationWaitlist:
        """Add a customer to the waitlist."""
        # Calculate priority score based on party size and preferred time
        priority_score = WaitlistService._calculate_priority_score(
            party_size=waitlist_data.party_size,
            preferred_date=waitlist_data.preferred_date,
            preferred_time=waitlist_data.preferred_time,
        )
        
        # Get the data and override priority_score with calculated value
        waitlist_data_dict = waitlist_data.model_dump()
        waitlist_data_dict['priority_score'] = priority_score
        
        waitlist_entry = ReservationWaitlist(
            **waitlist_data_dict,
            organization_id=organization_id,
            restaurant_id=restaurant_id,
        )
        
        session.add(waitlist_entry)
        await session.commit()
        await session.refresh(waitlist_entry)
        
        return waitlist_entry
    
    @staticmethod
    # @cached(ttl=settings.REDIS_TTL_RESERVATIONS, key_prefix="waitlist")  # Disabled due to serialization issues
    async def get_waitlist(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None,
        preferred_date: Optional[date] = None,
    ) -> List[ReservationWaitlist]:
        """Get waitlist entries for a restaurant."""
        statement = select(ReservationWaitlist).where(
            ReservationWaitlist.organization_id == organization_id,
            ReservationWaitlist.restaurant_id == restaurant_id,
        )
        
        if status:
            statement = statement.where(ReservationWaitlist.status == status)
        
        if preferred_date:
            statement = statement.where(ReservationWaitlist.preferred_date == preferred_date)
        
        # Order by priority score (highest first), then by creation time
        statement = statement.order_by(
            ReservationWaitlist.priority_score.desc(),
            ReservationWaitlist.created_at
        )
        statement = statement.offset(skip).limit(limit)
        
        result = await session.exec(statement)
        return result.all()
    
    @staticmethod
    async def get_waitlist_entry_by_id(
        session: AsyncSession,
        waitlist_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> Optional[ReservationWaitlist]:
        """Get a waitlist entry by ID."""
        statement = select(ReservationWaitlist).where(
            ReservationWaitlist.id == waitlist_id,
            ReservationWaitlist.organization_id == organization_id,
            ReservationWaitlist.restaurant_id == restaurant_id,
        )
        
        result = await session.exec(statement)
        return result.first()
    
    @staticmethod
    async def update_waitlist_entry(
        session: AsyncSession,
        waitlist_id: str,
        waitlist_data: WaitlistUpdate,
        organization_id: str,
        restaurant_id: str,
    ) -> ReservationWaitlist:
        """Update a waitlist entry."""
        waitlist_entry = await WaitlistService.get_waitlist_entry_by_id(
            session, waitlist_id, organization_id, restaurant_id
        )
        
        if not waitlist_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Waitlist entry not found",
            )
        
        update_data = waitlist_data.model_dump(exclude_unset=True)
        
        # Recalculate priority score if relevant fields are updated
        if any(key in update_data for key in ["party_size", "preferred_date", "preferred_time"]):
            party_size = update_data.get("party_size", waitlist_entry.party_size)
            preferred_date = update_data.get("preferred_date", waitlist_entry.preferred_date)
            preferred_time = update_data.get("preferred_time", waitlist_entry.preferred_time)
            
            update_data["priority_score"] = WaitlistService._calculate_priority_score(
                party_size=party_size,
                preferred_date=preferred_date,
                preferred_time=preferred_time,
            )
        
        # Update fields
        for field, value in update_data.items():
            setattr(waitlist_entry, field, value)
        
        session.add(waitlist_entry)
        await session.commit()
        await session.refresh(waitlist_entry)
        
        return waitlist_entry
    
    @staticmethod
    async def remove_from_waitlist(
        session: AsyncSession,
        waitlist_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> bool:
        """Remove a customer from the waitlist."""
        waitlist_entry = await WaitlistService.get_waitlist_entry_by_id(
            session, waitlist_id, organization_id, restaurant_id
        )
        
        if not waitlist_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Waitlist entry not found",
            )
        
        await session.delete(waitlist_entry)
        await session.commit()
        
        return True
    
    @staticmethod
    async def notify_customer(
        session: AsyncSession,
        waitlist_id: str,
        notify_data: WaitlistNotify,
        organization_id: str,
        restaurant_id: str,
    ) -> ReservationWaitlist:
        """Notify a customer from the waitlist about availability."""
        waitlist_entry = await WaitlistService.get_waitlist_entry_by_id(
            session, waitlist_id, organization_id, restaurant_id
        )
        
        if not waitlist_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Waitlist entry not found",
            )
        
        if waitlist_entry.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot notify customer with non-active status",
            )
        
        # Update status to notified
        waitlist_entry.status = "notified"
        
        # Add notification details to notes
        notification_time = datetime.utcnow().isoformat()
        notification_note = f"Notified on {notification_time}"
        if notify_data.available_time:
            notification_note += f" - Available time: {notify_data.available_time}"
        if notify_data.message:
            notification_note += f" - Message: {notify_data.message}"
        
        if waitlist_entry.notes:
            waitlist_entry.notes += f"\n{notification_note}"
        else:
            waitlist_entry.notes = notification_note
        
        session.add(waitlist_entry)
        await session.commit()
        await session.refresh(waitlist_entry)
        
        return waitlist_entry
    
    @staticmethod
    async def mark_as_seated(
        session: AsyncSession,
        waitlist_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> ReservationWaitlist:
        """Mark a waitlist customer as seated."""
        waitlist_entry = await WaitlistService.get_waitlist_entry_by_id(
            session, waitlist_id, organization_id, restaurant_id
        )
        
        if not waitlist_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Waitlist entry not found",
            )
        
        waitlist_entry.status = "seated"
        session.add(waitlist_entry)
        await session.commit()
        await session.refresh(waitlist_entry)
        
        return waitlist_entry
    
    @staticmethod
    async def get_waitlist_analytics(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
        start_date: date,
        end_date: date,
    ) -> Dict[str, Any]:
        """Get waitlist analytics for a date range."""
        statement = select(ReservationWaitlist).where(
            ReservationWaitlist.organization_id == organization_id,
            ReservationWaitlist.restaurant_id == restaurant_id,
            ReservationWaitlist.created_at >= datetime.combine(start_date, time.min),
            ReservationWaitlist.created_at <= datetime.combine(end_date, time.max),
        )
        
        result = await session.exec(statement)
        waitlist_entries = result.all()
        
        # Calculate analytics
        total_entries = len(waitlist_entries)
        status_counts = {}
        party_sizes = []
        conversion_count = 0
        
        for entry in waitlist_entries:
            status = entry.status
            status_counts[status] = status_counts.get(status, 0) + 1
            party_sizes.append(entry.party_size)
            
            if entry.status == "seated":
                conversion_count += 1
        
        # Calculate rates
        avg_party_size = sum(party_sizes) / len(party_sizes) if party_sizes else 0
        conversion_rate = (conversion_count / total_entries * 100) if total_entries > 0 else 0
        
        # Get current active waitlist
        active_waitlist_stmt = select(func.count(ReservationWaitlist.id)).where(
            ReservationWaitlist.organization_id == organization_id,
            ReservationWaitlist.restaurant_id == restaurant_id,
            ReservationWaitlist.status == "active",
        )
        active_result = await session.exec(active_waitlist_stmt)
        current_active = active_result.one()
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
            },
            "total_waitlist_entries": total_entries,
            "current_active_waitlist": current_active,
            "status_breakdown": status_counts,
            "average_party_size": round(avg_party_size, 2),
            "conversion_rate": round(conversion_rate, 2),
            "seated_customers": conversion_count,
        }
    
    @staticmethod
    async def check_availability_for_waitlist(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
        target_date: Optional[date] = None,
    ) -> List[Dict[str, Any]]:
        """Check availability for customers on waitlist and suggest notifications."""
        # Get active waitlist entries
        waitlist_entries = await WaitlistService.get_waitlist(
            session=session,
            organization_id=organization_id,
            restaurant_id=restaurant_id,
            status="active",
            preferred_date=target_date,
        )
        
        notification_suggestions = []
        
        for entry in waitlist_entries:
            if entry.preferred_date and entry.preferred_time:
                # Check availability for this customer's preferences
                query = AvailabilityQuery(
                    date=entry.preferred_date,
                    party_size=entry.party_size,
                    time_preference=entry.preferred_time,
                    duration_minutes=90,
                )
                
                availability = await AvailabilityService.get_available_slots(
                    session=session,
                    organization_id=organization_id,
                    restaurant_id=restaurant_id,
                    query=query,
                )
                
                if not availability.is_fully_booked and availability.available_slots:
                    # Find best matching slot
                    best_slot = None
                    if availability.recommendations:
                        best_slot = availability.recommendations[0]
                    elif availability.available_slots:
                        best_slot = availability.available_slots[0]
                    
                    if best_slot:
                        notification_suggestions.append({
                            "waitlist_entry": {
                                "id": str(entry.id),
                                "customer_name": entry.customer_name,
                                "customer_phone": entry.customer_phone,
                                "customer_email": entry.customer_email,
                                "party_size": entry.party_size,
                                "preferred_date": entry.preferred_date.isoformat(),
                                "preferred_time": entry.preferred_time.isoformat(),
                                "priority_score": entry.priority_score,
                            },
                            "suggested_slot": {
                                "date": entry.preferred_date.isoformat(),
                                "time": best_slot.time.isoformat(),
                                "available_tables": best_slot.available_tables,
                                "total_capacity": best_slot.total_capacity,
                            },
                            "match_quality": "exact" if best_slot.time == entry.preferred_time else "close",
                        })
        
        # Sort by priority score
        notification_suggestions.sort(
            key=lambda x: x["waitlist_entry"]["priority_score"],
            reverse=True
        )
        
        return notification_suggestions
    
    @staticmethod
    def _calculate_priority_score(
        party_size: int,
        preferred_date: Optional[date] = None,
        preferred_time: Optional[time] = None,
    ) -> int:
        """Calculate priority score for waitlist ordering."""
        score = 0
        
        # Base score
        score += 100
        
        # Party size factor (larger parties get higher priority for efficiency)
        if party_size >= 6:
            score += 50
        elif party_size >= 4:
            score += 25
        elif party_size >= 2:
            score += 10
        
        # Date proximity factor
        if preferred_date:
            days_until = (preferred_date - date.today()).days
            if days_until <= 1:  # Same day or next day
                score += 100
            elif days_until <= 3:  # Within 3 days
                score += 50
            elif days_until <= 7:  # Within a week
                score += 25
        
        # Time preference factor (peak hours get higher priority)
        if preferred_time:
            hour = preferred_time.hour
            if 18 <= hour <= 20:  # Peak dinner hours
                score += 30
            elif 12 <= hour <= 14:  # Peak lunch hours
                score += 20
            elif 17 <= hour <= 21:  # Popular dinner hours
                score += 15
        
        return score