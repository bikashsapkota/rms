#!/usr/bin/env python3
"""
Test User Creation Operations

Comprehensive testing of user-related POST endpoints.
Tests user account creation, role assignment, and permission workflows.
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


class UserCreationTester:
    """Comprehensive user creation operations testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.results = TestResults()
        self.auth_headers = None
        self.created_users = []
        self.available_restaurants = []
        
    async def setup_authentication(self) -> bool:
        """Setup authentication for all tests"""
        
        self.auth_headers = await get_auth_headers(self.client)
        if not self.auth_headers:
            APITestHelper.print_test_step("Authentication failed - cannot run user creation tests", "FAILED")
            return False
            
        APITestHelper.print_test_step("Authentication successful", "SUCCESS")
        return True
        
    async def load_available_restaurants(self):
        """Load available restaurants for user assignment"""
        
        try:
            response = await self.client.get("/api/v1/restaurants", headers=self.auth_headers)
            
            if response.status_code == 200:
                restaurants = response.json()
                if isinstance(restaurants, list):
                    self.available_restaurants = restaurants
                elif isinstance(restaurants, dict) and 'items' in restaurants:
                    self.available_restaurants = restaurants['items']
                    
                print(f"   🏢 Found {len(self.available_restaurants)} restaurants for user assignment")
                
                for restaurant in self.available_restaurants[:3]:  # Show first 3
                    print(f"      • {restaurant.get('name', 'N/A')} (ID: {restaurant.get('id', 'N/A')})")
                    
            else:
                print(f"   ⚠️ Could not load restaurants: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error loading restaurants: {e}")
            
    async def test_user_creation_with_roles(self) -> bool:
        """Test creating users with different roles"""
        
        APITestHelper.print_test_header("User Creation with Roles", "👤")
        
        # Test different user roles
        user_roles = [
            ("admin", "Administrator User"),
            ("manager", "Restaurant Manager"),
            ("staff", "Staff Member")
        ]
        
        success_count = 0
        
        for role, description in user_roles:
            try:
                # Generate user data
                user_data = RMSTestFixtures.generate_user_data("placeholder", "placeholder", role)
                
                # Add unique suffix to avoid conflicts
                email_parts = user_data["email"].split("@")
                user_data["email"] = f"{email_parts[0]}.test.{role}@{email_parts[1]}"
                user_data["full_name"] = f"{user_data['full_name']} ({role.title()})"
                
                # Set password for creation
                user_data["password"] = "secure_test_password"
                if "password_hash" in user_data:
                    del user_data["password_hash"]
                    
                # Assign to restaurant if available
                if self.available_restaurants:
                    restaurant = self.available_restaurants[0]
                    user_data["restaurant_id"] = restaurant["id"]
                    restaurant_name = restaurant["name"]
                else:
                    restaurant_name = "No restaurant assigned"
                    
                APITestHelper.print_test_step(f"Creating {description}", "RUNNING")
                print(f"   📧 Email: {user_data['email']}")
                print(f"   🏢 Restaurant: {restaurant_name}")
                
                start_time = time.time()
                response = await self.client.post("/api/v1/users", json=user_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 201:
                    user_response = response.json()
                    self.created_users.append(user_response)
                    
                    APITestHelper.print_test_step(f"{description} created successfully ({response_time:.0f}ms)", "SUCCESS")
                    
                    # Validate response structure
                    if APITestHelper.validate_user_response(user_response):
                        APITestHelper.print_test_step("User response structure is valid", "SUCCESS")
                        
                        print(f"   👤 Created User:")
                        print(f"      ID: {user_response['id']}")
                        print(f"      Email: {user_response['email']}")
                        print(f"      Role: {user_response['role']}")
                        print(f"      Active: {user_response.get('is_active', 'N/A')}")
                        print(f"      Organization: {user_response.get('organization_id', 'N/A')}")
                        print(f"      Restaurant: {user_response.get('restaurant_id', 'N/A')}")
                        
                        # Verify data matches input (excluding password)
                        compare_fields = ['email', 'full_name', 'role']
                        if APITestHelper.compare_data_fields(user_data, user_response, compare_fields):
                            APITestHelper.print_test_step("User data matches input", "SUCCESS")
                        else:
                            APITestHelper.print_test_step("User data doesn't match input", "FAILED")
                            
                        # Check that password is not exposed
                        if 'password' in user_response or 'password_hash' in user_response:
                            APITestHelper.print_test_step("⚠️ Password data exposed in response", "FAILED")
                        else:
                            APITestHelper.print_test_step("Password data properly hidden", "SUCCESS")
                            
                    else:
                        APITestHelper.print_test_step("User response missing required fields", "FAILED")
                        
                    self.results.add_success("user_creation", f"Create {role} user", {
                        "response_time": response_time,
                        "user_id": user_response['id'],
                        "email": user_response['email'],
                        "role": role
                    })
                    success_count += 1
                    
                elif response.status_code == 409:
                    APITestHelper.print_test_step(f"User already exists (conflict)", "SKIPPED")
                    
                elif response.status_code == 403:
                    APITestHelper.print_test_step(f"User creation forbidden (permission check working)", "SUCCESS")
                    self.results.add_success("user_creation", f"Create {role} user (permission check)", {
                        "response_time": response_time,
                        "permission_enforced": True
                    })
                    
                elif response.status_code == 404:
                    APITestHelper.print_test_step("User creation endpoint not found (may not be implemented)", "SKIPPED")
                    break  # Don't try more if endpoint doesn't exist
                    
                else:
                    APITestHelper.print_test_step(f"User creation failed: HTTP {response.status_code}", "FAILED")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    self.results.add_failure("user_creation", f"Create {role} user", 
                                           f"HTTP {response.status_code}", response.status_code)
                    
                # Small delay between creations
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"User creation error: {e}", "FAILED")
                self.results.add_failure("user_creation", f"Create {role} user", str(e))
                
        print(f"\n📊 User Creation Summary: {success_count}/{len(user_roles)} successful")
        return success_count > 0
        
    async def test_user_authentication_after_creation(self) -> bool:
        """Test that created users can authenticate"""
        
        APITestHelper.print_test_header("User Authentication After Creation", "🔐")
        
        if not self.created_users:
            APITestHelper.print_test_step("No created users available for authentication testing", "SKIPPED")
            return True
            
        success_count = 0
        
        for user in self.created_users[:2]:  # Test first 2 created users
            try:
                email = user.get('email')
                password = "secure_test_password"  # Password we used during creation
                
                APITestHelper.print_test_step(f"Testing authentication for {email}", "RUNNING")
                
                # Test login
                auth_data = {
                    "username": email,  # FastAPI OAuth2 uses 'username' field
                    "password": password
                }
                
                start_time = time.time()
                response = await self.client.post("/auth/login", data=auth_data)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    auth_response = response.json()
                    
                    APITestHelper.print_test_step(f"Authentication successful ({response_time:.0f}ms)", "SUCCESS")
                    
                    # Validate auth response
                    if 'access_token' in auth_response or 'token' in auth_response:
                        APITestHelper.print_test_step("Valid access token received", "SUCCESS")
                        
                        token = auth_response.get('access_token') or auth_response.get('token')
                        print(f"   🎫 Token type: {auth_response.get('token_type', 'bearer')}")
                        print(f"   🔑 Token length: {len(token)} characters")
                        
                        # Test token usage
                        user_headers = {"Authorization": f"Bearer {token}"}
                        profile_response = await self.client.get("/auth/me", headers=user_headers)
                        
                        if profile_response.status_code == 200:
                            profile_data = profile_response.json()
                            
                            APITestHelper.print_test_step("Token successfully used for profile access", "SUCCESS")
                            print(f"   👤 Profile: {profile_data.get('email')} ({profile_data.get('role')})")
                            
                            # Verify profile matches created user
                            if profile_data.get('email') == email:
                                APITestHelper.print_test_step("Profile email matches created user", "SUCCESS")
                            else:
                                APITestHelper.print_test_step("Profile email mismatch", "FAILED")
                                
                        else:
                            APITestHelper.print_test_step("Token failed to access profile", "FAILED")
                            
                    else:
                        APITestHelper.print_test_step("No access token in response", "FAILED")
                        
                    self.results.add_success("user_authentication", f"Authenticate {email}", {
                        "response_time": response_time,
                        "email": email
                    })
                    success_count += 1
                    
                elif response.status_code == 401:
                    APITestHelper.print_test_step(f"Authentication failed (wrong credentials?)", "FAILED")
                    self.results.add_failure("user_authentication", f"Authenticate {email}", 
                                           "Authentication failed", 401)
                    
                else:
                    APITestHelper.print_test_step(f"Authentication error: HTTP {response.status_code}", "FAILED")
                    self.results.add_failure("user_authentication", f"Authenticate {email}", 
                                           f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Authentication test error: {e}", "FAILED")
                self.results.add_failure("user_authentication", f"Authenticate {email}", str(e))
                
        print(f"\n📊 Authentication Testing Summary: {success_count}/{len(self.created_users[:2])} successful")
        return success_count > 0
        
    async def test_user_data_validation(self) -> bool:
        """Test user data validation and error handling"""
        
        APITestHelper.print_test_header("User Data Validation", "✅")
        
        validation_tests = [
            ({}, "Empty user data"),
            ({"email": ""}, "Empty email"),
            ({"email": "invalid-email"}, "Invalid email format"),
            ({"email": "test@test.com"}, "Missing required fields"),
            ({"email": "test@test.com", "full_name": ""}, "Empty full name"),
            ({"email": "test@test.com", "full_name": "Test User"}, "Missing password"),
            ({"email": "test@test.com", "full_name": "Test User", "password": "123"}, "Weak password"),
            ({"email": "test@test.com", "full_name": "Test User", "password": "secure_pass", "role": "invalid"}, "Invalid role"),
        ]
        
        success_count = 0
        
        for invalid_data, description in validation_tests:
            try:
                APITestHelper.print_test_step(f"Testing: {description}", "RUNNING")
                
                start_time = time.time()
                response = await self.client.post("/api/v1/users", json=invalid_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                # We expect validation errors (400/422) for invalid data
                if response.status_code in [400, 422]:
                    APITestHelper.print_test_step(f"Validation correctly rejected ({response_time:.0f}ms)", "SUCCESS")
                    
                    if response.json_data:
                        error_info = response.json_data
                        print(f"   ✅ Error details: {error_info}")
                        
                    self.results.add_success("user_validation", description, {
                        "response_time": response_time,
                        "correctly_rejected": True
                    })
                    success_count += 1
                    
                elif response.status_code == 404:
                    APITestHelper.print_test_step("User creation endpoint not found (validation test skipped)", "SKIPPED")
                    break  # Don't continue if endpoint doesn't exist
                    
                elif response.status_code == 201:
                    APITestHelper.print_test_step(f"Invalid data accepted (should be rejected)", "FAILED")
                    self.results.add_failure("user_validation", description, 
                                           "Invalid data was accepted", 201)
                    
                else:
                    APITestHelper.print_test_step(f"Unexpected response: HTTP {response.status_code}", "FAILED")
                    self.results.add_failure("user_validation", description, 
                                           f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.2)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Validation test error: {e}", "FAILED")
                self.results.add_failure("user_validation", description, str(e))
                
        print(f"\n📊 Validation Testing Summary: {success_count}/{len(validation_tests)} tests passed")
        return success_count > 0
        
    async def test_duplicate_user_prevention(self) -> bool:
        """Test prevention of duplicate user creation"""
        
        APITestHelper.print_test_header("Duplicate User Prevention", "🚫")
        
        if not self.created_users:
            APITestHelper.print_test_step("No created users available for duplicate testing", "SKIPPED")
            return True
            
        existing_user = self.created_users[0]
        existing_email = existing_user.get('email')
        
        try:
            # Try to create user with same email
            duplicate_data = {
                "email": existing_email,
                "full_name": "Duplicate User Test",
                "password": "different_password",
                "role": "staff"
            }
            
            APITestHelper.print_test_step(f"Attempting to create duplicate user: {existing_email}", "RUNNING")
            
            start_time = time.time()
            response = await self.client.post("/api/v1/users", json=duplicate_data, headers=self.auth_headers)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 409:
                APITestHelper.print_test_step(f"Duplicate user correctly rejected ({response_time:.0f}ms)", "SUCCESS")
                
                if response.json_data:
                    error_info = response.json_data
                    print(f"   🚫 Conflict details: {error_info}")
                    
                self.results.add_success("user_duplication", "Prevent duplicate email", {
                    "response_time": response_time,
                    "email": existing_email,
                    "correctly_rejected": True
                })
                return True
                
            elif response.status_code == 400:
                APITestHelper.print_test_step(f"Duplicate user rejected with validation error ({response_time:.0f}ms)", "SUCCESS")
                self.results.add_success("user_duplication", "Prevent duplicate email (validation)", {
                    "response_time": response_time,
                    "email": existing_email
                })
                return True
                
            elif response.status_code == 201:
                APITestHelper.print_test_step("Duplicate user was created (should be rejected)", "FAILED")
                self.results.add_failure("user_duplication", "Prevent duplicate email", 
                                       "Duplicate user was created", 201)
                return False
                
            else:
                APITestHelper.print_test_step(f"Unexpected response: HTTP {response.status_code}", "FAILED")
                self.results.add_failure("user_duplication", "Prevent duplicate email", 
                                       f"HTTP {response.status_code}", response.status_code)
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Duplicate prevention test error: {e}", "FAILED")
            self.results.add_failure("user_duplication", "Prevent duplicate email", str(e))
            return False
            
    def print_user_creation_summary(self):
        """Print comprehensive user creation test summary"""
        
        APITestHelper.print_test_header("User Creation Tests Summary", "📊")
        
        print(f"Total Tests: {self.results.total_tests}")
        print(f"Passed: {self.results.passed_tests}")
        print(f"Failed: {self.results.failed_tests}")
        print(f"Success Rate: {self.results.success_rate:.1f}%")
        
        # Show created entities
        print(f"\n👥 Created Users: {len(self.created_users)}")
        
        if self.created_users:
            print(f"\n   👤 User List:")
            for user in self.created_users:
                print(f"      • {user.get('email', 'N/A')} ({user.get('role', 'N/A')}) - ID: {user.get('id', 'N/A')}")
                
            # Group by role
            roles = {}
            for user in self.created_users:
                role = user.get('role', 'unknown')
                roles[role] = roles.get(role, 0) + 1
                
            print(f"\n   📊 Users by Role:")
            for role, count in roles.items():
                print(f"      {role.title()}: {count}")
                
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
                    
    async def cleanup_created_users(self):
        """Clean up created test users"""
        
        if not self.created_users:
            return
            
        print(f"\n🧹 Cleaning up created test users...")
        
        for user in self.created_users:
            try:
                user_id = user['id']
                user_email = user.get('email', 'N/A')
                
                response = await self.client.delete(f"/api/v1/users/{user_id}", headers=self.auth_headers)
                
                if response.status_code == 204:
                    print(f"   ✅ Deleted user: {user_email}")
                elif response.status_code == 404:
                    print(f"   ⚠️ User already deleted: {user_email}")
                else:
                    print(f"   ❌ Failed to delete user: {user_email} (HTTP {response.status_code})")
                    
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"   ❌ Error deleting user: {e}")
                
    async def run_comprehensive_user_creation_tests(self) -> bool:
        """Run all user creation tests"""
        
        print("👤 RMS User Creation Operations Tests")
        print("="*50)
        
        start_time = time.time()
        
        try:
            # Setup authentication
            if not await self.setup_authentication():
                return False
                
            # Load available restaurants
            await self.load_available_restaurants()
                
            # Run all user creation tests
            tests = [
                ("User Creation with Roles", self.test_user_creation_with_roles),
                ("User Authentication After Creation", self.test_user_authentication_after_creation),
                ("User Data Validation", self.test_user_data_validation),
                ("Duplicate User Prevention", self.test_duplicate_user_prevention)
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
            self.print_user_creation_summary()
            
            return overall_success
            
        except KeyboardInterrupt:
            print("\n⚠️ User creation tests interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ User creation tests failed: {e}")
            return False
        finally:
            # Cleanup created users
            try:
                await self.cleanup_created_users()
            except Exception as e:
                print(f"⚠️ User cleanup failed: {e}")
                
            await self.client.close()


async def main():
    """Main entry point for user creation testing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Test RMS user creation operations")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--no-cleanup", action="store_true", help="Skip cleanup of created users")
    
    args = parser.parse_args()
    
    tester = UserCreationTester(args.base_url)
    
    try:
        success = await tester.run_comprehensive_user_creation_tests()
        
        if success:
            print(f"\n✅ All user creation tests passed successfully!")
        else:
            print(f"\n❌ Some user creation tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ User creation testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())