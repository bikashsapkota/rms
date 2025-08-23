"""
Comprehensive Phase 3 API Tests: Complete Order Management Workflow
Tests the entire order lifecycle from creation to completion.
"""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class Phase3OrderWorkflowTester:
    def __init__(self):
        self.auth_token = None
        self.restaurant_id = None
        self.organization_id = None
        self.table_id = None
        self.menu_items = []
        self.modifiers = []
        self.order_id = None
        self.qr_session_id = None
        
    def run_complete_workflow(self):
        """Run the complete Phase 3 order workflow test."""
        print("🚀 Starting Phase 3 Complete Order Workflow Test")
        print("=" * 60)
        
        try:
            # Step 1: Setup restaurant and authenticate
            self._setup_restaurant()
            self._authenticate()
            
            # Step 2: Create menu items for testing
            self._create_test_menu()
            
            # Step 3: Create tables for dining
            self._create_test_tables()
            
            # Step 4: Test QR ordering workflow
            self._test_qr_ordering_workflow()
            
            # Step 5: Test complete order management
            self._test_order_management_workflow()
            
            # Step 6: Test kitchen operations
            self._test_kitchen_operations()
            
            # Step 7: Test payment processing
            self._test_payment_processing()
            
            # Step 8: Test analytics and reporting
            self._test_analytics_reporting()
            
            print("\\n✅ All Phase 3 workflow tests passed!")
            return True
            
        except Exception as e:
            print(f"\\n❌ Phase 3 workflow test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def _setup_restaurant(self):
        """Setup a test restaurant."""
        print("\\n📋 Setting up restaurant...")
        
        setup_data = {
            "restaurant_name": "Phase 3 Test Restaurant",
            "address": {
                "street": "123 Phase 3 Street",
                "city": "Test City",
                "state": "TS",
                "zip_code": "12345"
            },
            "phone": "+1-555-PHASE3",
            "email": "phase3@test.com",
            "admin_user": {
                "email": f"admin.phase3.{int(time.time())}@test.com",
                "password": "testpassword123",
                "full_name": "Phase 3 Admin"
            }
        }
        
        response = requests.post(f"{BASE_URL}/setup", json=setup_data)
        assert response.status_code == 200, f"Setup failed: {response.text}"
        
        data = response.json()
        self.restaurant_id = data["restaurant"]["id"]
        self.organization_id = data["organization"]["id"]
        self.admin_email = setup_data["admin_user"]["email"]
        print(f"✅ Restaurant created: {self.restaurant_id}")
    
    def _authenticate(self):
        """Authenticate admin user."""
        print("\\n🔐 Authenticating admin user...")
        
        auth_data = {
            "email": self.admin_email,
            "password": "testpassword123"
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=auth_data)
        assert response.status_code == 200, f"Login failed: {response.text}"
        
        data = response.json()
        self.auth_token = data["access_token"]
        print("✅ Authentication successful")
    
    @property
    def headers(self):
        """Auth headers for API requests."""
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    def _create_test_menu(self):
        """Create test menu items and modifiers."""
        print("\\n🍽️ Creating test menu...")
        
        # Create category
        category_data = {"name": "Phase 3 Menu", "description": "Test menu for Phase 3"}
        response = requests.post(f"{API_BASE}/menu/categories/", json=category_data, headers=self.headers)
        assert response.status_code == 200, f"Category creation failed: {response.text}"
        category_id = response.json()["id"]
        
        # Create menu items
        items = [
            {"name": "Burger", "description": "Test burger", "price": 12.99, "category_id": category_id},
            {"name": "Pizza", "description": "Test pizza", "price": 18.99, "category_id": category_id},
            {"name": "Salad", "description": "Test salad", "price": 8.99, "category_id": category_id}
        ]
        
        for item_data in items:
            response = requests.post(f"{API_BASE}/menu/items/", json=item_data, headers=self.headers)
            assert response.status_code == 200, f"Menu item creation failed: {response.text}"
            self.menu_items.append(response.json())
        
        # Create modifiers
        modifiers = [
            {"name": "Extra Cheese", "modifier_type": "addon", "price_adjustment": 2.00},
            {"name": "Large Size", "modifier_type": "size", "price_adjustment": 3.00},
            {"name": "No Onions", "modifier_type": "substitution", "price_adjustment": 0.00}
        ]
        
        for mod_data in modifiers:
            response = requests.post(f"{API_BASE}/menu/modifiers/", json=mod_data, headers=self.headers)
            if response.status_code != 200:
                print(f"Failed to create modifier: {response.status_code} - {response.text}")
            assert response.status_code == 200
            self.modifiers.append(response.json())
        
        print(f"✅ Created {len(self.menu_items)} menu items and {len(self.modifiers)} modifiers")
    
    def _create_test_tables(self):
        """Create test tables."""
        print("\\n🪑 Creating test tables...")
        
        table_data = {
            "table_number": "T10",
            "capacity": 4,
            "location": "main_dining"
        }
        
        response = requests.post(f"{API_BASE}/tables/", json=table_data, headers=self.headers)
        assert response.status_code == 200
        self.table_id = response.json()["id"]
        print(f"✅ Created table: {self.table_id}")
    
    def _test_qr_ordering_workflow(self):
        """Test complete QR ordering workflow."""
        print("\\n📱 Testing QR ordering workflow...")
        
        # Create QR session
        qr_data = {
            "table_id": self.table_id,
            "customer_name": "QR Customer"
        }
        
        response = requests.post(f"{API_BASE}/qr-orders/sessions", json=qr_data, headers=self.headers)
        assert response.status_code == 200
        qr_session = response.json()
        self.qr_session_id = qr_session["session_id"]
        
        # Verify QR session info (no auth required)
        response = requests.get(f"{API_BASE}/qr-orders/sessions/{self.qr_session_id}")
        assert response.status_code == 200
        
        # Place order via QR (no auth required)
        qr_order_data = {
            "session_id": self.qr_session_id,
            "customer_name": "QR Customer",
            "items": [
                {
                    "menu_item_id": self.menu_items[0]["id"],
                    "quantity": 1,
                    "modifiers": [{"modifier_id": self.modifiers[0]["id"], "quantity": 1}]
                }
            ],
            "special_instructions": "Test QR order"
        }
        
        response = requests.post(f"{API_BASE}/qr-orders/place-order", json=qr_order_data)
        if response.status_code != 200:
            print(f"Failed to place QR order: {response.status_code} - {response.text}")
        assert response.status_code == 200
        qr_order = response.json()
        
        # Get session orders
        response = requests.get(f"{API_BASE}/qr-orders/sessions/{self.qr_session_id}/orders")
        assert response.status_code == 200
        
        # Close QR session
        response = requests.post(f"{API_BASE}/qr-orders/sessions/{self.qr_session_id}/close", headers=self.headers)
        assert response.status_code == 200
        
        print("✅ QR ordering workflow completed successfully")
    
    def _test_order_management_workflow(self):
        """Test complete order management workflow."""
        print("\\n📝 Testing order management workflow...")
        
        # Create new order
        order_data = {
            "order_type": "dine_in",
            "customer_name": "Test Customer",
            "customer_phone": "+1-555-TEST",
            "customer_email": "customer@test.com",
            "table_id": self.table_id,
            "items": [
                {
                    "menu_item_id": self.menu_items[1]["id"],
                    "quantity": 2,
                    "special_instructions": "Extra crispy",
                    "modifiers": [
                        {"modifier_id": self.modifiers[0]["id"], "quantity": 1},
                        {"modifier_id": self.modifiers[1]["id"], "quantity": 1}
                    ]
                }
            ],
            "special_instructions": "Rush order please"
        }
        
        response = requests.post(f"{API_BASE}/orders/", json=order_data, headers=self.headers)
        assert response.status_code == 200
        order = response.json()
        self.order_id = order["id"]
        
        # Get order details
        response = requests.get(f"{API_BASE}/orders/{self.order_id}", headers=self.headers)
        assert response.status_code == 200
        
        # List orders
        response = requests.get(f"{API_BASE}/orders/", headers=self.headers)
        assert response.status_code == 200
        orders = response.json()
        assert len(orders) >= 1
        
        # Update order status
        status_data = {
            "status": "confirmed",
            "kitchen_notes": "Order confirmed"
        }
        
        response = requests.put(f"{API_BASE}/orders/{self.order_id}/status", json=status_data, headers=self.headers)
        assert response.status_code == 200
        
        print("✅ Order management workflow completed successfully")
    
    def _test_kitchen_operations(self):
        """Test kitchen operations workflow."""
        print("\\n👨‍🍳 Testing kitchen operations...")
        
        # Get kitchen orders
        response = requests.get(f"{API_BASE}/kitchen/orders", headers=self.headers)
        assert response.status_code == 200
        kitchen_orders = response.json()
        
        # Start order preparation
        response = requests.post(f"{API_BASE}/kitchen/orders/{self.order_id}/start", 
                               params={"estimated_prep_time": 15}, headers=self.headers)
        assert response.status_code == 200
        
        # Get prep queue
        response = requests.get(f"{API_BASE}/kitchen/prep-queue", headers=self.headers)
        assert response.status_code == 200
        
        # Complete order preparation
        kitchen_data = {
            "kitchen_notes": "Order completed perfectly"
        }
        response = requests.post(f"{API_BASE}/kitchen/orders/{self.order_id}/complete", 
                               json=kitchen_data, headers=self.headers)
        assert response.status_code == 200
        
        # Get kitchen performance metrics
        response = requests.get(f"{API_BASE}/kitchen/performance", headers=self.headers)
        assert response.status_code == 200
        
        print("✅ Kitchen operations completed successfully")
    
    def _test_payment_processing(self):
        """Test payment processing workflow."""
        print("\\n💳 Testing payment processing...")
        
        # Process payment
        payment_data = {
            "amount": 25.00,
            "payment_method": "credit_card",
            "tip_amount": 5.00
        }
        
        response = requests.post(f"{API_BASE}/payments/orders/{self.order_id}/pay", 
                               json=payment_data, headers=self.headers)
        assert response.status_code == 200
        payment = response.json()
        payment_id = payment["id"]
        
        # Get order payments
        response = requests.get(f"{API_BASE}/payments/orders/{self.order_id}", headers=self.headers)
        assert response.status_code == 200
        
        # Test split payment for another order
        split_order_data = {
            "order_type": "takeout",
            "customer_name": "Split Customer",
            "items": [{"menu_item_id": self.menu_items[2]["id"], "quantity": 1}]
        }
        
        response = requests.post(f"{API_BASE}/orders/", json=split_order_data, headers=self.headers)
        assert response.status_code == 200
        split_order = response.json()
        
        # Process split payment
        split_payment_data = {
            "payments": [
                {"amount": 5.00, "payment_method": "cash", "tip_amount": 1.00},
                {"amount": 4.99, "payment_method": "credit_card", "tip_amount": 1.00}
            ],
            "split_method": "custom"
        }
        
        response = requests.post(f"{API_BASE}/payments/orders/{split_order['id']}/split-pay", 
                               json=split_payment_data, headers=self.headers)
        assert response.status_code == 200
        
        # Get payment summary
        response = requests.get(f"{API_BASE}/payments/summary", headers=self.headers)
        assert response.status_code == 200
        
        # Get daily payment totals
        response = requests.get(f"{API_BASE}/payments/daily-totals", headers=self.headers)
        assert response.status_code == 200
        
        print("✅ Payment processing completed successfully")
    
    def _test_analytics_reporting(self):
        """Test analytics and reporting features."""
        print("\\n📊 Testing analytics and reporting...")
        
        # Get order analytics
        response = requests.get(f"{API_BASE}/orders/analytics/summary", headers=self.headers)
        assert response.status_code == 200
        
        # Get QR analytics
        response = requests.get(f"{API_BASE}/qr-orders/analytics", headers=self.headers)
        assert response.status_code == 200
        
        print("✅ Analytics and reporting completed successfully")


def main():
    """Main test function."""
    tester = Phase3OrderWorkflowTester()
    success = tester.run_complete_workflow()
    
    if success:
        print("\\n🎉 Phase 3 Complete Order Workflow Test: PASSED")
        return 0
    else:
        print("\\n💥 Phase 3 Complete Order Workflow Test: FAILED")
        return 1


if __name__ == "__main__":
    exit(main())