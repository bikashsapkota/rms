import pytest
from datetime import date, time, datetime, timedelta
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.tables.models.table import Table, TableCreate
from app.modules.tables.models.reservation import Reservation, ReservationCreate, ReservationUpdate
from app.modules.tables.services.table import TableService
from app.modules.tables.services.reservation import ReservationService


@pytest.mark.asyncio
async def test_create_reservation(db_session: AsyncSession):
    """Test creating a new reservation."""
    # Create a table first
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
    
    # Create reservation
    reservation_data = ReservationCreate(
        customer_name="John Doe",
        customer_phone="+1234567890",
        customer_email="john@example.com",
        party_size=2,
        reservation_date=date.today() + timedelta(days=1),
        reservation_time=time(19, 0),
        duration_minutes=90,
        table_id=table.id,
        special_requests="Window table preferred",
    )
    
    reservation = await ReservationService.create_reservation(
        session=db_session,
        reservation_data=reservation_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert reservation.customer_name == "John Doe"
    assert reservation.customer_phone == "+1234567890"
    assert reservation.party_size == 2
    assert reservation.status == "confirmed"
    assert reservation.table_id == table.id
    assert reservation.special_requests == "Window table preferred"


@pytest.mark.asyncio
async def test_create_reservation_without_table(db_session: AsyncSession):
    """Test creating a reservation without assigning a table."""
    reservation_data = ReservationCreate(
        customer_name="Jane Doe",
        customer_phone="+1234567891",
        party_size=4,
        reservation_date=date.today() + timedelta(days=1),
        reservation_time=time(20, 0),
        duration_minutes=120,
    )
    
    reservation = await ReservationService.create_reservation(
        session=db_session,
        reservation_data=reservation_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert reservation.customer_name == "Jane Doe"
    assert reservation.party_size == 4
    assert reservation.table_id is None
    assert reservation.status == "confirmed"


@pytest.mark.asyncio
async def test_create_reservation_capacity_validation(db_session: AsyncSession):
    """Test reservation creation validates table capacity."""
    # Create a small table
    table_data = TableCreate(
        table_number="T001",
        capacity=2,
        location="main_dining",
    )
    
    table = await TableService.create_table(
        session=db_session,
        table_data=table_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    # Try to create reservation with party larger than capacity
    reservation_data = ReservationCreate(
        customer_name="Large Party",
        party_size=6,  # Exceeds table capacity of 2
        reservation_date=date.today() + timedelta(days=1),
        reservation_time=time(19, 0),
        table_id=table.id,
    )
    
    with pytest.raises(Exception):  # Should raise HTTPException
        await ReservationService.create_reservation(
            session=db_session,
            reservation_data=reservation_data,
            organization_id="org123",
            restaurant_id="rest123",
        )


@pytest.mark.asyncio
async def test_update_reservation(db_session: AsyncSession):
    """Test updating a reservation."""
    # Create reservation
    reservation_data = ReservationCreate(
        customer_name="John Doe",
        customer_phone="+1234567890",
        party_size=2,
        reservation_date=date.today() + timedelta(days=1),
        reservation_time=time(19, 0),
    )
    
    reservation = await ReservationService.create_reservation(
        session=db_session,
        reservation_data=reservation_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    # Update reservation
    update_data = ReservationUpdate(
        party_size=4,
        reservation_time=time(20, 0),
        special_requests="Birthday celebration",
    )
    
    updated_reservation = await ReservationService.update_reservation(
        session=db_session,
        reservation_id=str(reservation.id),
        reservation_data=update_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert updated_reservation.party_size == 4
    assert updated_reservation.reservation_time == time(20, 0)
    assert updated_reservation.special_requests == "Birthday celebration"
    assert updated_reservation.customer_name == "John Doe"  # Unchanged


@pytest.mark.asyncio
async def test_cancel_reservation(db_session: AsyncSession):
    """Test cancelling a reservation."""
    # Create reservation
    reservation_data = ReservationCreate(
        customer_name="John Doe",
        customer_phone="+1234567890",
        party_size=2,
        reservation_date=date.today() + timedelta(days=1),
        reservation_time=time(19, 0),
    )
    
    reservation = await ReservationService.create_reservation(
        session=db_session,
        reservation_data=reservation_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    # Cancel reservation
    cancelled_reservation = await ReservationService.cancel_reservation(
        session=db_session,
        reservation_id=str(reservation.id),
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert cancelled_reservation.status == "cancelled"


@pytest.mark.asyncio
async def test_get_today_reservations(db_session: AsyncSession):
    """Test getting today's reservations."""
    today = date.today()
    tomorrow = today + timedelta(days=1)
    
    # Create reservations for today and tomorrow
    for i, reservation_date in enumerate([today, tomorrow]):
        reservation_data = ReservationCreate(
            customer_name=f"Customer {i+1}",
            customer_phone=f"+123456789{i}",
            party_size=2,
            reservation_date=reservation_date,
            reservation_time=time(19, 0),
        )
        
        await ReservationService.create_reservation(
            session=db_session,
            reservation_data=reservation_data,
            organization_id="org123",
            restaurant_id="rest123",
        )
    
    # Get today's reservations
    today_reservations = await ReservationService.get_today_reservations(
        session=db_session,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert len(today_reservations) == 1
    assert today_reservations[0]["customer_name"] == "Customer 1"
    assert today_reservations[0]["reservation_date"] == today.isoformat()


@pytest.mark.asyncio
async def test_get_reservation_analytics(db_session: AsyncSession):
    """Test getting reservation analytics."""
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Create reservations with different statuses
    statuses = ["confirmed", "completed", "no_show", "cancelled"]
    
    for i, status in enumerate(statuses):
        reservation_data = ReservationCreate(
            customer_name=f"Customer {i+1}",
            customer_phone=f"+123456789{i}",
            party_size=2 + i,  # Different party sizes
            reservation_date=yesterday,
            reservation_time=time(19 + i, 0),  # Different times
        )
        
        reservation = await ReservationService.create_reservation(
            session=db_session,
            reservation_data=reservation_data,
            organization_id="org123",
            restaurant_id="rest123",
        )
        
        # Update status
        if status != "confirmed":
            reservation.status = status
            db_session.add(reservation)
    
    await db_session.commit()
    
    # Get analytics
    analytics = await ReservationService.get_reservation_analytics(
        session=db_session,
        organization_id="org123",
        restaurant_id="rest123",
        start_date=yesterday,
        end_date=today,
    )
    
    assert analytics["total_reservations"] == 4
    assert analytics["status_breakdown"]["confirmed"] == 1
    assert analytics["status_breakdown"]["completed"] == 1
    assert analytics["status_breakdown"]["no_show"] == 1
    assert analytics["status_breakdown"]["cancelled"] == 1
    assert analytics["average_party_size"] == 3.5  # (2+3+4+5)/4
    assert analytics["completion_rate"] == 25.0  # 1/4 * 100