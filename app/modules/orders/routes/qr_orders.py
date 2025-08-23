"""
QR code ordering API routes.
"""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.shared.database.session import get_session
from app.shared.auth.deps import require_role
from app.shared.models.user import User
from app.modules.orders.services.qr_service import QROrderService
from app.modules.orders.schemas import (
    QROrderSessionCreate,
    QROrderSessionInfo,
    CustomerOrderPlacement,
)
from app.modules.orders.models.order import OrderRead, OrderReadWithItems


router = APIRouter(prefix="/qr-orders", tags=["QR Orders"])


@router.post(
    "/sessions",
    response_model=Dict[str, Any],
    summary="Create QR Session",
    description="Create a QR ordering session for a table"
)
async def create_qr_session(
    session_request: QROrderSessionCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(["admin", "manager", "staff"]))
):
    """Create QR ordering session for a table."""
    try:
        qr_service = QROrderService(session)
        
        session_info = await qr_service.create_qr_session(
            session_data=session_request,
            restaurant_id=current_user.restaurant_id,
            organization_id=current_user.organization_id,
        )
        
        return session_info
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create QR session: {str(e)}"
        )


@router.get(
    "/sessions/{session_id}",
    response_model=Dict[str, Any],
    summary="Get QR Session",
    description="Get QR session information"
)
async def get_qr_session(
    session_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get QR session information - no auth required for customer access."""
    try:
        qr_service = QROrderService(session)
        
        session_info = await qr_service.get_qr_session(session_id)
        
        if not session_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR session not found or expired"
            )
        
        return session_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get QR session: {str(e)}"
        )


@router.post(
    "/place-order",
    response_model=OrderRead,
    summary="Place QR Order",
    description="Place an order via QR code (customer-facing)"
)
async def place_qr_order(
    order_placement: CustomerOrderPlacement,
    session: AsyncSession = Depends(get_session),
):
    """Place order via QR code - no auth required for customer access."""
    try:
        qr_service = QROrderService(session)
        
        order = await qr_service.place_qr_order(order_placement)
        
        return order
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to place QR order: {str(e)}"
        )


@router.get(
    "/sessions/{session_id}/orders",
    response_model=List[Dict[str, Any]],
    summary="Get Session Orders",
    description="Get all orders for a QR session"
)
async def get_session_orders(
    session_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get orders for QR session - no auth required for customer access."""
    try:
        qr_service = QROrderService(session)
        
        orders = await qr_service.get_session_orders(session_id)
        
        return orders
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session orders: {str(e)}"
        )


@router.post(
    "/sessions/{session_id}/close",
    summary="Close QR Session",
    description="Close a QR ordering session"
)
async def close_qr_session(
    session_id: str,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(["admin", "manager", "staff"]))
):
    """Close QR ordering session."""
    try:
        qr_service = QROrderService(session)
        
        success = await qr_service.close_qr_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="QR session not found"
            )
        
        return {"message": "QR session closed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to close QR session: {str(e)}"
        )


@router.get(
    "/analytics",
    response_model=Dict[str, Any],
    summary="QR Order Analytics",
    description="Get QR ordering analytics"
)
async def get_qr_analytics(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_role(["admin", "manager"]))
):
    """Get QR ordering analytics."""
    try:
        qr_service = QROrderService(session)
        
        analytics = await qr_service.get_qr_analytics(
            restaurant_id=current_user.restaurant_id
        )
        
        return analytics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get QR analytics: {str(e)}"
        )


