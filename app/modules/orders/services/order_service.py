"""
Order management service for handling order operations.
"""

import uuid
from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timedelta
from sqlmodel import select, and_, or_, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.orders.models.order import Order, OrderStatus, OrderType, OrderCreate, OrderUpdate
from app.modules.orders.models.order_item import OrderItem, OrderItemModifier, OrderItemCreate, OrderItemModifierCreate
from app.modules.orders.models.payment import Payment, PaymentStatus
from app.modules.menu.models.item import MenuItem
from app.modules.menu.models.modifier import Modifier
from app.modules.tables.models.table import Table
from app.shared.cache.service import cache_service


class OrderService:
    """Service for order management operations."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        
    async def create_order(
        self,
        order_data: Dict[str, Any],
        items_data: List[OrderItemCreate],
        restaurant_id: UUID,
        organization_id: UUID,
    ) -> Order:
        """Create a new order with items."""
        
        # Generate unique order number
        order_number = await self._generate_order_number(restaurant_id)
        
        # Calculate pricing
        subtotal, items_with_pricing = await self._calculate_order_pricing(items_data, restaurant_id)
        
        # Calculate tax (assuming 8.5% tax rate - should be configurable)
        tax_rate = Decimal("0.085")
        tax_amount = subtotal * tax_rate
        
        # Total amount (before tip)
        total_amount = subtotal + tax_amount
        
        # Create order
        order = Order(
            order_number=order_number,
            organization_id=organization_id,
            restaurant_id=restaurant_id,
            subtotal=subtotal,
            tax_amount=tax_amount,
            total_amount=total_amount,
            **order_data
        )
        
        self.session.add(order)
        await self.session.commit()
        await self.session.refresh(order)
        
        # Create order items
        for item_data, pricing_info in zip(items_data, items_with_pricing):
            order_item = await self._create_order_item(
                order.id, item_data, pricing_info, organization_id, restaurant_id
            )
            
        await self.session.commit()
        
        # Clear related cache
        await self._clear_order_cache(restaurant_id)
        
        return order
    
    async def get_order(self, order_id: str, restaurant_id: UUID) -> Optional[Order]:
        """Get order by ID."""
        cache_key = f"order:{restaurant_id}:{order_id}"
        
        # Try cache first
        cached_order = await cache_service.get(cache_key)
        if cached_order:
            return cached_order
            
        # Query database
        stmt = select(Order).where(
            and_(
                Order.id == order_id,
                Order.restaurant_id == restaurant_id
            )
        )
        result = await self.session.exec(stmt)
        order = result.first()
        
        if order:
            await cache_service.set(cache_key, order, ttl=300)  # 5 minutes
            
        return order
    
    async def list_orders(
        self,
        restaurant_id: UUID,
        filters: Dict[str, Any] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Order]:
        """List orders with filters."""
        
        stmt = select(Order).where(Order.restaurant_id == restaurant_id)
        
        # Apply filters
        if filters:
            if filters.get('status'):
                stmt = stmt.where(Order.status.in_(filters['status']))
            if filters.get('order_type'):
                stmt = stmt.where(Order.order_type.in_(filters['order_type']))
            if filters.get('customer_name'):
                stmt = stmt.where(Order.customer_name.ilike(f"%{filters['customer_name']}%"))
            if filters.get('table_id'):
                stmt = stmt.where(Order.table_id == filters['table_id'])
            if filters.get('date_from'):
                stmt = stmt.where(Order.created_at >= filters['date_from'])
            if filters.get('date_to'):
                stmt = stmt.where(Order.created_at <= filters['date_to'])
        
        # Order by created_at desc
        stmt = stmt.order_by(Order.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.session.exec(stmt)
        return result.all()
    
    async def update_order_status(
        self,
        order_id: str,
        new_status: OrderStatus,
        restaurant_id: UUID,
        kitchen_notes: Optional[str] = None,
        estimated_ready_time: Optional[datetime] = None,
    ) -> Order:
        """Update order status."""
        
        # Always query fresh from database for updates to avoid detached instances
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
        
        # Update status and timing
        order.status = new_status
        if kitchen_notes:
            order.kitchen_notes = kitchen_notes
        if estimated_ready_time:
            order.estimated_ready_time = estimated_ready_time
            
        # Set actual ready time when order is ready
        if new_status == OrderStatus.READY and not order.actual_ready_time:
            order.actual_ready_time = datetime.utcnow()
            
        self.session.add(order)  # Ensure order is in session
        await self.session.commit()
        await self.session.refresh(order)
        
        # Clear cache
        await self._clear_order_cache(restaurant_id, order_id)
        
        return order
    
    async def get_kitchen_orders(self, restaurant_id: UUID) -> List[Order]:
        """Get orders for kitchen display (confirmed, preparing, ready)."""
        
        cache_key = f"kitchen_orders:{restaurant_id}"
        cached_orders = await cache_service.get(cache_key)
        if cached_orders:
            return cached_orders
            
        stmt = select(Order).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.status.in_([OrderStatus.CONFIRMED, OrderStatus.PREPARING, OrderStatus.READY])
            )
        ).order_by(Order.created_at.asc())
        
        result = await self.session.exec(stmt)
        orders = result.all()
        
        await cache_service.set(cache_key, orders, ttl=60)  # 1 minute
        return orders
    
    async def get_order_analytics(
        self,
        restaurant_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get order analytics for a date range."""
        
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=30)
        if not date_to:
            date_to = datetime.utcnow()
            
        # Total orders
        stmt = select(func.count(Order.id)).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.created_at >= date_from,
                Order.created_at <= date_to
            )
        )
        result = await self.session.exec(stmt)
        total_orders = result.first()
        
        # Orders by status
        stmt = select(Order.status, func.count(Order.id)).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.created_at >= date_from,
                Order.created_at <= date_to
            )
        ).group_by(Order.status)
        result = await self.session.exec(stmt)
        orders_by_status = {status: count for status, count in result.all()}
        
        # Revenue calculations
        stmt = select(
            func.sum(Order.total_amount),
            func.avg(Order.total_amount)
        ).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.status.in_([OrderStatus.DELIVERED, OrderStatus.READY]),
                Order.created_at >= date_from,
                Order.created_at <= date_to
            )
        )
        result = await self.session.exec(stmt)
        revenue_data = result.first()
        total_revenue = revenue_data[0] or Decimal(0)
        avg_order_value = revenue_data[1] or Decimal(0)
        
        # Orders by type
        stmt = select(Order.order_type, func.count(Order.id)).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.created_at >= date_from,
                Order.created_at <= date_to
            )
        ).group_by(Order.order_type)
        result = await self.session.exec(stmt)
        orders_by_type = {order_type.value: count for order_type, count in result.all()}
        
        # Average prep time
        stmt = select(func.avg(Order.prep_time_minutes)).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.prep_time_minutes.isnot(None),
                Order.created_at >= date_from,
                Order.created_at <= date_to
            )
        )
        result = await self.session.exec(stmt)
        avg_prep_time = result.first() or 0.0
        
        # Peak hours
        stmt = select(
            func.extract('hour', Order.created_at).label('hour'),
            func.count(Order.id).label('order_count')
        ).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.created_at >= date_from,
                Order.created_at <= date_to
            )
        ).group_by(func.extract('hour', Order.created_at)).order_by(func.count(Order.id).desc()).limit(3)
        result = await self.session.exec(stmt)
        peak_hours = [{"hour": int(hour), "orders": count} for hour, count in result.all()]

        return {
            "total_orders": total_orders or 0,
            "orders_by_status": orders_by_status,
            "orders_by_type": orders_by_type,
            "total_revenue": total_revenue,
            "average_order_value": avg_order_value,
            "average_prep_time": float(avg_prep_time),
            "peak_hours": peak_hours,
            "date_range": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            }
        }
    
    async def _generate_order_number(self, restaurant_id: UUID) -> str:
        """Generate unique order number."""
        import random
        
        now = datetime.utcnow()
        today = now.strftime("%Y%m%d")
        
        # Get count of orders today
        stmt = select(func.count(Order.id)).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.created_at >= now.replace(hour=0, minute=0, second=0, microsecond=0)
            )
        )
        result = await self.session.exec(stmt)
        count = result.first() + 1
        
        # Add microseconds and small random number for uniqueness
        microseconds = now.microsecond // 1000  # Convert to 3 digits
        random_suffix = random.randint(10, 99)
        
        return f"ORD-{today}-{count:04d}-{microseconds:03d}{random_suffix}"
    
    async def _calculate_order_pricing(
        self,
        items_data: List[OrderItemCreate],
        restaurant_id: UUID,
    ) -> tuple[Decimal, List[Dict[str, Any]]]:
        """Calculate order pricing and return items with pricing info."""
        
        subtotal = Decimal(0)
        items_with_pricing = []
        
        for item_data in items_data:
            # Get menu item
            stmt = select(MenuItem).where(
                and_(
                    MenuItem.id == item_data.menu_item_id,
                    MenuItem.restaurant_id == restaurant_id
                )
            )
            result = await self.session.exec(stmt)
            menu_item = result.first()
            
            if not menu_item:
                raise ValueError(f"Menu item {item_data.menu_item_id} not found")
            
            # Calculate item price
            unit_price = menu_item.price
            modifier_total = Decimal(0)
            
            # Calculate modifier prices
            modifier_details = []
            for modifier_data in item_data.modifiers:
                stmt = select(Modifier).where(
                    and_(
                        Modifier.id == modifier_data.modifier_id,
                        Modifier.restaurant_id == restaurant_id
                    )
                )
                result = await self.session.exec(stmt)
                modifier = result.first()
                
                if modifier:
                    modifier_price = modifier.price * modifier_data.quantity
                    modifier_total += modifier_price
                    modifier_details.append({
                        "modifier": modifier,
                        "quantity": modifier_data.quantity,
                        "total_price": modifier_price
                    })
            
            # Total price for this item
            item_total = (unit_price + modifier_total) * item_data.quantity
            subtotal += item_total
            
            items_with_pricing.append({
                "menu_item": menu_item,
                "quantity": item_data.quantity,
                "unit_price": unit_price,
                "modifier_total": modifier_total,
                "total_price": item_total,
                "modifiers": modifier_details,
                "special_instructions": item_data.special_instructions
            })
        
        return subtotal, items_with_pricing
    
    async def _create_order_item(
        self,
        order_id: str,
        item_data: OrderItemCreate,
        pricing_info: Dict[str, Any],
        organization_id: UUID,
        restaurant_id: UUID,
    ) -> OrderItem:
        """Create order item with modifiers."""
        
        menu_item = pricing_info["menu_item"]
        
        order_item = OrderItem(
            order_id=order_id,
            organization_id=organization_id,
            restaurant_id=restaurant_id,
            menu_item_id=menu_item.id,
            menu_item_name=menu_item.name,
            menu_item_description=menu_item.description,
            quantity=pricing_info["quantity"],
            unit_price=pricing_info["unit_price"],
            total_price=pricing_info["total_price"],
            special_instructions=pricing_info["special_instructions"]
        )
        
        self.session.add(order_item)
        await self.session.commit()
        await self.session.refresh(order_item)
        
        # Create modifiers
        for modifier_info in pricing_info["modifiers"]:
            modifier = modifier_info["modifier"]
            order_item_modifier = OrderItemModifier(
                order_item_id=order_item.id,
                organization_id=organization_id,
                restaurant_id=restaurant_id,
                modifier_id=modifier.id,
                modifier_name=modifier.name,
                modifier_price=modifier.price,
                quantity=modifier_info["quantity"],
                total_price=modifier_info["total_price"]
            )
            self.session.add(order_item_modifier)
        
        return order_item
    
    async def _clear_order_cache(self, restaurant_id: UUID, order_id: str = None):
        """Clear order-related cache."""
        patterns = [
            f"order:{restaurant_id}:*",
            f"kitchen_orders:{restaurant_id}",
            f"orders:{restaurant_id}:*"
        ]
        
        if order_id:
            patterns.append(f"order:{restaurant_id}:{order_id}")
            
        for pattern in patterns:
            await cache_service.clear_pattern(pattern)