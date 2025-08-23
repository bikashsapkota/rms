#!/usr/bin/env python3
"""
Production-Level Complete Order Workflow Tests

Comprehensive end-to-end testing of the complete order lifecycle
from creation through payment and kitchen operations.
"""

import sys
import asyncio
import time
from pathlib import Path
from decimal import Decimal
from datetime import datetime, timedelta

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.api_tester.shared.utils import APITestClient, APITestHelper, TestResults
from tests.api_tester.shared.auth import get_auth_headers
from tests.api_tester.shared.setup import setup_test_restaurant


class CompleteOrderWorkflowTester:
    """Complete order lifecycle workflow testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.results = TestResults()
        self.auth_headers = None
        self.restaurant_data = None
        
    async def setup_test_environment(self) -> bool:
        """Set up test restaurant and authentication"""
        APITestHelper.print_test_header("Environment Setup", "🏗️")
        
        try:
            # Setup test restaurant
            self.restaurant_data = await setup_test_restaurant(self.client)
            if not self.restaurant_data:
                APITestHelper.print_test_step("Failed to setup test restaurant", "FAILED")
                return False
                
            # Get authentication headers
            self.auth_headers = await get_auth_headers(self.client, 
                                                    self.restaurant_data["admin_email"],
                                                    self.restaurant_data["admin_password"])
            if not self.auth_headers:
                APITestHelper.print_test_step("Failed to get authentication", "FAILED")
                return False
                
            APITestHelper.print_test_step("Test environment ready", "SUCCESS")
            return True
            
        except Exception as e:
            APITestHelper.print_test_step(f"Environment setup failed: {e}", "FAILED")
            return False
    
    async def test_menu_setup_for_orders(self) -> Dict[str, str]:
        """Set up menu items required for order testing"""
        APITestHelper.print_test_header("Menu Setup for Orders", "🍽️")
        
        try:
            # Create category
            category_data = {
                "name": "Test Category",
                "description": "Category for order testing",
                "is_active": True
            }
            
            response = await self.client.post("/api/v1/menu/categories/", 
                                           json=category_data, 
                                           headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to create category: {response.status_code}")
            
            category_id = response.json()["id"]
            APITestHelper.print_test_step("Created test category", "SUCCESS")
            
            # Create menu items
            menu_items = []
            items_data = [
                {"name": "Burger", "price": 15.99, "description": "Delicious burger"},
                {"name": "Pizza", "price": 22.50, "description": "Cheese pizza"},
                {"name": "Salad", "price": 12.75, "description": "Fresh garden salad"},
                {"name": "Drink", "price": 4.50, "description": "Soft drink"}
            ]
            
            for item_data in items_data:
                item_data["category_id"] = category_id
                item_data["is_available"] = True
                
                response = await self.client.post("/api/v1/menu/items/", 
                                               json=item_data, 
                                               headers=self.auth_headers)
                
                if response.status_code != 200:
                    raise Exception(f"Failed to create menu item {item_data['name']}")
                
                menu_items.append({
                    "id": response.json()["id"],
                    "name": item_data["name"],
                    "price": item_data["price"]
                })
            
            APITestHelper.print_test_step(f"Created {len(menu_items)} menu items", "SUCCESS")
            
            return {
                "category_id": category_id,
                "menu_items": menu_items
            }
            
        except Exception as e:
            APITestHelper.print_test_step(f"Menu setup failed: {e}", "FAILED")
            return None
    
    async def test_complete_dine_in_order_workflow(self, menu_data: Dict) -> bool:
        """Test complete dine-in order workflow"""
        APITestHelper.print_test_header("Complete Dine-In Order Workflow", "🏪")
        
        try:
            # Step 1: Create order
            order_data = {
                "order_type": "dine_in",
                "customer_name": "John Doe",
                "customer_phone": "+1234567890",
                "special_instructions": "No onions please",
                "table_id": None,  # Can be null for testing
                "items": [
                    {
                        "menu_item_id": menu_data["menu_items"][0]["id"],  # Burger
                        "quantity": 2,
                        "special_instructions": "Medium rare"
                    },
                    {
                        "menu_item_id": menu_data["menu_items"][3]["id"],  # Drink
                        "quantity": 2,
                        "special_instructions": ""
                    }
                ]
            }
            
            response = await self.client.post("/api/v1/orders/", 
                                           json=order_data, 
                                           headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to create order: {response.status_code} - {response.text}")
            
            order = response.json()
            order_id = order["id"]
            expected_total = (15.99 * 2) + (4.50 * 2)  # 2 burgers + 2 drinks
            
            APITestHelper.print_test_step(f"Created order {order_id[:8]}... (${order['total_amount']})", "SUCCESS")
            
            # Verify order total calculation
            if abs(float(order["total_amount"]) - expected_total) > 0.01:
                raise Exception(f"Order total mismatch: expected {expected_total}, got {order['total_amount']}")
            
            # Step 2: Update order status to confirmed
            status_update = {
                "status": "confirmed",
                "kitchen_notes": "Order confirmed by kitchen"
            }
            
            response = await self.client.put(f"/api/v1/orders/{order_id}/status", 
                                          json=status_update, 
                                          headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to update order status: {response.status_code}")
            
            APITestHelper.print_test_step("Order confirmed", "SUCCESS")
            
            # Step 3: Kitchen operations - start preparation
            response = await self.client.post(f"/api/v1/kitchen/orders/{order_id}/start", 
                                           params={"estimated_prep_time": 15},
                                           headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to start order preparation: {response.status_code}")
            
            APITestHelper.print_test_step("Started order preparation", "SUCCESS")
            
            # Step 4: Complete preparation
            kitchen_update = {
                "kitchen_notes": "Order ready for serving"
            }
            
            response = await self.client.post(f"/api/v1/kitchen/orders/{order_id}/complete", 
                                           json=kitchen_update, 
                                           headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to complete order preparation: {response.status_code}")
            
            APITestHelper.print_test_step("Completed order preparation", "SUCCESS")
            
            # Step 5: Process payment
            payment_data = {
                "payment_method": "credit_card",
                "amount": str(order["total_amount"]),
                "currency": "USD",
                "payment_metadata": {
                    "card_last_four": "1234",
                    "transaction_id": f"txn_{int(time.time())}"
                }
            }
            
            response = await self.client.post(f"/api/v1/payments/orders/{order_id}/pay", 
                                           json=payment_data, 
                                           headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to process payment: {response.status_code}")
            
            payment = response.json()
            APITestHelper.print_test_step(f"Payment processed: ${payment['amount']}", "SUCCESS")
            
            # Step 6: Mark order as delivered
            delivery_update = {
                "status": "delivered",
                "kitchen_notes": "Order delivered to customer"
            }
            
            response = await self.client.put(f"/api/v1/orders/{order_id}/status", 
                                          json=delivery_update, 
                                          headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to mark order as delivered: {response.status_code}")
            
            APITestHelper.print_test_step("Order marked as delivered", "SUCCESS")
            
            # Step 7: Verify final order state
            response = await self.client.get(f"/api/v1/orders/{order_id}", 
                                          headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to retrieve final order state: {response.status_code}")
            
            final_order = response.json()
            
            # Verify order completion
            if final_order["status"] != "delivered":
                raise Exception(f"Expected order status 'delivered', got '{final_order['status']}'")
            
            APITestHelper.print_test_step("Order workflow completed successfully", "SUCCESS")
            
            # Record workflow success
            self.results.add_success("workflow", "Complete dine-in order", {
                "order_id": order_id,
                "total_amount": order["total_amount"],
                "final_status": final_order["status"],
                "payment_id": payment["id"]
            })
            
            return True
            
        except Exception as e:
            APITestHelper.print_test_step(f"Dine-in workflow failed: {e}", "FAILED")
            self.results.add_failure("workflow", "Complete dine-in order", str(e))
            return False
    
    async def test_complete_takeout_order_workflow(self, menu_data: Dict) -> bool:
        """Test complete takeout order workflow"""
        APITestHelper.print_test_header("Complete Takeout Order Workflow", "🥡")
        
        try:
            # Create takeout order
            order_data = {
                "order_type": "takeout",
                "customer_name": "Jane Smith",
                "customer_phone": "+1987654321",
                "customer_email": "jane@example.com",
                "requested_time": (datetime.utcnow() + timedelta(minutes=30)).isoformat(),
                "special_instructions": "Extra sauce on the side",
                "items": [
                    {
                        "menu_item_id": menu_data["menu_items"][1]["id"],  # Pizza
                        "quantity": 1,
                        "special_instructions": "Extra cheese"
                    },
                    {
                        "menu_item_id": menu_data["menu_items"][2]["id"],  # Salad
                        "quantity": 1,
                        "special_instructions": "Dressing on the side"
                    }
                ]
            }
            
            response = await self.client.post("/api/v1/orders/", 
                                           json=order_data, 
                                           headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to create takeout order: {response.status_code}")
            
            order = response.json()
            order_id = order["id"]
            
            APITestHelper.print_test_step(f"Created takeout order {order_id[:8]}...", "SUCCESS")
            
            # Fast-track through preparation
            await self.client.put(f"/api/v1/orders/{order_id}/status", 
                               json={"status": "confirmed"}, 
                               headers=self.auth_headers)
            
            await self.client.post(f"/api/v1/kitchen/orders/{order_id}/start", 
                                headers=self.auth_headers)
            
            await self.client.post(f"/api/v1/kitchen/orders/{order_id}/complete", 
                                json={"kitchen_notes": "Takeout ready"}, 
                                headers=self.auth_headers)
            
            # Process split payment
            total_amount = float(order["total_amount"])
            split_payment_data = {
                "payments": [
                    {
                        "payment_method": "credit_card",
                        "amount": str(total_amount * 0.7),  # 70% on card
                        "currency": "USD",
                        "payment_metadata": {"card_last_four": "5678"}
                    },
                    {
                        "payment_method": "cash",
                        "amount": str(total_amount * 0.3),  # 30% cash
                        "currency": "USD",
                        "payment_metadata": {"cash_received": str(total_amount * 0.3)}
                    }
                ]
            }
            
            response = await self.client.post(f"/api/v1/payments/orders/{order_id}/split-pay", 
                                           json=split_payment_data, 
                                           headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to process split payment: {response.status_code}")
            
            payments = response.json()
            APITestHelper.print_test_step(f"Split payment processed: {len(payments)} payments", "SUCCESS")
            
            # Mark as completed/picked up
            await self.client.put(f"/api/v1/orders/{order_id}/status", 
                               json={"status": "delivered"}, 
                               headers=self.auth_headers)
            
            APITestHelper.print_test_step("Takeout order workflow completed", "SUCCESS")
            
            self.results.add_success("workflow", "Complete takeout order", {
                "order_id": order_id,
                "payment_count": len(payments)
            })
            
            return True
            
        except Exception as e:
            APITestHelper.print_test_step(f"Takeout workflow failed: {e}", "FAILED")
            self.results.add_failure("workflow", "Complete takeout order", str(e))
            return False
    
    async def test_qr_order_workflow(self, menu_data: Dict) -> bool:
        """Test complete QR code order workflow"""
        APITestHelper.print_test_header("QR Code Order Workflow", "📱")
        
        try:
            # Step 1: Create QR session (staff action)
            qr_session_data = {
                "table_id": None,  # Using null for testing
                "session_duration_hours": 2,
                "max_orders_per_session": 3,
                "session_metadata": {
                    "server_name": "Test Server",
                    "notes": "QR order test session"
                }
            }
            
            response = await self.client.post("/api/v1/qr-orders/sessions", 
                                           json=qr_session_data, 
                                           headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to create QR session: {response.status_code}")
            
            qr_session = response.json()
            session_id = qr_session["session_id"]
            
            APITestHelper.print_test_step(f"Created QR session {session_id[:8]}...", "SUCCESS")
            
            # Step 2: Customer places order via QR (no auth required)
            customer_order = {
                "session_id": session_id,
                "customer_name": "QR Customer",
                "customer_phone": "+1555123456",
                "items": [
                    {
                        "menu_item_id": menu_data["menu_items"][0]["id"],  # Burger
                        "quantity": 1,
                        "special_instructions": "Well done"
                    }
                ],
                "special_instructions": "QR order - please bring to table"
            }
            
            response = await self.client.post("/api/v1/qr-orders/place-order", 
                                           json=customer_order)
            
            if response.status_code != 200:
                raise Exception(f"Failed to place QR order: {response.status_code}")
            
            qr_order = response.json()
            qr_order_id = qr_order["id"]
            
            APITestHelper.print_test_step(f"QR order placed: {qr_order_id[:8]}...", "SUCCESS")
            
            # Step 3: Process order through kitchen (with auth)
            await self.client.put(f"/api/v1/orders/{qr_order_id}/status", 
                               json={"status": "confirmed"}, 
                               headers=self.auth_headers)
            
            await self.client.post(f"/api/v1/kitchen/orders/{qr_order_id}/start", 
                                headers=self.auth_headers)
            
            await self.client.post(f"/api/v1/kitchen/orders/{qr_order_id}/complete", 
                                json={"kitchen_notes": "QR order ready"}, 
                                headers=self.auth_headers)
            
            # Step 4: Process payment
            payment_data = {
                "payment_method": "digital_wallet",
                "amount": str(qr_order["total_amount"]),
                "currency": "USD",
                "payment_metadata": {
                    "wallet_type": "apple_pay",
                    "transaction_id": f"qr_txn_{int(time.time())}"
                }
            }
            
            response = await self.client.post(f"/api/v1/payments/orders/{qr_order_id}/pay", 
                                           json=payment_data, 
                                           headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to process QR order payment: {response.status_code}")
            
            APITestHelper.print_test_step("QR order payment processed", "SUCCESS")
            
            # Step 5: Mark as served
            await self.client.put(f"/api/v1/orders/{qr_order_id}/status", 
                               json={"status": "delivered"}, 
                               headers=self.auth_headers)
            
            # Step 6: Check session orders
            response = await self.client.get(f"/api/v1/qr-orders/sessions/{session_id}/orders")
            
            if response.status_code != 200:
                raise Exception(f"Failed to get session orders: {response.status_code}")
            
            session_orders = response.json()
            
            if len(session_orders) != 1:
                raise Exception(f"Expected 1 order in session, got {len(session_orders)}")
            
            APITestHelper.print_test_step("QR order workflow completed", "SUCCESS")
            
            # Step 7: Close QR session
            response = await self.client.post(f"/api/v1/qr-orders/sessions/{session_id}/close", 
                                           headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to close QR session: {response.status_code}")
            
            APITestHelper.print_test_step("QR session closed", "SUCCESS")
            
            self.results.add_success("workflow", "QR order workflow", {
                "session_id": session_id,
                "order_id": qr_order_id,
                "session_orders_count": len(session_orders)
            })
            
            return True
            
        except Exception as e:
            APITestHelper.print_test_step(f"QR workflow failed: {e}", "FAILED")
            self.results.add_failure("workflow", "QR order workflow", str(e))
            return False
    
    async def test_order_cancellation_and_refund_workflow(self, menu_data: Dict) -> bool:
        """Test order cancellation and refund workflow"""
        APITestHelper.print_test_header("Order Cancellation & Refund Workflow", "❌")
        
        try:
            # Create order
            order_data = {
                "order_type": "dine_in",
                "customer_name": "Cancel Customer",
                "items": [
                    {
                        "menu_item_id": menu_data["menu_items"][1]["id"],  # Pizza
                        "quantity": 1
                    }
                ]
            }
            
            response = await self.client.post("/api/v1/orders/", 
                                           json=order_data, 
                                           headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to create order for cancellation test: {response.status_code}")
            
            order = response.json()
            order_id = order["id"]
            
            # Process payment first
            payment_data = {
                "payment_method": "credit_card",
                "amount": str(order["total_amount"]),
                "currency": "USD",
                "payment_metadata": {"card_last_four": "9999"}
            }
            
            response = await self.client.post(f"/api/v1/payments/orders/{order_id}/pay", 
                                           json=payment_data, 
                                           headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to process payment for cancellation test: {response.status_code}")
            
            payment = response.json()
            payment_id = payment["id"]
            
            APITestHelper.print_test_step("Order created and paid", "SUCCESS")
            
            # Cancel the order
            response = await self.client.delete(f"/api/v1/orders/{order_id}", 
                                             headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to cancel order: {response.status_code}")
            
            APITestHelper.print_test_step("Order cancelled", "SUCCESS")
            
            # Process refund
            refund_data = {
                "amount": str(payment["amount"]),
                "reason": "Customer cancellation",
                "refund_metadata": {
                    "refund_id": f"ref_{int(time.time())}",
                    "initiated_by": "staff"
                }
            }
            
            response = await self.client.post(f"/api/v1/payments/{payment_id}/refund", 
                                           json=refund_data, 
                                           headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to process refund: {response.status_code}")
            
            refund_result = response.json()
            
            if refund_result["status"] != "refunded":
                raise Exception(f"Expected refund status 'refunded', got '{refund_result['status']}'")
            
            APITestHelper.print_test_step(f"Refund processed: ${refund_result['refunded_amount']}", "SUCCESS")
            
            self.results.add_success("workflow", "Order cancellation and refund", {
                "order_id": order_id,
                "payment_id": payment_id,
                "refund_amount": refund_result["refunded_amount"]
            })
            
            return True
            
        except Exception as e:
            APITestHelper.print_test_step(f"Cancellation workflow failed: {e}", "FAILED")
            self.results.add_failure("workflow", "Order cancellation and refund", str(e))
            return False
    
    async def test_kitchen_analytics_workflow(self) -> bool:
        """Test kitchen analytics and reporting workflow"""
        APITestHelper.print_test_header("Kitchen Analytics Workflow", "📊")
        
        try:
            # Get kitchen performance metrics
            response = await self.client.get("/api/v1/kitchen/performance", 
                                          headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to get kitchen performance: {response.status_code}")
            
            performance = response.json()
            APITestHelper.print_test_step("Kitchen performance metrics retrieved", "SUCCESS")
            
            # Get daily analytics
            response = await self.client.get("/api/v1/kitchen/analytics/daily", 
                                          headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to get daily analytics: {response.status_code}")
            
            daily_analytics = response.json()
            APITestHelper.print_test_step("Daily kitchen analytics retrieved", "SUCCESS")
            
            # Get order analytics
            response = await self.client.get("/api/v1/orders/analytics/summary", 
                                          headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to get order analytics: {response.status_code}")
            
            order_analytics = response.json()
            APITestHelper.print_test_step("Order analytics retrieved", "SUCCESS")
            
            # Get payment summary
            response = await self.client.get("/api/v1/payments/summary", 
                                          headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to get payment summary: {response.status_code}")
            
            payment_summary = response.json()
            APITestHelper.print_test_step("Payment summary retrieved", "SUCCESS")
            
            # Get QR analytics
            response = await self.client.get("/api/v1/qr-orders/analytics", 
                                          headers=self.auth_headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to get QR analytics: {response.status_code}")
            
            qr_analytics = response.json()
            APITestHelper.print_test_step("QR order analytics retrieved", "SUCCESS")
            
            self.results.add_success("workflow", "Kitchen analytics workflow", {
                "performance_metrics": bool(performance),
                "daily_analytics": bool(daily_analytics),
                "order_analytics": bool(order_analytics),
                "payment_summary": bool(payment_summary),
                "qr_analytics": bool(qr_analytics)
            })
            
            return True
            
        except Exception as e:
            APITestHelper.print_test_step(f"Analytics workflow failed: {e}", "FAILED")
            self.results.add_failure("workflow", "Kitchen analytics workflow", str(e))
            return False
    
    def print_workflow_summary(self):
        """Print comprehensive workflow test summary"""
        
        APITestHelper.print_test_header("Workflow Test Summary", "📋")
        
        print(f"Total Workflows Tested: {self.results.total_tests}")
        print(f"Successful Workflows: {self.results.passed_tests}")
        print(f"Failed Workflows: {self.results.failed_tests}")
        print(f"Success Rate: {self.results.success_rate:.1f}%")
        
        # Show workflow results
        if self.results.results:
            print(f"\\n📝 Workflow Results:")
            for result in self.results.results:
                status = "✅" if result.success else "❌"
                print(f"   {status} {result.test_name}")
                if not result.success:
                    print(f"      Error: {result.error_message}")
        
        # Performance summary
        if self.results.execution_time > 0:
            print(f"\\n⏱️ Total Execution Time: {self.results.execution_time:.2f}s")
    
    async def run_all_workflow_tests(self) -> bool:
        """Run all production workflow tests"""
        
        print("🔄 Production-Level Order Workflow Tests")
        print("="*60)
        
        start_time = time.time()
        
        try:
            # Setup environment
            if not await self.setup_test_environment():
                return False
            
            # Setup menu
            menu_data = await self.test_menu_setup_for_orders()
            if not menu_data:
                return False
            
            # Run workflow tests
            workflows = [
                ("Complete Dine-In Order", self.test_complete_dine_in_order_workflow),
                ("Complete Takeout Order", self.test_complete_takeout_order_workflow),
                ("QR Code Order", self.test_qr_order_workflow),
                ("Order Cancellation & Refund", self.test_order_cancellation_and_refund_workflow),
                ("Kitchen Analytics", self.test_kitchen_analytics_workflow)
            ]
            
            overall_success = True
            
            for workflow_name, workflow_func in workflows:
                try:
                    if hasattr(workflow_func, '__call__'):
                        # Pass menu_data if the function accepts it
                        import inspect
                        sig = inspect.signature(workflow_func)
                        if 'menu_data' in sig.parameters:
                            success = await workflow_func(menu_data)
                        else:
                            success = await workflow_func()
                    else:
                        success = await workflow_func
                    
                    if not success:
                        overall_success = False
                        
                except Exception as e:
                    APITestHelper.print_test_step(f"{workflow_name} failed with error: {e}", "FAILED")
                    self.results.add_failure("workflow", workflow_name, str(e))
                    overall_success = False
                
                # Small delay between workflows
                await asyncio.sleep(1)
            
            # Calculate execution time
            self.results.execution_time = time.time() - start_time
            
            # Print summary
            self.print_workflow_summary()
            
            return overall_success
            
        except KeyboardInterrupt:
            print("\\n⚠️ Workflow tests interrupted by user")
            return False
        except Exception as e:
            print(f"\\n❌ Workflow tests failed: {e}")
            return False
        finally:
            await self.client.close()


async def main():
    """Main entry point for complete order workflow testing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Test complete order workflows")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    tester = CompleteOrderWorkflowTester(args.base_url)
    
    try:
        success = await tester.run_all_workflow_tests()
        
        if success:
            print(f"\\n✅ All workflow tests passed successfully!")
            print(f"   Phase 3 order management is production-ready")
        else:
            print(f"\\n❌ Some workflow tests failed")
            print(f"   Review the issues above before production deployment")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Workflow testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())