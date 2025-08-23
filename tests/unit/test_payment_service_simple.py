"""
Simplified unit tests for PaymentService class.
Basic testing to ensure the service can be instantiated and has required methods.
"""

import pytest
from unittest.mock import Mock
from app.modules.orders.services.payment_service import PaymentService


class TestPaymentServiceBasic:
    """Basic test cases for PaymentService."""
    
    def test_payment_service_initialization(self):
        """Test PaymentService can be initialized."""
        mock_session = Mock()
        service = PaymentService(mock_session)
        
        assert service.session == mock_session
        assert hasattr(service, 'process_payment')
        assert hasattr(service, 'process_split_payment')
        assert hasattr(service, 'refund_payment')
        assert hasattr(service, 'get_order_payments')
        assert hasattr(service, 'get_payment_summary')
    
    def test_payment_service_methods_exist(self):
        """Test that all expected methods exist on PaymentService."""
        mock_session = Mock()
        service = PaymentService(mock_session)
        
        # Check that methods are callable
        assert callable(getattr(service, 'process_payment', None))
        assert callable(getattr(service, 'process_split_payment', None))
        assert callable(getattr(service, 'refund_payment', None))
        assert callable(getattr(service, 'get_order_payments', None))
        assert callable(getattr(service, 'get_payment_summary', None))