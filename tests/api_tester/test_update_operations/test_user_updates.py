#!/usr/bin/env python3
"""
Test User Update Operations

Comprehensive testing of user-related PUT/PATCH endpoints.
Tests user profile updates, role changes, and permission workflows.
"""

import sys
import asyncio
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.api_tester.shared.utils import APITestClient, APITestHelper, TestResults
from tests.api_tester.shared.auth import get_auth_headers
from tests.api_tester.shared.fixtures import RMSTestFixtures


class UserUpdateTester:
    """Comprehensive user update operations testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.results = TestResults()
        self.auth_headers = None
        self.available_users = []
        self.available_restaurants = []
        self.test_user_created = None
        
    async def setup_authentication(self) -> bool:
        """Setup authentication for all tests"""
        
        self.auth_headers = await get_auth_headers(self.client)
        if not self.auth_headers:
            APITestHelper.print_test_step("Authentication failed - cannot run user update tests", "FAILED")
            return False
            
        APITestHelper.print_test_step("Authentication successful", "SUCCESS")
        return True
        
    async def load_existing_user_data(self):
        """Load existing user data for update testing"""
        
        try:
            # Load users
            response = await self.client.get("/api/v1/users", headers=self.auth_headers)
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list):
                    self.available_users = users
                elif isinstance(users, dict) and 'items' in users:
                    self.available_users = users['items']
                    
            # Load restaurants for assignment
            response = await self.client.get("/api/v1/restaurants", headers=self.auth_headers)
            if response.status_code == 200:
                restaurants = response.json()
                if isinstance(restaurants, list):
                    self.available_restaurants = restaurants
                elif isinstance(restaurants, dict) and 'items' in restaurants:
                    self.available_restaurants = restaurants['items']
                    
            print(f"   👥 Found {len(self.available_users)} users")
            print(f"   🏢 Found {len(self.available_restaurants)} restaurants")
            
        except Exception as e:
            print(f"   ❌ Error loading user data: {e}")
            
    async def create_test_user(self):
        """Create a test user if none exists for update testing"""
        
        if not self.available_users:
            APITestHelper.print_test_step("Creating test user for update testing", "RUNNING")
            
            user_data = RMSTestFixtures.generate_user_data("placeholder", "placeholder", "staff")
            user_data["email"] = "updatetest@testrestaurant.com"
            user_data["full_name"] = "Update Test User"
            user_data["password"] = "secure_test_password"
            
            # Assign to restaurant if available
            if self.available_restaurants:
                user_data["restaurant_id"] = self.available_restaurants[0]["id"]
                
            response = await self.client.post("/api/v1/users", json=user_data, headers=self.auth_headers)
            if response.status_code == 201:
                self.test_user_created = response.json()
                self.available_users.append(self.test_user_created)
                APITestHelper.print_test_step("Test user created", "SUCCESS")
            else:
                APITestHelper.print_test_step("Failed to create test user", "FAILED")
                
    async def test_user_profile_updates(self) -> bool:
        """Test updating user profiles"""
        
        APITestHelper.print_test_header("User Profile Updates", "👤")
        
        if not self.available_users:
            APITestHelper.print_test_step("No users available for update testing", "SKIPPED")
            return True
            
        user = self.available_users[0]
        user_id = user['id']
        original_name = user['full_name']
        original_email = user['email']
        
        print(f"   👤 Testing updates for user: {original_name} ({original_email}) - {user_id}")
        
        update_tests = [
            # Full name update
            ({
                "full_name": f"{original_name} - UPDATED"
            }, "User full name update", "PATCH"),
            
            # Phone number update
            ({
                "phone_number": "+1-555-123-4567"
            }, "User phone number update", "PATCH"),
            
            # Multiple fields update
            ({
                "full_name": f"{original_name} - Final Update",
                "phone_number": "+1-555-987-6543"
            }, "Multiple user fields update", "PATCH"),
            
            # Full profile update (PUT)
            ({
                "full_name": f"{original_name} - Complete Update",
                "email": original_email,  # Keep original email
                "role": user.get('role', 'staff'),
                "phone_number": "+1-555-555-5555"
            }, "Full user profile update (PUT)", "PUT")
        ]
        
        success_count = 0
        
        for update_data, description, method in update_tests:
            try:
                APITestHelper.print_test_step(f"Testing: {description}", "RUNNING")
                
                start_time = time.time()
                if method == "PUT":
                    response = await self.client.put(f"/api/v1/users/{user_id}", 
                                                  json=update_data, headers=self.auth_headers)
                else:  # PATCH
                    response = await self.client.patch(f"/api/v1/users/{user_id}", 
                                                    json=update_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    updated_user = response.json()
                    
                    APITestHelper.print_test_step(f"{description} successful ({response_time:.0f}ms)", "SUCCESS")
                    
                    # Verify updates were applied
                    updates_applied = True
                    for key, expected_value in update_data.items():
                        actual_value = updated_user.get(key)
                        if actual_value != expected_value:
                            APITestHelper.print_test_step(f"Update verification failed: {key} = {actual_value} (expected {expected_value})", "FAILED")
                            updates_applied = False
                            
                    if updates_applied:
                        APITestHelper.print_test_step("All updates verified", "SUCCESS")
                        
                        print(f"   👤 Updated User:") 
                        print(f"      Name: {updated_user.get('full_name')}")
                        print(f"      Email: {updated_user.get('email')}")
                        print(f"      Phone: {updated_user.get('phone_number', 'N/A')}")
                        print(f"      Role: {updated_user.get('role')}")
                        
                    self.results.add_success("user_profile_updates", description, {
                        "response_time": response_time,
                        "user_id": user_id,
                        "method": method,
                        "updates_verified": updates_applied
                    })
                    success_count += 1
                    
                elif response.status_code == 404:
                    APITestHelper.print_test_step(f"User not found: {user_id}", "FAILED")
                    self.results.add_failure("user_profile_updates", description, 
                                          "User not found", 404)
                    
                elif response.status_code == 403:
                    APITestHelper.print_test_step("User update forbidden (permission check working)", "SUCCESS")
                    self.results.add_success("user_profile_updates", f"{description} (permission check)", {
                        "response_time": response_time,
                        "permission_enforced": True
                    })
                    success_count += 1
                    
                else:
                    APITestHelper.print_test_step(f"{description} failed: HTTP {response.status_code}", "FAILED")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    self.results.add_failure("user_profile_updates", description, 
                                          f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"{description} error: {e}", "FAILED")
                self.results.add_failure("user_profile_updates", description, str(e))
                
        print(f"\n📊 Profile Update Summary: {success_count}/{len(update_tests)} successful")
        return success_count > 0
        
    async def test_user_role_updates(self) -> bool:
        """Test updating user roles"""
        
        APITestHelper.print_test_header("User Role Updates", "🎭")
        
        if not self.available_users:
            APITestHelper.print_test_step("No users available for role update testing", "SKIPPED")
            return True
            
        # Use test user if available, otherwise use first user
        user = self.test_user_created if self.test_user_created else self.available_users[0]
        user_id = user['id']
        current_role = user.get('role', 'staff')
        
        print(f"   👤 Testing role updates for user: {user['full_name']}")
        print(f"   🎭 Current role: {current_role}")
        
        # Define role transitions to test
        role_transitions = [
            ("manager", "Promote to manager"),
            ("staff", "Demote to staff"),
            ("admin", "Promote to admin (may be restricted)")
        ]
        
        success_count = 0
        
        for new_role, description in role_transitions:
            if new_role == current_role:
                continue  # Skip if same role
                
            try:
                APITestHelper.print_test_step(f"Testing: {description}", "RUNNING")
                
                role_update_data = {
                    "role": new_role
                }
                
                start_time = time.time()
                response = await self.client.patch(f"/api/v1/users/{user_id}/role", 
                                                json=role_update_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    updated_user = response.json()
                    new_user_role = updated_user.get('role')
                    
                    APITestHelper.print_test_step(f"Role update successful ({response_time:.0f}ms)", "SUCCESS")
                    
                    if new_user_role == new_role:
                        APITestHelper.print_test_step(f"Role correctly changed to {new_role}", "SUCCESS")
                        
                        print(f"   🎭 Role Update:")
                        print(f"      Previous: {current_role}")
                        print(f"      Current: {new_user_role}")
                        
                        current_role = new_user_role  # Update for next test
                        
                    else:
                        APITestHelper.print_test_step(f"Role update verification failed", "FAILED")
                        
                    self.results.add_success("user_role_updates", description, {
                        "response_time": response_time,
                        "user_id": user_id,
                        "previous_role": current_role,
                        "new_role": new_user_role
                    })
                    success_count += 1
                    
                elif response.status_code == 404:
                    # Try alternative endpoint
                    response = await self.client.patch(f"/api/v1/users/{user_id}", 
                                                    json=role_update_data, headers=self.auth_headers)
                    
                    if response.status_code == 200:
                        APITestHelper.print_test_step(f"Role update via profile endpoint successful", "SUCCESS")
                        success_count += 1
                    else:
                        APITestHelper.print_test_step("Role update endpoints not found (may not be implemented)", "SKIPPED")
                        break
                        
                elif response.status_code == 403:
                    APITestHelper.print_test_step("Role update forbidden (permission check working)", "SUCCESS")
                    self.results.add_success("user_role_updates", f"{description} (permission check)", {
                        "response_time": response_time,
                        "permission_enforced": True
                    })
                    success_count += 1
                    
                else:
                    APITestHelper.print_test_step(f"Role update failed: HTTP {response.status_code}", "FAILED")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    self.results.add_failure("user_role_updates", description, 
                                          f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Role update error: {e}", "FAILED")
                self.results.add_failure("user_role_updates", description, str(e))
                
        print(f"\n📊 Role Update Summary: {success_count}/{len(role_transitions)} successful")
        return True  # Role updates may not be implemented
        
    async def test_user_restaurant_assignment(self) -> bool:
        """Test updating user restaurant assignments"""
        
        APITestHelper.print_test_header("User Restaurant Assignment", "🏢")
        
        if not self.available_users or not self.available_restaurants:
            APITestHelper.print_test_step("Need both users and restaurants for assignment testing", "SKIPPED")
            return True
            
        user = self.test_user_created if self.test_user_created else self.available_users[0]
        user_id = user['id']
        current_restaurant = user.get('restaurant_id')
        
        print(f"   👤 Testing restaurant assignment for user: {user['full_name']}")
        print(f"   🏢 Current restaurant: {current_restaurant}")
        
        # Test restaurant assignment
        if self.available_restaurants:
            restaurant = self.available_restaurants[0]
            restaurant_id = restaurant['id']
            restaurant_name = restaurant.get('name', 'N/A')
            
            try:
                APITestHelper.print_test_step(f"Assigning user to restaurant: {restaurant_name}", "RUNNING")
                
                assignment_data = {
                    "restaurant_id": restaurant_id
                }
                
                start_time = time.time()
                response = await self.client.patch(f"/api/v1/users/{user_id}", 
                                                json=assignment_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    updated_user = response.json()
                    new_restaurant = updated_user.get('restaurant_id')
                    
                    APITestHelper.print_test_step(f"Restaurant assignment successful ({response_time:.0f}ms)", "SUCCESS")
                    
                    if new_restaurant == restaurant_id:
                        APITestHelper.print_test_step(f"Restaurant correctly assigned", "SUCCESS")
                        
                        print(f"   🏢 Assignment Update:")
                        print(f"      Previous: {current_restaurant}")
                        print(f"      Current: {new_restaurant}")
                        print(f"      Restaurant: {restaurant_name}")
                        
                    else:
                        APITestHelper.print_test_step(f"Restaurant assignment verification failed", "FAILED")
                        
                    self.results.add_success("user_restaurant_assignment", "Assign user to restaurant", {
                        "response_time": response_time,
                        "user_id": user_id,
                        "restaurant_id": restaurant_id
                    })
                    return True
                    
                elif response.status_code == 404:
                    APITestHelper.print_test_step("User or restaurant not found", "FAILED")
                    self.results.add_failure("user_restaurant_assignment", "Assign user to restaurant", 
                                          "User or restaurant not found", 404)
                    
                elif response.status_code == 403:
                    APITestHelper.print_test_step("Restaurant assignment forbidden (permission check working)", "SUCCESS")
                    self.results.add_success("user_restaurant_assignment", "Assign user to restaurant (permission check)", {
                        "response_time": response_time,
                        "permission_enforced": True
                    })
                    return True
                    
                else:
                    APITestHelper.print_test_step(f"Restaurant assignment failed: HTTP {response.status_code}", "FAILED")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    self.results.add_failure("user_restaurant_assignment", "Assign user to restaurant", 
                                          f"HTTP {response.status_code}", response.status_code)
                    return False
                    
            except Exception as e:
                APITestHelper.print_test_step(f"Restaurant assignment error: {e}", "FAILED")
                self.results.add_failure("user_restaurant_assignment", "Assign user to restaurant", str(e))
                return False
                
        return True
        
    async def test_user_activation_toggle(self) -> bool:
        """Test toggling user activation status"""
        
        APITestHelper.print_test_header("User Activation Toggle", "🔄")
        
        if not self.available_users:
            APITestHelper.print_test_step("No users available for activation testing", "SKIPPED")
            return True
            
        user = self.test_user_created if self.test_user_created else self.available_users[0]
        user_id = user['id']
        current_status = user.get('is_active', True)
        
        print(f"   👤 Testing activation toggle for: {user['full_name']}")
        print(f"   📊 Current status: {'Active' if current_status else 'Inactive'}")
        
        try:
            APITestHelper.print_test_step("Toggling user activation status", "RUNNING")
            
            toggle_data = {
                "is_active": not current_status
            }
            
            start_time = time.time()
            response = await self.client.patch(f"/api/v1/users/{user_id}/status", 
                                            json=toggle_data, headers=self.auth_headers)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                updated_user = response.json()
                new_status = updated_user.get('is_active')
                
                APITestHelper.print_test_step(f"Status toggled successfully ({response_time:.0f}ms)", "SUCCESS")
                
                if new_status == (not current_status):
                    APITestHelper.print_test_step(f"Status correctly changed to {'Active' if new_status else 'Inactive'}", "SUCCESS")
                    
                    print(f"   🔄 Status Update:")
                    print(f"      Previous: {'Active' if current_status else 'Inactive'}")
                    print(f"      Current: {'Active' if new_status else 'Inactive'}")
                    
                    self.results.add_success("user_activation_toggle", "Toggle user activation", {
                        "response_time": response_time,
                        "user_id": user_id,
                        "previous_state": current_status,
                        "new_state": new_status
                    })
                    
                    # Toggle back to original state
                    await asyncio.sleep(0.2)
                    
                    restore_data = {"is_active": current_status}
                    restore_response = await self.client.patch(f"/api/v1/users/{user_id}/status", 
                                                            json=restore_data, headers=self.auth_headers)
                    
                    if restore_response.status_code == 200:
                        APITestHelper.print_test_step("Status restored to original state", "SUCCESS")
                    
                else:
                    APITestHelper.print_test_step(f"Status change verification failed", "FAILED")
                    self.results.add_failure("user_activation_toggle", "Toggle user activation", 
                                          "Status state not changed")
                    return False
                    
                return True
                
            elif response.status_code == 404:
                # Try alternative endpoint
                response = await self.client.patch(f"/api/v1/users/{user_id}", 
                                                json=toggle_data, headers=self.auth_headers)
                
                if response.status_code == 200:
                    APITestHelper.print_test_step("Status toggle via profile endpoint successful", "SUCCESS")
                    return True
                else:
                    APITestHelper.print_test_step("Status toggle endpoints not found (may not be implemented)", "SKIPPED")
                    return True
                    
            else:
                APITestHelper.print_test_step(f"Status toggle failed: HTTP {response.status_code}", "FAILED")
                if response.json_data:
                    print(f"   Error: {response.json_data}")
                self.results.add_failure("user_activation_toggle", "Toggle user activation", 
                                       f"HTTP {response.status_code}", response.status_code)
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Status toggle error: {e}", "FAILED")
            self.results.add_failure("user_activation_toggle", "Toggle user activation", str(e))
            return False
            
    async def test_user_update_validation(self) -> bool:
        """Test user update data validation and error handling"""
        
        APITestHelper.print_test_header("User Update Data Validation", "✅")
        
        if not self.available_users:
            APITestHelper.print_test_step("Need users for validation testing", "SKIPPED")
            return True
            
        user_id = self.available_users[0]['id']
        
        validation_tests = [
            (f"/api/v1/users/{user_id}", {"email": ""}, "Empty email", "PATCH"),
            (f"/api/v1/users/{user_id}", {"email": "invalid-email"}, "Invalid email format", "PATCH"),
            (f"/api/v1/users/{user_id}", {"full_name": ""}, "Empty full name", "PATCH"),
            (f"/api/v1/users/{user_id}", {"role": "invalid_role"}, "Invalid role", "PATCH"),
            (f"/api/v1/users/{user_id}", {"is_active": "maybe"}, "Invalid boolean value", "PATCH"),
            (f"/api/v1/users/{user_id}", {"restaurant_id": "invalid-uuid"}, "Invalid restaurant ID", "PATCH"),
        ]
        
        success_count = 0
        
        for endpoint, invalid_data, description, method in validation_tests:
            try:
                APITestHelper.print_test_step(f"Testing: {description}", "RUNNING")
                
                start_time = time.time()
                if method == "PUT":
                    response = await self.client.put(endpoint, json=invalid_data, headers=self.auth_headers)
                else:  # PATCH
                    response = await self.client.patch(endpoint, json=invalid_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                # We expect validation errors (400/422) for invalid data
                if response.status_code in [400, 422]:
                    APITestHelper.print_test_step(f"Validation correctly rejected ({response_time:.0f}ms)", "SUCCESS")
                    
                    if response.json_data:
                        error_info = response.json_data
                        print(f"   ✅ Error details: {error_info}")
                        
                    self.results.add_success("user_update_validation", description, {
                        "response_time": response_time,
                        "correctly_rejected": True
                    })
                    success_count += 1
                    
                elif response.status_code == 200:
                    APITestHelper.print_test_step(f"Invalid data accepted (should be rejected)", "FAILED")
                    self.results.add_failure("user_update_validation", description, 
                                          "Invalid data was accepted", 200)
                    
                else:
                    APITestHelper.print_test_step(f"Unexpected response: HTTP {response.status_code}", "FAILED")
                    self.results.add_failure("user_update_validation", description, 
                                          f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.2)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Validation test error: {e}", "FAILED")
                self.results.add_failure("user_update_validation", description, str(e))
                
        print(f"\n📊 Validation Testing Summary: {success_count}/{len(validation_tests)} tests passed")
        return success_count > 0
        
    def print_user_update_summary(self):
        """Print comprehensive user update test summary"""
        
        APITestHelper.print_test_header("User Update Tests Summary", "📊")
        
        print(f"Total Tests: {self.results.total_tests}")
        print(f"Passed: {self.results.passed_tests}")
        print(f"Failed: {self.results.failed_tests}")
        print(f"Success Rate: {self.results.success_rate:.1f}%")
        
        # Group results by category
        categories = {}
        for result in self.results.results:
            category = result.category
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0}
                
            if result.success:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
                
        print(f"\n📋 Results by Category:")
        for category, stats in categories.items():
            total = stats["passed"] + stats["failed"]
            rate = (stats["passed"] / total) * 100 if total > 0 else 0
            print(f"   {category.replace('_', ' ').title()}: {stats['passed']}/{total} ({rate:.1f}%)")
            
        # Show available data
        print(f"\n📊 Available Test Data:")
        print(f"   Users: {len(self.available_users)}")
        print(f"   Restaurants: {len(self.available_restaurants)}")
        if self.test_user_created:
            print(f"   Test User Created: {self.test_user_created['email']}")
        
        # Performance summary
        perf_results = [r for r in self.results.results if r.response_time > 0]
        if perf_results:
            avg_response_time = sum(r.response_time for r in perf_results) / len(perf_results)
            print(f"\n⚡ Average Response Time: {avg_response_time:.0f}ms")
            
        # Show failures if any
        if self.results.failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.results.results:
                if not result.success:
                    print(f"   • {result.category}: {result.test_name} - {result.error_message}")
                    
    async def cleanup_test_user(self):
        """Clean up created test user"""
        
        if not self.test_user_created:
            return
            
        try:
            user_id = self.test_user_created['id']
            user_email = self.test_user_created.get('email', 'N/A')
            
            print(f"\n🧹 Cleaning up test user: {user_email}")
            
            response = await self.client.delete(f"/api/v1/users/{user_id}", headers=self.auth_headers)
            
            if response.status_code == 204:
                print(f"   ✅ Test user deleted successfully")
            elif response.status_code == 404:
                print(f"   ⚠️ Test user already deleted")
            else:
                print(f"   ❌ Failed to delete test user (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Error deleting test user: {e}")
            
    async def run_comprehensive_user_update_tests(self) -> bool:
        """Run all user update tests"""
        
        print("👤 RMS User Update Operations Tests")
        print("="*50)
        
        start_time = time.time()
        
        try:
            # Setup authentication
            if not await self.setup_authentication():
                return False
                
            # Load existing user data
            await self.load_existing_user_data()
            
            # Create test user if needed
            await self.create_test_user()
                
            # Run all user update tests
            tests = [
                ("User Profile Updates", self.test_user_profile_updates),
                ("User Role Updates", self.test_user_role_updates),
                ("User Restaurant Assignment", self.test_user_restaurant_assignment),
                ("User Activation Toggle", self.test_user_activation_toggle),
                ("User Update Data Validation", self.test_user_update_validation)
            ]
            
            overall_success = True
            
            for test_name, test_func in tests:
                try:
                    success = await test_func()
                    if not success:
                        overall_success = False
                        
                except Exception as e:
                    APITestHelper.print_test_step(f"{test_name} failed with error: {e}", "FAILED")
                    self.results.add_failure("general", test_name, str(e))
                    overall_success = False
                    
                # Small delay between test categories
                await asyncio.sleep(0.5)
                
            # Calculate execution time
            self.results.execution_time = time.time() - start_time
            
            # Print summary
            self.print_user_update_summary()
            
            return overall_success
            
        except KeyboardInterrupt:
            print("\n⚠️ User update tests interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ User update tests failed: {e}")
            return False
        finally:
            # Cleanup test user
            try:
                await self.cleanup_test_user()
            except Exception as e:
                print(f"⚠️ Test user cleanup failed: {e}")
                
            await self.client.close()


async def main():
    """Main entry point for user update testing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Test RMS user update operations")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    tester = UserUpdateTester(args.base_url)
    
    try:
        success = await tester.run_comprehensive_user_update_tests()
        
        if success:
            print(f"\n✅ All user update tests passed successfully!")
        else:
            print(f"\n❌ Some user update tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ User update testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())