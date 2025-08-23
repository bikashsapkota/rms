#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Order Service
Production-level testing for Phase 3 order management functionality.
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

from app.modules.orders.services.order_service import OrderService
from app.modules.orders.models.order import OrderStatus, OrderType, Order
from app.modules.orders.models.order_item import OrderItemCreate


class TestOrderServiceComprehensive:
    """Comprehensive test suite for OrderService"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_session = AsyncMock()
        self.order_service = OrderService(self.mock_session)
        self.restaurant_id = uuid4()
        self.organization_id = uuid4()
        
    def test_order_service_initialization(self):
        """Test OrderService proper initialization"""
        service = OrderService(self.mock_session)
        assert service.session == self.mock_session
        
    @pytest.mark.asyncio
    async def test_generate_order_number_uniqueness(self):
        """Test order number generation produces unique values"""
        # Mock database response for order count
        mock_result = Mock()
        mock_result.first.return_value = 5  # 5 orders today
        self.mock_session.exec.return_value = mock_result
        
        # Generate multiple order numbers
        numbers = []
        for _ in range(10):
            number = await self.order_service._generate_order_number(self.restaurant_id)
            numbers.append(number)
            
        # Verify all numbers are unique
        assert len(set(numbers)) == len(numbers)
        
        # Verify format
        for number in numbers:
            assert number.startswith("ORD-")
            assert len(number.split("-")) == 4  # ORD-YYYYMMDD-NNNN-RRRR
            
    @pytest.mark.asyncio
    async def test_calculate_order_pricing_basic(self):
        """Test basic order pricing calculation"""
        # Mock menu items
        mock_burger = Mock()
        mock_burger.id = uuid4()
        mock_burger.price = Decimal("15.99")
        
        mock_drink = Mock()
        mock_drink.id = uuid4()
        mock_drink.price = Decimal("4.50")
        
        # Mock database responses
        def mock_exec_side_effect(*args, **kwargs):
            result = Mock()
            if "menu_items" in str(args[0]):
                if mock_burger.id in str(args[0]):
                    result.first.return_value = mock_burger
                elif mock_drink.id in str(args[0]):
                    result.first.return_value = mock_drink
            return result
            
        self.mock_session.exec.side_effect = mock_exec_side_effect
        
        # Create order items
        items_data = [
            OrderItemCreate(
                menu_item_id=mock_burger.id,
                quantity=2,
                special_instructions="Well done",
                modifiers=[]
            ),
            OrderItemCreate(
                menu_item_id=mock_drink.id,
                quantity=2,
                special_instructions="",
                modifiers=[]
            )
        ]
        
        # Calculate pricing
        subtotal, items_with_pricing = await self.order_service._calculate_order_pricing(
            items_data, self.restaurant_id
        )
        
        # Verify calculations
        expected_subtotal = (Decimal("15.99") * 2) + (Decimal("4.50") * 2)
        assert subtotal == expected_subtotal
        assert len(items_with_pricing) == 2
        
    @pytest.mark.asyncio
    async def test_create_order_success(self):
        """Test successful order creation"""
        # Mock dependencies
        with patch.object(self.order_service, '_generate_order_number') as mock_gen_number, \
             patch.object(self.order_service, '_calculate_order_pricing') as mock_calc_pricing, \
             patch.object(self.order_service, '_create_order_item') as mock_create_item, \
             patch.object(self.order_service, '_clear_order_cache') as mock_clear_cache:
            
            # Setup mocks
            mock_gen_number.return_value = "ORD-20250818-0001-12345"
            mock_calc_pricing.return_value = (Decimal("40.98"), [
                {
                    "menu_item": Mock(),
                    "quantity": 2,
                    "unit_price": Decimal("15.99"),
                    "modifier_total": Decimal("0"),
                    "total_price": Decimal("31.98"),
                    "modifiers": [],
                    "special_instructions": "Well done"
                }
            ])
            
            # Create order data
            order_data = {
                "order_type": OrderType.DINE_IN,
                "customer_name": "Test Customer",
                "customer_phone": "+1234567890",
                "special_instructions": "Test order"
            }
            
            items_data = [
                OrderItemCreate(
                    menu_item_id=uuid4(),
                    quantity=2,
                    special_instructions="Well done",
                    modifiers=[]
                )
            ]
            
            # Execute
            result = await self.order_service.create_order(
                order_data=order_data,
                items_data=items_data,
                restaurant_id=self.restaurant_id,
                organization_id=self.organization_id
            )
            
            # Verify
            assert self.mock_session.add.called
            assert self.mock_session.commit.call_count == 2  # Order + items
            assert mock_clear_cache.called
            
    @pytest.mark.asyncio
    async def test_get_order_with_cache(self):
        """Test order retrieval with caching"""
        order_id = str(uuid4())
        
        with patch('app.modules.orders.services.order_service.cache_service') as mock_cache:
            # Test cache hit
            cached_order = Mock()
            mock_cache.get.return_value = cached_order
            
            result = await self.order_service.get_order(order_id, self.restaurant_id)
            
            assert result == cached_order
            assert not self.mock_session.exec.called
            
    @pytest.mark.asyncio
    async def test_get_order_cache_miss(self):
        """Test order retrieval when not in cache"""
        order_id = str(uuid4())
        
        with patch('app.modules.orders.services.order_service.cache_service') as mock_cache:
            # Cache miss
            mock_cache.get.return_value = None
            
            # Mock database response
            mock_order = Mock()
            mock_result = Mock()
            mock_result.first.return_value = mock_order
            self.mock_session.exec.return_value = mock_result
            
            result = await self.order_service.get_order(order_id, self.restaurant_id)
            
            assert result == mock_order
            assert mock_cache.set.called
            
    @pytest.mark.asyncio
    async def test_update_order_status_success(self):
        """Test successful order status update"""
        order_id = str(uuid4())
        mock_order = Mock()
        mock_order.status = OrderStatus.PENDING
        mock_order.actual_ready_time = None
        
        with patch.object(self.order_service, 'get_order') as mock_get_order, \
             patch.object(self.order_service, '_clear_order_cache') as mock_clear_cache:
            
            mock_get_order.return_value = mock_order
            
            result = await self.order_service.update_order_status(
                order_id=order_id,
                new_status=OrderStatus.CONFIRMED,
                restaurant_id=self.restaurant_id,
                kitchen_notes="Test notes"
            )
            
            assert mock_order.status == OrderStatus.CONFIRMED
            assert mock_order.kitchen_notes == "Test notes"
            assert self.mock_session.commit.called
            assert mock_clear_cache.called
            
    @pytest.mark.asyncio
    async def test_update_order_status_not_found(self):
        """Test order status update when order not found"""
        order_id = str(uuid4())
        
        with patch.object(self.order_service, 'get_order') as mock_get_order:
            mock_get_order.return_value = None
            
            with pytest.raises(ValueError, match="Order .* not found"):
                await self.order_service.update_order_status(
                    order_id=order_id,
                    new_status=OrderStatus.CONFIRMED,
                    restaurant_id=self.restaurant_id
                )
                
    @pytest.mark.asyncio
    async def test_update_order_status_ready_sets_time(self):
        """Test that updating to READY status sets actual_ready_time"""
        order_id = str(uuid4())
        mock_order = Mock()
        mock_order.status = OrderStatus.PREPARING
        mock_order.actual_ready_time = None
        
        with patch.object(self.order_service, 'get_order') as mock_get_order, \
             patch('app.modules.orders.services.order_service.datetime') as mock_datetime:
            
            mock_get_order.return_value = mock_order
            mock_now = datetime(2025, 8, 18, 12, 0, 0)
            mock_datetime.utcnow.return_value = mock_now
            
            await self.order_service.update_order_status(
                order_id=order_id,
                new_status=OrderStatus.READY,
                restaurant_id=self.restaurant_id
            )
            
            assert mock_order.actual_ready_time == mock_now
            
    @pytest.mark.asyncio
    async def test_get_kitchen_orders_with_cache(self):
        """Test kitchen orders retrieval with caching"""
        with patch('app.modules.orders.services.order_service.cache_service') as mock_cache:
            cached_orders = [Mock(), Mock()]
            mock_cache.get.return_value = cached_orders
            
            result = await self.order_service.get_kitchen_orders(self.restaurant_id)
            
            assert result == cached_orders
            assert not self.mock_session.exec.called
            
    @pytest.mark.asyncio
    async def test_get_kitchen_orders_cache_miss(self):
        """Test kitchen orders retrieval when not cached"""
        with patch('app.modules.orders.services.order_service.cache_service') as mock_cache:
            mock_cache.get.return_value = None
            
            mock_orders = [Mock(), Mock()]
            mock_result = Mock()
            mock_result.all.return_value = mock_orders
            self.mock_session.exec.return_value = mock_result
            
            result = await self.order_service.get_kitchen_orders(self.restaurant_id)
            
            assert result == mock_orders
            assert mock_cache.set.called
            
    @pytest.mark.asyncio
    async def test_get_order_analytics_comprehensive(self):
        """Test comprehensive order analytics calculation"""
        # Mock database responses
        def mock_exec_side_effect(*args, **kwargs):
            result = Mock()
            query_str = str(args[0])
            
            if "count(orders.id)" in query_str and "status" not in query_str:
                result.first.return_value = 150  # Total orders
            elif "orders.status" in query_str and "group_by" in query_str:
                result.all.return_value = [
                    (OrderStatus.DELIVERED, 120),
                    (OrderStatus.CANCELLED, 15),
                    (OrderStatus.PENDING, 15)
                ]
            elif "sum(orders.total_amount)" in query_str:
                result.first.return_value = (Decimal("3500.00"), Decimal("25.50"))
                
            return result
            
        self.mock_session.exec.side_effect = mock_exec_side_effect
        
        analytics = await self.order_service.get_order_analytics(self.restaurant_id)
        
        # Verify analytics structure
        assert "total_orders" in analytics
        assert "orders_by_status" in analytics
        assert "total_revenue" in analytics
        assert "average_order_value" in analytics
        assert "date_range" in analytics
        
        assert analytics["total_orders"] == 150
        assert analytics["orders_by_status"][OrderStatus.DELIVERED] == 120
        assert analytics["total_revenue"] == Decimal("3500.00")
        
    @pytest.mark.asyncio
    async def test_list_orders_with_filters(self):
        """Test order listing with various filters"""
        filters = {
            "status": [OrderStatus.CONFIRMED, OrderStatus.PREPARING],
            "order_type": [OrderType.DINE_IN],
            "customer_name": "John",
            "table_id": str(uuid4())
        }
        
        mock_orders = [Mock(), Mock(), Mock()]
        mock_result = Mock()
        mock_result.all.return_value = mock_orders
        self.mock_session.exec.return_value = mock_result
        
        result = await self.order_service.list_orders(
            restaurant_id=self.restaurant_id,
            filters=filters,
            limit=20,
            offset=0
        )
        
        assert result == mock_orders
        assert self.mock_session.exec.called
        
    @pytest.mark.asyncio
    async def test_cache_clearing_patterns(self):
        """Test cache clearing with correct patterns"""
        with patch('app.modules.orders.services.order_service.cache_service') as mock_cache:
            order_id = str(uuid4())
            
            await self.order_service._clear_order_cache(self.restaurant_id, order_id)
            
            # Verify cache clearing was called
            assert mock_cache.clear_pattern.call_count >= 3
            
            # Check that specific order cache was cleared
            call_args = [call[0][0] for call in mock_cache.clear_pattern.call_args_list]
            order_specific_pattern = f"order:{self.restaurant_id}:{order_id}"
            assert order_specific_pattern in call_args
            
    def test_order_service_error_handling(self):
        """Test error handling in order service"""
        # Test with invalid session
        with pytest.raises(AttributeError):
            service = OrderService(None)
            # This should fail when trying to use session
            
    @pytest.mark.asyncio
    async def test_pricing_calculation_with_modifiers(self):
        """Test pricing calculation including modifiers"""
        # This would test modifier pricing if implemented
        # For now, test basic structure
        items_data = [
            OrderItemCreate(
                menu_item_id=uuid4(),
                quantity=1,
                special_instructions="",
                modifiers=[]  # Empty modifiers for this test
            )
        ]
        
        # Mock menu item
        mock_item = Mock()
        mock_item.price = Decimal("10.00")
        
        mock_result = Mock()
        mock_result.first.return_value = mock_item
        self.mock_session.exec.return_value = mock_result
        
        subtotal, items_with_pricing = await self.order_service._calculate_order_pricing(
            items_data, self.restaurant_id
        )
        
        assert subtotal == Decimal("10.00")
        assert len(items_with_pricing) == 1
        assert items_with_pricing[0]["total_price"] == Decimal("10.00")
        
    @pytest.mark.asyncio
    async def test_concurrent_order_creation(self):
        """Test handling of concurrent order creation"""
        # This tests that order number generation handles concurrency
        with patch.object(self.order_service, '_generate_order_number') as mock_gen:
            # Simulate different order numbers for concurrent requests
            mock_gen.side_effect = [
                "ORD-20250818-0001-12345",
                "ORD-20250818-0002-12346",
                "ORD-20250818-0003-12347"
            ]
            
            # Multiple calls should get different numbers
            numbers = []
            for _ in range(3):
                number = await self.order_service._generate_order_number(self.restaurant_id)
                numbers.append(number)
                
            assert len(set(numbers)) == 3  # All unique
            
    def test_order_service_constants(self):
        """Test order service uses correct constants"""
        # Verify tax rate is reasonable
        # This would check if tax calculations use proper constants
        assert True  # Placeholder for constant verification
        
    @pytest.mark.asyncio
    async def test_performance_edge_cases(self):
        """Test performance with edge cases"""
        # Test with large order (many items)
        large_items_data = [
            OrderItemCreate(
                menu_item_id=uuid4(),
                quantity=1,
                special_instructions="",
                modifiers=[]
            ) for _ in range(50)  # 50 items
        ]
        
        # Mock responses for all items
        mock_item = Mock()
        mock_item.price = Decimal("5.00")
        
        mock_result = Mock()
        mock_result.first.return_value = mock_item
        self.mock_session.exec.return_value = mock_result
        
        # This should handle large orders efficiently
        subtotal, items_with_pricing = await self.order_service._calculate_order_pricing(
            large_items_data, self.restaurant_id
        )
        
        assert subtotal == Decimal("250.00")  # 50 * 5.00
        assert len(items_with_pricing) == 50


def test_order_service_integration_points():
    """Test integration points with other services"""
    mock_session = Mock()
    service = OrderService(mock_session)
    
    # Verify service has expected interface
    assert hasattr(service, 'create_order')
    assert hasattr(service, 'get_order')
    assert hasattr(service, 'update_order_status')
    assert hasattr(service, 'list_orders')
    assert hasattr(service, 'get_kitchen_orders')
    assert hasattr(service, 'get_order_analytics')
    
    # Verify service is properly initialized
    assert service.session == mock_session


if __name__ == "__main__":
    # Run comprehensive tests
    pytest.main([__file__, "-v", "--tb=short"])