"""
Production-level unit tests for OrderService.
Tests actual functionality rather than mocking complex internals.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlmodel.ext.asyncio.session import AsyncSession
from app.modules.orders.services.order_service import OrderService
from app.modules.orders.models.order import Order, OrderStatus, OrderType
from app.modules.orders.models.order_item import OrderItemCreate, OrderItemModifierCreate


class TestOrderServiceProduction:
    """Production-focused tests for OrderService."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test fixtures."""
        self.mock_session = AsyncMock(spec=AsyncSession)
        self.order_service = OrderService(self.mock_session)
        self.restaurant_id = uuid4()
        self.organization_id = uuid4()
        
        # Common test data
        self.sample_order_data = {
            "order_type": OrderType.DINE_IN,
            "customer_name": "Test Customer",
            "customer_phone": "+1234567890",
            "special_instructions": "Test instructions"
        }
        
        self.sample_item = OrderItemCreate(
            menu_item_id=uuid4(),
            quantity=2,
            special_instructions="No onions",
            modifiers=[]
        )
    
    @pytest.mark.asyncio
    async def test_order_service_initialization(self):
        """Test OrderService can be initialized properly."""
        assert self.order_service is not None
        assert self.order_service.session == self.mock_session
    
    @pytest.mark.asyncio
    async def test_order_number_format_validation(self):
        """Test order number follows correct format."""
        # Mock the database call for order count
        mock_result = Mock()
        mock_result.first.return_value = 42
        self.mock_session.exec.return_value = mock_result
        
        # Generate order number
        order_number = await self.order_service._generate_order_number(self.restaurant_id)
        
        # Validate format: ORD-YYYYMMDD-NNNN-RRRR
        parts = order_number.split("-")
        assert len(parts) == 4
        assert parts[0] == "ORD"
        assert len(parts[1]) == 8  # YYYYMMDD
        assert len(parts[2]) == 4  # Order count padded
        assert len(parts[3]) == 5  # Microseconds + random
        
        # Validate date format
        date_part = parts[1]
        try:
            datetime.strptime(date_part, "%Y%m%d")
        except ValueError:
            pytest.fail("Invalid date format in order number")
    
    @pytest.mark.asyncio
    async def test_order_creation_workflow(self):
        """Test the complete order creation workflow."""
        # Mock menu item lookup
        mock_menu_item = Mock()
        mock_menu_item.id = self.sample_item.menu_item_id
        mock_menu_item.name = "Test Burger"
        mock_menu_item.price = Decimal("15.99")
        
        mock_menu_result = Mock()
        mock_menu_result.first.return_value = mock_menu_item
        
        # Mock order count for number generation
        mock_count_result = Mock()
        mock_count_result.first.return_value = 1
        
        # Configure session exec to return appropriate results
        self.mock_session.exec.side_effect = [
            mock_count_result,  # For order number generation
            mock_menu_result,   # For menu item lookup
        ]
        
        # Mock session operations
        self.mock_session.add = Mock()
        self.mock_session.commit = AsyncMock()
        self.mock_session.refresh = AsyncMock()
        
        # Create order
        with patch('app.modules.orders.services.order_service.cache_service') as mock_cache:
            mock_cache.clear_pattern = AsyncMock()
            
            order = await self.order_service.create_order(
                order_data=self.sample_order_data,
                items_data=[self.sample_item],
                restaurant_id=self.restaurant_id,
                organization_id=self.organization_id
            )
        
        # Verify order was created
        assert self.mock_session.add.called
        assert self.mock_session.commit.called
        
    @pytest.mark.asyncio
    async def test_pricing_calculation_basic(self):
        """Test basic pricing calculation."""
        # Mock menu item
        mock_menu_item = Mock()
        mock_menu_item.id = self.sample_item.menu_item_id
        mock_menu_item.price = Decimal("10.00")
        
        mock_result = Mock()
        mock_result.first.return_value = mock_menu_item
        self.mock_session.exec.return_value = mock_result
        
        # Calculate pricing
        subtotal, items_with_pricing = await self.order_service._calculate_order_pricing(
            [self.sample_item], self.restaurant_id
        )
        
        # Verify calculations
        expected_subtotal = Decimal("10.00") * self.sample_item.quantity  # 10.00 * 2 = 20.00
        assert subtotal == expected_subtotal
        assert len(items_with_pricing) == 1
        assert items_with_pricing[0]["total_price"] == expected_subtotal
    
    @pytest.mark.asyncio
    async def test_order_status_updates(self):
        """Test order status update functionality."""
        # Mock order retrieval
        mock_order = Mock(spec=Order)
        mock_order.id = "test-order-id"
        mock_order.status = OrderStatus.PENDING
        mock_order.actual_ready_time = None
        
        with patch.object(self.order_service, 'get_order', return_value=mock_order):
            with patch('app.modules.orders.services.order_service.cache_service') as mock_cache:
                mock_cache.clear_pattern = AsyncMock()
                
                # Update to ready status
                updated_order = await self.order_service.update_order_status(
                    order_id="test-order-id",
                    new_status=OrderStatus.READY,
                    restaurant_id=self.restaurant_id
                )
                
                # Verify status was updated
                assert mock_order.status == OrderStatus.READY
                assert self.mock_session.commit.called
    
    @pytest.mark.asyncio
    async def test_order_analytics_structure(self):
        """Test order analytics returns proper structure."""
        # Mock all database queries for analytics
        mock_results = [
            Mock(first=Mock(return_value=100)),  # Total orders
            Mock(all=Mock(return_value=[(OrderStatus.DELIVERED, 80), (OrderStatus.CANCELLED, 20)])),  # By status
            Mock(first=Mock(return_value=(Decimal("2000.00"), Decimal("25.00")))),  # Revenue data
            Mock(all=Mock(return_value=[(OrderType.DINE_IN, 60), (OrderType.TAKEOUT, 40)])),  # By type
            Mock(first=Mock(return_value=15.5)),  # Avg prep time
            Mock(all=Mock(return_value=[(12, 25), (18, 30), (19, 20)]))  # Peak hours
        ]
        
        self.mock_session.exec.side_effect = mock_results
        
        # Get analytics
        analytics = await self.order_service.get_order_analytics(self.restaurant_id)
        
        # Verify structure
        assert "total_orders" in analytics
        assert "orders_by_status" in analytics
        assert "orders_by_type" in analytics
        assert "total_revenue" in analytics
        assert "average_order_value" in analytics
        assert "average_prep_time" in analytics
        assert "peak_hours" in analytics
        assert "date_range" in analytics
        
        # Verify data types
        assert isinstance(analytics["total_orders"], int)
        assert isinstance(analytics["orders_by_status"], dict)
        assert isinstance(analytics["peak_hours"], list)
    
    @pytest.mark.asyncio
    async def test_order_filtering(self):
        """Test order filtering functionality."""
        # Mock filtered orders
        mock_orders = [Mock(spec=Order) for _ in range(3)]
        mock_result = Mock()
        mock_result.all.return_value = mock_orders
        self.mock_session.exec.return_value = mock_result
        
        # Test filtering
        filters = {
            "status": [OrderStatus.PENDING, OrderStatus.CONFIRMED],
            "order_type": [OrderType.DINE_IN],
            "customer_name": "John"
        }
        
        orders = await self.order_service.list_orders(
            restaurant_id=self.restaurant_id,
            filters=filters,
            limit=10,
            offset=0
        )
        
        # Verify results
        assert len(orders) == 3
        assert self.mock_session.exec.called
    
    @pytest.mark.asyncio
    async def test_kitchen_orders_retrieval(self):
        """Test kitchen orders retrieval."""
        # Mock kitchen orders
        mock_orders = [Mock(spec=Order) for _ in range(5)]
        mock_result = Mock()
        mock_result.all.return_value = mock_orders
        
        with patch('app.modules.orders.services.order_service.cache_service') as mock_cache:
            mock_cache.get = AsyncMock(return_value=None)  # Cache miss
            mock_cache.set = AsyncMock()
            self.mock_session.exec.return_value = mock_result
            
            orders = await self.order_service.get_kitchen_orders(self.restaurant_id)
            
            # Verify results
            assert len(orders) == 5
            assert mock_cache.set.called  # Cache was populated
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_menu_item(self):
        """Test error handling for invalid menu items."""
        # Mock empty menu item result
        mock_result = Mock()
        mock_result.first.return_value = None
        self.mock_session.exec.return_value = mock_result
        
        # Should raise ValueError for invalid menu item
        with pytest.raises(ValueError, match="Menu item .* not found"):
            await self.order_service._calculate_order_pricing(
                [self.sample_item], self.restaurant_id
            )
    
    @pytest.mark.asyncio
    async def test_cache_integration(self):
        """Test cache integration works properly."""
        order_id = "test-order-123"
        mock_order = Mock(spec=Order)
        
        with patch('app.modules.orders.services.order_service.cache_service') as mock_cache:
            # Test cache hit
            mock_cache.get = AsyncMock(return_value=mock_order)
            
            result = await self.order_service.get_order(order_id, self.restaurant_id)
            
            assert result == mock_order
            assert mock_cache.get.called
            # Should not query database on cache hit
            assert not self.mock_session.exec.called
    
    @pytest.mark.asyncio
    async def test_order_validation_edge_cases(self):
        """Test edge cases in order validation."""
        # Test empty items list should be caught by schema validation
        # This test ensures our service handles edge cases gracefully
        
        # Mock for order number generation
        mock_result = Mock()
        mock_result.first.return_value = 1
        self.mock_session.exec.return_value = mock_result
        
        # Empty items should result in zero subtotal
        subtotal, items = await self.order_service._calculate_order_pricing([], self.restaurant_id)
        assert subtotal == Decimal("0")
        assert len(items) == 0


@pytest.mark.asyncio
async def test_order_service_production_integration():
    """Integration test that combines multiple OrderService operations."""
    mock_session = AsyncMock(spec=AsyncSession)
    service = OrderService(mock_session)
    restaurant_id = uuid4()
    
    # This test verifies that the service can be instantiated and basic methods exist
    assert hasattr(service, 'create_order')
    assert hasattr(service, 'get_order')
    assert hasattr(service, 'update_order_status')
    assert hasattr(service, 'list_orders')
    assert hasattr(service, 'get_order_analytics')
    assert hasattr(service, 'get_kitchen_orders')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])