#!/usr/bin/env python3
"""
RMS Comprehensive API Tester - Master Test Orchestrator

This script orchestrates comprehensive testing of the Restaurant Management System API,
inspired by the ABC API Modular project's api-tester framework.

Usage:
    python run_comprehensive_tests.py full           # Run complete test suite
    python run_comprehensive_tests.py generate       # Generate sample data only
    python run_comprehensive_tests.py health         # API health checks only
    python run_comprehensive_tests.py read           # Read operations only
    python run_comprehensive_tests.py create         # Create operations only
    python run_comprehensive_tests.py update         # Update operations only
    python run_comprehensive_tests.py delete --confirm-deletes  # Delete operations (destructive)
    python run_comprehensive_tests.py workflows      # Business workflow tests
    python run_comprehensive_tests.py performance    # Performance testing
"""

import sys
import argparse
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional
import subprocess

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.api_tester.shared.utils import APITestClient, TestResults
from tests.api_tester.shared.auth import get_auth_headers


class RMSTestOrchestrator:
    """Orchestrates comprehensive RMS API testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.results = TestResults()
        
    def print_header(self, title: str, emoji: str = "🍽️"):
        """Print formatted test section header"""
        print(f"\n{'=' * 60}")
        print(f"{emoji}  RMS API Testing: {title}")
        print(f"{'=' * 60}")
        
    def print_step(self, step: str, status: str = "RUNNING"):
        """Print test step with status"""
        if status == "RUNNING":
            print(f"🔄 {step}...")
        elif status == "SUCCESS":
            print(f"✅ {step}")
        elif status == "FAILED":
            print(f"❌ {step}")
        elif status == "SKIPPED":
            print(f"⏭️  {step}")
            
    async def run_health_checks(self) -> bool:
        """Run API health and connectivity checks"""
        self.print_header("API Health & Connectivity Checks", "🩺")
        
        try:
            # Basic connectivity
            self.print_step("Checking API connectivity", "RUNNING")
            response = await self.client.get("/health")
            if response.status_code == 200:
                self.print_step("API connectivity verified", "SUCCESS")
                self.results.add_success("health", "API connectivity")
            else:
                self.print_step(f"API connectivity failed: {response.status_code}", "FAILED")
                self.results.add_failure("health", "API connectivity", f"Status: {response.status_code}")
                return False
                
            # Database connectivity
            self.print_step("Checking database connectivity", "RUNNING")
            response = await self.client.get("/health/db")
            if response.status_code == 200:
                self.print_step("Database connectivity verified", "SUCCESS")
                self.results.add_success("health", "Database connectivity")
            else:
                self.print_step("Database connectivity failed", "FAILED")
                self.results.add_failure("health", "Database connectivity", f"Status: {response.status_code}")
                
            # Authentication endpoint
            self.print_step("Checking authentication endpoint", "RUNNING")
            auth_data = {
                "username": "admin@testrestaurant.com",
                "password": "secure_test_password"
            }
            response = await self.client.post("/auth/login", data=auth_data)
            if response.status_code in [200, 404]:  # 404 is ok if no test user exists yet
                self.print_step("Authentication endpoint verified", "SUCCESS")
                self.results.add_success("health", "Authentication endpoint")
            else:
                self.print_step("Authentication endpoint failed", "FAILED")
                self.results.add_failure("health", "Authentication endpoint", f"Status: {response.status_code}")
                
            return True
            
        except Exception as e:
            self.print_step(f"Health checks failed: {str(e)}", "FAILED")
            self.results.add_failure("health", "General health check", str(e))
            return False
            
    async def run_sample_data_generation(self) -> bool:
        """Generate comprehensive sample data"""
        self.print_header("Sample Data Generation", "🏗️")
        
        try:
            # Run sample data generation scripts
            scripts = [
                "sample_data_generator/generate_organizations.py",
                "sample_data_generator/generate_restaurants.py", 
                "sample_data_generator/generate_users.py",
                "sample_data_generator/generate_menu_data.py"
            ]
            
            for script in scripts:
                script_path = Path(__file__).parent / script
                if script_path.exists():
                    script_name = script.split('/')[-1].replace('generate_', '').replace('.py', '')
                    self.print_step(f"Generating {script_name} data", "RUNNING")
                    
                    result = subprocess.run([
                        sys.executable, str(script_path)
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        self.print_step(f"Generated {script_name} data", "SUCCESS")
                        self.results.add_success("generate", f"{script_name} data")
                    else:
                        self.print_step(f"Failed to generate {script_name} data", "FAILED")
                        self.results.add_failure("generate", f"{script_name} data", result.stderr)
                else:
                    self.print_step(f"Sample data script not found: {script}", "SKIPPED")
                    
            return True
            
        except Exception as e:
            self.print_step(f"Sample data generation failed: {str(e)}", "FAILED")
            self.results.add_failure("generate", "Sample data generation", str(e))
            return False
            
    async def run_read_operations(self) -> bool:
        """Run comprehensive read operation tests"""
        self.print_header("Read Operations Testing", "📖")
        
        try:
            # Get authentication headers
            headers = await get_auth_headers(self.client)
            if not headers:
                self.print_step("Authentication failed - skipping read tests", "FAILED")
                return False
                
            # Test menu endpoints
            endpoints = [
                ("/api/v1/menu/categories", "Menu categories"),
                ("/api/v1/menu/items", "Menu items"),
                ("/api/v1/restaurants", "Restaurants"),
                ("/api/v1/users", "Users"),
                ("/auth/me", "Current user profile")
            ]
            
            for endpoint, description in endpoints:
                self.print_step(f"Testing {description}", "RUNNING")
                
                start_time = time.time()
                response = await self.client.get(endpoint, headers=headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code in [200, 404]:  # 404 is ok for empty data
                    self.print_step(f"✅ {description} ({response_time:.0f}ms)", "SUCCESS")
                    self.results.add_success("read", description, {
                        "endpoint": endpoint,
                        "response_time": response_time,
                        "status_code": response.status_code
                    })
                else:
                    self.print_step(f"❌ {description} failed: {response.status_code}", "FAILED")
                    self.results.add_failure("read", description, f"Status: {response.status_code}")
                    
            return True
            
        except Exception as e:
            self.print_step(f"Read operations failed: {str(e)}", "FAILED")
            self.results.add_failure("read", "Read operations", str(e))
            return False
            
    async def run_create_operations(self) -> bool:
        """Run comprehensive create operation tests"""
        self.print_header("Create Operations Testing", "➕")
        
        try:
            # Get authentication headers
            headers = await get_auth_headers(self.client)
            if not headers:
                self.print_step("Authentication failed - skipping create tests", "FAILED")
                return False
                
            # Test menu category creation
            self.print_step("Testing menu category creation", "RUNNING")
            category_data = {
                "name": "Test Category",
                "description": "A test menu category",
                "sort_order": 1
            }
            
            response = await self.client.post("/api/v1/menu/categories", json=category_data, headers=headers)
            if response.status_code == 201:
                self.print_step("Menu category creation successful", "SUCCESS")
                self.results.add_success("create", "Menu category creation")
                
                # Store created category ID for other tests
                category_id = response.json().get("id")
                
                # Test menu item creation
                if category_id:
                    self.print_step("Testing menu item creation", "RUNNING")
                    item_data = {
                        "name": "Test Menu Item",
                        "description": "A test menu item",
                        "price": 12.99,
                        "category_id": category_id,
                        "is_available": True
                    }
                    
                    response = await self.client.post("/api/v1/menu/items", json=item_data, headers=headers)
                    if response.status_code == 201:
                        self.print_step("Menu item creation successful", "SUCCESS")
                        self.results.add_success("create", "Menu item creation")
                    else:
                        self.print_step(f"Menu item creation failed: {response.status_code}", "FAILED")
                        self.results.add_failure("create", "Menu item creation", f"Status: {response.status_code}")
                        
            else:
                self.print_step(f"Menu category creation failed: {response.status_code}", "FAILED")
                self.results.add_failure("create", "Menu category creation", f"Status: {response.status_code}")
                
            return True
            
        except Exception as e:
            self.print_step(f"Create operations failed: {str(e)}", "FAILED")
            self.results.add_failure("create", "Create operations", str(e))
            return False
            
    async def run_update_operations(self) -> bool:
        """Run comprehensive update operation tests"""
        self.print_header("Update Operations Testing", "✏️")
        
        try:
            # Get authentication headers
            headers = await get_auth_headers(self.client)
            if not headers:
                self.print_step("Authentication failed - skipping update tests", "FAILED")
                return False
                
            # Get existing menu categories to update
            response = await self.client.get("/api/v1/menu/categories", headers=headers)
            if response.status_code == 200 and response.json():
                categories = response.json()
                if categories:
                    category = categories[0]
                    category_id = category["id"]
                    
                    self.print_step("Testing menu category update", "RUNNING")
                    update_data = {
                        "name": f"{category['name']} - UPDATED",
                        "description": "Updated description for testing"
                    }
                    
                    response = await self.client.put(f"/api/v1/menu/categories/{category_id}", 
                                                   json=update_data, headers=headers)
                    if response.status_code == 200:
                        self.print_step("Menu category update successful", "SUCCESS")
                        self.results.add_success("update", "Menu category update")
                    else:
                        self.print_step(f"Menu category update failed: {response.status_code}", "FAILED")
                        self.results.add_failure("update", "Menu category update", f"Status: {response.status_code}")
                else:
                    self.print_step("No categories found for update testing", "SKIPPED")
            else:
                self.print_step("Could not fetch categories for update testing", "SKIPPED")
                
            return True
            
        except Exception as e:
            self.print_step(f"Update operations failed: {str(e)}", "FAILED")
            self.results.add_failure("update", "Update operations", str(e))
            return False
            
    async def run_delete_operations(self, confirm_deletes: bool = False) -> bool:
        """Run comprehensive delete operation tests"""
        self.print_header("Delete Operations Testing", "🗑️")
        
        if not confirm_deletes:
            self.print_step("Delete operations require --confirm-deletes flag", "SKIPPED")
            print("⚠️  WARNING: Delete tests are destructive and will remove data!")
            print("Use --confirm-deletes flag to run these tests.")
            return True
            
        try:
            # Get authentication headers
            headers = await get_auth_headers(self.client)
            if not headers:
                self.print_step("Authentication failed - skipping delete tests", "FAILED")
                return False
                
            # Create a test item specifically for deletion
            self.print_step("Creating test data for deletion", "RUNNING")
            
            # Create test category
            category_data = {
                "name": "DELETE TEST Category",
                "description": "This category will be deleted",
                "sort_order": 999
            }
            
            response = await self.client.post("/api/v1/menu/categories", json=category_data, headers=headers)
            if response.status_code == 201:
                category_id = response.json()["id"]
                
                # Test category deletion
                self.print_step("Testing menu category deletion", "RUNNING")
                response = await self.client.delete(f"/api/v1/menu/categories/{category_id}", headers=headers)
                if response.status_code == 204:
                    self.print_step("Menu category deletion successful", "SUCCESS")
                    self.results.add_success("delete", "Menu category deletion")
                else:
                    self.print_step(f"Menu category deletion failed: {response.status_code}", "FAILED")
                    self.results.add_failure("delete", "Menu category deletion", f"Status: {response.status_code}")
            else:
                self.print_step("Could not create test category for deletion", "FAILED")
                self.results.add_failure("delete", "Test data creation", "Could not create test category")
                
            return True
            
        except Exception as e:
            self.print_step(f"Delete operations failed: {str(e)}", "FAILED")
            self.results.add_failure("delete", "Delete operations", str(e))
            return False
            
    async def run_business_workflows(self) -> bool:
        """Run end-to-end business workflow tests"""
        self.print_header("Business Workflow Testing", "🔄")
        
        try:
            # Get authentication headers
            headers = await get_auth_headers(self.client)
            if not headers:
                self.print_step("Authentication failed - skipping workflow tests", "FAILED")
                return False
                
            # Test complete menu setup workflow
            self.print_step("Testing complete menu setup workflow", "RUNNING")
            
            # 1. Create category
            category_data = {
                "name": "Workflow Test Category",
                "description": "Testing complete workflow",
                "sort_order": 1
            }
            
            response = await self.client.post("/api/v1/menu/categories", json=category_data, headers=headers)
            if response.status_code != 201:
                self.print_step("Workflow test failed at category creation", "FAILED")
                return False
                
            category_id = response.json()["id"]
            
            # 2. Create menu item in category
            item_data = {
                "name": "Workflow Test Item",
                "description": "Testing item creation workflow",
                "price": 15.99,
                "category_id": category_id,
                "is_available": True
            }
            
            response = await self.client.post("/api/v1/menu/items", json=item_data, headers=headers)
            if response.status_code != 201:
                self.print_step("Workflow test failed at item creation", "FAILED")
                return False
                
            item_id = response.json()["id"]
            
            # 3. Update item availability
            update_data = {"is_available": False}
            response = await self.client.patch(f"/api/v1/menu/items/{item_id}", json=update_data, headers=headers)
            if response.status_code != 200:
                self.print_step("Workflow test failed at item update", "FAILED")
                return False
                
            # 4. Verify the complete workflow
            response = await self.client.get(f"/api/v1/menu/items/{item_id}", headers=headers)
            if response.status_code == 200 and not response.json()["is_available"]:
                self.print_step("Complete menu workflow successful", "SUCCESS")
                self.results.add_success("workflow", "Menu management workflow")
            else:
                self.print_step("Workflow verification failed", "FAILED")
                self.results.add_failure("workflow", "Menu management workflow", "Verification failed")
                
            return True
            
        except Exception as e:
            self.print_step(f"Business workflow tests failed: {str(e)}", "FAILED")
            self.results.add_failure("workflow", "Business workflows", str(e))
            return False
            
    def print_final_results(self):
        """Print comprehensive test results summary"""
        self.print_header("Test Results Summary", "📊")
        
        print(f"\n🎯 Test Execution Summary:")
        print(f"   Total Tests: {self.results.total_tests}")
        print(f"   ✅ Passed: {self.results.passed_tests}")
        print(f"   ❌ Failed: {self.results.failed_tests}")
        print(f"   ⏭️  Skipped: {self.results.skipped_tests}")
        print(f"   📈 Success Rate: {self.results.success_rate:.1f}%")
        
        if self.results.failures:
            print(f"\n❌ Failed Tests:")
            for failure in self.results.failures:
                print(f"   • {failure['category']}: {failure['test']} - {failure['error']}")
                
        if self.results.successes:
            print(f"\n✅ Successful Test Categories:")
            categories = set(success['category'] for success in self.results.successes)
            for category in categories:
                count = len([s for s in self.results.successes if s['category'] == category])
                print(f"   • {category}: {count} tests passed")
                
        print(f"\n🕒 Total Execution Time: {self.results.execution_time:.2f} seconds")
        
    async def run_comprehensive_tests(self, test_type: str = "full", confirm_deletes: bool = False):
        """Run comprehensive test suite based on type"""
        start_time = time.time()
        
        print(f"🍽️  Starting RMS Comprehensive API Testing")
        print(f"Target API: {self.base_url}")
        print(f"Test Type: {test_type}")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        success = True
        
        try:
            if test_type in ["full", "health"]:
                if not await self.run_health_checks():
                    success = False
                    if test_type == "health":
                        return success
                        
            if test_type in ["full", "generate"]:
                if not await self.run_sample_data_generation():
                    success = False
                    if test_type == "generate":
                        return success
                        
            if test_type in ["full", "read"]:
                if not await self.run_read_operations():
                    success = False
                    if test_type == "read":
                        return success
                        
            if test_type in ["full", "create"]:
                if not await self.run_create_operations():
                    success = False
                    if test_type == "create":
                        return success
                        
            if test_type in ["full", "update"]:
                if not await self.run_update_operations():
                    success = False
                    if test_type == "update":
                        return success
                        
            if test_type in ["full", "delete"]:
                if not await self.run_delete_operations(confirm_deletes):
                    success = False
                    if test_type == "delete":
                        return success
                        
            if test_type in ["full", "workflows"]:
                if not await self.run_business_workflows():
                    success = False
                    
        except KeyboardInterrupt:
            self.print_step("Testing interrupted by user", "FAILED")
            success = False
        except Exception as e:
            self.print_step(f"Unexpected error: {str(e)}", "FAILED")
            success = False
            
        finally:
            self.results.execution_time = time.time() - start_time
            self.print_final_results()
            
        return success


async def main():
    """Main entry point for comprehensive testing"""
    parser = argparse.ArgumentParser(description="RMS Comprehensive API Tester")
    parser.add_argument("test_type", 
                       choices=["full", "generate", "health", "read", "create", "update", "delete", "workflows", "performance"],
                       help="Type of tests to run")
    parser.add_argument("--confirm-deletes", action="store_true",
                       help="Confirm running destructive delete tests")
    parser.add_argument("--base-url", default="http://localhost:8000",
                       help="Base URL for the RMS API")
    parser.add_argument("--performance", action="store_true",
                       help="Include performance metrics in testing")
    
    args = parser.parse_args()
    
    if args.test_type == "delete" and not args.confirm_deletes:
        print("❌ Delete tests require --confirm-deletes flag")
        print("⚠️  WARNING: Delete tests are destructive and will remove data!")
        sys.exit(1)
        
    orchestrator = RMSTestOrchestrator(args.base_url)
    success = await orchestrator.run_comprehensive_tests(args.test_type, args.confirm_deletes)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())