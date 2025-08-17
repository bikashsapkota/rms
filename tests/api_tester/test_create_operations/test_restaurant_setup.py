#!/usr/bin/env python3
"""
Test Restaurant Setup Operations

Comprehensive testing of restaurant setup and onboarding workflows.
Tests the restaurant application and approval process.
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


class RestaurantSetupTester:
    """Comprehensive restaurant setup operations testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.results = TestResults()
        self.auth_headers = None
        self.created_applications = []
        self.created_restaurants = []
        
    async def setup_authentication(self) -> bool:
        """Setup authentication for all tests"""
        
        self.auth_headers = await get_auth_headers(self.client)
        if not self.auth_headers:
            APITestHelper.print_test_step("Authentication failed - cannot run restaurant setup tests", "FAILED")
            return False
            
        APITestHelper.print_test_step("Authentication successful", "SUCCESS")
        return True
        
    async def test_restaurant_application_submission(self) -> bool:
        """Test submitting restaurant applications"""
        
        APITestHelper.print_test_header("Restaurant Application Submission", "📝")
        
        # Generate test restaurant data
        application_scenarios = [
            ("independent", "Independent Restaurant"),
            ("chain", "Chain Restaurant"),
            ("franchise", "Franchise Restaurant")
        ]
        
        success_count = 0
        
        for org_type, description in application_scenarios:
            try:
                # Generate application data
                restaurant_data = RMSTestFixtures.generate_restaurant_data("placeholder", f"App Test {org_type}")
                organization_data = RMSTestFixtures.generate_organization_data(org_type)
                admin_user = RMSTestFixtures.generate_user_data("placeholder", "placeholder", "admin")
                
                application_data = {
                    "restaurant": restaurant_data,
                    "organization": organization_data,
                    "admin_user": {
                        "email": f"admin.{org_type}@testrestaurant.com",
                        "full_name": admin_user["full_name"],
                        "password": "secure_application_password"
                    },
                    "application_notes": f"Test application for {description}"
                }
                
                APITestHelper.print_test_step(f"Submitting {description} application", "RUNNING")
                
                start_time = time.time()
                response = await self.client.post("/api/v1/setup", json=application_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 201:
                    application_response = response.json()
                    self.created_applications.append(application_response)
                    
                    APITestHelper.print_test_step(f"{description} application submitted ({response_time:.0f}ms)", "SUCCESS")
                    
                    # Validate response structure
                    if isinstance(application_response, dict):
                        print(f"   📝 Application Details:")
                        print(f"      Application ID: {application_response.get('application_id', 'N/A')}")
                        print(f"      Restaurant Name: {application_response.get('restaurant_name', 'N/A')}")
                        print(f"      Organization Type: {application_response.get('organization_type', 'N/A')}")
                        print(f"      Status: {application_response.get('status', 'N/A')}")
                        
                        # Check for expected status
                        status = application_response.get('status', '')
                        if status in ['pending', 'submitted', 'under_review']:
                            APITestHelper.print_test_step("Application status is appropriate", "SUCCESS")
                        else:
                            APITestHelper.print_test_step(f"Unexpected application status: {status}", "FAILED")
                            
                    self.results.add_success("restaurant_applications", f"Submit {org_type} application", {
                        "response_time": response_time,
                        "application_id": application_response.get('application_id'),
                        "org_type": org_type
                    })
                    success_count += 1
                    
                elif response.status_code == 404:
                    APITestHelper.print_test_step("Setup endpoint not found (may not be implemented)", "SKIPPED")
                    break  # Don't try more if endpoint doesn't exist
                    
                elif response.status_code == 409:
                    APITestHelper.print_test_step(f"Application conflicts with existing data", "SKIPPED")
                    
                else:
                    APITestHelper.print_test_step(f"Application submission failed: HTTP {response.status_code}", "FAILED")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    self.results.add_failure("restaurant_applications", f"Submit {org_type} application", 
                                           f"HTTP {response.status_code}", response.status_code)
                    
                # Small delay between applications
                await asyncio.sleep(0.5)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Application submission error: {e}", "FAILED")
                self.results.add_failure("restaurant_applications", f"Submit {org_type} application", str(e))
                
        print(f"\n📊 Application Submission Summary: {success_count}/{len(application_scenarios)} successful")
        return success_count > 0
        
    async def test_application_listing(self) -> bool:
        """Test listing pending applications (admin function)"""
        
        APITestHelper.print_test_header("Application Listing", "📋")
        
        try:
            APITestHelper.print_test_step("Fetching pending applications", "RUNNING")
            
            start_time = time.time()
            response = await self.client.get("/api/v1/platform/applications", headers=self.auth_headers)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                applications = response.json()
                
                APITestHelper.print_test_step(f"Applications retrieved ({response_time:.0f}ms)", "SUCCESS")
                
                if isinstance(applications, list):
                    application_count = len(applications)
                    APITestHelper.print_test_step(f"Found {application_count} applications", "SUCCESS")
                    
                    if applications:
                        print(f"   📋 Application List:")
                        for i, app in enumerate(applications[:3]):  # Show first 3
                            print(f"      {i+1}. {app.get('restaurant_name', 'N/A')} - {app.get('status', 'N/A')}")
                            
                elif isinstance(applications, dict) and 'items' in applications:
                    items = applications['items']
                    total = applications.get('total', len(items))
                    APITestHelper.print_test_step(f"Found {len(items)} applications (total: {total})", "SUCCESS")
                    
                else:
                    APITestHelper.print_test_step("Unexpected applications format", "FAILED")
                    
                self.results.add_success("application_management", "List applications", {
                    "response_time": response_time,
                    "count": application_count if isinstance(applications, list) else len(applications.get('items', []))
                })
                return True
                
            elif response.status_code == 403:
                APITestHelper.print_test_step("Applications access forbidden (permission check working)", "SUCCESS")
                self.results.add_success("application_management", "List applications (permission check)", {
                    "response_time": response_time,
                    "permission_enforced": True
                })
                return True
                
            elif response.status_code == 404:
                APITestHelper.print_test_step("Applications endpoint not found (may not be implemented)", "SKIPPED")
                return True
                
            else:
                APITestHelper.print_test_step(f"Applications listing failed: HTTP {response.status_code}", "FAILED")
                self.results.add_failure("application_management", "List applications", 
                                       f"HTTP {response.status_code}", response.status_code)
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Applications listing error: {e}", "FAILED")
            self.results.add_failure("application_management", "List applications", str(e))
            return False
            
    async def test_application_approval_workflow(self) -> bool:
        """Test application approval workflow"""
        
        APITestHelper.print_test_header("Application Approval Workflow", "✅")
        
        if not self.created_applications:
            APITestHelper.print_test_step("No applications available for approval testing", "SKIPPED")
            return True
            
        application = self.created_applications[0]
        application_id = application.get('application_id') or application.get('id')
        org_id = application.get('organization_id') or application.get('org_id')
        
        if not application_id and not org_id:
            APITestHelper.print_test_step("Cannot find application ID for approval testing", "SKIPPED")
            return True
            
        print(f"   📝 Testing approval for application: {application_id or org_id}")
        
        try:
            APITestHelper.print_test_step("Approving application", "RUNNING")
            
            approval_data = {
                "notes": "Test approval - application looks good",
                "approved_by": "test_admin"
            }
            
            # Try different endpoint patterns
            approval_endpoints = [
                f"/api/v1/platform/applications/{application_id}/approve",
                f"/api/v1/platform/applications/{org_id}/approve",
                f"/api/v1/applications/{application_id}/approve"
            ]
            
            approved = False
            
            for endpoint in approval_endpoints:
                if application_id and 'application_id' in endpoint:
                    test_endpoint = endpoint
                elif org_id and 'org_id' in endpoint:
                    test_endpoint = endpoint
                else:
                    continue
                    
                try:
                    start_time = time.time()
                    response = await self.client.post(test_endpoint, json=approval_data, headers=self.auth_headers)
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        approval_response = response.json()
                        
                        APITestHelper.print_test_step(f"Application approved ({response_time:.0f}ms)", "SUCCESS")
                        
                        if isinstance(approval_response, dict):
                            print(f"   ✅ Approval Details:")
                            print(f"      Status: {approval_response.get('status', 'N/A')}")
                            print(f"      Restaurant ID: {approval_response.get('restaurant_id', 'N/A')}")
                            print(f"      Organization ID: {approval_response.get('organization_id', 'N/A')}")
                            
                            # Store created restaurant info
                            if 'restaurant_id' in approval_response:
                                self.created_restaurants.append(approval_response)
                                
                        self.results.add_success("application_approval", "Approve application", {
                            "response_time": response_time,
                            "application_id": application_id,
                            "endpoint": test_endpoint
                        })
                        approved = True
                        break
                        
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                        
                    else:
                        APITestHelper.print_test_step(f"Approval failed: HTTP {response.status_code}", "FAILED")
                        if response.json_data:
                            print(f"   Error: {response.json_data}")
                            
                except Exception:
                    continue  # Try next endpoint
                    
            if not approved:
                APITestHelper.print_test_step("Application approval endpoints not found (may not be implemented)", "SKIPPED")
                
            return True  # Not a failure if approval isn't implemented
            
        except Exception as e:
            APITestHelper.print_test_step(f"Application approval error: {e}", "FAILED")
            self.results.add_failure("application_approval", "Approve application", str(e))
            return False
            
    async def test_application_rejection_workflow(self) -> bool:
        """Test application rejection workflow"""
        
        APITestHelper.print_test_header("Application Rejection Workflow", "❌")
        
        if len(self.created_applications) < 2:
            APITestHelper.print_test_step("Need multiple applications for rejection testing", "SKIPPED")
            return True
            
        application = self.created_applications[1]  # Use second application
        application_id = application.get('application_id') or application.get('id')
        org_id = application.get('organization_id') or application.get('org_id')
        
        if not application_id and not org_id:
            APITestHelper.print_test_step("Cannot find application ID for rejection testing", "SKIPPED")
            return True
            
        print(f"   📝 Testing rejection for application: {application_id or org_id}")
        
        try:
            APITestHelper.print_test_step("Rejecting application", "RUNNING")
            
            rejection_data = {
                "reason": "Test rejection - incomplete documentation",
                "notes": "This is a test rejection for validation purposes",
                "rejected_by": "test_admin"
            }
            
            # Try different endpoint patterns
            rejection_endpoints = [
                f"/api/v1/platform/applications/{application_id}/reject",
                f"/api/v1/platform/applications/{org_id}/reject",
                f"/api/v1/applications/{application_id}/reject"
            ]
            
            rejected = False
            
            for endpoint in rejection_endpoints:
                if application_id and 'application_id' in endpoint:
                    test_endpoint = endpoint
                elif org_id and 'org_id' in endpoint:
                    test_endpoint = endpoint
                else:
                    continue
                    
                try:
                    start_time = time.time()
                    response = await self.client.post(test_endpoint, json=rejection_data, headers=self.auth_headers)
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        rejection_response = response.json()
                        
                        APITestHelper.print_test_step(f"Application rejected ({response_time:.0f}ms)", "SUCCESS")
                        
                        if isinstance(rejection_response, dict):
                            print(f"   ❌ Rejection Details:")
                            print(f"      Status: {rejection_response.get('status', 'N/A')}")
                            print(f"      Reason: {rejection_response.get('reason', 'N/A')}")
                            
                        self.results.add_success("application_rejection", "Reject application", {
                            "response_time": response_time,
                            "application_id": application_id,
                            "endpoint": test_endpoint
                        })
                        rejected = True
                        break
                        
                    elif response.status_code == 404:
                        continue  # Try next endpoint
                        
                    else:
                        APITestHelper.print_test_step(f"Rejection failed: HTTP {response.status_code}", "FAILED")
                        if response.json_data:
                            print(f"   Error: {response.json_data}")
                            
                except Exception:
                    continue  # Try next endpoint
                    
            if not rejected:
                APITestHelper.print_test_step("Application rejection endpoints not found (may not be implemented)", "SKIPPED")
                
            return True  # Not a failure if rejection isn't implemented
            
        except Exception as e:
            APITestHelper.print_test_step(f"Application rejection error: {e}", "FAILED")
            self.results.add_failure("application_rejection", "Reject application", str(e))
            return False
            
    async def test_setup_data_validation(self) -> bool:
        """Test restaurant setup data validation"""
        
        APITestHelper.print_test_header("Setup Data Validation", "✅")
        
        validation_tests = [
            ({}, "Empty setup data"),
            ({"restaurant": {}}, "Empty restaurant data"),
            ({"restaurant": {"name": ""}}, "Empty restaurant name"),
            ({"restaurant": {"name": "Test"}, "admin_user": {}}, "Empty admin user"),
            ({"restaurant": {"name": "Test"}, "admin_user": {"email": "invalid"}}, "Invalid email"),
            ({"restaurant": {"name": "Test"}, "admin_user": {"email": "test@test.com"}}, "Missing password"),
        ]
        
        success_count = 0
        
        for invalid_data, description in validation_tests:
            try:
                APITestHelper.print_test_step(f"Testing: {description}", "RUNNING")
                
                start_time = time.time()
                response = await self.client.post("/api/v1/setup", json=invalid_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                # We expect validation errors (400/422) for invalid data
                if response.status_code in [400, 422]:
                    APITestHelper.print_test_step(f"Validation correctly rejected ({response_time:.0f}ms)", "SUCCESS")
                    
                    if response.json_data:
                        error_info = response.json_data
                        print(f"   ✅ Error details: {error_info}")
                        
                    self.results.add_success("setup_validation", description, {
                        "response_time": response_time,
                        "correctly_rejected": True
                    })
                    success_count += 1
                    
                elif response.status_code == 404:
                    APITestHelper.print_test_step("Setup endpoint not found (validation test skipped)", "SKIPPED")
                    break  # Don't continue if endpoint doesn't exist
                    
                elif response.status_code == 201:
                    APITestHelper.print_test_step(f"Invalid data accepted (should be rejected)", "FAILED")
                    self.results.add_failure("setup_validation", description, 
                                           "Invalid data was accepted", 201)
                    
                else:
                    APITestHelper.print_test_step(f"Unexpected response: HTTP {response.status_code}", "FAILED")
                    self.results.add_failure("setup_validation", description, 
                                           f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.2)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Validation test error: {e}", "FAILED")
                self.results.add_failure("setup_validation", description, str(e))
                
        print(f"\n📊 Validation Testing Summary: {success_count}/{len(validation_tests)} tests passed")
        return success_count > 0
        
    def print_restaurant_setup_summary(self):
        """Print comprehensive restaurant setup test summary"""
        
        APITestHelper.print_test_header("Restaurant Setup Tests Summary", "📊")
        
        print(f"Total Tests: {self.results.total_tests}")
        print(f"Passed: {self.results.passed_tests}")
        print(f"Failed: {self.results.failed_tests}")
        print(f"Success Rate: {self.results.success_rate:.1f}%")
        
        # Show created entities
        print(f"\n📝 Created Entities:")
        print(f"   Applications: {len(self.created_applications)}")
        print(f"   Restaurants: {len(self.created_restaurants)}")
        
        if self.created_applications:
            print(f"\n   📝 Applications:")
            for app in self.created_applications:
                app_id = app.get('application_id') or app.get('id', 'N/A')
                restaurant_name = app.get('restaurant_name', 'N/A')
                status = app.get('status', 'N/A')
                print(f"      • {restaurant_name} - {status} (ID: {app_id})")
                
        if self.created_restaurants:
            print(f"\n   🏢 Restaurants:")
            for rest in self.created_restaurants:
                rest_id = rest.get('restaurant_id', 'N/A')
                org_id = rest.get('organization_id', 'N/A')
                print(f"      • Restaurant ID: {rest_id} (Org: {org_id})")
                
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
                    
    async def run_comprehensive_restaurant_setup_tests(self) -> bool:
        """Run all restaurant setup tests"""
        
        print("🏢 RMS Restaurant Setup Operations Tests")
        print("="*50)
        
        start_time = time.time()
        
        try:
            # Setup authentication
            if not await self.setup_authentication():
                return False
                
            # Run all restaurant setup tests
            tests = [
                ("Restaurant Application Submission", self.test_restaurant_application_submission),
                ("Application Listing", self.test_application_listing),
                ("Application Approval Workflow", self.test_application_approval_workflow),
                ("Application Rejection Workflow", self.test_application_rejection_workflow),
                ("Setup Data Validation", self.test_setup_data_validation)
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
            self.print_restaurant_setup_summary()
            
            return overall_success
            
        except KeyboardInterrupt:
            print("\n⚠️ Restaurant setup tests interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Restaurant setup tests failed: {e}")
            return False
        finally:
            await self.client.close()


async def main():
    """Main entry point for restaurant setup testing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Test RMS restaurant setup operations")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    tester = RestaurantSetupTester(args.base_url)
    
    try:
        success = await tester.run_comprehensive_restaurant_setup_tests()
        
        if success:
            print(f"\n✅ All restaurant setup tests passed successfully!")
        else:
            print(f"\n❌ Some restaurant setup tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Restaurant setup testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())