"""
QR code ordering service for table-based ordering.
"""

import uuid
import qrcode
import io
import base64
from uuid import UUID
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlmodel import select, and_, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.tables.models.table import Table
from app.modules.orders.models.order import Order, OrderType, OrderStatus
from app.modules.orders.schemas import QROrderSessionCreate, CustomerOrderPlacement
from app.shared.cache.service import cache_service
from app.core.config import settings


class QROrderService:
    """Service for QR code ordering functionality."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_qr_session(
        self,
        session_data: QROrderSessionCreate,
        restaurant_id: UUID,
        organization_id: UUID,
    ) -> Dict[str, Any]:
        """Create a QR ordering session for a table."""
        
        # Verify table exists
        stmt = select(Table).where(
            and_(
                Table.id == session_data.table_id,
                Table.restaurant_id == restaurant_id
            )
        )
        result = await self.session.exec(stmt)
        table = result.first()
        
        if not table:
            raise ValueError(f"Table {session_data.table_id} not found")
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Create session data
        session_info = {
            "session_id": session_id,
            "table_id": session_data.table_id,
            "table_number": table.table_number,
            "restaurant_id": restaurant_id,
            "organization_id": organization_id,
            "customer_name": session_data.customer_name,
            "created_at": datetime.utcnow().isoformat(),
            "active_until": (datetime.utcnow() + timedelta(hours=3)).isoformat(),
            "status": "active"
        }
        
        # Store session in cache (3 hours expiry)
        cache_key = f"qr_session:{session_id}"
        await cache_service.set(cache_key, session_info, ttl=10800)  # 3 hours
        
        # Generate QR code
        qr_url = f"{settings.FRONTEND_URL}/qr-order/{session_id}"
        qr_image = self._generate_qr_code(qr_url)
        
        return {
            "session_id": session_id,
            "table_number": table.table_number,
            "qr_url": qr_url,
            "qr_image": qr_image,
            "active_until": session_info["active_until"],
            "menu_url": f"{settings.API_V1_STR}/menu/public?restaurant_id={restaurant_id}"
        }
    
    async def get_qr_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get QR session information."""
        
        cache_key = f"qr_session:{session_id}"
        session_info = await cache_service.get(cache_key)
        
        if not session_info:
            return None
        
        # Check if session is still active
        active_until = datetime.fromisoformat(session_info["active_until"])
        if datetime.utcnow() > active_until:
            await cache_service.delete(cache_key)
            return None
        
        return session_info
    
    async def place_qr_order(
        self,
        order_placement: CustomerOrderPlacement,
    ) -> Order:
        """Place an order via QR code."""
        
        # Get session info
        session_info = await self.get_qr_session(order_placement.session_id)
        if not session_info:
            raise ValueError("Invalid or expired QR session")
        
        # Import here to avoid circular imports
        from app.modules.orders.services.order_service import OrderService
        
        order_service = OrderService(self.session)
        
        # Prepare order data
        order_data = {
            "order_type": OrderType.QR_ORDER,
            "customer_name": order_placement.customer_name or session_info.get("customer_name"),
            "special_instructions": order_placement.special_instructions,
            "table_id": session_info["table_id"],
            "qr_session_id": order_placement.session_id,
        }
        
        # Create order
        order = await order_service.create_order(
            order_data=order_data,
            items_data=order_placement.items,
            restaurant_id=session_info["restaurant_id"],
            organization_id=session_info["organization_id"],
        )
        
        # Update session with order info
        session_info["orders"] = session_info.get("orders", [])
        session_info["orders"].append({
            "order_id": order.id,
            "order_number": order.order_number,
            "total_amount": float(order.total_amount),
            "created_at": datetime.utcnow().isoformat()
        })
        
        # Update session in cache
        cache_key = f"qr_session:{order_placement.session_id}"
        await cache_service.set(cache_key, session_info, ttl=10800)
        
        return order
    
    async def get_session_orders(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all orders for a QR session."""
        
        session_info = await self.get_qr_session(session_id)
        if not session_info:
            raise ValueError("Invalid or expired QR session")
        
        return session_info.get("orders", [])
    
    async def close_qr_session(self, session_id: str) -> bool:
        """Close a QR ordering session."""
        
        cache_key = f"qr_session:{session_id}"
        session_info = await cache_service.get(cache_key)
        
        if not session_info:
            return False
        
        # Mark session as closed
        session_info["status"] = "closed"
        session_info["closed_at"] = datetime.utcnow().isoformat()
        
        # Update cache with shorter TTL (1 hour for history)
        await cache_service.set(cache_key, session_info, ttl=3600)
        
        return True
    
    async def get_table_active_sessions(self, table_id: str, restaurant_id: UUID) -> List[Dict[str, Any]]:
        """Get active QR sessions for a table."""
        
        # This would require scanning cache keys or storing table->session mapping
        # For now, return empty list - in production, consider using a different storage approach
        return []
    
    def _generate_qr_code(self, url: str) -> str:
        """Generate QR code image as base64 string."""
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create QR code image
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        img_buffer = io.BytesIO()
        img.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    async def get_qr_analytics(
        self,
        restaurant_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get QR ordering analytics."""
        
        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=30)
        if not date_to:
            date_to = datetime.utcnow()
        
        # QR orders count
        stmt = select(func.count(Order.id)).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.order_type == OrderType.QR_ORDER,
                Order.created_at >= date_from,
                Order.created_at <= date_to
            )
        )
        result = await self.session.exec(stmt)
        total_qr_orders = result.first() or 0
        
        # QR orders revenue
        stmt = select(func.sum(Order.total_amount)).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.order_type == OrderType.QR_ORDER,
                Order.status.in_([OrderStatus.DELIVERED, OrderStatus.READY]),
                Order.created_at >= date_from,
                Order.created_at <= date_to
            )
        )
        result = await self.session.exec(stmt)
        qr_revenue = result.first() or 0
        
        # Average QR order value
        avg_qr_order_value = qr_revenue / total_qr_orders if total_qr_orders > 0 else 0
        
        # Most popular QR ordering tables
        stmt = select(
            Table.table_number,
            func.count(Order.id).label('order_count')
        ).select_from(
            Order.__table__.join(Table.__table__)
        ).where(
            and_(
                Order.restaurant_id == restaurant_id,
                Order.order_type == OrderType.QR_ORDER,
                Order.created_at >= date_from,
                Order.created_at <= date_to
            )
        ).group_by(
            Table.table_number
        ).order_by(
            func.count(Order.id).desc()
        ).limit(5)
        
        result = await self.session.exec(stmt)
        popular_tables = [
            {"table_number": table_number, "order_count": count}
            for table_number, count in result.all()
        ]
        
        return {
            "total_qr_orders": total_qr_orders,
            "qr_revenue": float(qr_revenue),
            "average_qr_order_value": float(avg_qr_order_value),
            "popular_tables": popular_tables,
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            }
        }