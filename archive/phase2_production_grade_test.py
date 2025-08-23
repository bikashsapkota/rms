#!/usr/bin/env python3
"""
Phase 2 Production-Grade Testing Suite
Comprehensive testing for Table and Reservation Management.
"""

import requests
import json
import time
import asyncio
import threading
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import string

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class Phase2ProductionTester:
    """Production-grade testing for Phase 2 Table and Reservation Management."""
    
    def __init__(self):
        self.auth_headers = None
        self.restaurant_id = None
        self.organization_id = None
        self.test_results = {
            "table_management": [],
            "reservation_system": [],
            "availability_management": [],
            "waitlist_functionality": [],
            "public_endpoints": [],
            "security": [],
            "performance": [],
            "data_integrity": [],
            "error_handling": []
        }
        self.test_data = {}
        
    def log_test_result(self, category, test_name, success, details=None, response_time=None):
        """Log test result with details."""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results[category].append(result)
        status = "✅" if success else "❌"
        time_info = f" ({response_time:.3f}s)" if response_time else ""
        print(f"  {status} {test_name}{time_info}")
        if not success and details:
            print(f"    Details: {details}")
    
    def setup_test_environment(self):
        """Set up test environment for Phase 2."""
        print("🏗️ Setting up Phase 2 test environment...")
        
        timestamp = int(time.time())
        test_data = {
            "restaurant_name": f"Phase2 Test {timestamp}",
            "admin_user": {
                "email": f"phase2.test.{timestamp}@example.com",
                "password": "SecurePassword123!",
                "full_name": "Phase2 Test Admin"
            }
        }
        
        try:
            # Setup restaurant
            response = requests.post(f"{BASE_URL}/setup", json=test_data)
            if response.status_code != 200:
                print(f"❌ Setup failed: {response.status_code}")
                return False
            
            setup_result = response.json()
            self.restaurant_id = setup_result["restaurant"]["id"]
            self.organization_id = setup_result["organization"]["id"]
            
            # Authenticate
            auth_data = {
                "email": test_data["admin_user"]["email"],
                "password": test_data["admin_user"]["password"]
            }
            response = requests.post(f"{API_BASE}/auth/login", json=auth_data)
            if response.status_code != 200:
                print(f"❌ Auth failed: {response.status_code}")
                return False
            
            auth_result = response.json()
            token = auth_result["access_token"]
            self.auth_headers = {"Authorization": f"Bearer {token}"}
            
            print("✅ Phase 2 test environment ready")
            return True
            
        except Exception as e:
            print(f"❌ Setup error: {e}")
            return False
    
    def test_table_management(self):
        """Test table management functionality."""
        print("\n🪑 Testing Table Management...")
        
        # Test 1: List tables (should be empty initially)
        start_time = time.time()
        response = requests.get(f"{API_BASE}/tables/", headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("table_management", "List Tables", success, 
                           f"Status: {response.status_code}", response_time)
        
        # Test 2: Create table
        table_data = {
            "table_number": "T001",
            "capacity": 4,
            "table_type": "standard",
            "location": "main_dining",
            "is_active": True
        }
        start_time = time.time()
        response = requests.post(f"{API_BASE}/tables/", json=table_data, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code in [200, 201]
        self.log_test_result("table_management", "Create Table", success,
                           f"Status: {response.status_code}", response_time)
        
        table_id = None
        if success and response.status_code in [200, 201]:
            table_result = response.json()
            table_id = table_result.get("id")
            self.test_data["table_id"] = table_id
            
            # Test 3: Get specific table
            start_time = time.time()
            response = requests.get(f"{API_BASE}/tables/{table_id}", headers=self.auth_headers)
            response_time = time.time() - start_time
            success = response.status_code == 200
            self.log_test_result("table_management", "Get Table Details", success,
                               f"Status: {response.status_code}", response_time)
            
            # Test 4: Update table
            update_data = {"capacity": 6}
            start_time = time.time()
            response = requests.put(f"{API_BASE}/tables/{table_id}", json=update_data, headers=self.auth_headers)
            response_time = time.time() - start_time
            success = response.status_code == 200
            self.log_test_result("table_management", "Update Table", success,
                               f"Status: {response.status_code}", response_time)
            
            # Test 5: Update table status
            start_time = time.time()
            response = requests.put(f"{API_BASE}/tables/{table_id}/status", 
                                  json={"status": "occupied"}, headers=self.auth_headers)
            response_time = time.time() - start_time
            success = response.status_code == 200
            self.log_test_result("table_management", "Update Table Status", success,
                               f"Status: {response.status_code}", response_time)
        
        # Test 6: Table layout view
        start_time = time.time()
        response = requests.get(f"{API_BASE}/tables/layout/restaurant", headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("table_management", "Get Table Layout", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 7: Table availability overview
        start_time = time.time()
        response = requests.get(f"{API_BASE}/tables/availability/overview", headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("table_management", "Table Availability Overview", success,
                           f"Status: {response.status_code}", response_time)
    
    def test_reservation_system(self):
        """Test reservation system functionality."""
        print("\n📅 Testing Reservation System...")
        
        # Test 1: List reservations
        start_time = time.time()
        response = requests.get(f"{API_BASE}/reservations/", headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("reservation_system", "List Reservations", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 2: Create reservation
        reservation_datetime = datetime.now() + timedelta(hours=2)
        reservation_data = {
            "customer_name": "John Doe",
            "customer_phone": "+1234567890",
            "customer_email": "john.doe@example.com",
            "party_size": 4,
            "reservation_date": reservation_datetime.date().isoformat(),
            "reservation_time": reservation_datetime.time().strftime("%H:%M:%S"),
            "special_requests": "Window table preferred"
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/reservations/", json=reservation_data, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code in [200, 201]
        self.log_test_result("reservation_system", "Create Reservation", success,
                           f"Status: {response.status_code}", response_time)
        
        reservation_id = None
        if success and response.status_code in [200, 201]:
            reservation_result = response.json()
            reservation_id = reservation_result.get("id")
            self.test_data["reservation_id"] = reservation_id
            
            # Test 3: Get specific reservation
            start_time = time.time()
            response = requests.get(f"{API_BASE}/reservations/{reservation_id}", headers=self.auth_headers)
            response_time = time.time() - start_time
            success = response.status_code == 200
            self.log_test_result("reservation_system", "Get Reservation Details", success,
                               f"Status: {response.status_code}", response_time)
            
            # Test 4: Update reservation
            update_data = {"party_size": 6}
            start_time = time.time()
            response = requests.put(f"{API_BASE}/reservations/{reservation_id}", json=update_data, headers=self.auth_headers)
            response_time = time.time() - start_time
            success = response.status_code == 200
            self.log_test_result("reservation_system", "Update Reservation", success,
                               f"Status: {response.status_code}", response_time)
            
            # Test 5: Check-in reservation
            start_time = time.time()
            response = requests.post(f"{API_BASE}/reservations/{reservation_id}/checkin", headers=self.auth_headers)
            response_time = time.time() - start_time
            success = response.status_code == 200
            self.log_test_result("reservation_system", "Check-in Reservation", success,
                               f"Status: {response.status_code}", response_time)
            
            # Test 6: Seat reservation (assign table)
            if self.test_data.get("table_id"):
                seat_data = {"table_id": self.test_data["table_id"]}
                start_time = time.time()
                response = requests.post(f"{API_BASE}/reservations/{reservation_id}/seat", 
                                       json=seat_data, headers=self.auth_headers)
                response_time = time.time() - start_time
                success = response.status_code == 200
                self.log_test_result("reservation_system", "Seat Reservation", success,
                                   f"Status: {response.status_code}", response_time)
        
        # Test 7: Today's overview
        start_time = time.time()
        response = requests.get(f"{API_BASE}/reservations/today/overview", headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("reservation_system", "Today's Overview", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 8: Calendar view
        start_time = time.time()
        today = datetime.now().date()
        params = {
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=7)).isoformat()
        }
        response = requests.get(f"{API_BASE}/reservations/calendar/view", params=params, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("reservation_system", "Calendar View", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 9: Analytics summary
        start_time = time.time()
        today = datetime.now().date()
        params = {
            "start_date": (today - timedelta(days=30)).isoformat(),
            "end_date": today.isoformat()
        }
        response = requests.get(f"{API_BASE}/reservations/analytics/summary", params=params, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("reservation_system", "Analytics Summary", success,
                           f"Status: {response.status_code}", response_time)
    
    def test_availability_management(self):
        """Test availability management."""
        print("\n📆 Testing Availability Management...")
        
        # Test 1: Get availability slots
        start_time = time.time()
        today = datetime.now().date()
        params = {
            "date": today.isoformat(),
            "party_size": 4
        }
        response = requests.get(f"{API_BASE}/availability/slots", params=params, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("availability_management", "Get Availability Slots", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 2: Get availability calendar
        start_time = time.time()
        params = {
            "year": today.year,
            "month": today.month
        }
        response = requests.get(f"{API_BASE}/availability/calendar", params=params, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("availability_management", "Get Availability Calendar", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 3: Get alternative times
        start_time = time.time()
        params = {
            "preferred_date": today.isoformat(),
            "preferred_time": "19:00:00",
            "party_size": 4
        }
        response = requests.get(f"{API_BASE}/availability/alternatives", params=params, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("availability_management", "Get Alternative Times", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 4: Capacity optimization
        start_time = time.time()
        params = {
            "target_date": today.isoformat()
        }
        response = requests.get(f"{API_BASE}/availability/capacity/optimization", params=params, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("availability_management", "Capacity Optimization", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 5: Availability overview
        start_time = time.time()
        params = {
            "start_date": today.isoformat(),
            "end_date": (today + timedelta(days=7)).isoformat()
        }
        response = requests.get(f"{API_BASE}/availability/overview", params=params, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("availability_management", "Availability Overview", success,
                           f"Status: {response.status_code}", response_time)
    
    def test_waitlist_functionality(self):
        """Test waitlist functionality."""
        print("\n⏰ Testing Waitlist Functionality...")
        
        # Test 1: List waitlist entries
        start_time = time.time()
        response = requests.get(f"{API_BASE}/waitlist/", headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("waitlist_functionality", "List Waitlist", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 2: Add to waitlist
        waitlist_data = {
            "customer_name": "Jane Smith",
            "customer_phone": "+1987654321",
            "party_size": 2,
            "estimated_wait_time": 30,
            "special_requests": "High chair needed"
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/waitlist/", json=waitlist_data, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code in [200, 201]
        self.log_test_result("waitlist_functionality", "Add to Waitlist", success,
                           f"Status: {response.status_code}", response_time)
        
        waitlist_id = None
        if success and response.status_code in [200, 201]:
            waitlist_result = response.json()
            waitlist_id = waitlist_result.get("id")
            self.test_data["waitlist_id"] = waitlist_id
            
            # Test 3: Get specific waitlist entry
            start_time = time.time()
            response = requests.get(f"{API_BASE}/waitlist/{waitlist_id}", headers=self.auth_headers)
            response_time = time.time() - start_time
            success = response.status_code == 200
            self.log_test_result("waitlist_functionality", "Get Waitlist Entry", success,
                               f"Status: {response.status_code}", response_time)
            
            # Test 4: Update waitlist entry
            update_data = {"estimated_wait_time": 20}
            start_time = time.time()
            response = requests.put(f"{API_BASE}/waitlist/{waitlist_id}", json=update_data, headers=self.auth_headers)
            response_time = time.time() - start_time
            success = response.status_code == 200
            self.log_test_result("waitlist_functionality", "Update Waitlist Entry", success,
                               f"Status: {response.status_code}", response_time)
            
            # Test 5: Notify customer
            start_time = time.time()
            response = requests.post(f"{API_BASE}/waitlist/{waitlist_id}/notify", headers=self.auth_headers)
            response_time = time.time() - start_time
            success = response.status_code == 200
            self.log_test_result("waitlist_functionality", "Notify Customer", success,
                               f"Status: {response.status_code}", response_time)
            
            # Test 6: Mark as seated
            if self.test_data.get("table_id"):
                seat_data = {"table_id": self.test_data["table_id"]}
                start_time = time.time()
                response = requests.post(f"{API_BASE}/waitlist/{waitlist_id}/seated", 
                                       json=seat_data, headers=self.auth_headers)
                response_time = time.time() - start_time
                success = response.status_code == 200
                self.log_test_result("waitlist_functionality", "Mark as Seated", success,
                                   f"Status: {response.status_code}", response_time)
        
        # Test 7: Waitlist analytics
        start_time = time.time()
        today = datetime.now().date()
        params = {
            "start_date": (today - timedelta(days=30)).isoformat(),
            "end_date": today.isoformat()
        }
        response = requests.get(f"{API_BASE}/waitlist/analytics/summary", params=params, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("waitlist_functionality", "Waitlist Analytics", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 8: Check availability for waitlist
        start_time = time.time()
        response = requests.get(f"{API_BASE}/waitlist/availability/check", headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("waitlist_functionality", "Check Waitlist Availability", success,
                           f"Status: {response.status_code}", response_time)
    
    def test_public_endpoints(self):
        """Test public customer-facing endpoints."""
        print("\n🌐 Testing Public Endpoints...")
        
        # Test 1: Public availability check
        start_time = time.time()
        today = datetime.now().date()
        params = {
            "date": today.isoformat(),
            "party_size": 4
        }
        response = requests.get(f"{API_BASE}/public/{self.restaurant_id}/availability", params=params)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("public_endpoints", "Public Availability Check", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 2: Public booking
        booking_datetime = datetime.now() + timedelta(hours=3)
        booking_data = {
            "customer_name": "Public Customer",
            "customer_phone": "+1555123456",
            "customer_email": "customer@example.com",
            "party_size": 3,
            "reservation_date": booking_datetime.date().isoformat(),
            "reservation_time": booking_datetime.time().strftime("%H:%M:%S")
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/public/{self.restaurant_id}/book", json=booking_data)
        response_time = time.time() - start_time
        success = response.status_code in [200, 201]
        self.log_test_result("public_endpoints", "Public Booking", success,
                           f"Status: {response.status_code}", response_time)
        
        public_reservation_id = None
        if success and response.status_code in [200, 201]:
            booking_result = response.json()
            public_reservation_id = booking_result.get("reservation_id")
            
            # Test 3: Check booking status
            start_time = time.time()
            response = requests.get(f"{API_BASE}/public/{self.restaurant_id}/status", 
                                  params={"reservation_id": public_reservation_id})
            response_time = time.time() - start_time
            success = response.status_code == 200
            self.log_test_result("public_endpoints", "Check Booking Status", success,
                               f"Status: {response.status_code}", response_time)
            
            # Test 4: Cancel booking
            start_time = time.time()
            response = requests.delete(f"{API_BASE}/public/{self.restaurant_id}/cancel/{public_reservation_id}")
            response_time = time.time() - start_time
            success = response.status_code in [200, 204]
            self.log_test_result("public_endpoints", "Cancel Booking", success,
                               f"Status: {response.status_code}", response_time)
        
        # Test 5: Join waitlist
        waitlist_data = {
            "customer_name": "Waitlist Customer",
            "customer_phone": "+1555987654",
            "party_size": 2
        }
        
        start_time = time.time()
        response = requests.post(f"{API_BASE}/public/{self.restaurant_id}/waitlist", json=waitlist_data)
        response_time = time.time() - start_time
        success = response.status_code in [200, 201]
        self.log_test_result("public_endpoints", "Join Waitlist", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 6: Check waitlist status
        start_time = time.time()
        response = requests.get(f"{API_BASE}/public/{self.restaurant_id}/waitlist/status")
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("public_endpoints", "Check Waitlist Status", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 7: Restaurant info
        start_time = time.time()
        response = requests.get(f"{API_BASE}/public/{self.restaurant_id}/info")
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("public_endpoints", "Get Restaurant Info", success,
                           f"Status: {response.status_code}", response_time)
    
    def test_security_and_validation(self):
        """Test security and validation measures."""
        print("\n🔒 Testing Security & Validation...")
        
        # Test 1: Unauthorized access to admin endpoints
        start_time = time.time()
        response = requests.get(f"{API_BASE}/tables/")
        response_time = time.time() - start_time
        success = response.status_code in [401, 403]
        self.log_test_result("security", "Unauthorized Access Protection", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 2: Invalid UUID handling
        start_time = time.time()
        response = requests.get(f"{API_BASE}/tables/invalid-uuid", headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 400
        self.log_test_result("security", "Invalid UUID Handling", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 3: Invalid reservation data
        invalid_data = {
            "customer_name": "",  # Empty name
            "party_size": -1,     # Negative party size
            "reservation_time": "invalid-date"
        }
        start_time = time.time()
        response = requests.post(f"{API_BASE}/reservations/", json=invalid_data, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 422
        self.log_test_result("security", "Invalid Data Validation", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 4: XSS protection in customer data
        xss_data = {
            "customer_name": "<script>alert('xss')</script>",
            "customer_phone": "+1234567890",
            "party_size": 2,
            "reservation_time": (datetime.now() + timedelta(hours=1)).isoformat()
        }
        start_time = time.time()
        response = requests.post(f"{API_BASE}/reservations/", json=xss_data, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 422
        self.log_test_result("security", "XSS Protection", success,
                           f"Status: {response.status_code}", response_time)
    
    def test_performance_and_concurrency(self):
        """Test performance under load."""
        print("\n⚡ Testing Performance & Concurrency...")
        
        # Test 1: Response time for key operations
        operations = [
            ("List Tables", lambda: requests.get(f"{API_BASE}/tables/", headers=self.auth_headers)),
            ("List Reservations", lambda: requests.get(f"{API_BASE}/reservations/", headers=self.auth_headers)),
            ("Check Availability", lambda: requests.get(f"{API_BASE}/availability/slots", 
                                                       params={"date": datetime.now().date().isoformat(), "party_size": 4}, 
                                                       headers=self.auth_headers)),
            ("List Waitlist", lambda: requests.get(f"{API_BASE}/waitlist/", headers=self.auth_headers))
        ]
        
        for operation_name, operation in operations:
            times = []
            for i in range(5):  # 5 requests per operation
                start_time = time.time()
                response = operation()
                response_time = time.time() - start_time
                times.append(response_time)
                if response.status_code not in [200, 201]:
                    break
            
            avg_time = sum(times) / len(times)
            success = avg_time < 1.0 and all(t < 2.0 for t in times)
            self.log_test_result("performance", f"{operation_name} Response Time", success,
                               f"Avg: {avg_time:.3f}s, Max: {max(times):.3f}s", avg_time)
        
        # Test 2: Concurrent availability checks
        def concurrent_availability_check():
            try:
                start_time = time.time()
                response = requests.get(f"{API_BASE}/availability/slots", 
                                      params={"date": datetime.now().date().isoformat(), "party_size": 4}, 
                                      headers=self.auth_headers)
                response_time = time.time() - start_time
                return response.status_code == 200, response_time
            except Exception:
                return False, 0
        
        print("    Testing concurrent availability checks...")
        with ThreadPoolExecutor(max_workers=10) as executor:
            start_time = time.time()
            futures = [executor.submit(concurrent_availability_check) for _ in range(20)]
            results = [future.result() for future in as_completed(futures)]
            total_time = time.time() - start_time
        
        successful_requests = sum(1 for success, _ in results if success)
        avg_response_time = sum(time for _, time in results) / len(results)
        
        success = successful_requests >= 18 and total_time < 10
        self.log_test_result("performance", "Concurrent Availability Checks", success,
                           f"Success: {successful_requests}/20, Total time: {total_time:.3f}s", avg_response_time)
    
    def generate_comprehensive_report(self):
        """Generate comprehensive Phase 2 report."""
        print("\n" + "=" * 70)
        print("📊 PHASE 2 PRODUCTION-GRADE TEST RESULTS")
        print("=" * 70)
        
        total_tests = 0
        passed_tests = 0
        category_results = {}
        
        for category, tests in self.test_results.items():
            if not tests:
                continue
                
            category_passed = sum(1 for test in tests if test["success"])
            category_total = len(tests)
            category_results[category] = {
                "passed": category_passed,
                "total": category_total,
                "success_rate": (category_passed / category_total) * 100 if category_total > 0 else 0
            }
            
            total_tests += category_total
            passed_tests += category_passed
        
        overall_success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Overall Success Rate: {overall_success_rate:.1f}% ({passed_tests}/{total_tests})")
        print(f"Tests Passed: {passed_tests}")
        print(f"Tests Failed: {total_tests - passed_tests}")
        
        print("\n📋 Category Breakdown:")
        for category, results in category_results.items():
            status = "✅" if results["success_rate"] >= 90 else "⚠️" if results["success_rate"] >= 75 else "❌"
            print(f"   {status} {category.replace('_', ' ').title()}: {results['passed']}/{results['total']} ({results['success_rate']:.1f}%)")
        
        # Performance summary
        performance_tests = self.test_results.get("performance", [])
        if performance_tests:
            print("\n⚡ Performance Summary:")
            for test in performance_tests:
                if test.get("response_time"):
                    status = "✅" if test["response_time"] < 1.0 else "⚠️"
                    print(f"   {status} {test['test']}: {test['response_time']:.3f}s")
        
        # Failed tests details
        failed_tests = []
        for category, tests in self.test_results.items():
            for test in tests:
                if not test["success"]:
                    failed_tests.append(f"{category}: {test['test']} - {test.get('details', 'No details')}")
        
        if failed_tests:
            print("\n❌ Failed Tests:")
            for failed_test in failed_tests:
                print(f"   • {failed_test}")
        
        # Production readiness assessment
        print("\n🎯 Phase 2 Production Readiness Assessment:")
        
        table_mgmt_score = category_results.get("table_management", {}).get("success_rate", 0)
        reservation_score = category_results.get("reservation_system", {}).get("success_rate", 0)
        availability_score = category_results.get("availability_management", {}).get("success_rate", 0)
        waitlist_score = category_results.get("waitlist_functionality", {}).get("success_rate", 0)
        public_score = category_results.get("public_endpoints", {}).get("success_rate", 0)
        security_score = category_results.get("security", {}).get("success_rate", 0)
        performance_score = category_results.get("performance", {}).get("success_rate", 0)
        
        core_functionality_avg = (table_mgmt_score + reservation_score + availability_score + waitlist_score + public_score) / 5
        
        if overall_success_rate >= 95 and security_score >= 90 and performance_score >= 85 and core_functionality_avg >= 90:
            print("   ✅ PHASE 2 PRODUCTION READY")
            print("   All table and reservation management systems meet production standards.")
            assessment = "PRODUCTION_READY"
        elif overall_success_rate >= 85 and security_score >= 80 and core_functionality_avg >= 80:
            print("   ⚠️  PHASE 2 MOSTLY READY")
            print("   Core functionality is solid, minor improvements recommended.")
            assessment = "MOSTLY_READY"
        else:
            print("   ❌ PHASE 2 NOT PRODUCTION READY")
            print("   Critical issues must be resolved before production deployment.")
            assessment = "NOT_PRODUCTION_READY"
        
        # Feature completeness
        print("\n🚀 Phase 2 Feature Assessment:")
        features = [
            ("Table Management", table_mgmt_score),
            ("Reservation System", reservation_score),
            ("Availability Management", availability_score),
            ("Waitlist Functionality", waitlist_score),
            ("Public Customer Access", public_score),
            ("Security & Validation", security_score),
            ("Performance & Scalability", performance_score)
        ]
        
        for feature_name, score in features:
            if score >= 90:
                status = "✅"
            elif score >= 75:
                status = "⚠️"
            else:
                status = "❌"
            print(f"   {status} {feature_name}: {score:.1f}%")
        
        return assessment
    
    def run_comprehensive_phase2_tests(self):
        """Run all Phase 2 production tests."""
        print("🚀 PHASE 2 PRODUCTION-GRADE TESTING")
        print("=" * 70)
        
        if not self.setup_test_environment():
            return False
        
        # Run all test categories
        self.test_table_management()
        self.test_reservation_system()
        self.test_availability_management()
        self.test_waitlist_functionality()
        self.test_public_endpoints()
        self.test_security_and_validation()
        self.test_performance_and_concurrency()
        
        # Generate comprehensive report
        assessment = self.generate_comprehensive_report()
        
        return assessment in ["PRODUCTION_READY", "MOSTLY_READY"]


def main():
    """Run Phase 2 production tests."""
    tester = Phase2ProductionTester()
    
    try:
        success = tester.run_comprehensive_phase2_tests()
        
        if success:
            print("\n✅ Phase 2 production testing completed successfully!")
            exit(0)
        else:
            print("\n❌ Phase 2 production testing encountered issues")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()