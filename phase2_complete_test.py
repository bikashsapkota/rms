#!/usr/bin/env python3
"""
Phase 2 Complete Testing and Validation Script
Tests all Phase 2 functionality and identifies missing features
"""

import asyncio
import json
import sys
import traceback
from typing import Optional, Dict, Any, List
from tests.api_tester.shared.utils import (
    APITestClient, TestResults, APITestHelper,
    print_test_header, print_success, print_error, print_info
)


class Phase2Tester:
    """Comprehensive Phase 2 testing and validation"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = TestResults()
        self.auth_token: Optional[str] = None
        self.organization_id: Optional[str] = None
        self.restaurant_id: Optional[str] = None
        self.user_id: Optional[str] = None
        
    async def setup_authentication(self, client: APITestClient) -> bool:
        """Set up authentication and test data"""
        print_test_header("Setting Up Authentication and Test Data", "🔐")
        
        try:
            # Step 1: Create organization
            org_data = {
                "name": "Phase 2 Test Restaurant",
                "email": "admin@phase2test.com",
                "phone": "+1-555-PHASE2"
            }
            
            print_info("Creating test organization...")
            response = await client.post("/api/organizations/", json=org_data)
            
            if not response.is_success():
                print_error(f"Failed to create organization: {response.status_code}")
                if response.json_data:
                    print_error(f"Error details: {response.json_data}")
                return False
                
            org_result = response.json_data
            self.organization_id = org_result["id"]
            print_success(f"Created organization: {self.organization_id}")
            
            # Step 2: Create admin user
            user_data = {
                "email": "admin@phase2test.com",
                "full_name": "Phase 2 Admin",
                "role": "admin",
                "password": "secure_phase2_password"
            }
            
            print_info("Creating admin user...")
            response = await client.post(
                f"/api/organizations/{self.organization_id}/users/",
                json=user_data
            )
            
            if not response.is_success():
                print_error(f"Failed to create user: {response.status_code}")
                if response.json_data:
                    print_error(f"Error details: {response.json_data}")
                return False
                
            user_result = response.json_data
            self.user_id = user_result["id"]
            print_success(f"Created user: {self.user_id}")
            
            # Step 3: Login to get authentication token
            login_data = {
                "username": "admin@phase2test.com",
                "password": "secure_phase2_password"
            }
            
            print_info("Logging in to get authentication token...")
            response = await client.post("/api/auth/login", data=login_data)
            
            if not response.is_success():
                print_error(f"Failed to login: {response.status_code}")
                if response.json_data:
                    print_error(f"Error details: {response.json_data}")
                return False
                
            login_result = response.json_data
            self.auth_token = login_result["access_token"]
            print_success("Successfully obtained authentication token")
            
            # Step 4: Create restaurant
            restaurant_data = {
                "name": "Phase 2 Test Restaurant",
                "address": {
                    "street": "123 Phase 2 Street",
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
                }
            }
            
            print_info("Creating test restaurant...")
            headers = {"Authorization": f"Bearer {self.auth_token}"}
            response = await client.post(
                f"/api/organizations/{self.organization_id}/restaurants/",
                json=restaurant_data,
                headers=headers
            )
            
            if not response.is_success():
                print_error(f"Failed to create restaurant: {response.status_code}")
                if response.json_data:
                    print_error(f"Error details: {response.json_data}")
                return False
                
            restaurant_result = response.json_data
            self.restaurant_id = restaurant_result["id"]
            print_success(f"Created restaurant: {self.restaurant_id}")
            
            return True
            
        except Exception as e:
            print_error(f"Authentication setup failed: {str(e)}")
            traceback.print_exc()
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authorization headers"""
        return {"Authorization": f"Bearer {self.auth_token}"} if self.auth_token else {}
    
    async def test_table_management(self, client: APITestClient) -> Dict[str, Any]:
        """Test table management functionality"""
        print_test_header("Testing Table Management", "🪑")
        
        results = {
            "total_endpoints": 0,
            "working_endpoints": 0,
            "failed_endpoints": 0,
            "missing_features": [],
            "errors": []
        }
        
        headers = self.get_auth_headers()
        base_path = f"/api/organizations/{self.organization_id}/restaurants/{self.restaurant_id}"
        
        # Test 1: Create table
        table_data = {
            "number": "T1",
            "capacity": 4,
            "table_type": "standard",
            "location": "main_dining",
            "is_active": True
        }
        
        print_info("Testing table creation...")
        results["total_endpoints"] += 1
        
        try:
            response = await client.post(f"{base_path}/tables/", json=table_data, headers=headers)
            if response.is_success():
                print_success(f"✅ Create table: {response.status_code}")
                results["working_endpoints"] += 1
                table_id = response.json_data.get("id")
            else:
                print_error(f"❌ Create table failed: {response.status_code}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Create table: {response.status_code}")
                table_id = None
        except Exception as e:
            print_error(f"❌ Create table error: {str(e)}")
            results["failed_endpoints"] += 1
            results["errors"].append(f"Create table: {str(e)}")
            table_id = None
        
        # Test 2: List tables
        print_info("Testing table listing...")
        results["total_endpoints"] += 1
        
        try:
            response = await client.get(f"{base_path}/tables/", headers=headers)
            if response.is_success():
                print_success(f"✅ List tables: {response.status_code}")
                results["working_endpoints"] += 1
            else:
                print_error(f"❌ List tables failed: {response.status_code}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"List tables: {response.status_code}")
        except Exception as e:
            print_error(f"❌ List tables error: {str(e)}")
            results["failed_endpoints"] += 1
            results["errors"].append(f"List tables: {str(e)}")
        
        # Test additional table endpoints if table was created
        if table_id:
            # Test 3: Get table by ID
            print_info("Testing get table by ID...")
            results["total_endpoints"] += 1
            
            try:
                response = await client.get(f"{base_path}/tables/{table_id}", headers=headers)
                if response.is_success():
                    print_success(f"✅ Get table: {response.status_code}")
                    results["working_endpoints"] += 1
                else:
                    print_error(f"❌ Get table failed: {response.status_code}")
                    results["failed_endpoints"] += 1
                    results["errors"].append(f"Get table: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Get table error: {str(e)}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Get table: {str(e)}")
            
            # Test 4: Update table
            print_info("Testing table update...")
            results["total_endpoints"] += 1
            
            update_data = {"capacity": 6, "location": "patio"}
            
            try:
                response = await client.patch(f"{base_path}/tables/{table_id}", json=update_data, headers=headers)
                if response.is_success():
                    print_success(f"✅ Update table: {response.status_code}")
                    results["working_endpoints"] += 1
                else:
                    print_error(f"❌ Update table failed: {response.status_code}")
                    results["failed_endpoints"] += 1
                    results["errors"].append(f"Update table: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Update table error: {str(e)}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Update table: {str(e)}")
        
        # Test 5: Table availability check
        print_info("Testing table availability...")
        results["total_endpoints"] += 1
        
        try:
            params = {
                "date": "2024-12-25",
                "time": "19:00",
                "party_size": 4
            }
            response = await client.get(f"{base_path}/tables/availability", params=params, headers=headers)
            if response.is_success():
                print_success(f"✅ Table availability: {response.status_code}")
                results["working_endpoints"] += 1
            else:
                print_error(f"❌ Table availability failed: {response.status_code}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Table availability: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Table availability error: {str(e)}")
            results["failed_endpoints"] += 1
            results["errors"].append(f"Table availability: {str(e)}")
        
        return results
    
    async def test_reservation_management(self, client: APITestClient) -> Dict[str, Any]:
        """Test reservation management functionality"""
        print_test_header("Testing Reservation Management", "📅")
        
        results = {
            "total_endpoints": 0,
            "working_endpoints": 0,
            "failed_endpoints": 0,
            "missing_features": [],
            "errors": []
        }
        
        headers = self.get_auth_headers()
        base_path = f"/api/organizations/{self.organization_id}/restaurants/{self.restaurant_id}"
        
        # Test 1: Create reservation
        reservation_data = {
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "customer_phone": "+1-555-1234",
            "party_size": 4,
            "reservation_date": "2024-12-25",
            "reservation_time": "19:00",
            "special_requests": "Window seat preferred"
        }
        
        print_info("Testing reservation creation...")
        results["total_endpoints"] += 1
        
        try:
            response = await client.post(f"{base_path}/reservations/", json=reservation_data, headers=headers)
            if response.is_success():
                print_success(f"✅ Create reservation: {response.status_code}")
                results["working_endpoints"] += 1
                reservation_id = response.json_data.get("id")
            else:
                print_error(f"❌ Create reservation failed: {response.status_code}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Create reservation: {response.status_code}")
                reservation_id = None
        except Exception as e:
            print_error(f"❌ Create reservation error: {str(e)}")
            results["failed_endpoints"] += 1
            results["errors"].append(f"Create reservation: {str(e)}")
            reservation_id = None
        
        # Test 2: List reservations
        print_info("Testing reservation listing...")
        results["total_endpoints"] += 1
        
        try:
            response = await client.get(f"{base_path}/reservations/", headers=headers)
            if response.is_success():
                print_success(f"✅ List reservations: {response.status_code}")
                results["working_endpoints"] += 1
            else:
                print_error(f"❌ List reservations failed: {response.status_code}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"List reservations: {response.status_code}")
        except Exception as e:
            print_error(f"❌ List reservations error: {str(e)}")
            results["failed_endpoints"] += 1
            results["errors"].append(f"List reservations: {str(e)}")
        
        # Test additional reservation endpoints if reservation was created
        if reservation_id:
            # Test 3: Get reservation by ID
            print_info("Testing get reservation by ID...")
            results["total_endpoints"] += 1
            
            try:
                response = await client.get(f"{base_path}/reservations/{reservation_id}", headers=headers)
                if response.is_success():
                    print_success(f"✅ Get reservation: {response.status_code}")
                    results["working_endpoints"] += 1
                else:
                    print_error(f"❌ Get reservation failed: {response.status_code}")
                    results["failed_endpoints"] += 1
                    results["errors"].append(f"Get reservation: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Get reservation error: {str(e)}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Get reservation: {str(e)}")
            
            # Test 4: Update reservation
            print_info("Testing reservation update...")
            results["total_endpoints"] += 1
            
            update_data = {
                "party_size": 6,
                "special_requests": "Anniversary celebration"
            }
            
            try:
                response = await client.patch(f"{base_path}/reservations/{reservation_id}", json=update_data, headers=headers)
                if response.is_success():
                    print_success(f"✅ Update reservation: {response.status_code}")
                    results["working_endpoints"] += 1
                else:
                    print_error(f"❌ Update reservation failed: {response.status_code}")
                    results["failed_endpoints"] += 1
                    results["errors"].append(f"Update reservation: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Update reservation error: {str(e)}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Update reservation: {str(e)}")
            
            # Test 5: Confirm reservation
            print_info("Testing reservation confirmation...")
            results["total_endpoints"] += 1
            
            try:
                response = await client.post(f"{base_path}/reservations/{reservation_id}/confirm", headers=headers)
                if response.is_success():
                    print_success(f"✅ Confirm reservation: {response.status_code}")
                    results["working_endpoints"] += 1
                else:
                    print_error(f"❌ Confirm reservation failed: {response.status_code}")
                    results["failed_endpoints"] += 1
                    results["errors"].append(f"Confirm reservation: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Confirm reservation error: {str(e)}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Confirm reservation: {str(e)}")
        
        # Test 6: Check availability
        print_info("Testing reservation availability...")
        results["total_endpoints"] += 1
        
        try:
            params = {
                "date": "2024-12-26",
                "time": "20:00",
                "party_size": 2
            }
            response = await client.get(f"{base_path}/reservations/availability", params=params, headers=headers)
            if response.is_success():
                print_success(f"✅ Reservation availability: {response.status_code}")
                results["working_endpoints"] += 1
            else:
                print_error(f"❌ Reservation availability failed: {response.status_code}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Reservation availability: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Reservation availability error: {str(e)}")
            results["failed_endpoints"] += 1
            results["errors"].append(f"Reservation availability: {str(e)}")
        
        return results
    
    async def test_availability_system(self, client: APITestClient) -> Dict[str, Any]:
        """Test availability system functionality"""
        print_test_header("Testing Availability System", "⏰")
        
        results = {
            "total_endpoints": 0,
            "working_endpoints": 0,
            "failed_endpoints": 0,
            "missing_features": [],
            "errors": []
        }
        
        headers = self.get_auth_headers()
        base_path = f"/api/organizations/{self.organization_id}/restaurants/{self.restaurant_id}"
        
        # Test 1: Set availability schedule
        schedule_data = {
            "day_of_week": 1,  # Monday
            "is_open": True,
            "open_time": "11:00",
            "close_time": "22:00",
            "break_start": "15:00",
            "break_end": "17:00"
        }
        
        print_info("Testing availability schedule creation...")
        results["total_endpoints"] += 1
        
        try:
            response = await client.post(f"{base_path}/availability/", json=schedule_data, headers=headers)
            if response.is_success():
                print_success(f"✅ Create availability: {response.status_code}")
                results["working_endpoints"] += 1
                availability_id = response.json_data.get("id")
            else:
                print_error(f"❌ Create availability failed: {response.status_code}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Create availability: {response.status_code}")
                availability_id = None
        except Exception as e:
            print_error(f"❌ Create availability error: {str(e)}")
            results["failed_endpoints"] += 1
            results["errors"].append(f"Create availability: {str(e)}")
            availability_id = None
        
        # Test 2: Get availability schedule
        print_info("Testing availability schedule listing...")
        results["total_endpoints"] += 1
        
        try:
            response = await client.get(f"{base_path}/availability/", headers=headers)
            if response.is_success():
                print_success(f"✅ List availability: {response.status_code}")
                results["working_endpoints"] += 1
            else:
                print_error(f"❌ List availability failed: {response.status_code}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"List availability: {response.status_code}")
        except Exception as e:
            print_error(f"❌ List availability error: {str(e)}")
            results["failed_endpoints"] += 1
            results["errors"].append(f"List availability: {str(e)}")
        
        # Test 3: Check time slot availability
        print_info("Testing time slot availability...")
        results["total_endpoints"] += 1
        
        try:
            params = {
                "date": "2024-12-23",  # Monday
                "party_size": 4
            }
            response = await client.get(f"{base_path}/availability/slots", params=params, headers=headers)
            if response.is_success():
                print_success(f"✅ Time slot availability: {response.status_code}")
                results["working_endpoints"] += 1
            else:
                print_error(f"❌ Time slot availability failed: {response.status_code}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Time slot availability: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Time slot availability error: {str(e)}")
            results["failed_endpoints"] += 1
            results["errors"].append(f"Time slot availability: {str(e)}")
        
        return results
    
    async def test_waitlist_management(self, client: APITestClient) -> Dict[str, Any]:
        """Test waitlist management functionality"""
        print_test_header("Testing Waitlist Management", "📝")
        
        results = {
            "total_endpoints": 0,
            "working_endpoints": 0,
            "failed_endpoints": 0,
            "missing_features": [],
            "errors": []
        }
        
        headers = self.get_auth_headers()
        base_path = f"/api/organizations/{self.organization_id}/restaurants/{self.restaurant_id}"
        
        # Test 1: Add to waitlist
        waitlist_data = {
            "customer_name": "Jane Smith",
            "customer_email": "jane@example.com", 
            "customer_phone": "+1-555-5678",
            "party_size": 2,
            "estimated_wait_time": 30,
            "notes": "Prefers quiet table"
        }
        
        print_info("Testing waitlist entry creation...")
        results["total_endpoints"] += 1
        
        try:
            response = await client.post(f"{base_path}/waitlist/", json=waitlist_data, headers=headers)
            if response.is_success():
                print_success(f"✅ Add to waitlist: {response.status_code}")
                results["working_endpoints"] += 1
                waitlist_id = response.json_data.get("id")
            else:
                print_error(f"❌ Add to waitlist failed: {response.status_code}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Add to waitlist: {response.status_code}")
                waitlist_id = None
        except Exception as e:
            print_error(f"❌ Add to waitlist error: {str(e)}")
            results["failed_endpoints"] += 1
            results["errors"].append(f"Add to waitlist: {str(e)}")
            waitlist_id = None
        
        # Test 2: List waitlist entries
        print_info("Testing waitlist listing...")
        results["total_endpoints"] += 1
        
        try:
            response = await client.get(f"{base_path}/waitlist/", headers=headers)
            if response.is_success():
                print_success(f"✅ List waitlist: {response.status_code}")
                results["working_endpoints"] += 1
            else:
                print_error(f"❌ List waitlist failed: {response.status_code}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"List waitlist: {response.status_code}")
        except Exception as e:
            print_error(f"❌ List waitlist error: {str(e)}")
            results["failed_endpoints"] += 1
            results["errors"].append(f"List waitlist: {str(e)}")
        
        # Test additional waitlist endpoints if entry was created
        if waitlist_id:
            # Test 3: Update waitlist entry
            print_info("Testing waitlist update...")
            results["total_endpoints"] += 1
            
            update_data = {
                "estimated_wait_time": 45,
                "notes": "Updated wait time"
            }
            
            try:
                response = await client.patch(f"{base_path}/waitlist/{waitlist_id}", json=update_data, headers=headers)
                if response.is_success():
                    print_success(f"✅ Update waitlist: {response.status_code}")
                    results["working_endpoints"] += 1
                else:
                    print_error(f"❌ Update waitlist failed: {response.status_code}")
                    results["failed_endpoints"] += 1
                    results["errors"].append(f"Update waitlist: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Update waitlist error: {str(e)}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Update waitlist: {str(e)}")
            
            # Test 4: Notify waitlist entry
            print_info("Testing waitlist notification...")
            results["total_endpoints"] += 1
            
            try:
                response = await client.post(f"{base_path}/waitlist/{waitlist_id}/notify", headers=headers)
                if response.is_success():
                    print_success(f"✅ Notify waitlist: {response.status_code}")
                    results["working_endpoints"] += 1
                else:
                    print_error(f"❌ Notify waitlist failed: {response.status_code}")
                    results["failed_endpoints"] += 1
                    results["errors"].append(f"Notify waitlist: {response.status_code}")
            except Exception as e:
                print_error(f"❌ Notify waitlist error: {str(e)}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Notify waitlist: {str(e)}")
        
        return results
    
    async def run_complete_test(self) -> Dict[str, Any]:
        """Run complete Phase 2 testing"""
        print_test_header("Phase 2 Complete Testing & Validation", "🚀")
        
        async with APITestClient(self.base_url) as client:
            # Setup authentication
            if not await self.setup_authentication(client):
                return {
                    "success": False,
                    "error": "Failed to setup authentication",
                    "results": {}
                }
            
            # Run all Phase 2 tests
            table_results = await self.test_table_management(client)
            reservation_results = await self.test_reservation_management(client)
            availability_results = await self.test_availability_system(client)
            waitlist_results = await self.test_waitlist_management(client)
            
            # Combine results
            total_endpoints = (
                table_results["total_endpoints"] +
                reservation_results["total_endpoints"] +
                availability_results["total_endpoints"] +
                waitlist_results["total_endpoints"]
            )
            
            working_endpoints = (
                table_results["working_endpoints"] +
                reservation_results["working_endpoints"] +
                availability_results["working_endpoints"] +
                waitlist_results["working_endpoints"]
            )
            
            failed_endpoints = (
                table_results["failed_endpoints"] +
                reservation_results["failed_endpoints"] +
                availability_results["failed_endpoints"] +
                waitlist_results["failed_endpoints"]
            )
            
            all_errors = (
                table_results["errors"] +
                reservation_results["errors"] +
                availability_results["errors"] +
                waitlist_results["errors"]
            )
            
            completion_percentage = (working_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0
            
            # Print summary
            print_test_header("Phase 2 Testing Summary", "📊")
            print_info(f"Total Phase 2 Endpoints Tested: {total_endpoints}")
            print_success(f"Working Endpoints: {working_endpoints}")
            if failed_endpoints > 0:
                print_error(f"Failed Endpoints: {failed_endpoints}")
            else:
                print_info(f"Failed Endpoints: {failed_endpoints}")
            
            print_info(f"Phase 2 Completion: {completion_percentage:.1f}%")
            
            if all_errors:
                print_error("Errors encountered:")
                for error in all_errors:
                    print_error(f"  - {error}")
            
            return {
                "success": True,
                "completion_percentage": completion_percentage,
                "total_endpoints": total_endpoints,
                "working_endpoints": working_endpoints,
                "failed_endpoints": failed_endpoints,
                "errors": all_errors,
                "detailed_results": {
                    "table_management": table_results,
                    "reservation_management": reservation_results,
                    "availability_system": availability_results,
                    "waitlist_management": waitlist_results
                }
            }


async def main():
    """Main function to run Phase 2 testing"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    tester = Phase2Tester(base_url)
    
    try:
        results = await tester.run_complete_test()
        
        if results["success"]:
            print_test_header("Phase 2 Testing Complete!", "✅")
            
            if results["completion_percentage"] >= 90:
                print_success(f"Phase 2 is {results['completion_percentage']:.1f}% complete - Excellent!")
            elif results["completion_percentage"] >= 70:
                print_info(f"Phase 2 is {results['completion_percentage']:.1f}% complete - Good progress")
            else:
                print_error(f"Phase 2 is {results['completion_percentage']:.1f}% complete - Needs work")
            
            # Save detailed results
            with open("phase2_test_results.json", "w") as f:
                json.dump(results, f, indent=2)
            print_info("Detailed results saved to phase2_test_results.json")
            
        else:
            print_error(f"Phase 2 testing failed: {results.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print_error(f"Phase 2 testing crashed: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())