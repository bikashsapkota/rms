import pytest
from datetime import date, time
from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.tables.models.table import Table, TableCreate, TableUpdate
from app.modules.tables.services.table import TableService


@pytest.mark.asyncio
async def test_create_table(db_session: AsyncSession):
    """Test creating a new table."""
    table_data = TableCreate(
        table_number="T001",
        capacity=4,
        location="main_dining",
        coordinates={"x": 100, "y": 200},
    )
    
    table = await TableService.create_table(
        session=db_session,
        table_data=table_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert table.table_number == "T001"
    assert table.capacity == 4
    assert table.location == "main_dining"
    assert table.status == "available"
    assert table.is_active is True
    assert table.coordinates == {"x": 100, "y": 200}


@pytest.mark.asyncio
async def test_create_table_duplicate_number(db_session: AsyncSession):
    """Test creating a table with duplicate number fails."""
    table_data = TableCreate(
        table_number="T001",
        capacity=4,
        location="main_dining",
    )
    
    # Create first table
    await TableService.create_table(
        session=db_session,
        table_data=table_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    # Try to create duplicate
    with pytest.raises(Exception):  # Should raise HTTPException
        await TableService.create_table(
            session=db_session,
            table_data=table_data,
            organization_id="org123",
            restaurant_id="rest123",
        )


@pytest.mark.asyncio
async def test_get_tables(db_session: AsyncSession):
    """Test getting tables for a restaurant."""
    # Create test tables
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
    
    tables = await TableService.get_tables(
        session=db_session,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert len(tables) == 3
    assert all(table.restaurant_id == "rest123" for table in tables)


@pytest.mark.asyncio
async def test_update_table(db_session: AsyncSession):
    """Test updating a table."""
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
    
    # Update table
    update_data = TableUpdate(
        capacity=6,
        location="patio",
        status="maintenance",
    )
    
    updated_table = await TableService.update_table(
        session=db_session,
        table_id=str(table.id),
        table_data=update_data,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert updated_table.capacity == 6
    assert updated_table.location == "patio"
    assert updated_table.status == "maintenance"
    assert updated_table.table_number == "T001"  # Unchanged


@pytest.mark.asyncio
async def test_get_table_with_details(db_session: AsyncSession):
    """Test getting table with reservation details."""
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
    
    # Get table details
    table_details = await TableService.get_table_with_details(
        session=db_session,
        table_id=str(table.id),
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert table_details is not None
    assert table_details["table_number"] == "T001"
    assert table_details["capacity"] == 4
    assert "active_reservations" in table_details
    assert "upcoming_reservations" in table_details


@pytest.mark.asyncio
async def test_get_availability_overview(db_session: AsyncSession):
    """Test getting availability overview."""
    # Create tables with different statuses
    statuses = ["available", "occupied", "reserved", "maintenance"]
    
    for i, status in enumerate(statuses):
        table_data = TableCreate(
            table_number=f"T00{i+1}",
            capacity=4,
            status=status,
        )
        await TableService.create_table(
            session=db_session,
            table_data=table_data,
            organization_id="org123",
            restaurant_id="rest123",
        )
    
    overview = await TableService.get_availability_overview(
        session=db_session,
        organization_id="org123",
        restaurant_id="rest123",
    )
    
    assert overview["total_tables"] == 4
    assert overview["total_capacity"] == 16
    assert overview["status_breakdown"]["available"] == 1
    assert overview["status_breakdown"]["occupied"] == 1
    assert overview["status_breakdown"]["reserved"] == 1
    assert overview["status_breakdown"]["maintenance"] == 1