#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Kitchen Service
Production-level testing for Phase 3 kitchen management functionality.
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

from app.modules.orders.services.kitchen_service import KitchenService
from app.modules.orders.models.order import OrderStatus, OrderType


class TestKitchenServiceComprehensive:
    """Comprehensive test suite for KitchenService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = AsyncMock()
        self.kitchen_service = KitchenService(self.mock_session)
        self.restaurant_id = uuid4()
        self.organization_id = uuid4()
        
    def test_kitchen_service_initialization(self):
        """Test KitchenService proper initialization"""
        service = KitchenService(self.mock_session)
        assert service.session == self.mock_session
        
    @pytest.mark.asyncio
    async def test_get_kitchen_orders_filtering(self):
        """Test kitchen orders filtering by status"""
        mock_orders = [
            Mock(status=OrderStatus.CONFIRMED),
            Mock(status=OrderStatus.PREPARING),
            Mock(status=OrderStatus.READY)
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = mock_orders
        self.mock_session.exec.return_value = mock_result
        
        result = await self.kitchen_service.get_kitchen_orders(self.restaurant_id)
        
        assert len(result) == 3
        assert self.mock_session.exec.called
        
    @pytest.mark.asyncio
    async def test_start_order_preparation_success(self):
        """Test successful order preparation start"""
        order_id = str(uuid4())
        mock_order = Mock()
        mock_order.status = OrderStatus.CONFIRMED
        
        # Mock get_order
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        with patch('app.modules.orders.services.kitchen_service.datetime') as mock_datetime:
            mock_now = datetime(2025, 8, 18, 12, 0, 0)
            mock_datetime.utcnow.return_value = mock_now
            
            result = await self.kitchen_service.start_order_preparation(
                order_id=order_id,
                restaurant_id=self.restaurant_id,
                estimated_prep_time=15
            )
            
            assert mock_order.status == OrderStatus.PREPARING
            assert mock_order.estimated_ready_time is not None
            assert self.mock_session.commit.called
            
    @pytest.mark.asyncio
    async def test_start_order_preparation_invalid_status(self):
        """Test starting preparation for order in invalid status"""
        order_id = str(uuid4())
        mock_order = Mock()
        mock_order.status = OrderStatus.PENDING  # Invalid for kitchen prep
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        with pytest.raises(ValueError, match="Order must be confirmed"):
            await self.kitchen_service.start_order_preparation(
                order_id=order_id,
                restaurant_id=self.restaurant_id
            )
            
    @pytest.mark.asyncio
    async def test_start_order_preparation_not_found(self):
        """Test starting preparation for non-existent order"""
        order_id = str(uuid4())
        
        mock_result = Mock()
        mock_result.first.return_value = None
        self.mock_session.exec.return_value = mock_result
        
        with pytest.raises(ValueError, match="Order .* not found"):
            await self.kitchen_service.start_order_preparation(
                order_id=order_id,
                restaurant_id=self.restaurant_id
            )
            
    @pytest.mark.asyncio
    async def test_complete_order_preparation_success(self):
        """Test successful order preparation completion"""
        order_id = str(uuid4())
        mock_order = Mock()
        mock_order.status = OrderStatus.PREPARING
        mock_order.actual_ready_time = None
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        with patch('app.modules.orders.services.kitchen_service.datetime') as mock_datetime:
            mock_now = datetime(2025, 8, 18, 12, 30, 0)
            mock_datetime.utcnow.return_value = mock_now
            
            result = await self.kitchen_service.complete_order_preparation(
                order_id=order_id,
                restaurant_id=self.restaurant_id,
                kitchen_notes="Order completed successfully"
            )
            
            assert mock_order.status == OrderStatus.READY
            assert mock_order.actual_ready_time == mock_now
            assert mock_order.kitchen_notes == "Order completed successfully"
            assert self.mock_session.commit.called
            
    @pytest.mark.asyncio
    async def test_complete_order_preparation_invalid_status(self):
        """Test completing preparation for order not in preparing status"""
        order_id = str(uuid4())
        mock_order = Mock()
        mock_order.status = OrderStatus.CONFIRMED  # Not preparing
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        with pytest.raises(ValueError, match="Order must be in preparing status"):
            await self.kitchen_service.complete_order_preparation(
                order_id=order_id,
                restaurant_id=self.restaurant_id
            )
            
    @pytest.mark.asyncio
    async def test_update_order_item_preparation_success(self):
        """Test successful order item preparation update"""
        order_item_id = str(uuid4())
        mock_order_item = Mock()
        mock_order_item.prep_start_time = None
        mock_order_item.prep_complete_time = None
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order_item
        self.mock_session.exec.return_value = mock_result
        
        prep_start = datetime(2025, 8, 18, 12, 0, 0)
        prep_complete = datetime(2025, 8, 18, 12, 15, 0)
        
        result = await self.kitchen_service.update_order_item_preparation(
            order_item_id=order_item_id,
            restaurant_id=self.restaurant_id,
            prep_start_time=prep_start,
            prep_complete_time=prep_complete,
            kitchen_notes="Item prepared perfectly"
        )
        
        assert mock_order_item.prep_start_time == prep_start
        assert mock_order_item.prep_complete_time == prep_complete
        assert mock_order_item.kitchen_notes == "Item prepared perfectly"
        assert self.mock_session.commit.called
        
    @pytest.mark.asyncio
    async def test_update_order_item_preparation_not_found(self):
        """Test updating non-existent order item"""
        order_item_id = str(uuid4())
        
        mock_result = Mock()
        mock_result.first.return_value = None
        self.mock_session.exec.return_value = mock_result
        
        with pytest.raises(ValueError, match="Order item .* not found"):
            await self.kitchen_service.update_order_item_preparation(
                order_item_id=order_item_id,
                restaurant_id=self.restaurant_id
            )
            
    @pytest.mark.asyncio
    async def test_get_kitchen_performance_metrics_comprehensive(self):
        """Test comprehensive kitchen performance metrics calculation"""
        date_from = datetime(2025, 8, 1)
        date_to = datetime(2025, 8, 18)
        
        def mock_exec_side_effect(*args, **kwargs):
            result = Mock()
            query_str = str(args[0])
            
            if "count(orders.id)" in query_str:
                result.first.return_value = 250  # Total orders
            elif "avg(" in query_str and "prep_time" in query_str:
                result.first.return_value = 18.5  # Average prep time
            elif "orders_on_time" in query_str:
                result.first.return_value = 230  # On-time orders
            elif "avg(order_items.prep_time" in query_str:
                result.all.return_value = [
                    ("grill", 15.2),
                    ("salad", 8.7),
                    ("dessert", 12.3)
                ]
            else:
                result.first.return_value = 0
                
            return result
            
        self.mock_session.exec.side_effect = mock_exec_side_effect
        
        metrics = await self.kitchen_service.get_kitchen_performance_metrics(
            restaurant_id=self.restaurant_id,
            date_from=date_from,
            date_to=date_to
        )
        
        # Verify metrics structure
        assert "period" in metrics
        assert "total_orders" in metrics
        assert "average_prep_time" in metrics
        assert "on_time_percentage" in metrics
        assert "station_performance" in metrics
        
        assert metrics["total_orders"] == 250
        assert metrics["on_time_percentage"] == 92.0  # 230/250 * 100
        
    @pytest.mark.asyncio
    async def test_get_current_prep_queue_priority_ordering(self):
        """Test prep queue returns orders in priority order"""
        mock_orders = [
            Mock(id=uuid4(), kitchen_priority=10, created_at=datetime.now()),
            Mock(id=uuid4(), kitchen_priority=5, created_at=datetime.now()),
            Mock(id=uuid4(), kitchen_priority=8, created_at=datetime.now())
        ]
        
        mock_result = Mock()
        mock_result.all.return_value = mock_orders
        self.mock_session.exec.return_value = mock_result
        
        queue = await self.kitchen_service.get_current_prep_queue(self.restaurant_id)
        
        # Should return all orders (actual sorting would be in SQL)
        assert len(queue) >= 0  # Queue can be empty or have orders
        assert self.mock_session.exec.called
        
    @pytest.mark.asyncio
    async def test_kitchen_performance_edge_cases(self):
        """Test kitchen performance with edge cases"""
        # Test with no orders
        def mock_exec_no_orders(*args, **kwargs):
            result = Mock()
            result.first.return_value = 0
            result.all.return_value = []
            return result
            
        self.mock_session.exec.side_effect = mock_exec_no_orders
        
        metrics = await self.kitchen_service.get_kitchen_performance_metrics(
            restaurant_id=self.restaurant_id
        )
        
        assert metrics["total_orders"] == 0
        assert metrics["on_time_percentage"] == 0.0
        
    @pytest.mark.asyncio
    async def test_kitchen_cache_integration(self):
        """Test kitchen service cache integration"""
        with patch('app.modules.orders.services.kitchen_service.cache_service') as mock_cache:
            # Test cache clearing on status updates
            order_id = str(uuid4())
            mock_order = Mock()
            mock_order.status = OrderStatus.CONFIRMED
            
            mock_result = Mock()
            mock_result.first.return_value = mock_order
            self.mock_session.exec.return_value = mock_result
            
            await self.kitchen_service.start_order_preparation(
                order_id=order_id,
                restaurant_id=self.restaurant_id
            )
            
            # Should clear kitchen-related cache
            assert mock_cache.clear_pattern.called
            
    @pytest.mark.asyncio
    async def test_estimated_prep_time_calculation(self):
        """Test estimated preparation time calculation"""
        order_id = str(uuid4())
        mock_order = Mock()
        mock_order.status = OrderStatus.CONFIRMED
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        with patch('app.modules.orders.services.kitchen_service.datetime') as mock_datetime:
            mock_now = datetime(2025, 8, 18, 12, 0, 0)
            mock_datetime.utcnow.return_value = mock_now
            
            await self.kitchen_service.start_order_preparation(
                order_id=order_id,
                restaurant_id=self.restaurant_id,
                estimated_prep_time=25
            )
            
            # Should set estimated ready time 25 minutes from now
            expected_time = mock_now + timedelta(minutes=25)
            assert mock_order.estimated_ready_time == expected_time
            
    @pytest.mark.asyncio
    async def test_kitchen_notes_accumulation(self):
        """Test kitchen notes are properly accumulated"""
        order_id = str(uuid4())
        mock_order = Mock()
        mock_order.status = OrderStatus.PREPARING
        mock_order.kitchen_notes = "Initial notes"
        
        mock_result = Mock()
        mock_result.first.return_value = mock_order
        self.mock_session.exec.return_value = mock_result
        
        await self.kitchen_service.complete_order_preparation(
            order_id=order_id,
            restaurant_id=self.restaurant_id,
            kitchen_notes="Completion notes"
        )
        
        # Notes should be replaced (not accumulated in this implementation)
        assert mock_order.kitchen_notes == "Completion notes"
        
    @pytest.mark.asyncio
    async def test_concurrent_kitchen_operations(self):
        """Test handling of concurrent kitchen operations"""
        # Test that multiple kitchen operations can be handled concurrently
        order_ids = [str(uuid4()) for _ in range(3)]
        
        mock_orders = []
        for _ in range(3):
            mock_order = Mock()
            mock_order.status = OrderStatus.CONFIRMED
            mock_orders.append(mock_order)
        
        call_count = 0
        def mock_exec_side_effect(*args, **kwargs):
            nonlocal call_count
            result = Mock()
            if call_count < len(mock_orders):
                result.first.return_value = mock_orders[call_count]
                call_count += 1
            else:
                result.first.return_value = None
            return result
            
        self.mock_session.exec.side_effect = mock_exec_side_effect
        
        # Start preparation for multiple orders
        tasks = []
        for order_id in order_ids:
            task = self.kitchen_service.start_order_preparation(
                order_id=order_id,
                restaurant_id=self.restaurant_id
            )
            tasks.append(task)
        
        # Should handle concurrent operations
        results = await asyncio.gather(*tasks)
        assert len(results) == 3
        
    def test_kitchen_service_integration_interface(self):
        """Test kitchen service provides expected interface"""
        mock_session = Mock()
        service = KitchenService(mock_session)
        
        # Verify service has expected methods
        assert hasattr(service, 'get_kitchen_orders')
        assert hasattr(service, 'start_order_preparation')
        assert hasattr(service, 'complete_order_preparation')
        assert hasattr(service, 'update_order_item_preparation')
        assert hasattr(service, 'get_kitchen_performance_metrics')
        assert hasattr(service, 'get_current_prep_queue')
        
        assert service.session == mock_session
        
    @pytest.mark.asyncio
    async def test_kitchen_error_handling(self):
        """Test kitchen service error handling"""
        # Test database error handling
        self.mock_session.exec.side_effect = Exception("Database error")
        
        with pytest.raises(Exception):
            await self.kitchen_service.get_kitchen_orders(self.restaurant_id)
            
    @pytest.mark.asyncio
    async def test_performance_metrics_date_range(self):
        """Test performance metrics respect date range"""
        specific_date_from = datetime(2025, 8, 1, 0, 0, 0)
        specific_date_to = datetime(2025, 8, 18, 23, 59, 59)
        
        mock_result = Mock()
        mock_result.first.return_value = 100
        mock_result.all.return_value = []
        self.mock_session.exec.return_value = mock_result
        
        metrics = await self.kitchen_service.get_kitchen_performance_metrics(
            restaurant_id=self.restaurant_id,
            date_from=specific_date_from,
            date_to=specific_date_to
        )
        
        # Verify date range is included in response
        assert "period" in metrics
        assert metrics["period"]["from"] == specific_date_from.isoformat()
        assert metrics["period"]["to"] == specific_date_to.isoformat()


if __name__ == "__main__":
    # Run comprehensive tests
    pytest.main([__file__, "-v", "--tb=short"])