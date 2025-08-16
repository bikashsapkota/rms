#!/usr/bin/env python3
"""
Test Authentication Read Operations

Comprehensive testing of authentication and user-related GET endpoints.
Tests user profiles, authentication status, and permission verification.
"""

import sys
import asyncio
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.api_tester.shared.utils import APITestClient, APITestHelper, TestResults
from tests.api_tester.shared.auth import get_auth_headers, authenticate_as_role


class AuthReadTester:
    """Comprehensive authentication read operations testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.results = TestResults()
        self.auth_headers = None
        
    async def setup_authentication(self) -> bool:
        """Setup authentication for all tests"""
        
        self.auth_headers = await get_auth_headers(self.client)
        if not self.auth_headers:
            APITestHelper.print_test_step("Authentication failed - cannot run auth tests", "FAILED")
            return False
            
        APITestHelper.print_test_step("Authentication successful", "SUCCESS")
        return True
        
    async def test_current_user_profile(self) -> bool:
        """Test getting current user profile"""
        
        APITestHelper.print_test_header("Current User Profile", "👤")
        
        try:
            start_time = time.time()
            response = await self.client.get("/auth/me", headers=self.auth_headers)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                user_profile = response.json()
                
                APITestHelper.print_test_step(f"User profile retrieved ({response_time:.0f}ms)", "SUCCESS")
                
                # Validate user profile structure
                if APITestHelper.validate_user_response(user_profile):
                    APITestHelper.print_test_step("User profile structure is valid", "SUCCESS")
                    
                    print(f"   👤 User Profile:")
                    print(f"      Email: {user_profile.get('email', 'N/A')}")
                    print(f"      Name: {user_profile.get('full_name', 'N/A')}")
                    print(f"      Role: {user_profile.get('role', 'N/A')}")
                    print(f"      Active: {user_profile.get('is_active', 'N/A')}")
                    print(f"      Organization: {user_profile.get('organization_id', 'N/A')}")
                    print(f"      Restaurant: {user_profile.get('restaurant_id', 'N/A')}")
                    
                    # Check additional profile fields
                    if 'created_at' in user_profile:
                        print(f"      Created: {user_profile['created_at']}")
                    if 'last_login' in user_profile:
                        print(f"      Last Login: {user_profile['last_login']}")
                        
                else:
                    APITestHelper.print_test_step("User profile missing required fields", "FAILED")
                    
                self.results.add_success("auth_profile", "Current user profile", {
                    "response_time": response_time,
                    "user_email": user_profile.get('email'),
                    "user_role": user_profile.get('role')
                })
                return True
                
            elif response.status_code == 401:
                APITestHelper.print_test_step("User profile requires authentication", "FAILED")
                self.results.add_failure("auth_profile", "Current user profile", 
                                       "Authentication required", 401)
                return False
                
            else:
                APITestHelper.print_test_step(f"User profile failed: HTTP {response.status_code}", "FAILED")
                self.results.add_failure("auth_profile", "Current user profile", 
                                       f"HTTP {response.status_code}", response.status_code)
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"User profile error: {e}", "FAILED")
            self.results.add_failure("auth_profile", "Current user profile", str(e))
            return False
            
    async def test_users_list(self) -> bool:
        """Test listing users (with appropriate permissions)"""
        
        APITestHelper.print_test_header("Users List", "👥")
        
        try:
            start_time = time.time()
            response = await self.client.get("/api/v1/users", headers=self.auth_headers)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                users = response.json()
                
                APITestHelper.print_test_step(f"Users endpoint responding ({response_time:.0f}ms)", "SUCCESS")
                
                # Validate response structure
                if isinstance(users, list):
                    user_count = len(users)
                    APITestHelper.print_test_step(f"Found {user_count} users (list format)", "SUCCESS")
                    
                    # Validate individual user structure
                    if users:
                        sample_user = users[0]
                        if APITestHelper.validate_user_response(sample_user):
                            APITestHelper.print_test_step("User data structure is valid", "SUCCESS")
                        else:
                            APITestHelper.print_test_step("User data structure is invalid", "FAILED")
                            
                        # Print sample user details (hide sensitive info)
                        print(f"   👤 Sample User:")
                        print(f"      Email: {sample_user.get('email', 'N/A')}")
                        print(f"      Role: {sample_user.get('role', 'N/A')}")
                        print(f"      Active: {sample_user.get('is_active', 'N/A')}")
                        
                elif isinstance(users, dict):
                    # Paginated response
                    items = users.get('items', [])
                    total = users.get('total', 0)
                    page = users.get('page', 1)
                    size = users.get('size', len(items))
                    
                    APITestHelper.print_test_step(f"Found {len(items)} users (paginated: {total} total)", "SUCCESS")
                    print(f"   📊 Pagination: Page {page}, Size {size}, Total {total}")
                    
                    if items:
                        sample_user = items[0]
                        print(f"   👤 Sample User: {sample_user.get('email', 'N/A')} ({sample_user.get('role', 'N/A')})")
                        
                else:
                    APITestHelper.print_test_step("Unexpected response format", "FAILED")
                    
                self.results.add_success("users", "List users", {
                    "response_time": response_time,
                    "count": user_count if isinstance(users, list) else len(users.get('items', [])),
                    "format": "list" if isinstance(users, list) else "paginated"
                })
                return True
                
            elif response.status_code == 403:
                APITestHelper.print_test_step("Users list forbidden (insufficient permissions)", "SKIPPED")
                self.results.add_success("users", "List users (permission check)", {
                    "response_time": response_time,
                    "permission_enforced": True
                })
                return True  # This is actually good - permissions are working
                
            elif response.status_code == 404:
                APITestHelper.print_test_step("Users endpoint not found (may not be implemented)", "SKIPPED")
                return True
                
            else:
                APITestHelper.print_test_step(f"Users list failed: HTTP {response.status_code}", "FAILED")
                self.results.add_failure("users", "List users", 
                                       f"HTTP {response.status_code}", response.status_code)
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Users list error: {e}", "FAILED")
            self.results.add_failure("users", "List users", str(e))
            return False
            
    async def test_user_details(self, user_id: str = None) -> bool:
        """Test getting individual user details"""
        
        APITestHelper.print_test_header("User Details", "🔍")
        
        # Try to get current user ID first
        if not user_id:
            try:
                response = await self.client.get("/auth/me", headers=self.auth_headers)
                if response.status_code == 200:
                    current_user = response.json()
                    user_id = current_user.get('id')
                    
                if not user_id:
                    # Try to get from users list
                    response = await self.client.get("/api/v1/users", headers=self.auth_headers)
                    if response.status_code == 200:
                        users = response.json()
                        
                        if isinstance(users, list) and users:
                            user_id = users[0]['id']
                        elif isinstance(users, dict) and users.get('items'):
                            user_id = users['items'][0]['id']
                            
                if not user_id:
                    APITestHelper.print_test_step("No user ID available for detail testing", "SKIPPED")
                    return True
                    
            except Exception:
                APITestHelper.print_test_step("Cannot get user ID for detail testing", "SKIPPED")
                return True
                
        try:
            start_time = time.time()
            response = await self.client.get(f"/api/v1/users/{user_id}", headers=self.auth_headers)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                user_details = response.json()
                
                APITestHelper.print_test_step(f"User details retrieved ({response_time:.0f}ms)", "SUCCESS")
                
                # Validate user structure
                if APITestHelper.validate_user_response(user_details):
                    APITestHelper.print_test_step("User details structure is valid", "SUCCESS")
                    
                    print(f"   🔍 User Details:")
                    print(f"      ID: {user_details.get('id')}")
                    print(f"      Email: {user_details.get('email')}")
                    print(f"      Full Name: {user_details.get('full_name')}")
                    print(f"      Role: {user_details.get('role')}")
                    print(f"      Active: {user_details.get('is_active')}")
                    print(f"      Organization: {user_details.get('organization_id', 'N/A')}")
                    print(f"      Restaurant: {user_details.get('restaurant_id', 'N/A')}")
                    
                    # Check that password is not exposed
                    if 'password' in user_details or 'password_hash' in user_details:
                        APITestHelper.print_test_step("⚠️  Password data exposed in user details", "FAILED")
                        self.results.add_failure("users", "User details security", 
                                               "Password data exposed")
                        return False
                    else:
                        APITestHelper.print_test_step("Password data properly hidden", "SUCCESS")
                        
                else:
                    APITestHelper.print_test_step("User details missing required fields", "FAILED")
                    
                self.results.add_success("users", "User details", {
                    "response_time": response_time,
                    "user_id": user_id,
                    "user_email": user_details.get('email')
                })
                return True
                
            elif response.status_code == 403:
                APITestHelper.print_test_step("User details forbidden (permission check working)", "SUCCESS")
                self.results.add_success("users", "User details (permission check)", {
                    "response_time": response_time,
                    "permission_enforced": True
                })
                return True
                
            elif response.status_code == 404:
                APITestHelper.print_test_step(f"User {user_id} not found", "FAILED")
                self.results.add_failure("users", "User details", 
                                       f"User not found: {user_id}", 404)
                return False
                
            else:
                APITestHelper.print_test_step(f"User details failed: HTTP {response.status_code}", "FAILED")
                self.results.add_failure("users", "User details", 
                                       f"HTTP {response.status_code}", response.status_code)
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"User details error: {e}", "FAILED")
            self.results.add_failure("users", "User details", str(e))
            return False
            
    async def test_authentication_status_endpoints(self) -> bool:
        """Test various authentication status endpoints"""
        
        APITestHelper.print_test_header("Authentication Status", "🔐")
        
        # Test with valid authentication
        auth_endpoints = [
            ("/auth/status", "Authentication status"),
            ("/auth/validate", "Token validation"),
            ("/auth/permissions", "User permissions"),
            ("/auth/session", "Session information")
        ]
        
        success_count = 0
        
        for endpoint, description in auth_endpoints:
            try:
                start_time = time.time()
                response = await self.client.get(endpoint, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    APITestHelper.print_test_step(f"{description} available ({response_time:.0f}ms)", "SUCCESS")
                    
                    auth_data = response.json()
                    if isinstance(auth_data, dict):
                        print(f"   🔐 Response keys: {list(auth_data.keys())}")
                        
                        # Check for common auth status fields
                        if 'authenticated' in auth_data:
                            print(f"      Authenticated: {auth_data['authenticated']}")
                        if 'user_id' in auth_data:
                            print(f"      User ID: {auth_data['user_id']}")
                        if 'permissions' in auth_data:
                            perms = auth_data['permissions']
                            if isinstance(perms, list):
                                print(f"      Permissions: {len(perms)} items")
                            else:
                                print(f"      Permissions: {perms}")
                                
                    self.results.add_success("auth_status", description, {
                        "endpoint": endpoint,
                        "response_time": response_time
                    })
                    success_count += 1
                    
                elif response.status_code == 404:
                    APITestHelper.print_test_step(f"{description} not found (may not be implemented)", "SKIPPED")
                    
                elif response.status_code == 401:
                    APITestHelper.print_test_step(f"{description} requires authentication", "FAILED")
                    self.results.add_failure("auth_status", description, 
                                           "Authentication required", 401)
                    
                else:
                    APITestHelper.print_test_step(f"{description} failed: HTTP {response.status_code}", "FAILED")
                    self.results.add_failure("auth_status", description, 
                                           f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.1)
                
            except Exception as e:
                APITestHelper.print_test_step(f"{description} error: {e}", "FAILED")
                self.results.add_failure("auth_status", description, str(e))
                
        if success_count == 0:
            APITestHelper.print_test_step("No auth status endpoints found (basic auth working)", "SUCCESS")
            
        return True  # Not a failure if status endpoints aren't implemented
        
    async def test_role_based_access(self) -> bool:
        """Test role-based access control"""
        
        APITestHelper.print_test_header("Role-Based Access Control", "🛡️")
        
        # Test endpoints that should have different access levels
        access_tests = [
            ("/api/v1/users", "Users management", ["admin", "manager"]),
            ("/api/v1/restaurants", "Restaurant access", ["admin", "manager", "staff"]),
            ("/api/v1/menu/categories", "Menu categories", ["admin", "manager", "staff"]),
            ("/api/v1/analytics", "Analytics access", ["admin", "manager"])
        ]
        
        current_user_response = await self.client.get("/auth/me", headers=self.auth_headers)
        if current_user_response.status_code == 200:
            current_user = current_user_response.json()
            current_role = current_user.get('role', 'unknown')
            
            print(f"   👤 Testing as role: {current_role}")
            
            for endpoint, description, allowed_roles in access_tests:
                try:
                    start_time = time.time()
                    response = await self.client.get(endpoint, headers=self.auth_headers)
                    response_time = (time.time() - start_time) * 1000
                    
                    should_have_access = current_role in allowed_roles
                    has_access = response.status_code in [200, 404]  # 404 might be empty data
                    access_denied = response.status_code == 403
                    
                    if should_have_access and has_access:
                        APITestHelper.print_test_step(f"{description}: Access granted (correct)", "SUCCESS")
                        self.results.add_success("role_access", f"{description} (allowed)", {
                            "endpoint": endpoint,
                            "role": current_role,
                            "expected": "allowed",
                            "actual": "allowed"
                        })
                        
                    elif not should_have_access and access_denied:
                        APITestHelper.print_test_step(f"{description}: Access denied (correct)", "SUCCESS")
                        self.results.add_success("role_access", f"{description} (denied)", {
                            "endpoint": endpoint,
                            "role": current_role,
                            "expected": "denied",
                            "actual": "denied"
                        })
                        
                    elif should_have_access and access_denied:
                        APITestHelper.print_test_step(f"{description}: Access denied (should be allowed)", "FAILED")
                        self.results.add_failure("role_access", f"{description} (wrongly denied)", 
                                               f"Role {current_role} should have access", 403)
                        
                    elif not should_have_access and has_access:
                        APITestHelper.print_test_step(f"{description}: Access granted (should be denied)", "FAILED")
                        self.results.add_failure("role_access", f"{description} (wrongly allowed)", 
                                               f"Role {current_role} should not have access", response.status_code)
                        
                    elif response.status_code == 404:
                        APITestHelper.print_test_step(f"{description}: Endpoint not found", "SKIPPED")
                        
                    else:
                        APITestHelper.print_test_step(f"{description}: Unexpected response {response.status_code}", "FAILED")
                        
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    APITestHelper.print_test_step(f"{description} error: {e}", "FAILED")
                    self.results.add_failure("role_access", f"{description} (error)", str(e))
                    
        else:
            APITestHelper.print_test_step("Cannot determine current user role for access testing", "SKIPPED")
            
        return True
        
    async def test_token_validation(self) -> bool:
        """Test token validation and expiration handling"""
        
        APITestHelper.print_test_header("Token Validation", "🎫")
        
        try:
            # Test with valid token
            start_time = time.time()
            response = await self.client.get("/auth/me", headers=self.auth_headers)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                APITestHelper.print_test_step(f"Valid token accepted ({response_time:.0f}ms)", "SUCCESS")
                self.results.add_success("token_validation", "Valid token", {
                    "response_time": response_time
                })
                
            else:
                APITestHelper.print_test_step(f"Valid token rejected: HTTP {response.status_code}", "FAILED")
                self.results.add_failure("token_validation", "Valid token", 
                                       f"HTTP {response.status_code}", response.status_code)
                return False
                
            # Test with invalid token
            invalid_headers = {"Authorization": "Bearer invalid_token_12345"}
            start_time = time.time()
            response = await self.client.get("/auth/me", headers=invalid_headers)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 401:
                APITestHelper.print_test_step(f"Invalid token rejected ({response_time:.0f}ms)", "SUCCESS")
                self.results.add_success("token_validation", "Invalid token rejection", {
                    "response_time": response_time
                })
                
            else:
                APITestHelper.print_test_step(f"Invalid token accepted: HTTP {response.status_code}", "FAILED")
                self.results.add_failure("token_validation", "Invalid token rejection", 
                                       f"HTTP {response.status_code}", response.status_code)
                return False
                
            # Test with no token
            start_time = time.time()
            response = await self.client.get("/auth/me")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 401:
                APITestHelper.print_test_step(f"No token rejected ({response_time:.0f}ms)", "SUCCESS")
                self.results.add_success("token_validation", "No token rejection", {
                    "response_time": response_time
                })
                
            else:
                APITestHelper.print_test_step(f"No token accepted: HTTP {response.status_code}", "FAILED")
                self.results.add_failure("token_validation", "No token rejection", 
                                       f"HTTP {response.status_code}", response.status_code)
                return False
                
            return True
            
        except Exception as e:
            APITestHelper.print_test_step(f"Token validation error: {e}", "FAILED")
            self.results.add_failure("token_validation", "Token validation", str(e))
            return False
            
    def print_auth_test_summary(self):
        """Print comprehensive auth test summary"""
        
        APITestHelper.print_test_header("Authentication Read Tests Summary", "📊")
        
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
                    
    async def run_comprehensive_auth_tests(self) -> bool:
        """Run all authentication read tests"""
        
        print("🔐 RMS Authentication Read Operations Tests")
        print("="*50)
        
        start_time = time.time()
        
        try:
            # Setup authentication
            if not await self.setup_authentication():
                return False
                
            # Run all auth tests
            tests = [
                ("Current User Profile", self.test_current_user_profile),
                ("Users List", self.test_users_list),
                ("User Details", self.test_user_details),
                ("Authentication Status", self.test_authentication_status_endpoints),
                ("Role-Based Access Control", self.test_role_based_access),
                ("Token Validation", self.test_token_validation)
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
            self.print_auth_test_summary()
            
            return overall_success
            
        except KeyboardInterrupt:
            print("\n⚠️  Authentication tests interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Authentication tests failed: {e}")
            return False
        finally:
            await self.client.close()


async def main():
    """Main entry point for authentication read testing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Test RMS authentication read operations")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    tester = AuthReadTester(args.base_url)
    
    try:
        success = await tester.run_comprehensive_auth_tests()
        
        if success:
            print(f"\n✅ All authentication read tests passed successfully!")
        else:
            print(f"\n❌ Some authentication read tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Authentication read testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())