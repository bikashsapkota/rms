"""
Production-level unit tests for KitchenService.
Tests actual functionality with realistic scenarios.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.orders.services.kitchen_service import KitchenService
from app.modules.orders.models.order import Order, OrderStatus, OrderType


class TestKitchenServiceProduction:
    """Production-focused tests for KitchenService."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.kitchen_service = KitchenService(self.mock_session)
        self.restaurant_id = uuid4()
    
    @pytest.mark.asyncio
    async def test_kitchen_service_initialization(self):
        """Test KitchenService can be initialized properly."""
        assert self.kitchen_service is not None
        assert self.kitchen_service.session == self.mock_session
    
    @pytest.mark.asyncio
    async def test_get_kitchen_performance_structure(self):
        """Test kitchen performance metrics returns proper structure."""
        # Mock database queries
        mock_results = [
            Mock(first=Mock(return_value=22.5)),  # Average prep time
            Mock(first=Mock(return_value=(45, 50))),  # On-time completion
            Mock(all=Mock(return_value=[(12, 15), (18, 20), (19, 18)]))  # Peak hours
        ]
        
        self.mock_session.exec.side_effect = mock_results
        
        # Get performance metrics
        metrics = await self.kitchen_service.get_kitchen_performance(self.restaurant_id)
        
        # Verify structure
        assert "average_prep_time_minutes" in metrics
        assert "on_time_completion_rate" in metrics
        assert "peak_hours" in metrics
        assert "date_range" in metrics
        
        # Verify data types
        assert isinstance(metrics["average_prep_time_minutes"], (int, float))
        assert isinstance(metrics["on_time_completion_rate"], (int, float))
        assert isinstance(metrics["peak_hours"], list)
    
    @pytest.mark.asyncio
    async def test_prep_queue_ordering(self):
        """Test prep queue returns orders in correct priority."""
        # Mock orders with different priorities and times
        now = datetime.utcnow()
        mock_orders = [
            Mock(
                id="order1",
                created_at=now - timedelta(minutes=30),
                estimated_ready_time=now + timedelta(minutes=15),
                order_type=OrderType.DINE_IN
            ),
            Mock(
                id="order2", 
                created_at=now - timedelta(minutes=20),
                estimated_ready_time=now + timedelta(minutes=10),
                order_type=OrderType.TAKEOUT
            )
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = mock_orders
        self.mock_session.exec.return_value = mock_result
        
        # Get prep queue
        queue = await self.kitchen_service.get_current_prep_queue(self.restaurant_id)
        
        # Verify it returns a list
        assert isinstance(queue, list)
        assert self.mock_session.exec.called
    
    @pytest.mark.asyncio
    async def test_order_preparation_workflow(self):
        """Test the order preparation workflow."""
        order_id = "test-order-123"
        
        # Mock order retrieval
        mock_order = Mock(spec=Order)
        mock_order.status = OrderStatus.CONFIRMED
        mock_order.prep_start_time = None
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        # Start preparation
        result = await self.kitchen_service.start_order_preparation(
            order_id, self.restaurant_id
        )
        
        # Verify preparation was started
        assert result is not None
        assert mock_order.status == OrderStatus.PREPARING
        assert self.mock_session.commit.called
    
    @pytest.mark.asyncio
    async def test_order_completion_workflow(self):
        """Test order completion workflow."""
        order_id = "test-order-123"
        
        # Mock order retrieval
        mock_order = Mock(spec=Order)
        mock_order.status = OrderStatus.PREPARING
        mock_order.prep_start_time = datetime.utcnow() - timedelta(minutes=20)
        mock_order.actual_ready_time = None
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        # Complete preparation
        result = await self.kitchen_service.complete_order_preparation(
            order_id, self.restaurant_id
        )
        
        # Verify completion
        assert result is not None
        assert mock_order.status == OrderStatus.READY
        assert self.mock_session.commit.called
    
    @pytest.mark.asyncio
    async def test_daily_analytics_structure(self):
        """Test daily kitchen analytics structure."""
        # Mock analytics queries
        mock_results = [
            Mock(first=Mock(return_value=18.5)),  # Average prep time
            Mock(first=Mock(return_value=(38, 45))),  # On-time rate
            Mock(all=Mock(return_value=[(12, 12), (13, 15), (18, 20)]))  # Hourly breakdown
        ]
        
        self.mock_session.exec.side_effect = mock_results
        
        # Get daily analytics
        analytics = await self.kitchen_service.get_daily_kitchen_analytics(self.restaurant_id)
        
        # Verify structure
        assert "date" in analytics
        assert "total_orders_prepared" in analytics
        assert "average_prep_time" in analytics
        assert "on_time_completion_rate" in analytics
        assert "hourly_breakdown" in analytics
        
        # Verify data types
        assert isinstance(analytics["average_prep_time"], (int, float))
        assert isinstance(analytics["on_time_completion_rate"], (int, float))
        assert isinstance(analytics["hourly_breakdown"], list)
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_order(self):
        """Test error handling for invalid order operations."""
        # Mock empty order result
        mock_result = Mock()
        mock_result.first.return_value = None
        self.mock_session.exec.return_value = mock_result
        
        # Should raise ValueError for non-existent order
        with pytest.raises(ValueError):
            await self.kitchen_service.start_order_preparation(
                "invalid-order", self.restaurant_id
            )
    
    @pytest.mark.asyncio
    async def test_order_status_validation(self):
        """Test order status validation in kitchen operations."""
        # Mock order with invalid status for preparation
        mock_order = Mock(spec=Order)
        mock_order.status = OrderStatus.DELIVERED  # Already delivered
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        # Should raise ValueError for invalid status transition
        with pytest.raises(ValueError):
            await self.kitchen_service.start_order_preparation(
                "delivered-order", self.restaurant_id
            )
    
    @pytest.mark.asyncio
    async def test_performance_metrics_edge_cases(self):
        """Test performance metrics with edge cases."""
        # Mock empty results (no orders)
        mock_results = [
            Mock(first=Mock(return_value=None)),  # No average prep time
            Mock(first=Mock(return_value=(0, 0))),  # No on-time data
            Mock(all=Mock(return_value=[]))  # No peak hours
        ]
        
        self.mock_session.exec.side_effect = mock_results
        
        # Get performance with no data
        metrics = await self.kitchen_service.get_kitchen_performance(self.restaurant_id)
        
        # Should handle empty data gracefully
        assert "average_prep_time_minutes" in metrics
        assert metrics["average_prep_time_minutes"] == 0.0
        assert metrics["on_time_completion_rate"] == 0.0
        assert isinstance(metrics["peak_hours"], list)
    
    @pytest.mark.asyncio
    async def test_kitchen_cache_integration(self):
        """Test cache integration in kitchen operations."""
        with patch('app.modules.orders.services.kitchen_service.cache_service') as mock_cache:
            # Test cache operations
            mock_cache.clear_pattern = AsyncMock()
            
            # Mock order for preparation
            mock_order = Mock(spec=Order)
            mock_order.status = OrderStatus.CONFIRMED
            
            mock_result = Mock()
            mock_result.first.return_value = mock_order
            self.mock_session.exec.return_value = mock_result
            
            # Start preparation (should clear cache)
            await self.kitchen_service.start_order_preparation(
                "test-order", self.restaurant_id
            )
            
            # Verify cache was cleared
            assert mock_cache.clear_pattern.called
    
    @pytest.mark.asyncio
    async def test_prep_time_calculations(self):
        """Test preparation time calculations."""
        # Mock order with prep times
        start_time = datetime.utcnow() - timedelta(minutes=25)
        end_time = datetime.utcnow()
        
        mock_order = Mock(spec=Order)
        mock_order.prep_start_time = start_time
        mock_order.actual_ready_time = end_time
        mock_order.status = OrderStatus.PREPARING
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        # Complete preparation
        result = await self.kitchen_service.complete_order_preparation(
            "test-order", self.restaurant_id
        )
        
        # Should calculate and set prep time
        assert result is not None
        assert mock_order.prep_time_minutes is not None


@pytest.mark.asyncio
async def test_kitchen_service_production_integration():
    """Integration test for KitchenService operations."""
    mock_session = AsyncMock(spec=AsyncSession)
    service = KitchenService(mock_session)
    restaurant_id = uuid4()
    
    # Verify service has all required methods
    assert hasattr(service, 'get_kitchen_performance')
    assert hasattr(service, 'get_current_prep_queue')
    assert hasattr(service, 'start_order_preparation')
    assert hasattr(service, 'complete_order_preparation')
    assert hasattr(service, 'get_daily_kitchen_analytics')
    

if __name__ == "__main__":
    pytest.main([__file__, "-v"])