import pytest
from datetime import date, time, datetime, timedelta
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.tables.models.waitlist import ReservationWaitlist, WaitlistCreate, WaitlistUpdate
from app.modules.tables.services.waitlist import WaitlistService


@pytest.mark.asyncio
async def test_add_to_waitlist(db_session: AsyncSession):
    """Test adding a customer to the waitlist."""
    waitlist_data = WaitlistCreate(
        customer_name="John Doe",
        customer_phone="+1234567890",
        customer_email="john@example.com",
        party_size=4,
        preferred_date=date.today() + timedelta(days=1),
        preferred_time=time(19, 0),
        notes="Anniversary dinner",
    )
    
    waitlist_entry = await WaitlistService.add_to_waitlist(
        session=db_session,
        waitlist_data=waitlist_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert waitlist_entry.customer_name == "John Doe"
    assert waitlist_entry.customer_phone == "+1234567890"
    assert waitlist_entry.party_size == 4
    assert waitlist_entry.status == "active"
    assert waitlist_entry.priority_score > 0
    assert waitlist_entry.notes == "Anniversary dinner"


@pytest.mark.asyncio
async def test_waitlist_priority_calculation(db_session: AsyncSession):
    """Test priority score calculation for waitlist entries."""
    today = date.today()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    
    # Entry for tomorrow, large party, peak time
    high_priority_data = WaitlistCreate(
        customer_name="High Priority",
        party_size=8,  # Large party
        preferred_date=tomorrow,  # Soon
        preferred_time=time(19, 0),  # Peak dinner hour
    )
    
    # Entry for next week, small party, off-peak time
    low_priority_data = WaitlistCreate(
        customer_name="Low Priority",
        party_size=2,  # Small party
        preferred_date=next_week,  # Later
        preferred_time=time(15, 0),  # Off-peak hour
    )
    
    high_priority_entry = await WaitlistService.add_to_waitlist(
        session=db_session,
        waitlist_data=high_priority_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    low_priority_entry = await WaitlistService.add_to_waitlist(
        session=db_session,
        waitlist_data=low_priority_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert high_priority_entry.priority_score > low_priority_entry.priority_score


@pytest.mark.asyncio
async def test_get_waitlist_ordered_by_priority(db_session: AsyncSession):
    """Test getting waitlist entries ordered by priority."""
    # Create entries with different priorities
    entries_data = [
        ("Medium Priority", 4, date.today() + timedelta(days=3), time(18, 0)),
        ("High Priority", 6, date.today() + timedelta(days=1), time(19, 0)),
        ("Low Priority", 2, date.today() + timedelta(days=7), time(15, 0)),
    ]
    
    for name, party_size, preferred_date, preferred_time in entries_data:
        waitlist_data = WaitlistCreate(
            customer_name=name,
            party_size=party_size,
            preferred_date=preferred_date,
            preferred_time=preferred_time,
        )
        
        await WaitlistService.add_to_waitlist(
            session=db_session,
            waitlist_data=waitlist_data,
            organization_id="org123",
            restaurant_id="rest123",
        )
    
    # Get waitlist entries
    waitlist_entries = await WaitlistService.get_waitlist(
        session=db_session,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert len(waitlist_entries) == 3
    
    # Should be ordered by priority score (highest first)
    assert waitlist_entries[0].customer_name == "High Priority"
    assert waitlist_entries[1].customer_name == "Medium Priority"
    assert waitlist_entries[2].customer_name == "Low Priority"
    
    # Priority scores should be in descending order
    for i in range(len(waitlist_entries) - 1):
        assert waitlist_entries[i].priority_score >= waitlist_entries[i + 1].priority_score


@pytest.mark.asyncio
async def test_update_waitlist_entry(db_session: AsyncSession):
    """Test updating a waitlist entry."""
    # Create waitlist entry
    waitlist_data = WaitlistCreate(
        customer_name="John Doe",
        customer_phone="+1234567890",
        party_size=4,
        preferred_date=date.today() + timedelta(days=7),
        preferred_time=time(15, 0),
    )
    
    waitlist_entry = await WaitlistService.add_to_waitlist(
        session=db_session,
        waitlist_data=waitlist_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    original_priority = waitlist_entry.priority_score
    
    # Update with higher priority preferences
    update_data = WaitlistUpdate(
        party_size=6,  # Larger party
        preferred_date=date.today() + timedelta(days=1),  # Sooner date
        preferred_time=time(19, 0),  # Peak time
        notes="Updated preferences for birthday celebration",
    )
    
    updated_entry = await WaitlistService.update_waitlist_entry(
        session=db_session,
        waitlist_id=str(waitlist_entry.id),
        waitlist_data=update_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert updated_entry.party_size == 6
    assert updated_entry.preferred_date == date.today() + timedelta(days=1)
    assert updated_entry.preferred_time == time(19, 0)
    assert updated_entry.notes == "Updated preferences for birthday celebration"
    # Priority should be recalculated and higher
    assert updated_entry.priority_score > original_priority


@pytest.mark.asyncio
async def test_notify_customer(db_session: AsyncSession):
    """Test notifying a customer from the waitlist."""
    # Create waitlist entry
    waitlist_data = WaitlistCreate(
        customer_name="John Doe",
        customer_phone="+1234567890",
        party_size=4,
    )
    
    waitlist_entry = await WaitlistService.add_to_waitlist(
        session=db_session,
        waitlist_data=waitlist_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert waitlist_entry.status == "active"
    
    # Notify customer
    from app.modules.tables.models.waitlist import WaitlistNotify
    notify_data = WaitlistNotify(
        message="Table available for your party",
        available_time=time(19, 30),
    )
    
    notified_entry = await WaitlistService.notify_customer(
        session=db_session,
        waitlist_id=str(waitlist_entry.id),
        notify_data=notify_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert notified_entry.status == "notified"
    assert "Notified on" in notified_entry.notes
    assert "Available time: 19:30:00" in notified_entry.notes
    assert "Message: Table available for your party" in notified_entry.notes


@pytest.mark.asyncio
async def test_mark_as_seated(db_session: AsyncSession):
    """Test marking a waitlist customer as seated."""
    # Create waitlist entry
    waitlist_data = WaitlistCreate(
        customer_name="John Doe",
        party_size=4,
    )
    
    waitlist_entry = await WaitlistService.add_to_waitlist(
        session=db_session,
        waitlist_data=waitlist_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    # Mark as seated
    seated_entry = await WaitlistService.mark_as_seated(
        session=db_session,
        waitlist_id=str(waitlist_entry.id),
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert seated_entry.status == "seated"


@pytest.mark.asyncio
async def test_remove_from_waitlist(db_session: AsyncSession):
    """Test removing a customer from the waitlist."""
    # Create waitlist entry
    waitlist_data = WaitlistCreate(
        customer_name="John Doe",
        party_size=4,
    )
    
    waitlist_entry = await WaitlistService.add_to_waitlist(
        session=db_session,
        waitlist_data=waitlist_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    # Remove from waitlist
    result = await WaitlistService.remove_from_waitlist(
        session=db_session,
        waitlist_id=str(waitlist_entry.id),
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert result is True
    
    # Verify entry is removed
    removed_entry = await WaitlistService.get_waitlist_entry_by_id(
        session=db_session,
        waitlist_id=str(waitlist_entry.id),
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert removed_entry is None


@pytest.mark.asyncio
async def test_get_waitlist_analytics(db_session: AsyncSession):
    """Test getting waitlist analytics."""
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Create waitlist entries with different statuses
    statuses = ["active", "notified", "seated", "cancelled"]
    
    for i, status in enumerate(statuses):
        waitlist_data = WaitlistCreate(
            customer_name=f"Customer {i+1}",
            party_size=2 + i,
        )
        
        waitlist_entry = await WaitlistService.add_to_waitlist(
            session=db_session,
            waitlist_data=waitlist_data,
            organization_id="org123",
            restaurant_id="rest123",
        )
        
        # Update status
        if status != "active":
            waitlist_entry.status = status
            db_session.add(waitlist_entry)
    
    await db_session.commit()
    
    # Get analytics
    analytics = await WaitlistService.get_waitlist_analytics(
        session=db_session,
        organization_id="org123",
        restaurant_id="rest123",
        start_date=yesterday,
        end_date=today,
    )
    
    assert analytics["total_waitlist_entries"] == 4
    assert analytics["status_breakdown"]["active"] == 1
    assert analytics["status_breakdown"]["notified"] == 1
    assert analytics["status_breakdown"]["seated"] == 1
    assert analytics["status_breakdown"]["cancelled"] == 1
    assert analytics["seated_customers"] == 1
    assert analytics["conversion_rate"] == 25.0  # 1/4 * 100
    assert analytics["average_party_size"] == 3.5  # (2+3+4+5)/4