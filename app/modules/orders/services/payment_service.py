"""
Payment processing service for order payments.
"""

from typing import List, Optional, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timedelta
from sqlmodel import select, and_, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.orders.models.order import Order, OrderStatus
from app.modules.orders.models.payment import (
    Payment, PaymentStatus, PaymentMethod, PaymentCreate, PaymentRefundRequest
)
from app.shared.cache.service import cache_service


class PaymentService:
    """Service for payment processing and management."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def process_payment(
        self,
        order_id: str,
        payment_data: PaymentCreate,
        restaurant_id: UUID,
        organization_id: UUID,
    ) -> Payment:
        """Process a payment for an order."""
        
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
        
        # Create payment record
        payment = Payment(
            order_id=order_id,
            organization_id=organization_id,
            restaurant_id=restaurant_id,
            amount=payment_data.amount,
            payment_method=payment_data.payment_method,
            tip_amount=payment_data.tip_amount,
            is_split_payment=payment_data.is_split_payment,
            split_payment_group_id=payment_data.split_payment_group_id,
            notes=payment_data.notes,
            payment_metadata=payment_data.payment_metadata or {},
        )
        
        # Simulate payment processing based on method
        if payment_data.payment_method == PaymentMethod.CASH:
            # Cash payments are immediately completed
            payment.status = PaymentStatus.COMPLETED
            payment.processed_at = datetime.utcnow()
            payment.transaction_id = f"CASH-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        else:
            # Other payment methods would integrate with payment processor
            payment.status = PaymentStatus.PROCESSING
            payment.transaction_id = f"TXN-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            # Simulate successful processing (in real implementation, call payment API)
            success = await self._simulate_payment_processing(payment)
            if success:
                payment.status = PaymentStatus.COMPLETED
                payment.processed_at = datetime.utcnow()
            else:
                payment.status = PaymentStatus.FAILED
        
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        
        # Update order status if payment is successful
        if payment.status == PaymentStatus.COMPLETED:
            await self._check_order_payment_completion(order)
        
        return payment
    
    async def process_split_payment(
        self,
        order_id: str,
        payments_data: List[PaymentCreate],
        restaurant_id: UUID,
        organization_id: UUID,
    ) -> List[Payment]:
        """Process multiple payments for an order (split payment)."""
        
        # Generate split payment group ID
        split_group_id = f"SPLIT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        payments = []
        for payment_data in payments_data:
            payment_data.is_split_payment = True
            payment_data.split_payment_group_id = split_group_id
            
            payment = await self.process_payment(
                order_id, payment_data, restaurant_id, organization_id
            )
            payments.append(payment)
        
        return payments
    
    async def refund_payment(
        self,
        payment_id: str,
        refund_request: PaymentRefundRequest,
        restaurant_id: UUID,
    ) -> Payment:
        """Process a payment refund."""
        
        # Get payment
        stmt = select(Payment).where(
            and_(
                Payment.id == payment_id,
                Payment.restaurant_id == restaurant_id
            )
        )
        result = await self.session.exec(stmt)
        payment = result.first()
        
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")
        
        if payment.status != PaymentStatus.COMPLETED:
            raise ValueError("Can only refund completed payments")
        
        if refund_request.refund_amount > payment.amount:
            raise ValueError("Refund amount cannot exceed original payment amount")
        
        # Update payment with refund information
        payment.refund_amount = refund_request.refund_amount
        payment.refund_reason = refund_request.refund_reason
        payment.refunded_at = datetime.utcnow()
        
        if refund_request.refund_amount == payment.amount:
            payment.status = PaymentStatus.REFUNDED
        else:
            payment.status = PaymentStatus.PARTIALLY_REFUNDED
        
        if refund_request.notes:
            payment.notes = f"{payment.notes or ''}\nRefund: {refund_request.notes}"
        
        await self.session.commit()
        await self.session.refresh(payment)
        
        return payment
    
    async def get_order_payments(self, order_id: str, restaurant_id: UUID) -> List[Payment]:
        """Get all payments for an order."""
        
        stmt = select(Payment).where(
            and_(
                Payment.order_id == order_id,
                Payment.restaurant_id == restaurant_id
            )
        ).order_by(Payment.created_at.asc())
        
        result = await self.session.exec(stmt)
        return result.all()
    
    async def get_payment_summary(
        self,
        restaurant_id: UUID,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get payment summary for a date range."""
        
        if not date_from:
            date_from = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        if not date_to:
            date_to = datetime.utcnow()
        
        # Total payments by method
        stmt = select(
            Payment.payment_method,
            func.count(Payment.id).label('count'),
            func.sum(Payment.amount).label('total_amount'),
            func.sum(Payment.tip_amount).label('total_tips')
        ).where(
            and_(
                Payment.restaurant_id == restaurant_id,
                Payment.status == PaymentStatus.COMPLETED,
                Payment.created_at >= date_from,
                Payment.created_at <= date_to
            )
        ).group_by(Payment.payment_method)
        
        result = await self.session.exec(stmt)
        payment_methods = {}
        total_revenue = Decimal(0)
        total_tips = Decimal(0)
        
        for method, count, amount, tips in result.all():
            payment_methods[method] = {
                "count": count,
                "total_amount": float(amount or 0),
                "total_tips": float(tips or 0)
            }
            total_revenue += amount or 0
            total_tips += tips or 0
        
        # Failed payments
        stmt = select(func.count(Payment.id)).where(
            and_(
                Payment.restaurant_id == restaurant_id,
                Payment.status == PaymentStatus.FAILED,
                Payment.created_at >= date_from,
                Payment.created_at <= date_to
            )
        )
        result = await self.session.exec(stmt)
        failed_payments = result.first() or 0
        
        # Refunded amount
        stmt = select(func.sum(Payment.refund_amount)).where(
            and_(
                Payment.restaurant_id == restaurant_id,
                Payment.status.in_([PaymentStatus.REFUNDED, PaymentStatus.PARTIALLY_REFUNDED]),
                Payment.refunded_at >= date_from,
                Payment.refunded_at <= date_to
            )
        )
        result = await self.session.exec(stmt)
        total_refunds = result.first() or 0
        
        return {
            "total_revenue": float(total_revenue),
            "total_tips": float(total_tips),
            "total_refunds": float(total_refunds),
            "net_revenue": float(total_revenue - total_refunds),
            "payment_methods": payment_methods,
            "failed_payments_count": failed_payments,
            "period": {
                "from": date_from.isoformat(),
                "to": date_to.isoformat()
            }
        }
    
    async def _simulate_payment_processing(self, payment: Payment) -> bool:
        """Simulate payment processing (replace with real payment gateway integration)."""
        
        # In real implementation, this would:
        # 1. Call payment processor API (Stripe, Square, etc.)
        # 2. Handle webhook responses
        # 3. Update payment status based on processor response
        
        # For simulation, assume 95% success rate
        import random
        success = random.random() < 0.95
        
        if success and payment.payment_method != PaymentMethod.CASH:
            # Simulate payment processor data
            payment.external_payment_id = f"ext_{payment.transaction_id}"
            payment.processor = "stripe"  # or "square", etc.
            
            if payment.payment_method in [PaymentMethod.CREDIT_CARD, PaymentMethod.DEBIT_CARD]:
                payment.card_last_four = "1234"
                payment.card_brand = "visa"
        
        return success
    
    async def _check_order_payment_completion(self, order: Order):
        """Check if order is fully paid and update status."""
        
        # Get all payments for the order
        stmt = select(
            func.sum(Payment.amount)
        ).where(
            and_(
                Payment.order_id == order.id,
                Payment.status == PaymentStatus.COMPLETED
            )
        )
        result = await self.session.exec(stmt)
        total_paid = result.first() or Decimal(0)
        
        # Check if order is fully paid
        if total_paid >= order.total_amount:
            if order.status == OrderStatus.PENDING:
                order.status = OrderStatus.CONFIRMED
                await self.session.commit()
                
                # Clear cache
                await cache_service.clear_pattern(f"kitchen_orders:{order.restaurant_id}")
    
    async def get_daily_payment_totals(
        self,
        restaurant_id: UUID,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get daily payment totals for the last N days."""
        
        # Calculate date range
        end_date = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
        start_date = end_date - timedelta(days=days-1)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Query daily totals
        stmt = select(
            func.date(Payment.created_at).label('payment_date'),
            func.sum(Payment.amount).label('total_amount'),
            func.sum(Payment.tip_amount).label('total_tips'),
            func.count(Payment.id).label('transaction_count')
        ).where(
            and_(
                Payment.restaurant_id == restaurant_id,
                Payment.status == PaymentStatus.COMPLETED,
                Payment.created_at >= start_date,
                Payment.created_at <= end_date
            )
        ).group_by(
            func.date(Payment.created_at)
        ).order_by(
            func.date(Payment.created_at).asc()
        )
        
        result = await self.session.exec(stmt)
        
        daily_totals = []
        for payment_date, total_amount, total_tips, count in result.all():
            daily_totals.append({
                "date": payment_date.isoformat(),
                "total_amount": float(total_amount or 0),
                "total_tips": float(total_tips or 0),
                "transaction_count": count,
                "average_transaction": float((total_amount or 0) / count) if count > 0 else 0
            })
        
        return daily_totals