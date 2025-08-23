from typing import List, Optional, Dict, Any
from datetime import date, time, datetime, timedelta
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, and_, or_
from app.modules.tables.models.table import Table
from app.modules.tables.models.reservation import Reservation
from app.modules.tables.models.availability import (
    AvailabilitySlot,
    DayAvailability,
    AvailabilityCalendar,
    AvailabilityQuery,
    AvailabilityResponse,
    CapacityOptimization,
)
from app.shared.cache import cached, cache_invalidate_pattern
from app.core.config import settings


class AvailabilityService:
    """Service for availability management and scheduling."""
    
    @staticmethod
    @cached(ttl=settings.REDIS_TTL_AVAILABILITY, key_prefix="availability")
    async def get_available_slots(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
        query: AvailabilityQuery,
    ) -> AvailabilityResponse:
        """Get available time slots for a given date and party size."""
        # Get all active tables that can accommodate the party size
        tables_stmt = select(Table).where(
            Table.organization_id == organization_id,
            Table.restaurant_id == restaurant_id,
            Table.is_active == True,
            Table.capacity >= query.party_size,
            Table.status.in_(["available", "reserved"]),  # Include reserved tables for scheduling
        )
        tables_result = await session.exec(tables_stmt)
        suitable_tables = tables_result.all()
        
        if not suitable_tables:
            return AvailabilityResponse(
                date=query.date,
                available_slots=[],
                is_fully_booked=True,
            )
        
        # Get existing reservations for the date
        reservations_stmt = select(Reservation).where(
            Reservation.organization_id == organization_id,
            Reservation.restaurant_id == restaurant_id,
            Reservation.reservation_date == query.date,
            Reservation.status.in_(["confirmed", "seated"]),
        )
        reservations_result = await session.exec(reservations_stmt)
        existing_reservations = reservations_result.all()
        
        # Generate time slots (every 30 minutes from 11:00 to 22:00)
        available_slots = []
        recommendations = []
        
        start_hour = 11
        end_hour = 22
        slot_interval = 30  # minutes
        
        current_time = time(start_hour, 0)
        while current_time.hour < end_hour or (current_time.hour == end_hour and current_time.minute == 0):
            slot_availability = await AvailabilityService._check_slot_availability(
                suitable_tables=suitable_tables,
                existing_reservations=existing_reservations,
                slot_time=current_time,
                party_size=query.party_size,
                duration_minutes=query.duration_minutes,
            )
            
            if slot_availability["available_tables"] > 0:
                slot = AvailabilitySlot(
                    time=current_time,
                    available_tables=slot_availability["available_tables"],
                    total_capacity=slot_availability["total_capacity"],
                    is_available=True,
                )
                available_slots.append(slot)
                
                # Add to recommendations if it's a preferred time
                if query.time_preference:
                    time_diff = abs(
                        (datetime.combine(date.today(), current_time) - 
                         datetime.combine(date.today(), query.time_preference)).total_seconds() / 60
                    )
                    if time_diff <= 60:  # Within 1 hour of preference
                        recommendations.append(slot)
            
            # Move to next slot
            current_datetime = datetime.combine(date.today(), current_time)
            next_datetime = current_datetime + timedelta(minutes=slot_interval)
            current_time = next_datetime.time()
        
        # Sort recommendations by proximity to preferred time
        if query.time_preference and recommendations:
            recommendations.sort(
                key=lambda s: abs(
                    (datetime.combine(date.today(), s.time) - 
                     datetime.combine(date.today(), query.time_preference)).total_seconds()
                )
            )
        
        return AvailabilityResponse(
            date=query.date,
            available_slots=available_slots,
            recommendations=recommendations[:3],  # Top 3 recommendations
            is_fully_booked=len(available_slots) == 0,
        )
    
    @staticmethod
    @cached(ttl=settings.REDIS_TTL_AVAILABILITY, key_prefix="availability")
    async def get_monthly_availability(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
        year: int,
        month: int,
    ) -> AvailabilityCalendar:
        """Get availability calendar for a month."""
        # Get first and last day of month
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        days = []
        current_date = first_day
        
        while current_date <= last_day:
            # For each day, check general availability
            query = AvailabilityQuery(
                date=current_date,
                party_size=2,  # Default party size for overview
                duration_minutes=90,
            )
            
            availability_response = await AvailabilityService.get_available_slots(
                session=session,
                organization_id=organization_id,
                restaurant_id=restaurant_id,
                query=query,
            )
            
            day_availability = DayAvailability(
                date=current_date,
                slots=availability_response.available_slots,
                is_open=not availability_response.is_fully_booked,
            )
            days.append(day_availability)
            
            current_date += timedelta(days=1)
        
        return AvailabilityCalendar(
            year=year,
            month=month,
            days=days,
        )
    
    @staticmethod
    async def get_capacity_optimization(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
        target_date: date,
    ) -> CapacityOptimization:
        """Get capacity optimization suggestions for a specific date."""
        # Get reservations for the date
        reservations_stmt = select(Reservation).where(
            Reservation.organization_id == organization_id,
            Reservation.restaurant_id == restaurant_id,
            Reservation.reservation_date == target_date,
            Reservation.status.in_(["confirmed", "seated", "completed"]),
        )
        reservations_result = await session.exec(reservations_stmt)
        reservations = reservations_result.all()
        
        # Get total table capacity
        tables_stmt = select(Table).where(
            Table.organization_id == organization_id,
            Table.restaurant_id == restaurant_id,
            Table.is_active == True,
        )
        tables_result = await session.exec(tables_stmt)
        tables = tables_result.all()
        
        total_capacity = sum(table.capacity for table in tables)
        total_tables = len(tables)
        
        # Calculate occupancy by hour
        hourly_occupancy = {}
        peak_hours = []
        
        for hour in range(11, 23):  # 11 AM to 10 PM
            hour_start = time(hour, 0)
            hour_end = time(hour + 1, 0) if hour < 22 else time(23, 59)
            
            occupied_capacity = 0
            for reservation in reservations:
                reservation_start = reservation.reservation_time
                reservation_end_datetime = (
                    datetime.combine(target_date, reservation.reservation_time) + 
                    timedelta(minutes=reservation.duration_minutes)
                )
                reservation_end = reservation_end_datetime.time()
                
                # Check if reservation overlaps with this hour
                if (reservation_start <= hour_end and reservation_end >= hour_start):
                    occupied_capacity += reservation.party_size
            
            occupancy_rate = (occupied_capacity / total_capacity * 100) if total_capacity > 0 else 0
            hourly_occupancy[f"{hour:02d}:00"] = occupancy_rate
            
            if occupancy_rate > 70:  # Consider >70% as peak
                peak_hours.append(time(hour, 0))
        
        # Calculate overall occupancy rate
        total_party_size = sum(r.party_size for r in reservations)
        current_occupancy_rate = (total_party_size / (total_capacity * 12)) * 100 if total_capacity > 0 else 0  # 12 hours operation
        
        # Generate suggestions
        suggestions = []
        recommended_actions = []
        
        if current_occupancy_rate < 50:
            suggestions.append("Consider promotional offers to increase bookings")
            recommended_actions.append("Launch happy hour specials during low-traffic periods")
        elif current_occupancy_rate > 85:
            suggestions.append("Consider adding more tables or extending hours")
            recommended_actions.append("Optimize table turnover time")
            
        if len(peak_hours) > 6:
            suggestions.append("High demand detected - consider premium pricing during peak hours")
            recommended_actions.append("Implement waitlist management for peak periods")
        
        if len([h for h in hourly_occupancy.values() if h < 30]) > 6:
            suggestions.append("Multiple low-occupancy hours - consider marketing initiatives")
            recommended_actions.append("Offer early bird or late night discounts")
        
        return CapacityOptimization(
            date=target_date,
            current_occupancy_rate=round(current_occupancy_rate, 2),
            suggested_improvements=suggestions,
            peak_hours=peak_hours,
            recommended_actions=recommended_actions,
        )
    
    @staticmethod
    async def _check_slot_availability(
        suitable_tables: List[Table],
        existing_reservations: List[Reservation],
        slot_time: time,
        party_size: int,
        duration_minutes: int,
    ) -> Dict[str, Any]:
        """Check availability for a specific time slot."""
        slot_end_time = (
            datetime.combine(date.today(), slot_time) + 
            timedelta(minutes=duration_minutes)
        ).time()
        
        # Count available tables for this slot
        available_tables = 0
        total_capacity = 0
        
        for table in suitable_tables:
            # Check if this table is free during the slot
            is_table_free = True
            
            for reservation in existing_reservations:
                if (reservation.table_id == table.id and 
                    reservation.status in ["confirmed", "seated"]):
                    
                    reservation_start = reservation.reservation_time
                    reservation_end = (
                        datetime.combine(date.today(), reservation.reservation_time) + 
                        timedelta(minutes=reservation.duration_minutes)
                    ).time()
                    
                    # Check for overlap
                    if not (slot_end_time <= reservation_start or slot_time >= reservation_end):
                        is_table_free = False
                        break
            
            if is_table_free:
                available_tables += 1
                total_capacity += table.capacity
        
        return {
            "available_tables": available_tables,
            "total_capacity": total_capacity,
        }
    
    @staticmethod
    @cached(ttl=settings.REDIS_TTL_AVAILABILITY, key_prefix="availability")
    async def find_alternative_slots(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
        preferred_date: date,
        preferred_time: time,
        party_size: int,
        duration_minutes: int = 90,
    ) -> List[AvailabilitySlot]:
        """Find alternative time slots if preferred time is not available."""
        alternatives = []
        
        # Check same day, different times (±2 hours)
        for time_offset in [-120, -90, -60, -30, 30, 60, 90, 120]:  # minutes
            try:
                alternative_time = (
                    datetime.combine(date.today(), preferred_time) + 
                    timedelta(minutes=time_offset)
                ).time()
                
                # Skip if outside business hours (11 AM - 10 PM)
                if alternative_time.hour < 11 or alternative_time.hour >= 22:
                    continue
                
                query = AvailabilityQuery(
                    date=preferred_date,
                    party_size=party_size,
                    time_preference=alternative_time,
                    duration_minutes=duration_minutes,
                )
                
                availability = await AvailabilityService.get_available_slots(
                    session=session,
                    organization_id=organization_id,
                    restaurant_id=restaurant_id,
                    query=query,
                )
                
                # Find slot closest to alternative time
                for slot in availability.available_slots:
                    if slot.time == alternative_time:
                        alternatives.append(slot)
                        break
            except (ValueError, OverflowError):
                continue
        
        # Check different dates (±3 days), same time
        for date_offset in [-3, -2, -1, 1, 2, 3]:
            try:
                alternative_date = preferred_date + timedelta(days=date_offset)
                
                # Skip past dates
                if alternative_date < date.today():
                    continue
                
                query = AvailabilityQuery(
                    date=alternative_date,
                    party_size=party_size,
                    time_preference=preferred_time,
                    duration_minutes=duration_minutes,
                )
                
                availability = await AvailabilityService.get_available_slots(
                    session=session,
                    organization_id=organization_id,
                    restaurant_id=restaurant_id,
                    query=query,
                )
                
                # Find slot closest to preferred time
                for slot in availability.available_slots:
                    time_diff = abs(
                        (datetime.combine(date.today(), slot.time) - 
                         datetime.combine(date.today(), preferred_time)).total_seconds() / 60
                    )
                    if time_diff <= 30:  # Within 30 minutes
                        alternatives.append(slot)
                        break
            except (ValueError, OverflowError):
                continue
        
        # Sort by proximity to preferred time and date
        alternatives.sort(key=lambda slot: abs(
            (datetime.combine(date.today(), slot.time) - 
             datetime.combine(date.today(), preferred_time)).total_seconds()
        ))
        
        return alternatives[:5]  # Return top 5 alternatives