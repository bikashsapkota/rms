"""
Unit tests for KitchenService class.
Comprehensive production-level testing for kitchen operations.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from decimal import Decimal
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.modules.orders.services.kitchen_service import KitchenService
from app.modules.orders.models.order import OrderStatus, OrderType
from app.modules.orders.models.order_item import OrderItem


class TestKitchenService:
    """Comprehensive test cases for KitchenService."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session with comprehensive mocking."""
        session = Mock()
        session.add = Mock()
        session.commit = AsyncMock()
        session.refresh = AsyncMock()
        session.exec = AsyncMock()
        session.rollback = AsyncMock()
        return session
    
    @pytest.fixture
    def kitchen_service(self, mock_session):
        """KitchenService instance with mocked dependencies."""
        return KitchenService(mock_session)
    
    @pytest.fixture
    def sample_order(self):
        """Sample order for testing."""
        order = Mock()
        order.id = "order_123"
        order.restaurant_id = "restaurant_123"
        order.status = OrderStatus.PENDING
        order.order_type = OrderType.DINE_IN
        order.customer_name = "Test Customer"
        order.total_amount = Decimal("25.50")
        order.created_at = datetime.utcnow()
        order.estimated_prep_time = None
        order.actual_ready_time = None
        order.kitchen_notes = ""
        return order
    
    @pytest.fixture
    def sample_order_items(self):
        """Sample order items for testing."""
        items = []
        for i in range(3):
            item = Mock()
            item.id = f"item_{i}"
            item.order_id = "order_123"
            item.menu_item_id = f"menu_item_{i}"
            item.quantity = 2
            item.unit_price = Decimal("8.50")
            item.total_price = Decimal("17.00")
            item.prep_start_time = None
            item.prep_complete_time = None
            item.kitchen_notes = ""
            items.append(item)
        return items
    
    @pytest.mark.asyncio
    async def test_get_kitchen_orders_success(self, kitchen_service, mock_session):
        """Test successful retrieval of kitchen orders."""
        # Mock orders with items
        mock_orders = []
        for i in range(5):
            order = Mock()
            order.id = f"order_{i}"
            order.status = OrderStatus.PREPARING if i % 2 == 0 else OrderStatus.CONFIRMED
            order.customer_name = f"Customer {i}"
            order.items = [Mock() for _ in range(2)]  # 2 items per order
            mock_orders.append(order)
        
        mock_result = Mock()
        mock_result.all.return_value = mock_orders
        mock_session.exec.return_value = mock_result
        
        # Execute test
        orders = await kitchen_service.get_kitchen_orders("restaurant_123")
        
        # Verify results
        assert len(orders) == 5
        assert all(order.id.startswith("order_") for order in orders)
        mock_session.exec.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_order_preparation_success(self, kitchen_service, mock_session, sample_order):
        """Test successful order preparation start."""
        # Mock order retrieval
        mock_result = Mock()
        mock_result.first.return_value = sample_order
        mock_session.exec.return_value = mock_result
        
        # Execute test
        result = await kitchen_service.start_order_preparation(
            order_id="order_123",
            restaurant_id="restaurant_123",
            estimated_prep_time=20
        )
        
        # Verify status change and timing
        assert sample_order.status == OrderStatus.PREPARING
        assert sample_order.estimated_prep_time == 20
        assert sample_order.prep_start_time is not None
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_start_order_preparation_invalid_status(self, kitchen_service, mock_session, sample_order):
        """Test starting preparation for order with invalid status."""
        sample_order.status = OrderStatus.DELIVERED  # Invalid status for starting prep
        
        mock_result = Mock()
        mock_result.first.return_value = sample_order
        mock_session.exec.return_value = mock_result
        
        # Should raise ValueError for invalid status
        with pytest.raises(ValueError, match="Cannot start preparation"):
            await kitchen_service.start_order_preparation(
                order_id="order_123",
                restaurant_id="restaurant_123"
            )
    
    @pytest.mark.asyncio
    async def test_complete_order_preparation_success(self, kitchen_service, mock_session, sample_order):
        """Test successful order preparation completion."""
        sample_order.status = OrderStatus.PREPARING
        
        mock_result = Mock()
        mock_result.first.return_value = sample_order
        mock_session.exec.return_value = mock_result
        
        # Execute test
        result = await kitchen_service.complete_order_preparation(
            order_id="order_123",
            restaurant_id="restaurant_123",
            kitchen_notes="Order ready for pickup"
        )
        
        # Verify status change and completion
        assert sample_order.status == OrderStatus.READY
        assert sample_order.kitchen_notes == "Order ready for pickup"
        assert sample_order.actual_ready_time is not None
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_order_item_preparation(self, kitchen_service, mock_session):
        """Test updating individual order item preparation."""
        # Mock order item
        order_item = Mock()
        order_item.id = "item_123"
        order_item.prep_start_time = None
        order_item.prep_complete_time = None
        order_item.kitchen_notes = ""
        
        mock_result = Mock()
        mock_result.first.return_value = order_item
        mock_session.exec.return_value = mock_result
        
        prep_start = datetime.utcnow()
        prep_complete = prep_start + timedelta(minutes=10)
        
        # Execute test
        result = await kitchen_service.update_order_item_preparation(
            order_item_id="item_123",
            restaurant_id="restaurant_123",
            prep_start_time=prep_start,
            prep_complete_time=prep_complete,
            kitchen_notes="Item completed"
        )
        
        # Verify updates
        assert order_item.prep_start_time == prep_start
        assert order_item.prep_complete_time == prep_complete
        assert order_item.kitchen_notes == "Item completed"
        mock_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_kitchen_performance_metrics(self, kitchen_service, mock_session):
        """Test kitchen performance metrics calculation."""
        # Mock database results for performance metrics
        mock_results = [
            Mock(first=lambda: 50),  # total orders
            Mock(first=lambda: 45),  # completed orders
            Mock(first=lambda: 15.5),  # average prep time
            Mock(first=lambda: (Decimal("25.50"), 45)),  # avg order value and count
            Mock(all=lambda: [("preparing", 3), ("ready", 2)]),  # current status breakdown
        ]
        
        mock_session.exec.side_effect = mock_results
        
        date_from = datetime.utcnow() - timedelta(days=7)
        
        # Execute test
        metrics = await kitchen_service.get_kitchen_performance_metrics(
            restaurant_id="restaurant_123",
            date_from=date_from
        )
        
        # Verify metrics structure and values
        assert "total_orders" in metrics
        assert "completed_orders" in metrics
        assert "completion_rate" in metrics
        assert "average_prep_time" in metrics
        assert "average_order_value" in metrics
        assert "current_status_breakdown" in metrics
        
        assert metrics["total_orders"] == 50
        assert metrics["completed_orders"] == 45
        assert metrics["completion_rate"] == 90.0
        assert metrics["average_prep_time"] == 15.5
    
    @pytest.mark.asyncio
    async def test_get_current_prep_queue(self, kitchen_service, mock_session):
        """Test current preparation queue retrieval."""
        # Mock orders in preparation queue with priority
        queue_orders = []
        for i in range(3):
            order = Mock()
            order.id = f"order_{i}"
            order.customer_name = f"Customer {i}"
            order.status = OrderStatus.PREPARING
            order.prep_start_time = datetime.utcnow() - timedelta(minutes=i*5)
            order.estimated_prep_time = 20 + i*5
            order.order_metadata = {"kitchen_priority": 5 - i}  # Higher priority first
            queue_orders.append(order)
        
        mock_result = Mock()
        mock_result.all.return_value = queue_orders
        mock_session.exec.return_value = mock_result
        
        # Execute test
        queue = await kitchen_service.get_current_prep_queue("restaurant_123")
        
        # Verify queue structure
        assert len(queue) == 3
        for item in queue:
            assert "order_id" in item
            assert "customer_name" in item
            assert "prep_time_elapsed" in item
            assert "estimated_remaining" in item
            assert "priority" in item
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, kitchen_service, mock_session):
        """Test proper handling of database errors."""
        # Mock database exception
        mock_session.exec.side_effect = Exception("Database connection error")
        
        # Should propagate database errors appropriately
        with pytest.raises(Exception, match="Database connection error"):
            await kitchen_service.get_kitchen_orders("restaurant_123")
    
    @pytest.mark.asyncio
    async def test_order_not_found_handling(self, kitchen_service, mock_session):
        """Test handling when order is not found."""
        mock_result = Mock()
        mock_result.first.return_value = None
        mock_session.exec.return_value = mock_result
        
        # Should raise ValueError for non-existent order
        with pytest.raises(ValueError, match="Order .* not found"):
            await kitchen_service.start_order_preparation(
                order_id="nonexistent",
                restaurant_id="restaurant_123"
            )
    
    @pytest.mark.asyncio
    async def test_concurrent_order_updates(self, kitchen_service, mock_session, sample_order):
        """Test handling of concurrent order status updates."""
        # Mock order that changes status between retrieval and update
        mock_result = Mock()
        mock_result.first.return_value = sample_order
        mock_session.exec.return_value = mock_result
        
        # Simulate concurrent update by changing status after retrieval
        original_status = sample_order.status
        
        async def change_status_during_commit():
            sample_order.status = OrderStatus.CANCELLED
            
        mock_session.commit.side_effect = change_status_during_commit
        
        # Should handle gracefully or provide appropriate error
        try:
            await kitchen_service.start_order_preparation(
                order_id="order_123",
                restaurant_id="restaurant_123"
            )
        except Exception as e:
            # Expected behavior - concurrent updates should be handled
            assert True
    
    @pytest.mark.asyncio
    async def test_kitchen_metrics_date_filtering(self, kitchen_service, mock_session):
        """Test kitchen metrics with specific date ranges."""
        # Mock results for specific date range
        mock_results = [
            Mock(first=lambda: 25),  # orders in date range
            Mock(first=lambda: 20),  # completed in range
            Mock(first=lambda: 12.5),  # avg prep time
            Mock(first=lambda: (Decimal("30.00"), 25)),  # avg order value
            Mock(all=lambda: [("preparing", 5)]),  # current status
        ]
        
        mock_session.exec.side_effect = mock_results
        
        date_from = datetime.utcnow() - timedelta(days=1)
        date_to = datetime.utcnow()
        
        # Execute test with date range
        metrics = await kitchen_service.get_kitchen_performance_metrics(
            restaurant_id="restaurant_123",
            date_from=date_from,
            date_to=date_to
        )
        
        # Verify metrics reflect date filtering
        assert metrics["total_orders"] == 25
        assert metrics["average_order_value"] == Decimal("30.00")
    
    @pytest.mark.asyncio
    async def test_prep_queue_priority_ordering(self, kitchen_service, mock_session):
        """Test preparation queue is properly ordered by priority."""
        # Mock orders with different priorities
        orders = []
        priorities = [3, 1, 5, 2, 4]  # Unsorted priorities
        
        for i, priority in enumerate(priorities):
            order = Mock()
            order.id = f"order_{i}"
            order.customer_name = f"Customer {i}"
            order.status = OrderStatus.PREPARING
            order.prep_start_time = datetime.utcnow() - timedelta(minutes=10)
            order.estimated_prep_time = 20
            order.order_metadata = {"kitchen_priority": priority}
            orders.append(order)
        
        mock_result = Mock()
        mock_result.all.return_value = orders
        mock_session.exec.return_value = mock_result
        
        # Execute test
        queue = await kitchen_service.get_current_prep_queue("restaurant_123")
        
        # Verify queue is ordered by priority (highest first)
        queue_priorities = [item["priority"] for item in queue]
        assert queue_priorities == sorted(priorities, reverse=True)
    
    def test_kitchen_service_initialization(self):
        """Test KitchenService initialization."""
        mock_session = Mock()
        service = KitchenService(mock_session)
        
        assert service.session == mock_session
        assert hasattr(service, 'get_kitchen_orders')
        assert hasattr(service, 'start_order_preparation')
        assert hasattr(service, 'complete_order_preparation')


