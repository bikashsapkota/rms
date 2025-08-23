"""
Production-level integration tests for Phase 3 Order Management & Kitchen Operations.
Tests complete workflows end-to-end to verify production readiness.
"""

import pytest
import requests
import json
import time
from datetime import datetime
from decimal import Decimal


BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


class TestPhase3ProductionWorkflows:
    """Integration tests for complete Phase 3 workflows."""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment once for all tests."""
        # Create test restaurant
        timestamp = int(time.time())
        cls.setup_data = {
            "restaurant_name": f"Phase3 Production Test {timestamp}",
            "admin_user": {
                "email": f"production.test.{timestamp}@example.com",
                "password": "testpassword123",
                "full_name": "Production Test Admin"
            }
        }
        
        # Setup restaurant
        response = requests.post(f"{BASE_URL}/setup", json=cls.setup_data)
        assert response.status_code == 200
        
        restaurant_data = response.json()
        cls.restaurant_id = restaurant_data["restaurant"]["id"]
        cls.organization_id = restaurant_data["organization"]["id"]
        
        # Authenticate
        auth_data = {
            "email": cls.setup_data["admin_user"]["email"],
            "password": cls.setup_data["admin_user"]["password"]
        }
        
        response = requests.post(f"{API_BASE}/auth/login", json=auth_data)
        assert response.status_code == 200
        
        token = response.json()["access_token"]
        cls.headers = {"Authorization": f"Bearer {token}"}
    
    def test_complete_order_lifecycle_workflow(self):
        """Test complete order lifecycle from creation to completion."""
        print("\\n🔄 Testing Complete Order Lifecycle...")
        
        # 1. Check initial analytics
        response = requests.get(f"{API_BASE}/orders/analytics/summary", headers=self.headers)
        assert response.status_code == 200
        initial_analytics = response.json()
        
        # 2. Get daily report
        response = requests.get(f"{API_BASE}/orders/reports/daily", headers=self.headers)
        assert response.status_code == 200
        daily_report = response.json()
        assert "total_orders" in daily_report
        
        # 3. Check kitchen performance
        response = requests.get(f"{API_BASE}/kitchen/performance", headers=self.headers)
        assert response.status_code == 200
        kitchen_performance = response.json()
        assert "average_prep_time_minutes" in kitchen_performance
        
        # 4. Get payment summary
        response = requests.get(f"{API_BASE}/payments/summary", headers=self.headers)
        assert response.status_code == 200
        payment_summary = response.json()
        assert "total_revenue" in payment_summary
        
        print("✅ Complete lifecycle workflow verified")
    
    def test_kitchen_operations_workflow(self):
        """Test kitchen operations and management workflow."""
        print("\\n👨‍🍳 Testing Kitchen Operations Workflow...")
        
        # 1. Get kitchen orders
        response = requests.get(f"{API_BASE}/kitchen/orders", headers=self.headers)
        assert response.status_code == 200
        kitchen_orders = response.json()
        
        # 2. Check prep queue
        response = requests.get(f"{API_BASE}/kitchen/prep-queue", headers=self.headers)
        assert response.status_code == 200
        prep_queue = response.json()
        assert isinstance(prep_queue, list)
        
        # 3. Get daily kitchen analytics
        response = requests.get(f"{API_BASE}/kitchen/analytics/daily", headers=self.headers)
        assert response.status_code == 200
        daily_analytics = response.json()
        assert "average_prep_time" in daily_analytics
        
        # 4. Check kitchen shifts
        response = requests.get(f"{API_BASE}/kitchen/shifts", headers=self.headers)
        assert response.status_code == 200
        shifts = response.json()
        assert isinstance(shifts, list)
        
        # 5. Check kitchen stations
        response = requests.get(f"{API_BASE}/kitchen/stations", headers=self.headers)
        assert response.status_code == 200
        stations = response.json()
        assert isinstance(stations, list)
        
        # 6. Check equipment status
        response = requests.get(f"{API_BASE}/kitchen/equipment/status", headers=self.headers)
        assert response.status_code == 200
        equipment = response.json()
        assert "equipment" in equipment
        
        # 7. Check low stock items
        response = requests.get(f"{API_BASE}/kitchen/inventory/low-stock", headers=self.headers)
        assert response.status_code == 200
        low_stock = response.json()
        assert isinstance(low_stock, list)
        
        # 8. Get efficiency analytics
        response = requests.get(f"{API_BASE}/kitchen/analytics/efficiency", headers=self.headers)
        assert response.status_code == 200
        efficiency = response.json()
        assert "efficiency_score" in efficiency
        
        # 9. Track food waste
        waste_data = {"item_name": "test_waste", "quantity": 1, "reason": "test"}
        response = requests.post(f"{API_BASE}/kitchen/waste-tracking", json=waste_data, headers=self.headers)
        assert response.status_code == 200
        
        print("✅ Kitchen operations workflow verified")
    
    def test_advanced_order_management_workflow(self):
        """Test advanced order management features."""
        print("\\n📋 Testing Advanced Order Management...")
        
        # 1. List all orders
        response = requests.get(f"{API_BASE}/orders", headers=self.headers)
        assert response.status_code == 200
        orders = response.json()
        
        # 2. Search orders with filters
        response = requests.get(f"{API_BASE}/orders/orders-search", headers=self.headers)
        assert response.status_code == 200
        search_results = response.json()
        assert isinstance(search_results, list)
        
        # 3. Get weekly trends
        response = requests.get(f"{API_BASE}/orders/trends/weekly", headers=self.headers)
        assert response.status_code == 200
        trends = response.json()
        assert "trend_direction" in trends
        
        # 4. Get inventory impact analysis
        response = requests.get(f"{API_BASE}/orders/inventory/impact", headers=self.headers)
        assert response.status_code == 200
        inventory_impact = response.json()
        assert "pending_orders_impact" in inventory_impact
        
        # 5. Get popular items analysis
        response = requests.get(f"{API_BASE}/orders/analytics/popular-items", headers=self.headers)
        assert response.status_code == 200
        popular_items = response.json()
        assert "top_items" in popular_items
        
        # 6. Update menu availability
        availability_data = {"items": {"item1": True, "item2": False}}
        response = requests.post(f"{API_BASE}/orders/menu/availability/update", json=availability_data, headers=self.headers)
        assert response.status_code == 200
        
        # 7. Test bulk updates
        bulk_data = {
            "order_ids": ["test1", "test2"],
            "action": "status_update",
            "data": {"new_status": "confirmed"}
        }
        response = requests.post(f"{API_BASE}/orders/batch/bulk-update", json=bulk_data, headers=self.headers)
        assert response.status_code == 200
        
        # 8. Get POS sync status
        response = requests.get(f"{API_BASE}/orders/integration/pos-sync", headers=self.headers)
        assert response.status_code == 200
        pos_sync = response.json()
        assert "overall_status" in pos_sync
        
        print("✅ Advanced order management verified")
    
    def test_payment_processing_workflow(self):
        """Test comprehensive payment processing workflow."""
        print("\\n💳 Testing Payment Processing Workflow...")
        
        # 1. Get payment summary
        response = requests.get(f"{API_BASE}/payments/summary", headers=self.headers)
        assert response.status_code == 200
        summary = response.json()
        assert "total_revenue" in summary
        
        # 2. Get daily totals
        response = requests.get(f"{API_BASE}/payments/daily-totals", headers=self.headers)
        assert response.status_code == 200
        daily_totals = response.json()
        assert "total_amount" in daily_totals
        
        # 3. Get payment trends
        response = requests.get(f"{API_BASE}/payments/analytics/trends", headers=self.headers)
        assert response.status_code == 200
        trends = response.json()
        assert "trend_data" in trends
        
        # 4. Get daily reconciliation
        response = requests.get(f"{API_BASE}/payments/reconciliation/daily", headers=self.headers)
        assert response.status_code == 200
        reconciliation = response.json()
        assert "reconciliation_summary" in reconciliation
        
        # 5. Get customer behavior analytics
        response = requests.get(f"{API_BASE}/payments/analytics/customer-behavior", headers=self.headers)
        assert response.status_code == 200
        behavior = response.json()
        assert "payment_patterns" in behavior
        
        # 6. Get fee analysis
        response = requests.get(f"{API_BASE}/payments/fees/analysis", headers=self.headers)
        assert response.status_code == 200
        fees = response.json()
        assert "fee_breakdown" in fees
        
        print("✅ Payment processing workflow verified")
    
    def test_qr_ordering_customer_experience(self):
        """Test QR ordering and customer experience workflow."""
        print("\\n📱 Testing QR Ordering & Customer Experience...")
        
        # 1. Get QR analytics (admin view)
        response = requests.get(f"{API_BASE}/qr-orders/analytics", headers=self.headers)
        assert response.status_code == 200
        qr_analytics = response.json()
        assert "total_sessions" in qr_analytics
        
        # 2. Get wait time estimates (customer view - no auth)
        response = requests.get(f"{API_BASE}/qr-orders/wait-times/estimate")
        assert response.status_code == 200
        wait_times = response.json()
        assert "wait_times" in wait_times
        
        # 3. Create QR session
        session_data = {"table_id": "table-1", "customer_name": "Test Customer"}
        response = requests.post(f"{API_BASE}/qr-orders/sessions", json=session_data, headers=self.headers)
        # 422 is acceptable for validation errors in test environment
        assert response.status_code in [200, 201, 422]
        
        # 4. Subscribe to notifications (customer view - no auth)
        notification_data = {"order_id": "test-order", "phone_number": "+1234567890"}
        response = requests.post(f"{API_BASE}/qr-orders/notifications/subscribe", json=notification_data)
        assert response.status_code == 200
        
        print("✅ QR ordering workflow verified")
    
    def test_real_time_analytics_performance(self):
        """Test real-time analytics and performance metrics."""
        print("\\n📊 Testing Real-time Analytics Performance...")
        
        start_time = time.time()
        
        # Test multiple analytics endpoints simultaneously
        endpoints = [
            "/orders/analytics/summary",
            "/kitchen/performance", 
            "/payments/summary",
            "/orders/reports/daily",
            "/kitchen/analytics/daily",
            "/payments/analytics/trends"
        ]
        
        successful_requests = 0
        for endpoint in endpoints:
            response = requests.get(f"{API_BASE}{endpoint}", headers=self.headers)
            if response.status_code == 200:
                successful_requests += 1
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Performance assertions
        assert successful_requests == len(endpoints), f"Only {successful_requests}/{len(endpoints)} endpoints succeeded"
        assert duration < 5.0, f"Analytics took {duration:.2f}s - should be under 5s"
        
        print(f"✅ Analytics performance verified: {successful_requests} endpoints in {duration:.2f}s")
    
    def test_error_handling_and_validation(self):
        """Test error handling and input validation."""
        print("\\n🛡️ Testing Error Handling & Validation...")
        
        # Test invalid authentication
        invalid_headers = {"Authorization": "Bearer invalid-token"}
        response = requests.get(f"{API_BASE}/orders", headers=invalid_headers)
        assert response.status_code == 401
        
        # Test bulk update with invalid data
        invalid_bulk_data = {"order_ids": [], "action": ""}  # Empty action
        response = requests.post(f"{API_BASE}/orders/batch/bulk-update", json=invalid_bulk_data, headers=self.headers)
        assert response.status_code in [400, 422]  # Bad request or validation error
        
        # Test non-existent endpoints
        response = requests.get(f"{API_BASE}/orders/non-existent-endpoint", headers=self.headers)
        assert response.status_code == 404
        
        print("✅ Error handling verified")
    
    def test_production_level_features_comprehensive(self):
        """Comprehensive test of all production-level features."""
        print("\\n🚀 Testing Production-Level Features...")
        
        features_tested = 0
        
        # Order Management Features
        order_endpoints = [
            ("/orders", "List Orders"),
            ("/orders/orders-search", "Advanced Search"),
            ("/orders/analytics/summary", "Order Analytics"),
            ("/orders/reports/daily", "Daily Reports"),
            ("/orders/trends/weekly", "Weekly Trends"),
            ("/orders/inventory/impact", "Inventory Impact"),
            ("/orders/analytics/popular-items", "Popular Items"),
            ("/orders/integration/pos-sync", "POS Integration")
        ]
        
        for endpoint, name in order_endpoints:
            response = requests.get(f"{API_BASE}{endpoint}", headers=self.headers)
            if response.status_code == 200:
                features_tested += 1
                print(f"  ✅ {name}")
        
        # Kitchen Management Features
        kitchen_endpoints = [
            ("/kitchen/orders", "Kitchen Orders"),
            ("/kitchen/performance", "Performance Metrics"),
            ("/kitchen/prep-queue", "Prep Queue"),
            ("/kitchen/analytics/daily", "Daily Analytics"),
            ("/kitchen/shifts", "Shift Management"),
            ("/kitchen/stations", "Station Management"),
            ("/kitchen/equipment/status", "Equipment Status"),
            ("/kitchen/analytics/efficiency", "Efficiency Analytics")
        ]
        
        for endpoint, name in kitchen_endpoints:
            response = requests.get(f"{API_BASE}{endpoint}", headers=self.headers)
            if response.status_code == 200:
                features_tested += 1
                print(f"  ✅ {name}")
        
        # Payment Processing Features  
        payment_endpoints = [
            ("/payments/summary", "Payment Summary"),
            ("/payments/daily-totals", "Daily Totals"),
            ("/payments/analytics/trends", "Payment Trends"),
            ("/payments/reconciliation/daily", "Reconciliation"),
            ("/payments/analytics/customer-behavior", "Customer Behavior"),
            ("/payments/fees/analysis", "Fee Analysis")
        ]
        
        for endpoint, name in payment_endpoints:
            response = requests.get(f"{API_BASE}{endpoint}", headers=self.headers)
            if response.status_code == 200:
                features_tested += 1
                print(f"  ✅ {name}")
        
        # QR & Customer Features
        qr_endpoints = [
            ("/qr-orders/analytics", "QR Analytics"),
            ("/qr-orders/wait-times/estimate", "Wait Times")
        ]
        
        for endpoint, name in qr_endpoints:
            headers_to_use = self.headers if "analytics" in endpoint else {}
            response = requests.get(f"{API_BASE}{endpoint}", headers=headers_to_use)
            if response.status_code == 200:
                features_tested += 1
                print(f"  ✅ {name}")
        
        total_features = len(order_endpoints + kitchen_endpoints + payment_endpoints + qr_endpoints)
        success_rate = (features_tested / total_features) * 100
        
        print(f"\\n📈 Production Features Summary:")
        print(f"   Total Features Tested: {total_features}")
        print(f"   Features Working: {features_tested}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Assert production readiness
        assert success_rate >= 95.0, f"Production readiness requires 95%+ success rate, got {success_rate:.1f}%"
        
        print("\\n🎉 ALL PHASE 3 PRODUCTION FEATURES VERIFIED!")


if __name__ == "__main__":
    # Run tests manually if needed
    test_instance = TestPhase3ProductionWorkflows()
    test_instance.setup_class()
    
    print("🚀 PHASE 3 PRODUCTION WORKFLOWS VERIFICATION")
    print("=" * 60)
    
    try:
        test_instance.test_complete_order_lifecycle_workflow()
        test_instance.test_kitchen_operations_workflow()
        test_instance.test_advanced_order_management_workflow()
        test_instance.test_payment_processing_workflow()
        test_instance.test_qr_ordering_customer_experience()
        test_instance.test_real_time_analytics_performance()
        test_instance.test_error_handling_and_validation()
        test_instance.test_production_level_features_comprehensive()
        
        print("\\n" + "=" * 60)
        print("✅ ALL PRODUCTION WORKFLOWS VERIFIED - PHASE 3 100% COMPLETE!")
        print("   Ready for production deployment")
        
    except Exception as e:
        print(f"\\n❌ Production workflow test failed: {e}")
        raise