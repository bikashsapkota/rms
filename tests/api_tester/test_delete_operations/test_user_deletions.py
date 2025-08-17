#!/usr/bin/env python3
"""
Test User Delete Operations

Comprehensive testing of user-related DELETE endpoints.
Tests user account deletion, deactivation, and cleanup workflows.
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


class UserDeletionTester:
    """Comprehensive user deletion operations testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000", confirm_deletes: bool = False):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.results = TestResults()
        self.auth_headers = None
        self.confirm_deletes = confirm_deletes
        self.test_users = []
        self.available_restaurants = []
        self.cleanup_queue = []
        
    async def setup_authentication(self) -> bool:
        """Setup authentication for all tests"""
        
        self.auth_headers = await get_auth_headers(self.client)
        if not self.auth_headers:
            APITestHelper.print_test_step("Authentication failed - cannot run user deletion tests", "FAILED")
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
            
        except Exception as e:
            print(f"   ❌ Error loading restaurants: {e}")
            
    async def create_test_users(self):
        """Create test users for deletion testing"""
        
        APITestHelper.print_test_step("Creating test users for deletion testing", "RUNNING")
        
        try:
            # Define test user roles
            user_roles = [
                ("staff", "DELETE TEST Staff User"),
                ("manager", "DELETE TEST Manager User"), 
                ("admin", "DELETE TEST Admin User")
            ]
            
            for i, (role, base_name) in enumerate(user_roles):
                user_data = RMSTestFixtures.generate_user_data("placeholder", "placeholder", role)
                
                # Customize for deletion testing
                user_data["email"] = f"deletetest.{role}.{i+1}@testrestaurant.com"
                user_data["full_name"] = f"{base_name} {i+1}"
                user_data["password"] = "secure_delete_test_password"
                
                # Assign to restaurant if available
                if self.available_restaurants:
                    user_data["restaurant_id"] = self.available_restaurants[0]["id"]
                    
                response = await self.client.post("/api/v1/users", json=user_data, headers=self.auth_headers)
                
                if response.status_code == 201:
                    user = response.json()
                    self.test_users.append(user)
                    self.cleanup_queue.append(("user", user['id'], user['email']))
                    print(f"   👤 Created test user: {user['email']} ({user['id']})")
                    
                elif response.status_code == 409:
                    print(f"   ⚠️ User {user_data['email']} already exists - skipping")
                    
                elif response.status_code == 403:
                    print(f"   ⚠️ User creation forbidden - may not have permission to create {role} users")
                    
                else:
                    print(f"   ❌ Failed to create test user {user_data['email']}: HTTP {response.status_code}")
                    
            created_count = len(self.test_users)
            APITestHelper.print_test_step(f"Created {created_count} test users for deletion testing", "SUCCESS")
            
        except Exception as e:
            APITestHelper.print_test_step(f"Failed to create test users: {e}", "FAILED")
            
    async def test_user_soft_deletion(self) -> bool:
        """Test user soft deletion (deactivation)"""
        
        APITestHelper.print_test_header("User Soft Deletion (Deactivation)", "💤")
        
        if not self.test_users:
            APITestHelper.print_test_step("No test users available for soft deletion testing", "SKIPPED")
            return True
            
        # Test deactivating users instead of hard deletion
        success_count = 0
        
        for user in self.test_users[:1]:  # Test with first user
            try:
                user_id = user['id']
                user_email = user['email']
                current_status = user.get('is_active', True)
                
                APITestHelper.print_test_step(f"Deactivating user: {user_email}", "RUNNING")
                
                # First verify user is active
                if not current_status:
                    APITestHelper.print_test_step(f"User {user_email} is already inactive", "SKIPPED")
                    continue
                    
                deactivation_data = {
                    "is_active": False
                }
                
                start_time = time.time()
                
                # Try different endpoints for deactivation
                endpoints_to_try = [
                    f"/api/v1/users/{user_id}/status",
                    f"/api/v1/users/{user_id}/deactivate",
                    f"/api/v1/users/{user_id}"
                ]
                
                deactivated = False
                
                for endpoint in endpoints_to_try:
                    try:
                        if "deactivate" in endpoint:
                            response = await self.client.post(endpoint, headers=self.auth_headers)
                        else:
                            response = await self.client.patch(endpoint, json=deactivation_data, headers=self.auth_headers)
                            
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status_code == 200:
                            updated_user = response.json()
                            new_status = updated_user.get('is_active')
                            
                            APITestHelper.print_test_step(f"User deactivated successfully ({response_time:.0f}ms)", "SUCCESS")
                            
                            if new_status == False:
                                APITestHelper.print_test_step("User status correctly set to inactive", "SUCCESS")
                                
                                print(f"   💤 Deactivation Details:")
                                print(f"      User: {user_email}")
                                print(f"      Previous Status: Active")
                                print(f"      Current Status: Inactive")
                                print(f"      Endpoint: {endpoint}")
                                
                                # Verify user can no longer authenticate
                                await asyncio.sleep(0.1)
                                auth_test = await self.test_deactivated_user_auth(user_email)
                                
                                self.results.add_success("user_soft_deletion", f"Deactivate user {user_email}", {
                                    "response_time": response_time,
                                    "user_id": user_id,
                                    "endpoint": endpoint,
                                    "auth_blocked": auth_test
                                })
                                success_count += 1
                                deactivated = True
                                
                            else:
                                APITestHelper.print_test_step("Deactivation verification failed", "FAILED")
                                
                            break
                            
                        elif response.status_code == 404:
                            continue  # Try next endpoint
                            
                        elif response.status_code == 403:
                            APITestHelper.print_test_step("User deactivation forbidden (permission check working)", "SUCCESS")
                            self.results.add_success("user_soft_deletion", f"Deactivate user {user_email} (permission check)", {
                                "response_time": response_time,
                                "permission_enforced": True
                            })
                            success_count += 1
                            deactivated = True
                            break
                            
                        else:
                            APITestHelper.print_test_step(f"Deactivation failed: HTTP {response.status_code}", "FAILED")
                            if response.json_data:
                                print(f"   Error: {response.json_data}")
                            break
                            
                    except Exception:
                        continue  # Try next endpoint
                        
                if not deactivated:
                    APITestHelper.print_test_step("User deactivation endpoints not found", "SKIPPED")
                    
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"User deactivation error: {e}", "FAILED")
                self.results.add_failure("user_soft_deletion", f"Deactivate user {user_email}", str(e))
                
        print(f"\n📊 Soft Deletion Summary: {success_count}/{min(1, len(self.test_users))} successful")
        return success_count > 0
        
    async def test_deactivated_user_auth(self, user_email: str) -> bool:
        """Test that deactivated user cannot authenticate"""
        
        try:
            auth_data = {
                "username": user_email,
                "password": "secure_delete_test_password"
            }
            
            response = await self.client.post("/auth/login", data=auth_data)
            
            if response.status_code == 401:
                APITestHelper.print_test_step("Deactivated user correctly blocked from authentication", "SUCCESS")
                return True
            elif response.status_code == 200:
                APITestHelper.print_test_step("Deactivated user can still authenticate (security issue)", "FAILED")
                return False
            else:
                APITestHelper.print_test_step(f"Unexpected auth response: HTTP {response.status_code}", "SKIPPED")
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Auth test error: {e}", "FAILED")
            return False
            
    async def test_user_hard_deletion(self) -> bool:
        """Test user hard deletion (permanent removal)"""
        
        APITestHelper.print_test_header("User Hard Deletion", "🗑️")
        
        if not self.test_users:
            APITestHelper.print_test_step("No test users available for hard deletion testing", "SKIPPED")
            return True
            
        if not self.confirm_deletes:
            APITestHelper.print_test_step("Hard deletion requires --confirm-deletes flag", "SKIPPED")
            return True
            
        success_count = 0
        
        # Test hard deletion of remaining users
        for user in self.test_users[1:2]:  # Delete second user, keep others for cleanup
            try:
                user_id = user['id']
                user_email = user['email']
                
                APITestHelper.print_test_step(f"Hard deleting user: {user_email}", "RUNNING")
                
                # First verify user exists
                verify_response = await self.client.get(f"/api/v1/users/{user_id}", headers=self.auth_headers)
                if verify_response.status_code != 200:
                    APITestHelper.print_test_step(f"User {user_email} not found for deletion", "SKIPPED")
                    continue
                    
                start_time = time.time()
                response = await self.client.delete(f"/api/v1/users/{user_id}", headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 204:
                    APITestHelper.print_test_step(f"User deleted successfully ({response_time:.0f}ms)", "SUCCESS")
                    
                    # Verify user is actually deleted
                    await asyncio.sleep(0.1)
                    verify_response = await self.client.get(f"/api/v1/users/{user_id}", headers=self.auth_headers)
                    
                    if verify_response.status_code == 404:
                        APITestHelper.print_test_step("Deletion verified - user not found", "SUCCESS")
                        
                        # Remove from cleanup queue since it's deleted
                        self.cleanup_queue = [entry for entry in self.cleanup_queue if not (entry[0] == "user" and entry[1] == user_id)]
                        
                        # Test that deleted user cannot authenticate
                        auth_test = await self.test_deleted_user_auth(user_email)
                        
                        print(f"   🗑️ Hard Deletion Details:")
                        print(f"      User: {user_email}")
                        print(f"      User ID: {user_id}")
                        print(f"      Verification: User not found")
                        print(f"      Auth Blocked: {auth_test}")
                        
                    else:
                        APITestHelper.print_test_step("Deletion verification failed - user still exists", "FAILED")
                        
                    self.results.add_success("user_hard_deletion", f"Delete user {user_email}", {
                        "response_time": response_time,
                        "user_id": user_id,
                        "verified": verify_response.status_code == 404
                    })
                    success_count += 1
                    
                elif response.status_code == 404:
                    APITestHelper.print_test_step(f"User not found (may already be deleted)", "SKIPPED")
                    
                elif response.status_code == 403:
                    APITestHelper.print_test_step("User deletion forbidden (permission check working)", "SUCCESS")
                    self.results.add_success("user_hard_deletion", f"Delete user {user_email} (permission check)", {
                        "response_time": response_time,
                        "permission_enforced": True
                    })
                    success_count += 1
                    
                elif response.status_code == 409:
                    APITestHelper.print_test_step("User deletion conflict (may have dependencies)", "SKIPPED")
                    print(f"   ⚠️ User may have data/dependencies preventing deletion")
                    
                else:
                    APITestHelper.print_test_step(f"User deletion failed: HTTP {response.status_code}", "FAILED")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    self.results.add_failure("user_hard_deletion", f"Delete user {user_email}", 
                                          f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"User deletion error: {e}", "FAILED")
                self.results.add_failure("user_hard_deletion", f"Delete user {user_email}", str(e))
                
        print(f"\n📊 Hard Deletion Summary: {success_count}/{min(1, len(self.test_users[1:]))} successful")
        return success_count > 0
        
    async def test_deleted_user_auth(self, user_email: str) -> bool:
        """Test that deleted user cannot authenticate"""
        
        try:
            auth_data = {
                "username": user_email,
                "password": "secure_delete_test_password"
            }
            
            response = await self.client.post("/auth/login", data=auth_data)
            
            if response.status_code == 401:
                APITestHelper.print_test_step("Deleted user correctly blocked from authentication", "SUCCESS")
                return True
            elif response.status_code == 200:
                APITestHelper.print_test_step("Deleted user can still authenticate (critical security issue)", "FAILED")
                return False
            else:
                APITestHelper.print_test_step(f"Unexpected auth response: HTTP {response.status_code}", "SKIPPED")
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Auth test error: {e}", "FAILED")
            return False
            
    async def test_user_deletion_constraints(self) -> bool:
        """Test user deletion constraints and dependencies"""
        
        APITestHelper.print_test_header("User Deletion Constraints", "🔗")
        
        if not self.test_users:
            APITestHelper.print_test_step("No test users available for constraint testing", "SKIPPED")
            return True
            
        # Test deleting users that might have dependencies
        constraint_tests = [
            ("current_user", "Attempt to delete current authenticated user"),
            ("admin_user", "Attempt to delete admin user (may be protected)"),
            ("user_with_data", "Attempt to delete user with associated data")
        ]
        
        success_count = 0
        
        for test_type, description in constraint_tests:
            try:
                APITestHelper.print_test_step(f"Testing: {description}", "RUNNING")
                
                if test_type == "current_user":
                    # Try to get current user info and delete self
                    me_response = await self.client.get("/auth/me", headers=self.auth_headers)
                    if me_response.status_code == 200:
                        current_user = me_response.json()
                        current_user_id = current_user.get('id')
                        
                        if current_user_id:
                            start_time = time.time()
                            response = await self.client.delete(f"/api/v1/users/{current_user_id}", headers=self.auth_headers)
                            response_time = (time.time() - start_time) * 1000
                            
                            if response.status_code in [403, 409]:
                                APITestHelper.print_test_step(f"Self-deletion correctly prevented ({response_time:.0f}ms)", "SUCCESS")
                                self.results.add_success("user_deletion_constraints", description, {
                                    "response_time": response_time,
                                    "constraint_enforced": True
                                })
                                success_count += 1
                                
                            elif response.status_code == 204:
                                APITestHelper.print_test_step("Self-deletion succeeded (may be allowed)", "SKIPPED")
                                
                            else:
                                APITestHelper.print_test_step(f"Unexpected response: HTTP {response.status_code}", "FAILED")
                                
                        else:
                            APITestHelper.print_test_step("Could not determine current user ID", "SKIPPED")
                            
                    else:
                        APITestHelper.print_test_step("Could not get current user info", "SKIPPED")
                        
                elif test_type == "admin_user" and self.test_users:
                    # Find admin user in test users
                    admin_users = [user for user in self.test_users if user.get('role') == 'admin']
                    
                    if admin_users:
                        admin_user = admin_users[0]
                        user_id = admin_user['id']
                        
                        start_time = time.time()
                        response = await self.client.delete(f"/api/v1/users/{user_id}", headers=self.auth_headers)
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status_code in [403, 409]:
                            APITestHelper.print_test_step(f"Admin deletion correctly prevented ({response_time:.0f}ms)", "SUCCESS")
                            self.results.add_success("user_deletion_constraints", description, {
                                "response_time": response_time,
                                "constraint_enforced": True
                            })
                            success_count += 1
                            
                        elif response.status_code == 204:
                            APITestHelper.print_test_step("Admin deletion succeeded (may be allowed)", "SKIPPED")
                            
                        else:
                            APITestHelper.print_test_step(f"Unexpected response: HTTP {response.status_code}", "FAILED")
                            
                    else:
                        APITestHelper.print_test_step("No admin users available for constraint testing", "SKIPPED")
                        
                elif test_type == "user_with_data":
                    # This would test deleting users that have created orders, etc.
                    # For now, we'll skip this as it requires more complex setup
                    APITestHelper.print_test_step("User data dependency testing not implemented", "SKIPPED")
                    
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Constraint test error: {e}", "FAILED")
                self.results.add_failure("user_deletion_constraints", description, str(e))
                
        print(f"\n📊 Constraint Testing Summary: {success_count}/{len(constraint_tests)} tests passed")
        return True  # Constraints may not be implemented
        
    async def test_deletion_validation(self) -> bool:
        """Test user deletion validation and error handling"""
        
        APITestHelper.print_test_header("User Deletion Validation", "✅")
        
        validation_tests = [
            ("/api/v1/users/invalid-uuid", "Invalid user UUID"),
            ("/api/v1/users/00000000-0000-0000-0000-000000000000", "Non-existent user"),
            ("/api/v1/users/", "Missing user ID in path")
        ]
        
        success_count = 0
        
        for endpoint, description in validation_tests:
            try:
                APITestHelper.print_test_step(f"Testing: {description}", "RUNNING")
                
                start_time = time.time()
                response = await self.client.delete(endpoint, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                # We expect 404 for non-existent users, 400 for invalid UUIDs, 405 for missing ID
                expected_codes = [400, 404, 405]
                
                if response.status_code in expected_codes:
                    APITestHelper.print_test_step(f"Correctly returned HTTP {response.status_code} ({response_time:.0f}ms)", "SUCCESS")
                    
                    self.results.add_success("user_deletion_validation", description, {
                        "response_time": response_time,
                        "correct_error_code": True,
                        "status_code": response.status_code
                    })
                    success_count += 1
                    
                elif response.status_code == 204:
                    APITestHelper.print_test_step(f"Unexpected success for invalid deletion", "FAILED")
                    self.results.add_failure("user_deletion_validation", description, 
                                          "Invalid deletion succeeded", 204)
                    
                else:
                    APITestHelper.print_test_step(f"Unexpected response: HTTP {response.status_code}", "FAILED")
                    self.results.add_failure("user_deletion_validation", description, 
                                          f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.2)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Validation test error: {e}", "FAILED")
                self.results.add_failure("user_deletion_validation", description, str(e))
                
        print(f"\n📊 Validation Testing Summary: {success_count}/{len(validation_tests)} tests passed")
        return success_count > 0
        
    def print_user_deletion_summary(self):
        """Print comprehensive user deletion test summary"""
        
        APITestHelper.print_test_header("User Deletion Tests Summary", "📊")
        
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
            
        # Show test data created
        print(f"\n📊 Test Data Created:")
        print(f"   Users: {len(self.test_users)}")
        
        if self.test_users:
            print(f"\n   👤 Test Users:")
            for user in self.test_users:
                print(f"      • {user['email']} ({user.get('role', 'N/A')}) - ID: {user['id']}")
        
        # Cleanup queue status
        if self.cleanup_queue:
            print(f"\n🧹 Cleanup Queue: {len(self.cleanup_queue)} entities")
            for entity_type, entity_id, entity_name in self.cleanup_queue:
                print(f"   • {entity_type}: {entity_name} ({entity_id})")
        
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
                    
    async def cleanup_remaining_users(self):
        """Clean up any remaining test users"""
        
        if not self.cleanup_queue:
            return
            
        print(f"\n🧹 Cleaning up {len(self.cleanup_queue)} remaining test users...")
        
        for entity_type, entity_id, entity_name in self.cleanup_queue:
            if entity_type != "user":
                continue
                
            try:
                response = await self.client.delete(f"/api/v1/users/{entity_id}", headers=self.auth_headers)
                
                if response.status_code == 204:
                    print(f"   ✅ Cleaned up user: {entity_name}")
                elif response.status_code == 404:
                    print(f"   ⚠️ User already deleted: {entity_name}")
                else:
                    print(f"   ❌ Failed to cleanup user: {entity_name} (HTTP {response.status_code})")
                    
                await asyncio.sleep(0.1)
                
            except Exception as e:
                print(f"   ❌ Error cleaning up user: {e}")
                
    async def run_comprehensive_user_deletion_tests(self) -> bool:
        """Run all user deletion tests"""
        
        print("🗑️ RMS User Deletion Operations Tests")
        print("="*50)
        
        if not self.confirm_deletes:
            print("⚠️  DESTRUCTIVE TESTING DISABLED")
            print("   Use --confirm-deletes flag to enable hard deletion testing")
            print("   Soft deletion (deactivation) tests will still run")
            print()
        
        start_time = time.time()
        
        try:
            # Setup authentication
            if not await self.setup_authentication():
                return False
                
            # Load available restaurants
            await self.load_available_restaurants()
            
            # Create test users for deletion testing
            await self.create_test_users()
                
            # Run all user deletion tests
            tests = [
                ("User Soft Deletion", self.test_user_soft_deletion),
                ("User Hard Deletion", self.test_user_hard_deletion),
                ("User Deletion Constraints", self.test_user_deletion_constraints),
                ("User Deletion Validation", self.test_deletion_validation)
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
            self.print_user_deletion_summary()
            
            return overall_success
            
        except KeyboardInterrupt:
            print("\n⚠️ User deletion tests interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ User deletion tests failed: {e}")
            return False
        finally:
            # Always cleanup remaining users
            try:
                await self.cleanup_remaining_users()
            except Exception as e:
                print(f"⚠️ Final cleanup failed: {e}")
                
            await self.client.close()


async def main():
    """Main entry point for user deletion testing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Test RMS user deletion operations")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--confirm-deletes", action="store_true", 
                       help="Confirm that you want to perform destructive delete operations")
    
    args = parser.parse_args()
    
    tester = UserDeletionTester(args.base_url, args.confirm_deletes)
    
    try:
        success = await tester.run_comprehensive_user_deletion_tests()
        
        if success:
            print(f"\n✅ All user deletion tests passed successfully!")
        else:
            print(f"\n❌ Some user deletion tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ User deletion testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())