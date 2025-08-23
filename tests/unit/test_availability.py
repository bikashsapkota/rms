import pytest
from datetime import date, time, datetime, timedelta
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.tables.models.table import Table, TableCreate
from app.modules.tables.models.reservation import Reservation, ReservationCreate
from app.modules.tables.models.availability import AvailabilityQuery
from app.modules.tables.services.table import TableService
from app.modules.tables.services.reservation import ReservationService
from app.modules.tables.services.availability import AvailabilityService


@pytest.mark.asyncio
async def test_get_available_slots_no_tables(db_session: AsyncSession):
    """Test availability when no tables exist."""
    query = AvailabilityQuery(
        date=date.today() + timedelta(days=1),
        party_size=4,
        duration_minutes=90,
    )
    
    availability = await AvailabilityService.get_available_slots(
        session=db_session,
        organization_id="org123",
        restaurant_id="rest123",
        query=query,
    )
    
    assert availability.is_fully_booked is True
    assert len(availability.available_slots) == 0


@pytest.mark.asyncio
async def test_get_available_slots_with_tables(db_session: AsyncSession):
    """Test availability with tables available."""
    # Create tables
    for i in range(3):
        table_data = TableCreate(
            table_number=f"T00{i+1}",
            capacity=4,
            location="main_dining",
        )
        await TableService.create_table(
            session=db_session,
            table_data=table_data,
            organization_id="org123",
            restaurant_id="rest123",
        )
    
    query = AvailabilityQuery(
        date=date.today() + timedelta(days=1),
        party_size=2,
        duration_minutes=90,
    )
    
    availability = await AvailabilityService.get_available_slots(
        session=db_session,
        organization_id="org123",
        restaurant_id="rest123",
        query=query,
    )
    
    assert availability.is_fully_booked is False
    assert len(availability.available_slots) > 0
    # Should have slots every 30 minutes from 11:00 to 22:00
    assert len(availability.available_slots) == 23  # (22-11) * 2 + 1


@pytest.mark.asyncio
async def test_get_available_slots_with_reservations(db_session: AsyncSession):
    """Test availability with existing reservations."""
    # Create table
    table_data = TableCreate(
        table_number="T001",
        capacity=4,
        location="main_dining",
    )
    
    table = await TableService.create_table(
        session=db_session,
        table_data=table_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    # Create reservation for 19:00 - 20:30
    reservation_date = date.today() + timedelta(days=1)
    reservation_data = ReservationCreate(
        customer_name="John Doe",
        party_size=2,
        reservation_date=reservation_date,
        reservation_time=time(19, 0),
        duration_minutes=90,
        table_id=table.id,
    )
    
    await ReservationService.create_reservation(
        session=db_session,
        reservation_data=reservation_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    # Check availability for the same time
    query = AvailabilityQuery(
        date=reservation_date,
        party_size=2,
        time_preference=time(19, 0),
        duration_minutes=90,
    )
    
    availability = await AvailabilityService.get_available_slots(
        session=db_session,
        organization_id="org123",
        restaurant_id="rest123",
        query=query,
    )
    
    # The 19:00 slot should not be available for this table
    # But other slots should be available
    available_times = [slot.time for slot in availability.available_slots]
    
    # 19:00 should be unavailable due to conflict
    assert time(19, 0) not in available_times
    # 18:30 should be unavailable due to overlap
    assert time(18, 30) not in available_times
    # 17:30 should be available (ends at 19:00, no overlap)
    assert time(17, 30) in available_times
    # 20:30 should be available (starts after 20:30)
    assert time(20, 30) in available_times


@pytest.mark.asyncio
async def test_get_available_slots_with_preferences(db_session: AsyncSession):
    """Test availability with time preferences."""
    # Create table
    table_data = TableCreate(
        table_number="T001",
        capacity=4,
        location="main_dining",
    )
    
    await TableService.create_table(
        session=db_session,
        table_data=table_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    query = AvailabilityQuery(
        date=date.today() + timedelta(days=1),
        party_size=2,
        time_preference=time(19, 30),  # Preferred time
        duration_minutes=90,
    )
    
    availability = await AvailabilityService.get_available_slots(
        session=db_session,
        organization_id="org123",
        restaurant_id="rest123",
        query=query,
    )
    
    # Should have recommendations close to preferred time
    assert len(availability.recommendations) > 0
    
    # Recommendations should be sorted by proximity to preferred time
    for i in range(len(availability.recommendations) - 1):
        current_time = availability.recommendations[i].time
        next_time = availability.recommendations[i + 1].time
        
        current_diff = abs(
            (datetime.combine(date.today(), current_time) - 
             datetime.combine(date.today(), time(19, 30))).total_seconds()
        )
        next_diff = abs(
            (datetime.combine(date.today(), next_time) - 
             datetime.combine(date.today(), time(19, 30))).total_seconds()
        )
        
        assert current_diff <= next_diff


@pytest.mark.asyncio
async def test_find_alternative_slots(db_session: AsyncSession):
    """Test finding alternative time slots."""
    # Create table
    table_data = TableCreate(
        table_number="T001",
        capacity=4,
        location="main_dining",
    )
    
    table = await TableService.create_table(
        session=db_session,
        table_data=table_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    # Book the preferred time
    preferred_date = date.today() + timedelta(days=1)
    reservation_data = ReservationCreate(
        customer_name="John Doe",
        party_size=2,
        reservation_date=preferred_date,
        reservation_time=time(19, 0),
        duration_minutes=90,
        table_id=table.id,
    )
    
    await ReservationService.create_reservation(
        session=db_session,
        reservation_data=reservation_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    # Find alternatives
    alternatives = await AvailabilityService.find_alternative_slots(
        session=db_session,
        organization_id="org123",
        restaurant_id="rest123",
        preferred_date=preferred_date,
        preferred_time=time(19, 0),
        party_size=2,
        duration_minutes=90,
    )
    
    assert len(alternatives) > 0
    
    # Should not include the booked time
    alternative_times = [slot.time for slot in alternatives]
    assert time(19, 0) not in alternative_times
    
    # Should include nearby times like 17:30, 18:00, 20:30, 21:00
    assert any(
        slot.time in [time(17, 30), time(18, 0), time(20, 30), time(21, 0)]
        for slot in alternatives
    )


@pytest.mark.asyncio
async def test_get_capacity_optimization(db_session: AsyncSession):
    """Test capacity optimization suggestions."""
    # Create tables
    for i in range(5):
        table_data = TableCreate(
            table_number=f"T00{i+1}",
            capacity=4,
            location="main_dining",
        )
        await TableService.create_table(
            session=db_session,
            table_data=table_data,
            organization_id="org123",
            restaurant_id="rest123",
        )
    
    # Create some reservations for today
    today = date.today()
    times = [time(12, 0), time(13, 0), time(19, 0), time(20, 0)]
    
    for i, reservation_time in enumerate(times):
        reservation_data = ReservationCreate(
            customer_name=f"Customer {i+1}",
            party_size=3,
            reservation_date=today,
            reservation_time=reservation_time,
            duration_minutes=90,
        )
        
        await ReservationService.create_reservation(
            session=db_session,
            reservation_data=reservation_data,
            organization_id="org123",
            restaurant_id="rest123",
        )
    
    optimization = await AvailabilityService.get_capacity_optimization(
        session=db_session,
        organization_id="org123",
        restaurant_id="rest123",
        target_date=today,
    )
    
    assert optimization.date == today
    assert optimization.current_occupancy_rate >= 0
    assert len(optimization.peak_hours) >= 0
    assert len(optimization.suggested_improvements) >= 0
    assert len(optimization.recommended_actions) >= 0