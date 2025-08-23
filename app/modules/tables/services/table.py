from typing import List, Optional, Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, func, and_, or_
from fastapi import HTTPException, status
from app.modules.tables.models.table import (
    Table,
    TableCreate,
    TableUpdate,
    TableStatusUpdate,
)
from app.modules.tables.models.reservation import Reservation
from app.shared.cache import cached, cache_invalidate_pattern
from app.core.config import settings


class TableService:
    """Service for table management operations."""
    
    @staticmethod
    @cache_invalidate_pattern("tables:*")
    async def create_table(
        session: AsyncSession,
        table_data: TableCreate,
        organization_id: str,
        restaurant_id: str,
    ) -> Table:
        """Create a new table."""
        # Check if table number already exists in restaurant
        existing_table_stmt = select(Table).where(
            Table.organization_id == organization_id,
            Table.restaurant_id == restaurant_id,
            Table.table_number == table_data.table_number,
        )
        existing_result = await session.exec(existing_table_stmt)
        existing_table = existing_result.first()
        
        if existing_table:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Table number '{table_data.table_number}' already exists in this restaurant",
            )
        
        table = Table(
            **table_data.model_dump(),
            organization_id=organization_id,
            restaurant_id=restaurant_id,
        )
        
        session.add(table)
        await session.commit()
        await session.refresh(table)
        
        return table
    
    @staticmethod
    # @cached(ttl=settings.REDIS_TTL_TABLES, key_prefix="tables")  # Disabled due to serialization issues
    async def get_tables(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
        skip: int = 0,
        limit: int = 100,
        location: Optional[str] = None,
        status: Optional[str] = None,
        include_inactive: bool = False,
    ) -> List[Table]:
        """Get tables for a restaurant with optional filters."""
        statement = select(Table).where(
            Table.organization_id == organization_id,
            Table.restaurant_id == restaurant_id,
        )
        
        if location:
            statement = statement.where(Table.location == location)
        
        if status:
            statement = statement.where(Table.status == status)
        
        if not include_inactive:
            statement = statement.where(Table.is_active == True)
        
        statement = statement.order_by(Table.table_number)
        statement = statement.offset(skip).limit(limit)
        
        result = await session.exec(statement)
        return result.all()
    
    @staticmethod
    async def get_table_by_id(
        session: AsyncSession,
        table_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> Optional[Table]:
        """Get a table by ID."""
        statement = select(Table).where(
            Table.id == table_id,
            Table.organization_id == organization_id,
            Table.restaurant_id == restaurant_id,
        )
        
        result = await session.exec(statement)
        return result.first()
    
    @staticmethod
    @cache_invalidate_pattern("tables:*")
    async def update_table(
        session: AsyncSession,
        table_id: str,
        table_data: TableUpdate,
        organization_id: str,
        restaurant_id: str,
    ) -> Table:
        """Update a table."""
        table = await TableService.get_table_by_id(
            session, table_id, organization_id, restaurant_id
        )
        
        if not table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table not found",
            )
        
        # Check if updating table number to one that already exists
        update_data = table_data.model_dump(exclude_unset=True)
        if "table_number" in update_data and update_data["table_number"] != table.table_number:
            existing_table_stmt = select(Table).where(
                Table.organization_id == organization_id,
                Table.restaurant_id == restaurant_id,
                Table.table_number == update_data["table_number"],
                Table.id != table_id,
            )
            existing_result = await session.exec(existing_table_stmt)
            existing_table = existing_result.first()
            
            if existing_table:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Table number '{update_data['table_number']}' already exists in this restaurant",
                )
        
        # Update fields
        for field, value in update_data.items():
            setattr(table, field, value)
        
        session.add(table)
        await session.commit()
        await session.refresh(table)
        
        return table
    
    @staticmethod
    async def delete_table(
        session: AsyncSession,
        table_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> bool:
        """Delete a table."""
        table = await TableService.get_table_by_id(
            session, table_id, organization_id, restaurant_id
        )
        
        if not table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table not found",
            )
        
        # Check if table has active reservations
        active_reservations_stmt = select(func.count(Reservation.id)).where(
            Reservation.table_id == table_id,
            Reservation.status.in_(["confirmed", "seated"]),
        )
        reservations_result = await session.exec(active_reservations_stmt)
        reservation_count = reservations_result.one()
        
        if reservation_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete table with active reservations",
            )
        
        await session.delete(table)
        await session.commit()
        
        return True
    
    @staticmethod
    @cache_invalidate_pattern("tables:*")
    async def update_table_status(
        session: AsyncSession,
        table_id: str,
        status_data: TableStatusUpdate,
        organization_id: str,
        restaurant_id: str,
    ) -> Table:
        """Update table status."""
        table = await TableService.get_table_by_id(
            session, table_id, organization_id, restaurant_id
        )
        
        if not table:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Table not found",
            )
        
        # Validate status
        valid_statuses = ["available", "occupied", "reserved", "maintenance"]
        if status_data.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
            )
        
        table.status = status_data.status
        session.add(table)
        await session.commit()
        await session.refresh(table)
        
        return table
    
    @staticmethod
    async def get_table_with_details(
        session: AsyncSession,
        table_id: str,
        organization_id: str,
        restaurant_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get table with reservation details."""
        table = await TableService.get_table_by_id(
            session, table_id, organization_id, restaurant_id
        )
        
        if not table:
            return None
        
        # Get reservation counts
        active_reservations_stmt = select(func.count(Reservation.id)).where(
            Reservation.table_id == table_id,
            Reservation.status.in_(["confirmed", "seated"]),
        )
        upcoming_reservations_stmt = select(func.count(Reservation.id)).where(
            Reservation.table_id == table_id,
            Reservation.status == "confirmed",
            Reservation.reservation_date >= func.current_date(),
        )
        
        active_result = await session.exec(active_reservations_stmt)
        upcoming_result = await session.exec(upcoming_reservations_stmt)
        
        active_count = active_result.one()
        upcoming_count = upcoming_result.one()
        
        return {
            "id": str(table.id),
            "table_number": table.table_number,
            "capacity": table.capacity,
            "location": table.location,
            "status": table.status,
            "coordinates": table.coordinates,
            "is_active": table.is_active,
            "organization_id": str(table.organization_id),
            "restaurant_id": str(table.restaurant_id),
            "created_at": table.created_at.isoformat(),
            "updated_at": table.updated_at.isoformat(),
            "active_reservations": active_count,
            "upcoming_reservations": upcoming_count,
        }
    
    @staticmethod
    async def get_restaurant_layout(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
    ) -> Dict[str, Any]:
        """Get restaurant floor plan layout."""
        tables = await TableService.get_tables(
            session=session,
            organization_id=organization_id,
            restaurant_id=restaurant_id,
            include_inactive=False,
        )
        
        # Convert to layout format
        table_data = []
        for table in tables:
            table_info = await TableService.get_table_with_details(
                session=session,
                table_id=str(table.id),
                organization_id=organization_id,
                restaurant_id=restaurant_id,
            )
            if table_info:
                table_data.append(table_info)
        
        return {
            "tables": table_data,
            "layout_settings": {
                "total_tables": len(table_data),
                "total_capacity": sum(t["capacity"] for t in table_data),
                "locations": list(set(t["location"] for t in table_data if t["location"])),
            }
        }
    
    @staticmethod
    async def get_availability_overview(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
    ) -> Dict[str, Any]:
        """Get real-time table availability overview."""
        # Get all active tables
        tables_stmt = select(Table).where(
            Table.organization_id == organization_id,
            Table.restaurant_id == restaurant_id,
            Table.is_active == True,
        )
        tables_result = await session.exec(tables_stmt)
        tables = tables_result.all()
        
        # Count by status
        status_counts = {}
        total_capacity = 0
        
        for table in tables:
            status_counts[table.status] = status_counts.get(table.status, 0) + 1
            total_capacity += table.capacity
        
        # Get current reservations
        current_reservations_stmt = select(func.count(Reservation.id)).where(
            Reservation.restaurant_id == restaurant_id,
            Reservation.reservation_date == func.current_date(),
            Reservation.status.in_(["confirmed", "seated"]),
        )
        current_reservations_result = await session.exec(current_reservations_stmt)
        current_reservations = current_reservations_result.one()
        
        return {
            "total_tables": len(tables),
            "total_capacity": total_capacity,
            "status_breakdown": status_counts,
            "current_reservations": current_reservations,
            "available_tables": status_counts.get("available", 0),
            "occupied_tables": status_counts.get("occupied", 0),
            "reserved_tables": status_counts.get("reserved", 0),
            "maintenance_tables": status_counts.get("maintenance", 0),
        }
    
    @staticmethod
    async def get_table_analytics(
        session: AsyncSession,
        organization_id: str,
        restaurant_id: str,
        days_back: int = 30,
    ) -> Dict[str, Any]:
        """Get table utilization analytics."""
        # This would be expanded with more complex analytics
        # For now, basic utilization data
        
        total_tables_stmt = select(func.count(Table.id)).where(
            Table.organization_id == organization_id,
            Table.restaurant_id == restaurant_id,
            Table.is_active == True,
        )
        total_tables_result = await session.exec(total_tables_stmt)
        total_tables = total_tables_result.one()
        
        # Recent reservations
        recent_reservations_stmt = select(func.count(Reservation.id)).where(
            Reservation.restaurant_id == restaurant_id,
            Reservation.reservation_date >= func.current_date() - days_back,
            Reservation.status == "completed",
        )
        recent_reservations_result = await session.exec(recent_reservations_stmt)
        recent_reservations = recent_reservations_result.one()
        
        # Calculate basic utilization
        utilization_rate = (recent_reservations / (total_tables * days_back)) * 100 if total_tables > 0 else 0
        
        return {
            "total_tables": total_tables,
            "recent_reservations": recent_reservations,
            "utilization_rate": round(utilization_rate, 2),
            "analysis_period_days": days_back,
            "recommendations": [
                "Consider adjusting table arrangements for peak hours" if utilization_rate > 80 else
                "Table utilization is optimal" if utilization_rate > 60 else
                "Consider marketing to increase table utilization"
            ]
        }