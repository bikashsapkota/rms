#!/usr/bin/env python3
"""
Debug script to identify UUID issues in Phase 3 endpoints.
"""

import asyncio
from sqlmodel.ext.asyncio.session import AsyncSession
from app.shared.database.session import get_session
from app.modules.orders.services.order_service import OrderService
from uuid import uuid4

async def test_order_service():
    """Test the OrderService directly to see exact error."""
    
    async for session in get_session():
        try:
            # Create service
            order_service = OrderService(session)
            
            # Test UUID
            test_restaurant_id = uuid4()
            print(f"Testing with restaurant_id: {test_restaurant_id} (type: {type(test_restaurant_id)})")
            
            # Try to list orders - this should reveal the exact error
            orders = await order_service.list_orders(restaurant_id=test_restaurant_id)
            print(f"Success! Found {len(orders)} orders")
            
        except Exception as e:
            print(f"Error details: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            await session.close()
        break

if __name__ == "__main__":
    asyncio.run(test_order_service())