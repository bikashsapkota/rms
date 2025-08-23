"""
Kitchen operations service for managing order preparation.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlmodel import select, and_, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.orders.models.order import Order, OrderStatus
from app.modules.orders.models.order_item import OrderItem, OrderItemKitchenView
from app.shared.cache.service import cache_service


class KitchenService:
    """Service for kitchen operations and order preparation tracking."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_kitchen_orders(self, restaurant_id: UUID) -> List[Order]:
        """Get all orders for kitchen display."""
        
        cache_key = f"kitchen_orders:{restaurant_id}"
        cached_orders = await cache_service.get(cache_key)
        if cached_orders:
            return cached_orders
        
        # Get orders that need kitchen attention
        stmt = select(Order).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.status.in_([
                    OrderStatus.CONFIRMED,
                    OrderStatus.PREPARING,
                    OrderStatus.READY
                ])
            )
        ).order_by(Order.created_at.asc())
        
        result = await self.session.exec(stmt)
        orders = result.all()
        
        # Cache for 30 seconds
        await cache_service.set(cache_key, orders, ttl=30)
        
        return orders
    
    async def start_order_preparation(
        self,
        order_id: str,
        restaurant_id: UUID,
        estimated_prep_time: Optional[int] = None
    ) -> Order:
        """Start preparing an order."""
        
        # Get order
        stmt = select(Order).where(
            and_(
                Order.id == order_id,
                Order.restaurant_id == restaurant_id
            )
        )
        result = await self.session.exec(stmt)
        order = result.first()
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        if order.status != OrderStatus.CONFIRMED:
            raise ValueError(f"Order {order_id} is not confirmed and cannot be started")
        
        # Update order status and timing
        order.status = OrderStatus.PREPARING
        
        if estimated_prep_time:
            order.prep_time_minutes = estimated_prep_time
            order.estimated_ready_time = datetime.utcnow() + timedelta(minutes=estimated_prep_time)
        
        await self.session.commit()
        await self.session.refresh(order)
        
        # Clear cache
        await self._clear_kitchen_cache(restaurant_id)
        
        return order
    
    async def complete_order_preparation(
        self,
        order_id: str,
        restaurant_id: UUID,
        kitchen_notes: Optional[str] = None
    ) -> Order:
        """Mark order as ready."""
        
        # Get order
        stmt = select(Order).where(
            and_(
                Order.id == order_id,
                Order.restaurant_id == restaurant_id
            )
        )
        result = await self.session.exec(stmt)
        order = result.first()
        
        if not order:
            raise ValueError(f"Order {order_id} not found")
        
        if order.status != OrderStatus.PREPARING:
            raise ValueError(f"Order {order_id} is not being prepared")
        
        # Update order
        order.status = OrderStatus.READY
        order.actual_ready_time = datetime.utcnow()
        
        if kitchen_notes:
            order.kitchen_notes = kitchen_notes
        
        await self.session.commit()
        await self.session.refresh(order)
        
        # Clear cache
        await self._clear_kitchen_cache(restaurant_id)
        
        return order
    
    async def update_order_item_preparation(
        self,
        order_item_id: str,
        restaurant_id: UUID,
        prep_start_time: Optional[datetime] = None,
        prep_complete_time: Optional[datetime] = None,
        kitchen_notes: Optional[str] = None
    ) -> OrderItem:
        """Update preparation status of individual order item."""
        
        # Get order item
        stmt = select(OrderItem).where(
            and_(
                OrderItem.id == order_item_id,
                OrderItem.restaurant_id == restaurant_id
            )
        )
        result = await self.session.exec(stmt)
        order_item = result.first()
        
        if not order_item:
            raise ValueError(f"Order item {order_item_id} not found")
        
        # Update preparation times
        if prep_start_time:
            order_item.prep_start_time = prep_start_time.isoformat()
        if prep_complete_time:
            order_item.prep_complete_time = prep_complete_time.isoformat()
        if kitchen_notes:
            order_item.kitchen_notes = kitchen_notes
        
        await self.session.commit()
        await self.session.refresh(order_item)
        
        # Clear cache
        await self._clear_kitchen_cache(restaurant_id)
        
        return order_item
    
    async def get_kitchen_performance_metrics(
        self,
        restaurant_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get kitchen performance metrics."""
        
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=7)
        if not date_to:
            date_to = datetime.utcnow()
        
        # Average preparation time
        stmt = select(
            func.avg(
                func.extract('epoch', Order.actual_ready_time) - 
                func.extract('epoch', Order.created_at)
            ) / 60  # Convert to minutes
        ).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.status == OrderStatus.DELIVERED,
                Order.actual_ready_time.isnot(None),
                Order.created_at >= date_from,
                Order.created_at <= date_to
            )
        )
        result = await self.session.exec(stmt)
        avg_prep_time = result.first()
        
        # Orders completed on time (within estimated time)
        stmt = select(
            func.count().filter(
                Order.actual_ready_time <= Order.estimated_ready_time
            ),
            func.count(Order.id)
        ).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.status == OrderStatus.DELIVERED,
                Order.actual_ready_time.isnot(None),
                Order.estimated_ready_time.isnot(None),
                Order.created_at >= date_from,
                Order.created_at <= date_to
            )
        )
        result = await self.session.exec(stmt)
        on_time_data = result.first()
        on_time_orders = on_time_data[0] if on_time_data else 0
        total_timed_orders = on_time_data[1] if on_time_data else 0
        
        on_time_percentage = (
            (on_time_orders / total_timed_orders * 100) 
            if total_timed_orders > 0 else 0
        )
        
        # Peak hours analysis
        stmt = select(
            func.extract('hour', Order.created_at).label('hour'),
            func.count(Order.id).label('order_count')
        ).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.created_at >= date_from,
                Order.created_at <= date_to
            )
        ).group_by(
            func.extract('hour', Order.created_at)
        ).order_by(
            func.count(Order.id).desc()
        ).limit(3)
        
        result = await self.session.exec(stmt)
        peak_hours = [
            {"hour": int(hour), "order_count": count}
            for hour, count in result.all()
        ]
        
        return {
            "average_prep_time_minutes": round(avg_prep_time or 0, 2),
            "on_time_percentage": round(on_time_percentage, 2),
            "on_time_orders": on_time_orders,
            "total_timed_orders": total_timed_orders,
            "peak_hours": peak_hours,
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            }
        }
    
    async def get_current_prep_queue(self, restaurant_id: UUID) -> List[Dict[str, Any]]:
        """Get current preparation queue with timing estimates."""
        
        # Get orders being prepared
        stmt = select(Order).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.PREPARING])
            )
        ).order_by(Order.created_at.asc())
        
        result = await self.session.exec(stmt)
        orders = result.all()
        
        queue = []
        current_time = datetime.utcnow()
        
        for order in orders:
            # Calculate time in queue
            time_in_queue = (current_time - order.created_at).total_seconds() / 60
            
            # Estimate remaining time
            if order.status == OrderStatus.PREPARING and order.estimated_ready_time:
                remaining_time = max(0, (order.estimated_ready_time - current_time).total_seconds() / 60)
            else:
                # Default estimate if no prep time set
                remaining_time = order.prep_time_minutes or 15
            
            queue.append({
                "order_id": order.id,
                "order_number": order.order_number,
                "status": order.status,
                "customer_name": order.customer_name,
                "order_type": order.order_type,
                "item_count": len(order.order_items) if order.order_items else 0,
                "time_in_queue_minutes": round(time_in_queue, 1),
                "estimated_remaining_minutes": round(remaining_time, 1),
                "priority": self._calculate_order_priority(order, time_in_queue)
            })
        
        # Sort by priority (high to low)
        queue.sort(key=lambda x: x["priority"], reverse=True)
        
        return queue
    
    def _calculate_order_priority(self, order: Order, time_in_queue: float) -> int:
        """Calculate order priority for kitchen queue."""
        priority = 0
        
        # Base priority by order type
        if order.order_type == "delivery":
            priority += 3
        elif order.order_type == "takeout":
            priority += 2
        else:  # dine_in
            priority += 1
        
        # Time-based priority (longer wait = higher priority)
        if time_in_queue > 30:
            priority += 3
        elif time_in_queue > 15:
            priority += 2
        elif time_in_queue > 5:
            priority += 1
        
        # Special requests priority
        if order.special_instructions:
            priority += 1
        
        return priority
    
    async def _clear_kitchen_cache(self, restaurant_id: UUID):
        """Clear kitchen-related cache."""
        patterns = [
            f"kitchen_orders:{restaurant_id}",
            f"kitchen_performance:{restaurant_id}",
            f"prep_queue:{restaurant_id}"
        ]
        
        for pattern in patterns:
            await cache_service.clear_pattern(pattern)