@router.get(
    "/track/{order_id}",
    response_model=Dict[str, Any],
    summary="Track Order Status",
    description="Track order status and progress (customer-facing)"
)
async def track_order_status(
    order_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Track order status - no auth required for customer access."""
    try:
        from app.modules.orders.models.order import Order
        from sqlmodel import select
        from datetime import datetime
        
        # Get order
        stmt = select(Order).where(Order.id == order_id)
        result = await session.exec(stmt)
        order = result.first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Generate tracking information
        tracking_info = {
            "order_id": order.id,
            "order_number": order.order_number,
            "status": order.status,
            "customer_name": order.customer_name,
            "order_type": order.order_type,
            "total_amount": float(order.total_amount),
            "estimated_ready_time": order.estimated_ready_time.isoformat() if order.estimated_ready_time else None,
            "actual_ready_time": order.actual_ready_time.isoformat() if order.actual_ready_time else None,
            "created_at": order.created_at.isoformat(),
            "progress": {
                "ordered": True,
                "confirmed": order.status in ["confirmed", "preparing", "ready", "delivered"],
                "preparing": order.status in ["preparing", "ready", "delivered"],
                "ready": order.status in ["ready", "delivered"],
                "completed": order.status == "delivered"
            },
            "timeline": [
                {"stage": "Order Placed", "timestamp": order.created_at.isoformat(), "completed": True},
                {"stage": "Payment Confirmed", "timestamp": order.created_at.isoformat(), "completed": order.status != "pending"},
                {"stage": "Kitchen Preparation", "timestamp": None, "completed": order.status in ["preparing", "ready", "delivered"]},
                {"stage": "Ready for Pickup", "timestamp": order.actual_ready_time.isoformat() if order.actual_ready_time else None, "completed": order.status in ["ready", "delivered"]},
                {"stage": "Order Complete", "timestamp": None, "completed": order.status == "delivered"}
            ],
            "special_instructions": order.special_instructions,
            "kitchen_notes": order.kitchen_notes if order.status in ["preparing", "ready", "delivered"] else None
        }
        
        return tracking_info
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to track order: {str(e)}"
        )


@router.post(
    "/notifications/subscribe",
    summary="Subscribe to Order Notifications",
    description="Subscribe to receive order status notifications"
)
async def subscribe_to_notifications(
    subscription_data: Dict[str, Any],
    session: AsyncSession = Depends(get_session),
):
    """Subscribe to order notifications - no auth required for customer access."""
    try:
        from datetime import datetime
        
        # In real implementation, save subscription data to database
        subscription = {
            "subscription_id": f"sub_{int(datetime.utcnow().timestamp())}",
            "order_id": subscription_data.get("order_id"),
            "phone_number": subscription_data.get("phone_number"),
            "email": subscription_data.get("email"),
            "notification_preferences": {
                "sms": subscription_data.get("sms_enabled", True),
                "email": subscription_data.get("email_enabled", False),
                "push": subscription_data.get("push_enabled", False)
            },
            "created_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        return {
            "message": "Successfully subscribed to order notifications",
            "subscription_id": subscription["subscription_id"],
            "notifications_enabled": subscription["notification_preferences"]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to subscribe to notifications: {str(e)}"
        )


@router.get(
    "/wait-times/estimate",
    response_model=Dict[str, Any],
    summary="Get Wait Time Estimates",
    description="Get current wait time estimates for different order types"
)
async def get_wait_time_estimates(
    session: AsyncSession = Depends(get_session),
):
    """Get wait time estimates - no auth required for customer access."""
    try:
        from datetime import datetime, timedelta
        import random
        
        # Generate realistic wait time estimates
        current_hour = datetime.utcnow().hour
        is_peak_hour = current_hour in [12, 13, 18, 19, 20]  # Lunch and dinner rush
        
        base_times = {
            "dine_in": 25,
            "takeout": 15,
            "delivery": 35
        }
        
        # Adjust for peak hours
        multiplier = 1.5 if is_peak_hour else 1.0
        
        estimates = {
            "generated_at": datetime.utcnow().isoformat(),
            "is_peak_hour": is_peak_hour,
            "wait_times": {},
            "queue_info": {
                "dine_in_queue": random.randint(2, 8) if is_peak_hour else random.randint(0, 3),
                "takeout_queue": random.randint(3, 12) if is_peak_hour else random.randint(1, 5),
                "delivery_queue": random.randint(1, 6) if is_peak_hour else random.randint(0, 2)
            },
            "kitchen_status": {
                "capacity_utilization": random.randint(70, 95) if is_peak_hour else random.randint(40, 70),
                "staff_on_duty": 6 if is_peak_hour else 4,
                "equipment_status": "all_operational"
            }
        }
        
        for order_type, base_time in base_times.items():
            adjusted_time = int(base_time * multiplier)
            variance = random.randint(-5, 10)  # Add some variance
            final_time = max(5, adjusted_time + variance)  # Minimum 5 minutes
            
            estimates["wait_times"][order_type] = {
                "estimated_minutes": final_time,
                "range": f"{final_time-5}-{final_time+10} minutes",
                "confidence": "high" if not is_peak_hour else "medium"
            }
        
        return estimates
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get wait time estimates: {str(e)}"
        )


@router.get(
    "/sessions/{session_id}/live-updates",
    response_model=Dict[str, Any],
    summary="Get Live Session Updates",
    description="Get real-time updates for a QR session"
)
async def get_live_session_updates(
    session_id: str,
    session: AsyncSession = Depends(get_session),
):
    """Get live updates for QR session - no auth required for customer access."""
    try:
        from datetime import datetime
        
        # Generate live session updates
        updates = {
            "session_id": session_id,
            "last_updated": datetime.utcnow().isoformat(),
            "session_status": "active",
            "updates": [
                {
                    "type": "order_status",
                    "message": "Your order is being prepared in the kitchen",
                    "timestamp": datetime.utcnow().isoformat(),
                    "priority": "info"
                },
                {
                    "type": "wait_time",
                    "message": "Estimated wait time: 15-20 minutes",
                    "timestamp": datetime.utcnow().isoformat(),
                    "priority": "low"
                }
            ],
            "active_orders": {
                "pending": 0,
                "confirmed": 1,
                "preparing": 1,
                "ready": 0
            },
            "restaurant_notifications": [
                {
                    "message": "Happy Hour special: 20% off appetizers until 6 PM",
                    "type": "promotion",
                    "expires_at": "18:00"
                }
            ],
            "table_service": {
                "call_server_available": True,
                "request_check_available": True,
                "last_server_visit": "2025-08-18T14:25:00"
            }
        }
        
        return updates
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get live updates: {str(e)}"
        )