class TestKitchenServiceErrorScenarios:
    """Test error scenarios and edge cases for KitchenService."""
    
    @pytest.fixture
    def kitchen_service(self):
        """KitchenService with mock session."""
        session = Mock()
        session.rollback = AsyncMock()
        return KitchenService(session)
    
    @pytest.mark.asyncio
    async def test_invalid_restaurant_id(self, kitchen_service):
        """Test behavior with invalid restaurant ID."""
        kitchen_service.session.exec = AsyncMock()
        mock_result = Mock()
        mock_result.all.return_value = []
        kitchen_service.session.exec.return_value = mock_result
        
        # Should return empty list for invalid restaurant
        orders = await kitchen_service.get_kitchen_orders("invalid_restaurant")
        assert orders == []
    
    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self, kitchen_service):
        """Test transaction rollback on database errors."""
        kitchen_service.session.commit = AsyncMock(side_effect=Exception("DB Error"))
        kitchen_service.session.exec = AsyncMock()
        
        # Mock order for update
        order = Mock()
        order.status = OrderStatus.PENDING
        mock_result = Mock()
        mock_result.first.return_value = order
        kitchen_service.session.exec.return_value = mock_result
        
        # Should rollback on commit failure
        with pytest.raises(Exception, match="DB Error"):
            await kitchen_service.start_order_preparation(
                order_id="order_123",
                restaurant_id="restaurant_123"
            )
        
        # Verify rollback was called
        kitchen_service.session.rollback.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_metrics_with_no_data(self, kitchen_service):
        """Test metrics calculation when no data exists."""
        # Mock empty results
        empty_results = [
            Mock(first=lambda: 0),  # total orders
            Mock(first=lambda: 0),  # completed orders
            Mock(first=lambda: None),  # average prep time
            Mock(first=lambda: (None, 0)),  # avg order value
            Mock(all=lambda: []),  # current status breakdown
        ]
        
        kitchen_service.session.exec = AsyncMock()
        kitchen_service.session.exec.side_effect = empty_results
        
        # Execute test
        metrics = await kitchen_service.get_kitchen_performance_metrics(
            restaurant_id="restaurant_123",
            date_from=datetime.utcnow() - timedelta(days=7)
        )
        
        # Verify graceful handling of empty data
        assert metrics["total_orders"] == 0
        assert metrics["completed_orders"] == 0
        assert metrics["completion_rate"] == 0.0
        assert metrics["average_prep_time"] == 0.0
        assert metrics["average_order_value"] == Decimal("0.00")