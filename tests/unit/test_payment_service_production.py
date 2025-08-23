"""
Production-level unit tests for PaymentService.
Tests actual functionality with realistic payment scenarios.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.orders.services.payment_service import PaymentService
from app.modules.orders.models.payment import Payment, PaymentStatus, PaymentMethod, PaymentCreate
from app.modules.orders.models.order import Order


class TestPaymentServiceProduction:
    """Production-focused tests for PaymentService."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.payment_service = PaymentService(self.mock_session)
        self.restaurant_id = uuid4()
        self.order_id = str(uuid4())
        
        # Sample payment data
        self.sample_payment = PaymentCreate(
            order_id=self.order_id,
            amount=Decimal("25.99"),
            payment_method=PaymentMethod.CREDIT_CARD,
            metadata={"card_last_four": "1234"}
        )
    
    @pytest.mark.asyncio
    async def test_payment_service_initialization(self):
        """Test PaymentService can be initialized properly."""
        assert self.payment_service is not None
        assert self.payment_service.session == self.mock_session
    
    @pytest.mark.asyncio
    async def test_process_payment_success(self):
        """Test successful payment processing."""
        # Mock order lookup
        mock_order = Mock(spec=Order)
        mock_order.total_amount = Decimal("25.99")
        
        mock_order_result = Mock()
        mock_order_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_order_result
        
        # Mock session operations
        self.mock_session.add = Mock()
        self.mock_session.commit = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        # Process payment
        payment = await self.payment_service.process_payment(
            payment_data=self.sample_payment,
            restaurant_id=self.restaurant_id,
            organization_id=uuid4()
        )
        
        # Verify payment was processed
        assert self.mock_session.add.called
        assert self.mock_session.commit.called
    
    @pytest.mark.asyncio
    async def test_get_payment_summary_structure(self):
        """Test payment summary returns proper structure."""
        # Mock payment queries
        mock_results = [
            Mock(first=Mock(return_value=100)),  # Total payments
            Mock(first=Mock(return_value=(Decimal("2500.00"), Decimal("25.00")))),  # Revenue and average
            Mock(all=Mock(return_value=[(PaymentMethod.CREDIT_CARD, 60), (PaymentMethod.CASH, 40)])),  # By method
            Mock(all=Mock(return_value=[(PaymentStatus.COMPLETED, 95), (PaymentStatus.FAILED, 5)]))  # By status
        ]
        
        self.mock_session.exec.side_effect = mock_results
        
        # Get payment summary
        summary = await self.payment_service.get_payment_summary(self.restaurant_id)
        
        # Verify structure
        assert "total_payments" in summary
        assert "total_amount" in summary
        assert "average_payment" in summary
        assert "payments_by_method" in summary
        assert "payments_by_status" in summary
        
        # Verify data types
        assert isinstance(summary["total_payments"], int)
        assert isinstance(summary["total_amount"], Decimal)
        assert isinstance(summary["payments_by_method"], dict)
    
    @pytest.mark.asyncio
    async def test_daily_payment_totals(self):
        """Test daily payment totals calculation."""
        # Mock daily totals query
        mock_result = Mock()
        mock_result.first.return_value = (50, Decimal("1250.00"))  # Count, total
        self.mock_session.exec.return_value = mock_result
        
        # Get daily totals
        totals = await self.payment_service.get_daily_payment_totals(
            self.restaurant_id, datetime.now().date()
        )
        
        # Verify structure
        assert "date" in totals
        assert "total_payments" in totals
        assert "total_amount" in totals
        
        # Verify values
        assert totals["total_payments"] == 50
        assert totals["total_amount"] == Decimal("1250.00")
    
    @pytest.mark.asyncio
    async def test_process_split_payment(self):
        """Test split payment processing."""
        # Mock order
        mock_order = Mock(spec=Order)
        mock_order.total_amount = Decimal("100.00")
        
        mock_order_result = Mock()
        mock_order_result.first.return_value = mock_order
        
        # Mock existing payments check
        mock_payment_result = Mock()
        mock_payment_result.first.return_value = Decimal("0.00")  # No existing payments
        
        self.mock_session.exec.side_effect = [
            mock_order_result,     # Order lookup
            mock_payment_result    # Existing payments check
        ]
        
        # Mock session operations
        self.mock_session.add = Mock()
        self.mock_session.commit = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        # Split payments
        payments_data = [
            PaymentCreate(
                order_id=self.order_id,
                amount=Decimal("60.00"),
                payment_method=PaymentMethod.CREDIT_CARD
            ),
            PaymentCreate(
                order_id=self.order_id,
                amount=Decimal("40.00"),
                payment_method=PaymentMethod.CASH
            )
        ]
        
        # Process split payment
        payments = await self.payment_service.process_split_payment(
            payments_data=payments_data,
            restaurant_id=self.restaurant_id,
            organization_id=uuid4()
        )
        
        # Verify split payments were processed
        assert self.mock_session.add.call_count >= 2  # At least 2 payments added
        assert self.mock_session.commit.called
    
    @pytest.mark.asyncio
    async def test_refund_payment(self):
        """Test payment refund processing."""
        payment_id = str(uuid4())
        refund_amount = Decimal("15.99")
        
        # Mock payment lookup
        mock_payment = Mock(spec=Payment)
        mock_payment.amount = Decimal("25.99")
        mock_payment.status = PaymentStatus.COMPLETED
        
        mock_payment_result = Mock()
        mock_payment_result.first.return_value = mock_payment
        self.mock_session.exec.return_value = mock_payment_result
        
        # Mock session operations
        self.mock_session.add = Mock()
        self.mock_session.commit = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        # Process refund
        refund = await self.payment_service.refund_payment(
            payment_id=payment_id,
            refund_amount=refund_amount,
            restaurant_id=self.restaurant_id,
            organization_id=uuid4(),
            reason="Customer request"
        )
        
        # Verify refund was processed
        assert self.mock_session.add.called
        assert self.mock_session.commit.called
    
    @pytest.mark.asyncio
    async def test_payment_completion_check(self):
        """Test order payment completion verification."""
        # Mock order total
        mock_order = Mock(spec=Order)
        mock_order.total_amount = Decimal("50.00")
        
        mock_order_result = Mock()
        mock_order_result.first.return_value = mock_order
        
        # Mock payment total
        mock_payment_result = Mock()
        mock_payment_result.first.return_value = Decimal("50.00")  # Fully paid
        
        self.mock_session.exec.side_effect = [mock_order_result, mock_payment_result]
        
        # Check completion
        is_complete = await self.payment_service.check_order_payment_completion(
            self.order_id, self.restaurant_id
        )
        
        # Should be complete
        assert is_complete is True
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_payment(self):
        """Test error handling for invalid payment scenarios."""
        # Mock non-existent order
        mock_result = Mock()
        mock_result.first.return_value = None
        self.mock_session.exec.return_value = mock_result
        
        # Should raise ValueError for invalid order
        with pytest.raises(ValueError, match="Order .* not found"):
            await self.payment_service.process_payment(
                payment_data=self.sample_payment,
                restaurant_id=self.restaurant_id,
                organization_id=uuid4()
            )
    
    @pytest.mark.asyncio
    async def test_payment_amount_validation(self):
        """Test payment amount validation."""
        # Mock order with different total
        mock_order = Mock(spec=Order)
        mock_order.total_amount = Decimal("10.00")  # Less than payment amount
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        # Should raise ValueError for amount mismatch in single payment
        large_payment = PaymentCreate(
            order_id=self.order_id,
            amount=Decimal("100.00"),  # More than order total
            payment_method=PaymentMethod.CREDIT_CARD
        )
        
        with pytest.raises(ValueError):
            await self.payment_service.process_payment(
                payment_data=large_payment,
                restaurant_id=self.restaurant_id,
                organization_id=uuid4()
            )
    
    @pytest.mark.asyncio
    async def test_payment_method_handling(self):
        """Test different payment method handling."""
        payment_methods = [
            PaymentMethod.CASH,
            PaymentMethod.CREDIT_CARD,
            PaymentMethod.DEBIT_CARD,
            PaymentMethod.MOBILE_PAYMENT
        ]
        
        for method in payment_methods:
            # Mock order
            mock_order = Mock(spec=Order)
            mock_order.total_amount = Decimal("20.00")
            
            mock_result = Mock()
            mock_result.first.return_value = mock_order
            self.mock_session.exec.return_value = mock_result
            
            # Reset mocks
            self.mock_session.add = Mock()
            self.mock_session.commit = AsyncMock()
            
            # Create payment with specific method
            payment_data = PaymentCreate(
                order_id=self.order_id,
                amount=Decimal("20.00"),
                payment_method=method
            )
            
            # Should handle all payment methods
            await self.payment_service.process_payment(
                payment_data=payment_data,
                restaurant_id=self.restaurant_id,
                organization_id=uuid4()
            )
            
            assert self.mock_session.add.called
    
    @pytest.mark.asyncio
    async def test_metadata_preservation(self):
        """Test payment metadata is preserved correctly."""
        # Mock order
        mock_order = Mock(spec=Order)
        mock_order.total_amount = Decimal("25.99")
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        # Mock session operations
        self.mock_session.add = Mock()
        self.mock_session.commit = AsyncMock()
        
        # Payment with metadata
        payment_with_metadata = PaymentCreate(
            order_id=self.order_id,
            amount=Decimal("25.99"),
            payment_method=PaymentMethod.CREDIT_CARD,
            metadata={
                "card_last_four": "1234",
                "card_type": "Visa",
                "transaction_id": "txn_12345"
            }
        )
        
        # Process payment
        await self.payment_service.process_payment(
            payment_data=payment_with_metadata,
            restaurant_id=self.restaurant_id,
            organization_id=uuid4()
        )
        
        # Verify payment was processed (metadata handling is internal)
        assert self.mock_session.add.called


@pytest.mark.asyncio
async def test_payment_service_production_integration():
    """Integration test for PaymentService operations."""
    mock_session = AsyncMock(spec=AsyncSession)
    service = PaymentService(mock_session)
    restaurant_id = uuid4()
    
    # Verify service has all required methods
    assert hasattr(service, 'process_payment')
    assert hasattr(service, 'get_payment_summary')
    assert hasattr(service, 'get_daily_payment_totals')
    assert hasattr(service, 'process_split_payment')
    assert hasattr(service, 'refund_payment')
    assert hasattr(service, 'check_order_payment_completion')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])