#!/usr/bin/env python3
"""
Comprehensive Phase 2 API Testing Suite
Tests all Phase 2 functionality with real data and authentication
"""

import asyncio
import json
import sys
import traceback
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, date, time, timedelta
from tests.api_tester.shared.utils import (
    APITestClient, TestResults, APITestHelper,
    print_test_header, print_success, print_error, print_info
)


class ComprehensivePhase2Tester:
    """Comprehensive Phase 2 API testing with real authentication and data"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = TestResults()
        self.auth_token: Optional[str] = None
        self.organization_id: Optional[str] = None
        self.restaurant_id: Optional[str] = None
        self.user_id: Optional[str] = None
        
        # Test data storage
        self.created_tables: List[str] = []
        self.created_reservations: List[str] = []
        self.created_waitlist: List[str] = []
        
    async def create_test_restaurant_and_authenticate(self, client: APITestClient) -> bool:
        """Create a new test restaurant and authenticate"""
        print_test_header("🔐 Creating Test Restaurant & Authenticating", "🔑")
        
        try:
            # Step 1: Create a new restaurant with admin user
            test_email = f"test.admin.{int(datetime.now().timestamp())}@phase2test.com"
            test_password = "TestPhase2Password123!"
            
            setup_data = {
                "restaurant_name": "Phase 2 Test Restaurant",
                "address": {
                    "street": "123 Phase 2 Test Street",
                    "city": "Test City",
                    "state": "TS",
                    "zip_code": "12345",
                    "country": "US"
                },
                "phone": "+1-555-PHASE2",
                "email": "restaurant@phase2test.com",
                "settings": {
                    "cuisine_type": "american",
                    "price_range": "medium",
                    "accepts_reservations": True,
                    "max_party_size": 8,
                    "reservation_advance_days": 30
                },
                "admin_user": {
                    "email": test_email,
                    "full_name": "Phase 2 Test Admin",
                    "password": test_password
                }
            }
            
            print_info("Creating new test restaurant and admin user...")
            response = await client.post("/setup", json=setup_data)
            
            if response.is_success():
                setup_result = response.json_data
                print_success(f"✅ Restaurant setup successful!")
                # Extract IDs from nested structure
                self.restaurant_id = setup_result.get('restaurant', {}).get('id')
                self.organization_id = setup_result.get('organization', {}).get('id')
                print_info(f"   Restaurant ID: {self.restaurant_id}")
                print_info(f"   Organization ID: {self.organization_id}")
            else:
                print_error(f"❌ Restaurant setup failed: {response.status_code}")
                if response.json_data:
                    print_error(f"   Error: {response.json_data}")
                return False
            
            # Step 2: Login with the created admin user
            login_data = {
                "email": test_email,
                "password": test_password
            }
            
            print_info(f"Logging in with created admin user: {test_email}...")
            response = await client.post("/api/v1/auth/login", json=login_data)
            
            if response.is_success():
                login_result = response.json_data
                self.auth_token = login_result.get("access_token")
                print_success(f"✅ Login successful! Token obtained.")
                
                # Get user details
                headers = {"Authorization": f"Bearer {self.auth_token}"}
                me_response = await client.get("/api/v1/auth/me", headers=headers)
                
                if me_response.is_success():
                    user_data = me_response.json_data
                    self.user_id = user_data.get("id")
                    self.organization_id = user_data.get("organization_id")
                    self.restaurant_id = user_data.get("restaurant_id")
                    
                    print_success(f"✅ User details retrieved:")
                    print_info(f"   User ID: {self.user_id}")
                    print_info(f"   Organization ID: {self.organization_id}")
                    print_info(f"   Restaurant ID: {self.restaurant_id}")
                    
                    return True
                else:
                    print_error(f"❌ Failed to get user details: {me_response.status_code}")
                    # Even if user details fail, we can continue with the organization and restaurant IDs from setup
                    print_info("⚠️  Continuing with setup data (user details endpoint has validation issues)")
                    return True
            else:
                print_error(f"❌ Login failed: {response.status_code}")
                if response.json_data:
                    print_error(f"   Error: {response.json_data}")
                return False
                
        except Exception as e:
            print_error(f"❌ Restaurant setup and authentication error: {str(e)}")
            traceback.print_exc()
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
    
    async def test_table_management_full(self, client: APITestClient) -> Dict[str, Any]:
        """Test complete table management functionality"""
        print_test_header("🪑 Testing Table Management (Full CRUD)", "🪑")
        
        results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "errors": []
        }
        
        headers = self.get_auth_headers()
        
        # Test 1: Create multiple tables
        print_info("Testing table creation...")
        table_data_list = [
            {
                "table_number": "T01",
                "capacity": 2,
                "location": "main_dining",
                "is_active": True
            },
            {
                "table_number": "T02", 
                "capacity": 4,
                "location": "main_dining",
                "is_active": True
            },
            {
                "table_number": "T03",
                "capacity": 6,
                "location": "window_section",
                "is_active": True
            },
            {
                "table_number": "T04",
                "capacity": 8,
                "location": "private_room",
                "is_active": True
            }
        ]
        
        for table_data in table_data_list:
            results["total_tests"] += 1
            try:
                response = await client.post("/api/v1/tables/", json=table_data, headers=headers)
                if response.is_success():
                    table_id = response.json_data.get("id")
                    self.created_tables.append(table_id)
                    print_success(f"✅ Created table {table_data['table_number']}: {table_id}")
                    results["passed_tests"] += 1
                else:
                    print_error(f"❌ Failed to create table {table_data['table_number']}: {response.status_code}")
                    if response.json_data:
                        print_error(f"   Error: {response.json_data}")
                    results["failed_tests"] += 1
                    results["errors"].append(f"Create table {table_data['table_number']}: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Error creating table {table_data['table_number']}: {str(e)}")
                results["failed_tests"] += 1
                results["errors"].append(f"Create table {table_data['table_number']}: {str(e)}")
        
        # Test 2: List all tables
        print_info("Testing table listing...")
        results["total_tests"] += 1
        try:
            response = await client.get("/api/v1/tables/", headers=headers)
            if response.is_success():
                tables = response.json_data
                print_success(f"✅ Listed {len(tables)} tables")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to list tables: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"List tables: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error listing tables: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"List tables: {str(e)}")
        
        # Test 3: Get individual table details
        if self.created_tables:
            table_id = self.created_tables[0]
            print_info(f"Testing get table details for {table_id}...")
            results["total_tests"] += 1
            try:
                response = await client.get(f"/api/v1/tables/{table_id}", headers=headers)
                if response.is_success():
                    table_details = response.json_data
                    print_success(f"✅ Retrieved table details: {table_details.get('number')}")
                    results["passed_tests"] += 1
                else:
                    print_error(f"❌ Failed to get table details: {response.status_code}")
                    results["failed_tests"] += 1
                    results["errors"].append(f"Get table details: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Error getting table details: {str(e)}")
                results["failed_tests"] += 1
                results["errors"].append(f"Get table details: {str(e)}")
        
        # Test 4: Update table status
        if self.created_tables:
            table_id = self.created_tables[0]
            print_info(f"Testing table status update for {table_id}...")
            results["total_tests"] += 1
            try:
                status_data = {"status": "occupied"}
                response = await client.put(f"/api/v1/tables/{table_id}/status", json=status_data, headers=headers)
                if response.is_success():
                    print_success(f"✅ Updated table status to occupied")
                    results["passed_tests"] += 1
                else:
                    print_error(f"❌ Failed to update table status: {response.status_code}")
                    results["failed_tests"] += 1
                    results["errors"].append(f"Update table status: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Error updating table status: {str(e)}")
                results["failed_tests"] += 1
                results["errors"].append(f"Update table status: {str(e)}")
        
        # Test 5: Table availability overview
        print_info("Testing table availability overview...")
        results["total_tests"] += 1
        try:
            response = await client.get("/api/v1/tables/availability/overview", headers=headers)
            if response.is_success():
                availability = response.json_data
                print_success(f"✅ Retrieved availability overview")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to get availability overview: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"Availability overview: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error getting availability overview: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Availability overview: {str(e)}")
        
        # Test 6: Table analytics
        print_info("Testing table analytics...")
        results["total_tests"] += 1
        try:
            response = await client.get("/api/v1/tables/analytics/utilization", headers=headers)
            if response.is_success():
                analytics = response.json_data
                print_success(f"✅ Retrieved table analytics")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to get table analytics: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"Table analytics: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error getting table analytics: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Table analytics: {str(e)}")
        
        return results
    
    async def test_reservation_management_full(self, client: APITestClient) -> Dict[str, Any]:
        """Test complete reservation management functionality"""
        print_test_header("📅 Testing Reservation Management (Full CRUD)", "📅")
        
        results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "errors": []
        }
        
        headers = self.get_auth_headers()
        
        # Test 1: Create multiple reservations
        print_info("Testing reservation creation...")
        
        # Create reservations for different dates and times
        base_date = datetime.now().date() + timedelta(days=1)  # Tomorrow
        reservation_data_list = [
            {
                "customer_name": "John Doe",
                "customer_email": "john@example.com", 
                "customer_phone": "+1-555-1234",
                "party_size": 2,
                "reservation_date": base_date.isoformat(),
                "reservation_time": "18:00",
                "special_requests": "Window seat preferred"
            },
            {
                "customer_name": "Jane Smith",
                "customer_email": "jane@example.com",
                "customer_phone": "+1-555-5678", 
                "party_size": 4,
                "reservation_date": base_date.isoformat(),
                "reservation_time": "19:00",
                "special_requests": "Birthday celebration"
            },
            {
                "customer_name": "Bob Johnson",
                "customer_email": "bob@example.com",
                "customer_phone": "+1-555-9999",
                "party_size": 6,
                "reservation_date": (base_date + timedelta(days=1)).isoformat(),
                "reservation_time": "20:00",
                "special_requests": "Anniversary dinner"
            }
        ]
        
        for reservation_data in reservation_data_list:
            results["total_tests"] += 1
            try:
                response = await client.post("/api/v1/reservations/", json=reservation_data, headers=headers)
                if response.is_success():
                    reservation_id = response.json_data.get("id")
                    self.created_reservations.append(reservation_id)
                    print_success(f"✅ Created reservation for {reservation_data['customer_name']}: {reservation_id}")
                    results["passed_tests"] += 1
                else:
                    print_error(f"❌ Failed to create reservation for {reservation_data['customer_name']}: {response.status_code}")
                    if response.json_data:
                        print_error(f"   Error: {response.json_data}")
                    results["failed_tests"] += 1
                    results["errors"].append(f"Create reservation {reservation_data['customer_name']}: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Error creating reservation for {reservation_data['customer_name']}: {str(e)}")
                results["failed_tests"] += 1
                results["errors"].append(f"Create reservation {reservation_data['customer_name']}: {str(e)}")
        
        # Test 2: List all reservations
        print_info("Testing reservation listing...")
        results["total_tests"] += 1
        try:
            response = await client.get("/api/v1/reservations/", headers=headers)
            if response.is_success():
                reservations = response.json_data
                print_success(f"✅ Listed {len(reservations)} reservations")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to list reservations: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"List reservations: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error listing reservations: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"List reservations: {str(e)}")
        
        # Test 3: Get individual reservation details
        if self.created_reservations:
            reservation_id = self.created_reservations[0]
            print_info(f"Testing get reservation details for {reservation_id}...")
            results["total_tests"] += 1
            try:
                response = await client.get(f"/api/v1/reservations/{reservation_id}", headers=headers)
                if response.is_success():
                    reservation_details = response.json_data
                    print_success(f"✅ Retrieved reservation details: {reservation_details.get('customer_name')}")
                    results["passed_tests"] += 1
                else:
                    print_error(f"❌ Failed to get reservation details: {response.status_code}")
                    results["failed_tests"] += 1
                    results["errors"].append(f"Get reservation details: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Error getting reservation details: {str(e)}")
                results["failed_tests"] += 1
                results["errors"].append(f"Get reservation details: {str(e)}")
        
        # Test 4: Update reservation
        if self.created_reservations:
            reservation_id = self.created_reservations[0]
            print_info(f"Testing reservation update for {reservation_id}...")
            results["total_tests"] += 1
            try:
                update_data = {
                    "party_size": 3,
                    "special_requests": "Updated: Window seat with high chair"
                }
                response = await client.patch(f"/api/v1/reservations/{reservation_id}", json=update_data, headers=headers)
                if response.is_success():
                    print_success(f"✅ Updated reservation successfully")
                    results["passed_tests"] += 1
                else:
                    print_error(f"❌ Failed to update reservation: {response.status_code}")
                    results["failed_tests"] += 1
                    results["errors"].append(f"Update reservation: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Error updating reservation: {str(e)}")
                results["failed_tests"] += 1
                results["errors"].append(f"Update reservation: {str(e)}")
        
        # Test 5: Check-in customer
        if self.created_reservations:
            reservation_id = self.created_reservations[0]
            print_info(f"Testing customer check-in for {reservation_id}...")
            results["total_tests"] += 1
            try:
                checkin_data = {"notes": "Customer arrived on time"}
                response = await client.post(f"/api/v1/reservations/{reservation_id}/checkin", json=checkin_data, headers=headers)
                if response.is_success():
                    print_success(f"✅ Customer checked in successfully")
                    results["passed_tests"] += 1
                else:
                    print_error(f"❌ Failed to check in customer: {response.status_code}")
                    results["failed_tests"] += 1
                    results["errors"].append(f"Customer check-in: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Error checking in customer: {str(e)}")
                results["failed_tests"] += 1
                results["errors"].append(f"Customer check-in: {str(e)}")
        
        # Test 6: Seat customer (assign table)
        if self.created_reservations and len(self.created_tables) > 1:
            reservation_id = self.created_reservations[0]
            table_id = self.created_tables[1]  # Use second table (first one is marked as occupied)
            print_info(f"Testing seat assignment for reservation {reservation_id}...")
            results["total_tests"] += 1
            try:
                seat_data = {"table_id": table_id}
                response = await client.post(f"/api/v1/reservations/{reservation_id}/seat", json=seat_data, headers=headers)
                if response.is_success():
                    print_success(f"✅ Customer seated at table successfully")
                    results["passed_tests"] += 1
                else:
                    print_error(f"❌ Failed to seat customer: {response.status_code}")
                    results["failed_tests"] += 1
                    results["errors"].append(f"Seat customer: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Error seating customer: {str(e)}")
                results["failed_tests"] += 1
                results["errors"].append(f"Seat customer: {str(e)}")
        
        # Test 7: Today's overview
        print_info("Testing today's reservations overview...")
        results["total_tests"] += 1
        try:
            response = await client.get("/api/v1/reservations/today/overview", headers=headers)
            if response.is_success():
                today_overview = response.json_data
                print_success(f"✅ Retrieved today's overview")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to get today's overview: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"Today's overview: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error getting today's overview: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Today's overview: {str(e)}")
        
        # Test 8: Calendar view
        print_info("Testing calendar view...")
        results["total_tests"] += 1
        try:
            today = datetime.now().date()
            next_week = today + timedelta(days=7)
            params = {
                "start_date": today.isoformat(),
                "end_date": next_week.isoformat()
            }
            response = await client.get("/api/v1/reservations/calendar/view", params=params, headers=headers)
            if response.is_success():
                calendar_view = response.json_data
                print_success(f"✅ Retrieved calendar view")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to get calendar view: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"Calendar view: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error getting calendar view: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Calendar view: {str(e)}")
        
        # Test 9: Reservation analytics
        print_info("Testing reservation analytics...")
        results["total_tests"] += 1
        try:
            last_week = datetime.now().date() - timedelta(days=7)
            today = datetime.now().date()
            params = {
                "start_date": last_week.isoformat(),
                "end_date": today.isoformat()
            }
            response = await client.get("/api/v1/reservations/analytics/summary", params=params, headers=headers)
            if response.is_success():
                analytics = response.json_data
                print_success(f"✅ Retrieved reservation analytics")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to get reservation analytics: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"Reservation analytics: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error getting reservation analytics: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Reservation analytics: {str(e)}")
        
        return results
    
    async def test_availability_system_full(self, client: APITestClient) -> Dict[str, Any]:
        """Test complete availability system functionality"""
        print_test_header("⏰ Testing Availability System (Full Functionality)", "⏰")
        
        results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "errors": []
        }
        
        headers = self.get_auth_headers()
        
        # Test 1: Available time slots
        print_info("Testing available time slots...")
        results["total_tests"] += 1
        try:
            tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
            params = {
                "reservation_date": tomorrow,
                "party_size": 4
            }
            response = await client.get("/api/v1/availability/slots", params=params, headers=headers)
            if response.is_success():
                slots = response.json_data
                print_success(f"✅ Retrieved {len(slots) if isinstance(slots, list) else 'availability'} time slots")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to get time slots: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"Time slots: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error getting time slots: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Time slots: {str(e)}")
        
        # Test 2: Availability calendar
        print_info("Testing availability calendar...")
        results["total_tests"] += 1
        try:
            current_date = datetime.now()
            params = {
                "year": current_date.year,
                "month": current_date.month
            }
            response = await client.get("/api/v1/availability/calendar", params=params, headers=headers)
            if response.is_success():
                calendar = response.json_data
                print_success(f"✅ Retrieved availability calendar")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to get availability calendar: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"Availability calendar: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error getting availability calendar: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Availability calendar: {str(e)}")
        
        # Test 3: Availability overview
        print_info("Testing availability overview...")
        results["total_tests"] += 1
        try:
            tomorrow = datetime.now().date() + timedelta(days=1)
            next_week = tomorrow + timedelta(days=7)
            params = {
                "start_date": tomorrow.isoformat(),
                "end_date": next_week.isoformat()
            }
            response = await client.get("/api/v1/availability/overview", params=params, headers=headers)
            if response.is_success():
                overview = response.json_data
                print_success(f"✅ Retrieved availability overview")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to get availability overview: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"Availability overview: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error getting availability overview: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Availability overview: {str(e)}")
        
        # Test 4: Alternative suggestions
        print_info("Testing availability alternatives...")
        results["total_tests"] += 1
        try:
            tomorrow = datetime.now().date() + timedelta(days=1)
            params = {
                "preferred_date": tomorrow.isoformat(),
                "preferred_time": "19:00:00",
                "party_size": 4,
                "duration_minutes": 90
            }
            response = await client.get("/api/v1/availability/alternatives", params=params, headers=headers)
            if response.is_success():
                alternatives = response.json_data
                print_success(f"✅ Retrieved availability alternatives")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to get availability alternatives: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"Availability alternatives: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error getting availability alternatives: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Availability alternatives: {str(e)}")
        
        # Test 5: Capacity optimization
        print_info("Testing capacity optimization...")
        results["total_tests"] += 1
        try:
            tomorrow = datetime.now().date() + timedelta(days=1)
            params = {
                "target_date": tomorrow.isoformat()
            }
            response = await client.get("/api/v1/availability/capacity/optimization", params=params, headers=headers)
            if response.is_success():
                optimization = response.json_data
                print_success(f"✅ Retrieved capacity optimization")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to get capacity optimization: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"Capacity optimization: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error getting capacity optimization: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Capacity optimization: {str(e)}")
        
        return results
    
    async def test_waitlist_management_full(self, client: APITestClient) -> Dict[str, Any]:
        """Test complete waitlist management functionality"""
        print_test_header("📝 Testing Waitlist Management (Full CRUD)", "📝")
        
        results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "errors": []
        }
        
        headers = self.get_auth_headers()
        
        # Test 1: Add customers to waitlist
        print_info("Testing waitlist entry creation...")
        
        waitlist_data_list = [
            {
                "customer_name": "Alice Wilson",
                "customer_email": "alice@example.com",
                "customer_phone": "+1-555-1111",
                "party_size": 2,
                "priority_score": 1,
                "notes": "First time customer"
            },
            {
                "customer_name": "Charlie Brown",
                "customer_email": "charlie@example.com",
                "customer_phone": "+1-555-2222",
                "party_size": 5,
                "priority_score": 2,
                "notes": "Family with children"
            }
        ]
        
        for waitlist_data in waitlist_data_list:
            results["total_tests"] += 1
            try:
                response = await client.post("/api/v1/waitlist/", json=waitlist_data, headers=headers)
                if response.is_success():
                    waitlist_id = response.json_data.get("id")
                    self.created_waitlist.append(waitlist_id)
                    print_success(f"✅ Added {waitlist_data['customer_name']} to waitlist: {waitlist_id}")
                    results["passed_tests"] += 1
                else:
                    print_error(f"❌ Failed to add {waitlist_data['customer_name']} to waitlist: {response.status_code}")
                    if response.json_data:
                        print_error(f"   Error: {response.json_data}")
                    results["failed_tests"] += 1
                    results["errors"].append(f"Add {waitlist_data['customer_name']} to waitlist: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Error adding {waitlist_data['customer_name']} to waitlist: {str(e)}")
                results["failed_tests"] += 1
                results["errors"].append(f"Add {waitlist_data['customer_name']} to waitlist: {str(e)}")
        
        # Test 2: List waitlist entries
        print_info("Testing waitlist listing...")
        results["total_tests"] += 1
        try:
            response = await client.get("/api/v1/waitlist/", headers=headers)
            if response.is_success():
                waitlist = response.json_data
                print_success(f"✅ Listed {len(waitlist)} waitlist entries")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to list waitlist: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"List waitlist: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error listing waitlist: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"List waitlist: {str(e)}")
        
        # Test 3: Get waitlist entry details
        if self.created_waitlist:
            waitlist_id = self.created_waitlist[0]
            print_info(f"Testing get waitlist details for {waitlist_id}...")
            results["total_tests"] += 1
            try:
                response = await client.get(f"/api/v1/waitlist/{waitlist_id}", headers=headers)
                if response.is_success():
                    waitlist_details = response.json_data
                    print_success(f"✅ Retrieved waitlist details: {waitlist_details.get('customer_name')}")
                    results["passed_tests"] += 1
                else:
                    print_error(f"❌ Failed to get waitlist details: {response.status_code}")
                    results["failed_tests"] += 1
                    results["errors"].append(f"Get waitlist details: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Error getting waitlist details: {str(e)}")
                results["failed_tests"] += 1
                results["errors"].append(f"Get waitlist details: {str(e)}")
        
        # Test 4: Update waitlist entry
        if self.created_waitlist:
            waitlist_id = self.created_waitlist[0]
            print_info(f"Testing waitlist update for {waitlist_id}...")
            results["total_tests"] += 1
            try:
                update_data = {
                    "estimated_wait_time": 20,
                    "notes": "Updated: Customer called to confirm"
                }
                response = await client.patch(f"/api/v1/waitlist/{waitlist_id}", json=update_data, headers=headers)
                if response.is_success():
                    print_success(f"✅ Updated waitlist entry successfully")
                    results["passed_tests"] += 1
                else:
                    print_error(f"❌ Failed to update waitlist entry: {response.status_code}")
                    results["failed_tests"] += 1
                    results["errors"].append(f"Update waitlist entry: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Error updating waitlist entry: {str(e)}")
                results["failed_tests"] += 1
                results["errors"].append(f"Update waitlist entry: {str(e)}")
        
        # Test 5: Notify customer
        if self.created_waitlist:
            waitlist_id = self.created_waitlist[0]
            print_info(f"Testing customer notification for {waitlist_id}...")
            results["total_tests"] += 1
            try:
                notify_data = {"message": "Your table is ready!"}
                response = await client.post(f"/api/v1/waitlist/{waitlist_id}/notify", json=notify_data, headers=headers)
                if response.is_success():
                    print_success(f"✅ Customer notified successfully")
                    results["passed_tests"] += 1
                else:
                    print_error(f"❌ Failed to notify customer: {response.status_code}")
                    results["failed_tests"] += 1
                    results["errors"].append(f"Notify customer: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Error notifying customer: {str(e)}")
                results["failed_tests"] += 1
                results["errors"].append(f"Notify customer: {str(e)}")
        
        # Test 6: Mark customer as seated
        if self.created_waitlist:
            waitlist_id = self.created_waitlist[1]  # Use second entry
            print_info(f"Testing mark customer seated for {waitlist_id}...")
            results["total_tests"] += 1
            try:
                response = await client.post(f"/api/v1/waitlist/{waitlist_id}/seated", headers=headers)
                if response.is_success():
                    print_success(f"✅ Customer marked as seated successfully")
                    results["passed_tests"] += 1
                else:
                    print_error(f"❌ Failed to mark customer as seated: {response.status_code}")
                    results["failed_tests"] += 1
                    results["errors"].append(f"Mark customer seated: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Error marking customer as seated: {str(e)}")
                results["failed_tests"] += 1
                results["errors"].append(f"Mark customer seated: {str(e)}")
        
        # Test 7: Waitlist analytics
        print_info("Testing waitlist analytics...")
        results["total_tests"] += 1
        try:
            last_week = datetime.now().date() - timedelta(days=7)
            today = datetime.now().date()
            params = {
                "start_date": last_week.isoformat(),
                "end_date": today.isoformat()
            }
            response = await client.get("/api/v1/waitlist/analytics/summary", params=params, headers=headers)
            if response.is_success():
                analytics = response.json_data
                print_success(f"✅ Retrieved waitlist analytics")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to get waitlist analytics: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"Waitlist analytics: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error getting waitlist analytics: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Waitlist analytics: {str(e)}")
        
        # Test 8: Waitlist availability check
        print_info("Testing waitlist availability check...")
        results["total_tests"] += 1
        try:
            response = await client.get("/api/v1/waitlist/availability/check", headers=headers)
            if response.is_success():
                availability = response.json_data
                print_success(f"✅ Retrieved waitlist availability check")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to get waitlist availability check: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"Waitlist availability check: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error getting waitlist availability check: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Waitlist availability check: {str(e)}")
        
        return results
    
    async def test_public_customer_apis(self, client: APITestClient) -> Dict[str, Any]:
        """Test public customer-facing APIs"""
        print_test_header("🌐 Testing Public Customer APIs", "🌐")
        
        results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "errors": []
        }
        
        # Test with the actual restaurant ID we have
        restaurant_id = self.restaurant_id
        
        # Test 1: Get restaurant info
        print_info(f"Testing restaurant info for {restaurant_id}...")
        results["total_tests"] += 1
        try:
            response = await client.get(f"/api/v1/public/reservations/{restaurant_id}/info")
            if response.is_success():
                info = response.json_data
                print_success(f"✅ Retrieved restaurant info: {info.get('name', 'Restaurant')}")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to get restaurant info: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"Restaurant info: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error getting restaurant info: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Restaurant info: {str(e)}")
        
        # Test 2: Check availability
        print_info("Testing public reservation availability...")
        results["total_tests"] += 1
        try:
            tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
            params = {
                "reservation_date": tomorrow,
                "party_size": 2,
                "time_preference": "19:00:00",
                "duration_minutes": 90
            }
            response = await client.get(f"/api/v1/public/reservations/{restaurant_id}/availability", params=params)
            if response.is_success():
                availability = response.json_data
                print_success(f"✅ Retrieved public availability")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to get public availability: {response.status_code}")
                results["failed_tests"] += 1
                results["errors"].append(f"Public availability: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error getting public availability: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Public availability: {str(e)}")
        
        # Test 3: Book reservation
        print_info("Testing public reservation booking...")
        results["total_tests"] += 1
        try:
            tomorrow = (datetime.now().date() + timedelta(days=2)).isoformat()
            booking_data = {
                "customer_name": "Public Customer",
                "customer_email": "public@example.com",
                "customer_phone": "+1-555-PUBLIC",
                "party_size": 2,
                "reservation_date": tomorrow,
                "reservation_time": "19:00:00",
                "special_requests": "Public booking test"
            }
            response = await client.post(f"/api/v1/public/reservations/{restaurant_id}/book", json=booking_data)
            if response.is_success():
                booking_result = response.json_data
                print_success(f"✅ Public booking successful: {booking_result.get('id')}")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to book reservation: {response.status_code}")
                if response.json_data:
                    print_error(f"   Error: {response.json_data}")
                results["failed_tests"] += 1
                results["errors"].append(f"Public booking: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error booking reservation: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Public booking: {str(e)}")
        
        # Test 4: Join waitlist
        print_info("Testing public waitlist entry...")
        results["total_tests"] += 1
        try:
            waitlist_data = {
                "customer_name": "Public Waitlist Customer",
                "customer_email": "waitlist@example.com",
                "customer_phone": "+1-555-WAIT",
                "party_size": 4,
                "special_requests": "Public waitlist test"
            }
            response = await client.post(f"/api/v1/public/reservations/{restaurant_id}/waitlist", json=waitlist_data)
            if response.is_success():
                waitlist_result = response.json_data
                print_success(f"✅ Public waitlist entry successful")
                results["passed_tests"] += 1
            else:
                print_error(f"❌ Failed to join waitlist: {response.status_code}")
                if response.json_data:
                    print_error(f"   Error: {response.json_data}")
                results["failed_tests"] += 1
                results["errors"].append(f"Public waitlist: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Error joining waitlist: {str(e)}")
            results["failed_tests"] += 1
            results["errors"].append(f"Public waitlist: {str(e)}")
        
        return results
    
    async def run_comprehensive_testing(self) -> Dict[str, Any]:
        """Run comprehensive Phase 2 API testing"""
        print_test_header("🚀 Comprehensive Phase 2 API Testing Suite", "🚀")
        
        async with APITestClient(self.base_url) as client:
            # Step 1: Create test restaurant and authenticate
            if not await self.create_test_restaurant_and_authenticate(client):
                return {
                    "success": False,
                    "error": "Failed to create test restaurant and authenticate",
                    "results": {}
                }
            
            # Step 2: Run all test suites
            print_info("🧪 Running comprehensive test suites...")
            
            table_results = await self.test_table_management_full(client)
            reservation_results = await self.test_reservation_management_full(client)
            availability_results = await self.test_availability_system_full(client)
            waitlist_results = await self.test_waitlist_management_full(client)
            public_results = await self.test_public_customer_apis(client)
            
            # Step 3: Compile comprehensive results
            total_tests = (
                table_results["total_tests"] + 
                reservation_results["total_tests"] +
                availability_results["total_tests"] +
                waitlist_results["total_tests"] +
                public_results["total_tests"]
            )
            
            passed_tests = (
                table_results["passed_tests"] +
                reservation_results["passed_tests"] +
                availability_results["passed_tests"] +
                waitlist_results["passed_tests"] +
                public_results["passed_tests"]
            )
            
            failed_tests = (
                table_results["failed_tests"] +
                reservation_results["failed_tests"] +
                availability_results["failed_tests"] +
                waitlist_results["failed_tests"] +
                public_results["failed_tests"]
            )
            
            all_errors = (
                table_results["errors"] +
                reservation_results["errors"] +
                availability_results["errors"] +
                waitlist_results["errors"] +
                public_results["errors"]
            )
            
            success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
            
            # Print comprehensive summary
            print_test_header("📊 Comprehensive Phase 2 Testing Results", "📊")
            print_info(f"Total Tests Executed: {total_tests}")
            print_success(f"Tests Passed: {passed_tests}")
            if failed_tests > 0:
                print_error(f"Tests Failed: {failed_tests}")
            else:
                print_info(f"Tests Failed: {failed_tests}")
            
            print_info(f"Success Rate: {success_rate:.1f}%")
            
            # Category breakdown
            print_info(f"\n📋 Category Breakdown:")
            print_info(f"  Tables: {table_results['passed_tests']}/{table_results['total_tests']} ({table_results['passed_tests']/table_results['total_tests']*100:.1f}%)")
            print_info(f"  Reservations: {reservation_results['passed_tests']}/{reservation_results['total_tests']} ({reservation_results['passed_tests']/reservation_results['total_tests']*100:.1f}%)")
            print_info(f"  Availability: {availability_results['passed_tests']}/{availability_results['total_tests']} ({availability_results['passed_tests']/availability_results['total_tests']*100:.1f}%)")
            print_info(f"  Waitlist: {waitlist_results['passed_tests']}/{waitlist_results['total_tests']} ({waitlist_results['passed_tests']/waitlist_results['total_tests']*100:.1f}%)")
            print_info(f"  Public APIs: {public_results['passed_tests']}/{public_results['total_tests']} ({public_results['passed_tests']/public_results['total_tests']*100:.1f}%)")
            
            if all_errors:
                print_error(f"\n❌ Errors encountered:")
                for error in all_errors:
                    print_error(f"  - {error}")
            
            # Data created summary
            print_info(f"\n📦 Test Data Created:")
            print_info(f"  Tables: {len(self.created_tables)}")
            print_info(f"  Reservations: {len(self.created_reservations)}")
            print_info(f"  Waitlist Entries: {len(self.created_waitlist)}")
            
            return {
                "success": True,
                "summary": {
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": failed_tests,
                    "success_rate": success_rate,
                    "test_data_created": {
                        "tables": len(self.created_tables),
                        "reservations": len(self.created_reservations),
                        "waitlist_entries": len(self.created_waitlist)
                    }
                },
                "detailed_results": {
                    "table_management": table_results,
                    "reservation_management": reservation_results, 
                    "availability_system": availability_results,
                    "waitlist_management": waitlist_results,
                    "public_apis": public_results
                },
                "errors": all_errors,
                "created_data": {
                    "tables": self.created_tables,
                    "reservations": self.created_reservations,
                    "waitlist": self.created_waitlist
                }
            }


async def main():
    """Main function to run comprehensive Phase 2 testing"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    tester = ComprehensivePhase2Tester(base_url)
    
    try:
        results = await tester.run_comprehensive_testing()
        
        if results["success"]:
            print_test_header("✅ Comprehensive Phase 2 Testing Complete!", "✅")
            
            summary = results["summary"]
            success_rate = summary["success_rate"]
            
            if success_rate >= 90:
                print_success(f"🎉 EXCELLENT: {success_rate:.1f}% success rate!")
                print_success("Phase 2 is working exceptionally well!")
            elif success_rate >= 80:
                print_success(f"✅ GOOD: {success_rate:.1f}% success rate!")
                print_info("Phase 2 is working well with minor issues.")
            elif success_rate >= 70:
                print_info(f"⚠️  FAIR: {success_rate:.1f}% success rate.")
                print_info("Phase 2 has some functionality but needs attention.")
            else:
                print_error(f"❌ NEEDS WORK: {success_rate:.1f}% success rate.")
                print_error("Phase 2 requires significant fixes.")
            
            print_info(f"\n📊 Final Statistics:")
            print_info(f"  Tests Executed: {summary['total_tests']}")
            print_info(f"  Tests Passed: {summary['passed_tests']}")
            print_info(f"  Tests Failed: {summary['failed_tests']}")
            print_info(f"  Data Created: {summary['test_data_created']['tables']} tables, {summary['test_data_created']['reservations']} reservations, {summary['test_data_created']['waitlist_entries']} waitlist")
            
            # Save detailed results
            with open("comprehensive_phase2_test_results.json", "w") as f:
                json.dump(results, f, indent=2, default=str)
            print_info("📄 Detailed results saved to comprehensive_phase2_test_results.json")
            
        else:
            print_error(f"❌ Comprehensive testing failed: {results.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print_error(f"❌ Comprehensive testing crashed: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())