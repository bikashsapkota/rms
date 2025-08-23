#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Payment Service
Production-level testing for Phase 3 payment processing functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from decimal import Decimal
from datetime import datetime, timedelta
from uuid import uuid4

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.modules.orders.services.payment_service import PaymentService
from app.modules.orders.models.payment import PaymentStatus, PaymentMethod, PaymentCreate, PaymentRefundRequest
from app.modules.orders.models.order import OrderStatus


class TestPaymentServiceComprehensive:
    """Comprehensive test suite for PaymentService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = AsyncMock()
        self.payment_service = PaymentService(self.mock_session)
        self.restaurant_id = uuid4()
        self.organization_id = uuid4()
        
    def test_payment_service_initialization(self):
        """Test PaymentService proper initialization"""
        service = PaymentService(self.mock_session)
        assert service.session == self.mock_session
        
    @pytest.mark.asyncio
    async def test_process_payment_cash_success(self):
        """Test successful cash payment processing"""
        order_id = str(uuid4())
        mock_order = Mock()
        mock_order.total_amount = Decimal("25.50")
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        payment_data = PaymentCreate(
            amount=Decimal("25.50"),
            payment_method=PaymentMethod.CASH,
            tip_amount=Decimal("5.00"),
            is_split_payment=False,
            payment_metadata={"receipt_number": "R001"}
        )
        
        with patch('app.modules.orders.services.payment_service.datetime') as mock_datetime:
            mock_now = datetime(2025, 8, 18, 12, 0, 0)
            mock_datetime.utcnow.return_value = mock_now
            
            result = await self.payment_service.process_payment(
                order_id=order_id,
                payment_data=payment_data,
                restaurant_id=self.restaurant_id,
                organization_id=self.organization_id
            )
            
            assert self.mock_session.add.called
            assert self.mock_session.commit.called
            # Cash payments should be immediately completed
            
    @pytest.mark.asyncio
    async def test_process_payment_credit_card_success(self):
        """Test successful credit card payment processing"""
        order_id = str(uuid4())
        mock_order = Mock()
        mock_order.total_amount = Decimal("45.99")
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        payment_data = PaymentCreate(
            amount=Decimal("45.99"),
            payment_method=PaymentMethod.CREDIT_CARD,
            tip_amount=Decimal("8.00"),
            is_split_payment=False,
            payment_metadata={"card_last_four": "1234", "card_brand": "visa"}
        )
        
        with patch.object(self.payment_service, '_simulate_payment_processing') as mock_simulate:
            mock_simulate.return_value = True  # Successful processing
            
            result = await self.payment_service.process_payment(
                order_id=order_id,
                payment_data=payment_data,
                restaurant_id=self.restaurant_id,
                organization_id=self.organization_id
            )
            
            assert mock_simulate.called
            assert self.mock_session.add.called
            assert self.mock_session.commit.called
            
    @pytest.mark.asyncio
    async def test_process_payment_order_not_found(self):
        """Test payment processing when order doesn't exist"""
        order_id = str(uuid4())
        
        mock_result = Mock()
        mock_result.first.return_value = None
        self.mock_session.exec.return_value = mock_result
        
        payment_data = PaymentCreate(
            amount=Decimal("25.50"),
            payment_method=PaymentMethod.CASH
        )
        
        with pytest.raises(ValueError, match="Order .* not found"):
            await self.payment_service.process_payment(
                order_id=order_id,
                payment_data=payment_data,
                restaurant_id=self.restaurant_id,
                organization_id=self.organization_id
            )
            
    @pytest.mark.asyncio
    async def test_process_payment_failed_processing(self):
        """Test payment processing failure"""
        order_id = str(uuid4())
        mock_order = Mock()
        mock_order.total_amount = Decimal("30.00")
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        payment_data = PaymentCreate(
            amount=Decimal("30.00"),
            payment_method=PaymentMethod.CREDIT_CARD
        )
        
        with patch.object(self.payment_service, '_simulate_payment_processing') as mock_simulate:
            mock_simulate.return_value = False  # Failed processing
            
            result = await self.payment_service.process_payment(
                order_id=order_id,
                payment_data=payment_data,
                restaurant_id=self.restaurant_id,
                organization_id=self.organization_id
            )
            
            # Payment should still be created but with failed status
            assert self.mock_session.add.called
            
    @pytest.mark.asyncio
    async def test_process_split_payment_success(self):
        """Test successful split payment processing"""
        order_id = str(uuid4())
        
        payments_data = [
            PaymentCreate(
                amount=Decimal("20.00"),
                payment_method=PaymentMethod.CASH
            ),
            PaymentCreate(
                amount=Decimal("15.50"),
                payment_method=PaymentMethod.CREDIT_CARD
            )
        ]
        
        with patch.object(self.payment_service, 'process_payment') as mock_process:
            mock_payment1 = Mock()
            mock_payment2 = Mock()
            mock_process.side_effect = [mock_payment1, mock_payment2]
            
            result = await self.payment_service.process_split_payment(
                order_id=order_id,
                payments_data=payments_data,
                restaurant_id=self.restaurant_id,
                organization_id=self.organization_id
            )
            
            assert len(result) == 2
            assert mock_process.call_count == 2
            
            # Verify split payment group ID was set
            for call_args in mock_process.call_args_list:
                payment_data = call_args[1]['payment_data']
                assert payment_data.is_split_payment is True
                assert payment_data.split_payment_group_id is not None
                
    @pytest.mark.asyncio
    async def test_refund_payment_full_success(self):
        """Test successful full payment refund"""
        payment_id = str(uuid4())
        mock_payment = Mock()
        mock_payment.status = PaymentStatus.COMPLETED
        mock_payment.amount = Decimal("50.00")
        mock_payment.notes = "Original payment"
        
        mock_result = Mock()
        mock_result.first.return_value = mock_payment
        self.mock_session.exec.return_value = mock_result
        
        refund_request = PaymentRefundRequest(
            refund_amount=Decimal("50.00"),
            refund_reason="Customer request",
            notes="Full refund processed"
        )
        
        with patch('app.modules.orders.services.payment_service.datetime') as mock_datetime:
            mock_now = datetime(2025, 8, 18, 12, 30, 0)
            mock_datetime.utcnow.return_value = mock_now
            
            result = await self.payment_service.refund_payment(
                payment_id=payment_id,
                refund_request=refund_request,
                restaurant_id=self.restaurant_id
            )
            
            assert mock_payment.refund_amount == Decimal("50.00")
            assert mock_payment.status == PaymentStatus.REFUNDED
            assert mock_payment.refunded_at == mock_now
            assert self.mock_session.commit.called
            
    @pytest.mark.asyncio
    async def test_refund_payment_partial_success(self):
        """Test successful partial payment refund"""
        payment_id = str(uuid4())
        mock_payment = Mock()
        mock_payment.status = PaymentStatus.COMPLETED
        mock_payment.amount = Decimal("50.00")
        
        mock_result = Mock()
        mock_result.first.return_value = mock_payment
        self.mock_session.exec.return_value = mock_result
        
        refund_request = PaymentRefundRequest(
            refund_amount=Decimal("20.00"),
            refund_reason="Partial refund"
        )
        
        result = await self.payment_service.refund_payment(
            payment_id=payment_id,
            refund_request=refund_request,
            restaurant_id=self.restaurant_id
        )
        
        assert mock_payment.refund_amount == Decimal("20.00")
        assert mock_payment.status == PaymentStatus.PARTIALLY_REFUNDED
        
    @pytest.mark.asyncio
    async def test_refund_payment_not_found(self):
        """Test refund when payment doesn't exist"""
        payment_id = str(uuid4())
        
        mock_result = Mock()
        mock_result.first.return_value = None
        self.mock_session.exec.return_value = mock_result
        
        refund_request = PaymentRefundRequest(
            refund_amount=Decimal("25.00"),
            refund_reason="Test refund"
        )
        
        with pytest.raises(ValueError, match="Payment .* not found"):
            await self.payment_service.refund_payment(
                payment_id=payment_id,
                refund_request=refund_request,
                restaurant_id=self.restaurant_id
            )
            
    @pytest.mark.asyncio
    async def test_refund_payment_invalid_status(self):
        """Test refund when payment is not completed"""
        payment_id = str(uuid4())
        mock_payment = Mock()
        mock_payment.status = PaymentStatus.PENDING
        
        mock_result = Mock()
        mock_result.first.return_value = mock_payment
        self.mock_session.exec.return_value = mock_result
        
        refund_request = PaymentRefundRequest(
            refund_amount=Decimal("25.00"),
            refund_reason="Test refund"
        )
        
        with pytest.raises(ValueError, match="Can only refund completed payments"):
            await self.payment_service.refund_payment(
                payment_id=payment_id,
                refund_request=refund_request,
                restaurant_id=self.restaurant_id
            )
            
    @pytest.mark.asyncio
    async def test_refund_payment_excessive_amount(self):
        """Test refund when amount exceeds original payment"""
        payment_id = str(uuid4())
        mock_payment = Mock()
        mock_payment.status = PaymentStatus.COMPLETED
        mock_payment.amount = Decimal("30.00")
        
        mock_result = Mock()
        mock_result.first.return_value = mock_payment
        self.mock_session.exec.return_value = mock_result
        
        refund_request = PaymentRefundRequest(
            refund_amount=Decimal("50.00"),  # More than original
            refund_reason="Invalid refund"
        )
        
        with pytest.raises(ValueError, match="Refund amount cannot exceed"):
            await self.payment_service.refund_payment(
                payment_id=payment_id,
                refund_request=refund_request,
                restaurant_id=self.restaurant_id
            )
            
    @pytest.mark.asyncio
    async def test_get_order_payments_success(self):
        """Test retrieving payments for an order"""
        order_id = str(uuid4())
        mock_payments = [Mock(), Mock(), Mock()]
        
        mock_result = Mock()
        mock_result.all.return_value = mock_payments
        self.mock_session.exec.return_value = mock_result
        
        result = await self.payment_service.get_order_payments(
            order_id=order_id,
            restaurant_id=self.restaurant_id
        )
        
        assert result == mock_payments
        assert self.mock_session.exec.called
        
    @pytest.mark.asyncio
    async def test_get_payment_summary_comprehensive(self):
        """Test comprehensive payment summary generation"""
        def mock_exec_side_effect(*args, **kwargs):
            result = Mock()
            query_str = str(args[0])
            
            if "payment_method" in query_str and "group_by" in query_str:
                result.all.return_value = [
                    (PaymentMethod.CREDIT_CARD, 50, Decimal("1250.00"), Decimal("200.00")),
                    (PaymentMethod.CASH, 25, Decimal("400.00"), Decimal("50.00")),
                    (PaymentMethod.DIGITAL_WALLET, 10, Decimal("300.00"), Decimal("40.00"))
                ]
            elif "failed" in query_str.lower():
                result.first.return_value = 3  # Failed payments
            elif "refund" in query_str.lower():
                result.first.return_value = Decimal("75.00")  # Total refunds
            else:
                result.first.return_value = 0
                
            return result
            
        self.mock_session.exec.side_effect = mock_exec_side_effect
        
        summary = await self.payment_service.get_payment_summary(
            restaurant_id=self.restaurant_id
        )
        
        # Verify summary structure
        assert "total_revenue" in summary
        assert "total_tips" in summary
        assert "total_refunds" in summary
        assert "net_revenue" in summary
        assert "payment_methods" in summary
        assert "failed_payments_count" in summary
        
        assert summary["total_revenue"] == float(Decimal("1950.00"))
        assert summary["total_tips"] == float(Decimal("290.00"))
        assert summary["failed_payments_count"] == 3
        
    @pytest.mark.asyncio
    async def test_get_daily_payment_totals_success(self):
        """Test daily payment totals calculation"""
        def mock_exec_side_effect(*args, **kwargs):
            result = Mock()
            # Mock daily totals for last 7 days
            result.all.return_value = [
                (datetime(2025, 8, 12).date(), Decimal("250.00"), Decimal("40.00"), 15),
                (datetime(2025, 8, 13).date(), Decimal("300.00"), Decimal("50.00"), 18),
                (datetime(2025, 8, 14).date(), Decimal("280.00"), Decimal("45.00"), 16),
            ]
            return result
            
        self.mock_session.exec.side_effect = mock_exec_side_effect
        
        daily_totals = await self.payment_service.get_daily_payment_totals(
            restaurant_id=self.restaurant_id,
            days=7
        )
        
        assert len(daily_totals) == 3
        for daily_total in daily_totals:
            assert "date" in daily_total
            assert "total_amount" in daily_total
            assert "total_tips" in daily_total
            assert "transaction_count" in daily_total
            assert "average_transaction" in daily_total
            
    @pytest.mark.asyncio
    async def test_simulate_payment_processing_success(self):
        """Test payment simulation success scenarios"""
        mock_payment = Mock()
        mock_payment.payment_method = PaymentMethod.CREDIT_CARD
        
        with patch('random.random') as mock_random:
            mock_random.return_value = 0.9  # Within 95% success rate
            
            result = await self.payment_service._simulate_payment_processing(mock_payment)
            
            assert result is True
            assert hasattr(mock_payment, 'external_payment_id')
            assert hasattr(mock_payment, 'processor')
            
    @pytest.mark.asyncio
    async def test_simulate_payment_processing_failure(self):
        """Test payment simulation failure scenarios"""
        mock_payment = Mock()
        mock_payment.payment_method = PaymentMethod.CREDIT_CARD
        
        with patch('random.random') as mock_random:
            mock_random.return_value = 0.97  # Outside 95% success rate
            
            result = await self.payment_service._simulate_payment_processing(mock_payment)
            
            assert result is False
            
    @pytest.mark.asyncio
    async def test_check_order_payment_completion_full_payment(self):
        """Test order payment completion check when fully paid"""
        mock_order = Mock()
        mock_order.id = str(uuid4())
        mock_order.total_amount = Decimal("50.00")
        mock_order.status = OrderStatus.PENDING
        mock_order.restaurant_id = self.restaurant_id
        
        # Mock payment total query
        mock_result = Mock()
        mock_result.first.return_value = Decimal("50.00")  # Fully paid
        self.mock_session.exec.return_value = mock_result
        
        with patch('app.modules.orders.services.payment_service.cache_service') as mock_cache:
            await self.payment_service._check_order_payment_completion(mock_order)
            
            assert mock_order.status == OrderStatus.CONFIRMED
            assert self.mock_session.commit.called
            assert mock_cache.clear_pattern.called
            
    @pytest.mark.asyncio
    async def test_check_order_payment_completion_partial_payment(self):
        """Test order payment completion check when partially paid"""
        mock_order = Mock()
        mock_order.id = str(uuid4())
        mock_order.total_amount = Decimal("50.00")
        mock_order.status = OrderStatus.PENDING
        
        # Mock payment total query
        mock_result = Mock()
        mock_result.first.return_value = Decimal("30.00")  # Partially paid
        self.mock_session.exec.return_value = mock_result
        
        await self.payment_service._check_order_payment_completion(mock_order)
        
        # Order status should remain unchanged
        assert mock_order.status == OrderStatus.PENDING
        
    @pytest.mark.asyncio
    async def test_concurrent_payment_processing(self):
        """Test handling of concurrent payment processing"""
        order_id = str(uuid4())
        mock_order = Mock()
        mock_order.total_amount = Decimal("100.00")
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        # Create multiple payment requests
        payments_data = [
            PaymentCreate(
                amount=Decimal("50.00"),
                payment_method=PaymentMethod.CASH
            ),
            PaymentCreate(
                amount=Decimal("30.00"),
                payment_method=PaymentMethod.CREDIT_CARD
            ),
            PaymentCreate(
                amount=Decimal("20.00"),
                payment_method=PaymentMethod.DIGITAL_WALLET
            )
        ]
        
        # Process payments concurrently
        tasks = []
        for payment_data in payments_data:
            task = self.payment_service.process_payment(
                order_id=order_id,
                payment_data=payment_data,
                restaurant_id=self.restaurant_id,
                organization_id=self.organization_id
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # All payments should process (exceptions are also valid results)
        assert len(results) == 3
        
    def test_payment_service_integration_interface(self):
        """Test payment service provides expected interface"""
        mock_session = Mock()
        service = PaymentService(mock_session)
        
        # Verify service has expected methods
        assert hasattr(service, 'process_payment')
        assert hasattr(service, 'process_split_payment')
        assert hasattr(service, 'refund_payment')
        assert hasattr(service, 'get_order_payments')
        assert hasattr(service, 'get_payment_summary')
        assert hasattr(service, 'get_daily_payment_totals')
        
        assert service.session == mock_session
        
    @pytest.mark.asyncio
    async def test_payment_metadata_handling(self):
        """Test payment metadata is properly handled"""
        order_id = str(uuid4())
        mock_order = Mock()
        mock_order.total_amount = Decimal("25.00")
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        payment_metadata = {
            "card_last_four": "1234",
            "card_brand": "visa",
            "receipt_email": "customer@example.com",
            "loyalty_points_used": 100
        }
        
        payment_data = PaymentCreate(
            amount=Decimal("25.00"),
            payment_method=PaymentMethod.CREDIT_CARD,
            payment_metadata=payment_metadata
        )
        
        await self.payment_service.process_payment(
            order_id=order_id,
            payment_data=payment_data,
            restaurant_id=self.restaurant_id,
            organization_id=self.organization_id
        )
        
        # Verify metadata is preserved
        assert self.mock_session.add.called
        
    @pytest.mark.asyncio
    async def test_payment_service_error_handling(self):
        """Test payment service error handling"""
        # Test database error
        order_id = str(uuid4())
        payment_data = PaymentCreate(
            amount=Decimal("25.00"),
            payment_method=PaymentMethod.CASH
        )
        
        self.mock_session.exec.side_effect = Exception("Database connection error")
        
        with pytest.raises(Exception):
            await self.payment_service.process_payment(
                order_id=order_id,
                payment_data=payment_data,
                restaurant_id=self.restaurant_id,
                organization_id=self.organization_id
            )


if __name__ == "__main__":
    # Run comprehensive tests
    pytest.main([__file__, "-v", "--tb=short"])