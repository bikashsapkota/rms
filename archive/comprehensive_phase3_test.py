#!/usr/bin/env python3
"""
Comprehensive Phase 3 Integration Test

This script tests the complete Phase 3 order management workflow
with real API calls to ensure production readiness.
"""

import requests
import json
import time
from decimal import Decimal
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class Phase3ComprehensiveTester:
    def __init__(self):
        self.auth_headers = None
        self.restaurant_id = None
        self.organization_id = None
        self.menu_items = []
        self.test_results = []
        
    def log_test(self, test_name, success, details=None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if not success and details:
            print(f"    Error: {details}")
    
    def setup_test_environment(self):
        """Set up test restaurant and authentication"""
        print("🏗️ Setting up test environment...")
        
        # Create test restaurant
        timestamp = int(time.time())
        setup_data = {
            "restaurant_name": f"Phase3 Test Restaurant {timestamp}",
            "admin_user": {
                "email": f"phase3.test.{timestamp}@example.com",
                "password": "testpassword123",
                "full_name": "Phase3 Test Admin"
            }
        }
        
        try:
            response = requests.post(f"{BASE_URL}/setup", json=setup_data)
            if response.status_code != 200:
                self.log_test("Restaurant Setup", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            restaurant_data = response.json()
            self.restaurant_id = restaurant_data["restaurant"]["id"]
            self.organization_id = restaurant_data["organization"]["id"]
            
            # Authenticate
            auth_data = {
                "email": setup_data["admin_user"]["email"],
                "password": setup_data["admin_user"]["password"]
            }
            
            response = requests.post(f"{API_BASE}/auth/login", json=auth_data)
            if response.status_code != 200:
                self.log_test("Authentication", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            token = response.json()["access_token"]
            self.auth_headers = {"Authorization": f"Bearer {token}"}
            
            self.log_test("Environment Setup", True, {"restaurant_id": self.restaurant_id})
            return True
            
        except Exception as e:
            self.log_test("Environment Setup", False, str(e))
            return False
    
    def setup_menu_items(self):
        """Create menu items for testing"""
        print("🍽️ Setting up menu items...")
        
        try:
            # Create category
            category_data = {
                "name": "Phase3 Test Category",
                "description": "Menu category for Phase 3 testing",
                "is_active": True
            }
            
            response = requests.post(f"{API_BASE}/menu/categories/", 
                                   json=category_data, 
                                   headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Menu Category Creation", False, f"HTTP {response.status_code}")
                return False
            
            category_id = response.json()["id"]
            
            # Create menu items
            items_data = [
                {"name": "Test Burger", "price": 15.99, "description": "Delicious test burger"},
                {"name": "Test Pizza", "price": 22.50, "description": "Test pizza"},
                {"name": "Test Salad", "price": 12.75, "description": "Fresh test salad"},
                {"name": "Test Drink", "price": 4.50, "description": "Test beverage"}
            ]
            
            for item_data in items_data:
                item_data.update({
                    "category_id": category_id,
                    "is_available": True
                })
                
                response = requests.post(f"{API_BASE}/menu/items/", 
                                       json=item_data, 
                                       headers=self.auth_headers)
                
                if response.status_code != 200:
                    self.log_test("Menu Item Creation", False, f"Failed to create {item_data['name']}")
                    return False
                
                self.menu_items.append({
                    "id": response.json()["id"],
                    "name": item_data["name"],
                    "price": item_data["price"]
                })
            
            self.log_test("Menu Setup", True, {"items_created": len(self.menu_items)})
            return True
            
        except Exception as e:
            self.log_test("Menu Setup", False, str(e))
            return False
    
    def test_order_creation_and_management(self):
        """Test complete order creation and management workflow"""
        print("📝 Testing order creation and management...")
        
        try:
            # Test 1: Create a dine-in order
            order_data = {
                "order_type": "dine_in",
                "customer_name": "Phase3 Test Customer",
                "customer_phone": "+1234567890",
                "special_instructions": "Test order for Phase 3 verification",
                "items": [
                    {
                        "menu_item_id": self.menu_items[0]["id"],  # Burger
                        "quantity": 2,
                        "special_instructions": "Well done"
                    },
                    {
                        "menu_item_id": self.menu_items[3]["id"],  # Drink
                        "quantity": 2,
                        "special_instructions": ""
                    }
                ]
            }
            
            response = requests.post(f"{API_BASE}/orders/", 
                                   json=order_data, 
                                   headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Order Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            order = response.json()
            order_id = order["id"]
            subtotal = (15.99 * 2) + (4.50 * 2)  # 2 burgers + 2 drinks
            expected_total = subtotal * 1.085  # With 8.5% tax
            
            # Verify order total calculation
            if abs(float(order["total_amount"]) - expected_total) > 0.01:
                self.log_test("Order Total Calculation", False, 
                             f"Expected {expected_total}, got {order['total_amount']}")
                return False
            
            self.log_test("Order Creation", True, {
                "order_id": order_id,
                "total_amount": order["total_amount"]
            })
            
            # Test 2: Get order details
            response = requests.get(f"{API_BASE}/orders/{order_id}", 
                                  headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Order Retrieval", False, f"HTTP {response.status_code}")
                return False
            
            retrieved_order = response.json()
            if retrieved_order["id"] != order_id:
                self.log_test("Order Retrieval", False, "Order ID mismatch")
                return False
            
            self.log_test("Order Retrieval", True)
            
            # Test 3: Update order status
            status_update = {
                "status": "confirmed",
                "kitchen_notes": "Order confirmed for Phase 3 testing"
            }
            
            response = requests.put(f"{API_BASE}/orders/{order_id}/status", 
                                  json=status_update, 
                                  headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Order Status Update", False, f"HTTP {response.status_code}")
                return False
            
            self.log_test("Order Status Update", True)
            
            # Test 4: Get order items
            response = requests.get(f"{API_BASE}/orders/{order_id}/items", 
                                  headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Order Items Retrieval", False, f"HTTP {response.status_code}")
                return False
            
            items = response.json()
            if len(items) != 2:
                self.log_test("Order Items Count", False, f"Expected 2 items, got {len(items)}")
                return False
            
            self.log_test("Order Items Retrieval", True, {"items_count": len(items)})
            
            # Test 5: Duplicate order
            response = requests.post(f"{API_BASE}/orders/{order_id}/duplicate", 
                                   headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Order Duplication", False, f"HTTP {response.status_code}")
                return False
            
            duplicate_order = response.json()
            if duplicate_order["id"] == order_id:
                self.log_test("Order Duplication", False, "Duplicate has same ID as original")
                return False
            
            self.log_test("Order Duplication", True, {"duplicate_id": duplicate_order["id"]})
            
            return order_id
            
        except Exception as e:
            self.log_test("Order Management", False, str(e))
            return None
    
    def test_kitchen_operations(self, order_id):
        """Test kitchen operations workflow"""
        print("👨‍🍳 Testing kitchen operations...")
        
        try:
            # Test 1: Get kitchen orders
            response = requests.get(f"{API_BASE}/kitchen/orders", 
                                  headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Kitchen Orders List", False, f"HTTP {response.status_code}")
                return False
            
            kitchen_orders = response.json()
            self.log_test("Kitchen Orders List", True, {"orders_count": len(kitchen_orders)})
            
            # Test 2: Start order preparation
            response = requests.post(f"{API_BASE}/kitchen/orders/{order_id}/start", 
                                   params={"estimated_prep_time": 15},
                                   headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Start Order Preparation", False, f"HTTP {response.status_code}")
                return False
            
            self.log_test("Start Order Preparation", True)
            
            # Test 3: Add kitchen notes
            notes_data = {
                "notes": "Phase 3 test - order in preparation"
            }
            
            response = requests.post(f"{API_BASE}/kitchen/orders/{order_id}/notes", 
                                   json=notes_data, 
                                   headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Kitchen Notes", False, f"HTTP {response.status_code}")
                return False
            
            self.log_test("Kitchen Notes", True)
            
            # Test 4: Set order priority
            response = requests.post(f"{API_BASE}/kitchen/orders/{order_id}/priority", 
                                   json={"priority": 8},
                                   headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Order Priority", False, f"HTTP {response.status_code}")
                return False
            
            self.log_test("Order Priority", True)
            
            # Test 5: Complete order preparation
            completion_data = {
                "kitchen_notes": "Phase 3 test order completed"
            }
            
            response = requests.post(f"{API_BASE}/kitchen/orders/{order_id}/complete", 
                                   json=completion_data, 
                                   headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Complete Order Preparation", False, f"HTTP {response.status_code}")
                return False
            
            self.log_test("Complete Order Preparation", True)
            
            # Test 6: Get kitchen performance metrics
            response = requests.get(f"{API_BASE}/kitchen/performance", 
                                  headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Kitchen Performance Metrics", False, f"HTTP {response.status_code}")
                return False
            
            performance = response.json()
            self.log_test("Kitchen Performance Metrics", True, {
                "metrics_available": bool(performance)
            })
            
            # Test 7: Get preparation queue
            response = requests.get(f"{API_BASE}/kitchen/prep-queue", 
                                  headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Kitchen Prep Queue", False, f"HTTP {response.status_code}")
                return False
            
            prep_queue = response.json()
            self.log_test("Kitchen Prep Queue", True, {"queue_length": len(prep_queue)})
            
            # Test 8: Get daily analytics
            response = requests.get(f"{API_BASE}/kitchen/analytics/daily", 
                                  headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Kitchen Daily Analytics", False, f"HTTP {response.status_code}")
                return False
            
            daily_analytics = response.json()
            self.log_test("Kitchen Daily Analytics", True, {
                "analytics_available": bool(daily_analytics)
            })
            
            return True
            
        except Exception as e:
            self.log_test("Kitchen Operations", False, str(e))
            return False
    
    def test_payment_processing(self, order_id):
        """Test payment processing workflow"""
        print("💳 Testing payment processing...")
        
        try:
            # Test 1: Process single payment  
            # Get the actual order total first
            response = requests.get(f"{API_BASE}/orders/{order_id}", headers=self.auth_headers)
            if response.status_code != 200:
                self.log_test("Get Order for Payment", False, f"HTTP {response.status_code}")
                return False
            
            order_details = response.json()
            order_total = str(order_details["total_amount"])
            
            payment_data = {
                "payment_method": "credit_card",
                "amount": order_total,  # Use actual order total
                "currency": "USD",
                "payment_metadata": {
                    "card_last_four": "1234",
                    "transaction_id": f"test_txn_{int(time.time())}"
                }
            }
            
            response = requests.post(f"{API_BASE}/payments/orders/{order_id}/pay", 
                                   json=payment_data, 
                                   headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Payment Processing", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            payment = response.json()
            payment_id = payment["id"]
            
            self.log_test("Payment Processing", True, {
                "payment_id": payment_id,
                "amount": payment["amount"]
            })
            
            # Test 2: Get order payments
            response = requests.get(f"{API_BASE}/payments/orders/{order_id}", 
                                  headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Order Payments Retrieval", False, f"HTTP {response.status_code}")
                return False
            
            order_payments = response.json()
            if len(order_payments) == 0:
                self.log_test("Order Payments Count", False, "No payments found for order")
                return False
            
            self.log_test("Order Payments Retrieval", True, {"payments_count": len(order_payments)})
            
            # Test 3: Process partial refund
            refund_data = {
                "amount": "10.00",  # Partial refund
                "reason": "Phase 3 test partial refund",
                "refund_metadata": {
                    "refund_id": f"test_refund_{int(time.time())}",
                    "initiated_by": "test_admin"
                }
            }
            
            response = requests.post(f"{API_BASE}/payments/{payment_id}/refund", 
                                   json=refund_data, 
                                   headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Payment Refund", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            refunded_payment = response.json()
            self.log_test("Payment Refund", True, {
                "refunded_amount": refunded_payment["refunded_amount"]
            })
            
            # Test 4: Get payment summary
            response = requests.get(f"{API_BASE}/payments/summary", 
                                  headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Payment Summary", False, f"HTTP {response.status_code}")
                return False
            
            payment_summary = response.json()
            self.log_test("Payment Summary", True, {
                "total_revenue": payment_summary.get("total_revenue", 0)
            })
            
            # Test 5: Get daily payment totals
            response = requests.get(f"{API_BASE}/payments/daily-totals", 
                                  params={"days": 7},
                                  headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Daily Payment Totals", False, f"HTTP {response.status_code}")
                return False
            
            daily_totals = response.json()
            self.log_test("Daily Payment Totals", True, {"days_returned": len(daily_totals)})
            
            return True
            
        except Exception as e:
            self.log_test("Payment Processing", False, str(e))
            return False
    
    def test_qr_order_workflow(self):
        """Test QR code ordering workflow"""
        print("📱 Testing QR code ordering...")
        
        try:
            # Test 1: Create QR session (would normally require table_id)
            qr_session_data = {
                "table_id": None,  # Using null for testing
                "session_duration_hours": 2,
                "max_orders_per_session": 3,
                "session_metadata": {
                    "server_name": "Test Server",
                    "notes": "Phase 3 test QR session"
                }
            }
            
            response = requests.post(f"{API_BASE}/qr-orders/sessions", 
                                   json=qr_session_data, 
                                   headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("QR Session Creation", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            qr_session = response.json()
            session_id = qr_session["session_id"]
            
            self.log_test("QR Session Creation", True, {"session_id": session_id})
            
            # Test 2: Get QR session info (public endpoint)
            response = requests.get(f"{API_BASE}/qr-orders/sessions/{session_id}")
            
            if response.status_code != 200:
                self.log_test("QR Session Info", False, f"HTTP {response.status_code}")
                return False
            
            session_info = response.json()
            self.log_test("QR Session Info", True, {"expires_at": session_info.get("expires_at")})
            
            # Test 3: Place QR order (public endpoint)
            customer_order = {
                "session_id": session_id,
                "customer_name": "QR Test Customer",
                "customer_phone": "+1555123456",
                "items": [
                    {
                        "menu_item_id": self.menu_items[1]["id"],  # Pizza
                        "quantity": 1,
                        "special_instructions": "QR test order"
                    }
                ],
                "special_instructions": "QR code order for Phase 3 testing"
            }
            
            response = requests.post(f"{API_BASE}/qr-orders/place-order", 
                                   json=customer_order)
            
            if response.status_code != 200:
                self.log_test("QR Order Placement", False, f"HTTP {response.status_code}: {response.text}")
                return False
            
            qr_order = response.json()
            qr_order_id = qr_order["id"]
            
            self.log_test("QR Order Placement", True, {"order_id": qr_order_id})
            
            # Test 4: Get session orders (public endpoint)
            response = requests.get(f"{API_BASE}/qr-orders/sessions/{session_id}/orders")
            
            if response.status_code != 200:
                self.log_test("QR Session Orders", False, f"HTTP {response.status_code}")
                return False
            
            session_orders = response.json()
            if len(session_orders) == 0:
                self.log_test("QR Session Orders Count", False, "No orders found in session")
                return False
            
            self.log_test("QR Session Orders", True, {"orders_count": len(session_orders)})
            
            # Test 5: Close QR session
            response = requests.post(f"{API_BASE}/qr-orders/sessions/{session_id}/close", 
                                   headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("QR Session Close", False, f"HTTP {response.status_code}")
                return False
            
            self.log_test("QR Session Close", True)
            
            # Test 6: Get QR analytics
            response = requests.get(f"{API_BASE}/qr-orders/analytics", 
                                  headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("QR Analytics", False, f"HTTP {response.status_code}")
                return False
            
            qr_analytics = response.json()
            self.log_test("QR Analytics", True, {
                "total_sessions": qr_analytics.get("total_sessions", 0)
            })
            
            return True
            
        except Exception as e:
            self.log_test("QR Order Workflow", False, str(e))
            return False
    
    def test_analytics_and_reporting(self):
        """Test analytics and reporting endpoints"""
        print("📊 Testing analytics and reporting...")
        
        try:
            # Test 1: Order analytics
            response = requests.get(f"{API_BASE}/orders/analytics/summary", 
                                  headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Order Analytics", False, f"HTTP {response.status_code}")
                return False
            
            order_analytics = response.json()
            self.log_test("Order Analytics", True, {
                "total_orders": order_analytics.get("total_orders", 0)
            })
            
            # Test 2: List orders with filters
            response = requests.get(f"{API_BASE}/orders/", 
                                  params={"limit": 10, "offset": 0},
                                  headers=self.auth_headers)
            
            if response.status_code != 200:
                self.log_test("Orders List", False, f"HTTP {response.status_code}")
                return False
            
            orders_list = response.json()
            self.log_test("Orders List", True, {"orders_count": len(orders_list)})
            
            return True
            
        except Exception as e:
            self.log_test("Analytics and Reporting", False, str(e))
            return False
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\\n" + "="*60)
        print("🏁 PHASE 3 COMPREHENSIVE TEST SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        # Group results by test category
        if failed_tests > 0:
            print(f"\\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   • {result['test']}")
                    if result["details"]:
                        print(f"     {result['details']}")
        
        # Production readiness assessment
        print(f"\\n🎯 Production Readiness Assessment:")
        
        if success_rate >= 95:
            print("   ✅ PRODUCTION READY")
            print("   All critical Phase 3 functionality is working correctly.")
        elif success_rate >= 85:
            print("   ⚠️  MOSTLY READY")
            print("   Most functionality works, but some issues need attention.")
        elif success_rate >= 70:
            print("   ⚠️  NEEDS IMPROVEMENT")
            print("   Several issues need to be resolved before production.")
        else:
            print("   ❌ NOT READY")
            print("   Significant issues prevent production deployment.")
        
        return success_rate >= 85
    
    def run_comprehensive_test(self):
        """Run all Phase 3 comprehensive tests"""
        print("🚀 PHASE 3 COMPREHENSIVE FUNCTIONALITY TEST")
        print("="*50)
        
        start_time = time.time()
        
        try:
            # Setup
            if not self.setup_test_environment():
                return False
            
            if not self.setup_menu_items():
                return False
            
            # Core workflow tests
            order_id = self.test_order_creation_and_management()
            if not order_id:
                return False
            
            if not self.test_kitchen_operations(order_id):
                return False
            
            if not self.test_payment_processing(order_id):
                return False
            
            if not self.test_qr_order_workflow():
                return False
            
            if not self.test_analytics_and_reporting():
                return False
            
            execution_time = time.time() - start_time
            print(f"\\n⏱️ Total execution time: {execution_time:.2f} seconds")
            
            return self.print_test_summary()
            
        except Exception as e:
            print(f"\\n❌ Comprehensive test failed: {e}")
            return False


def main():
    """Run the comprehensive Phase 3 test"""
    tester = Phase3ComprehensiveTester()
    
    try:
        success = tester.run_comprehensive_test()
        
        if success:
            print(f"\\n✅ Phase 3 comprehensive test PASSED!")
            print(f"   All core functionality is working at production level")
            exit(0)
        else:
            print(f"\\n❌ Phase 3 comprehensive test FAILED!")
            print(f"   Review the issues above before production deployment")
            exit(1)
            
    except KeyboardInterrupt:
        print(f"\\n⚠️ Test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\\n❌ Test execution failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()