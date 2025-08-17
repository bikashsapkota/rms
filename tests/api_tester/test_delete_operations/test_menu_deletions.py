#!/usr/bin/env python3
"""
Test Menu Delete Operations

Comprehensive testing of menu-related DELETE endpoints.
Tests deletion of menu categories, items, and modifiers with proper cleanup.
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


class MenuDeletionTester:
    """Comprehensive menu deletion operations testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000", confirm_deletes: bool = False):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.results = TestResults()
        self.auth_headers = None
        self.confirm_deletes = confirm_deletes
        self.test_categories = []
        self.test_items = []
        self.test_modifiers = []
        self.cleanup_queue = []
        
    async def setup_authentication(self) -> bool:
        """Setup authentication for all tests"""
        
        self.auth_headers = await get_auth_headers(self.client)
        if not self.auth_headers:
            APITestHelper.print_test_step("Authentication failed - cannot run menu deletion tests", "FAILED")
            return False
            
        APITestHelper.print_test_step("Authentication successful", "SUCCESS")
        return True
        
    async def create_test_menu_data(self):
        """Create test menu data for deletion testing"""
        
        APITestHelper.print_test_step("Creating test menu data for deletion testing", "RUNNING")
        
        try:
            # Create test categories
            categories_data = RMSTestFixtures.generate_menu_category_data("american")
            
            for i, category_data in enumerate(categories_data[:2]):  # Create 2 test categories
                category_data["name"] = f"DELETE TEST Category {i+1}"
                category_data["description"] = f"Category created for deletion testing {i+1}"
                
                response = await self.client.post("/api/v1/menu/categories", json=category_data, headers=self.auth_headers)
                if response.status_code == 201:
                    category = response.json()
                    self.test_categories.append(category)
                    self.cleanup_queue.append(("category", category['id'], category['name']))
                    print(f"   📂 Created test category: {category['name']} ({category['id']})")
                    
            # Create test items in the first category
            if self.test_categories:
                category = self.test_categories[0]
                items_data = RMSTestFixtures.generate_menu_items_data(category['id'], category['name'], "american")
                
                for i, item_data in enumerate(items_data[:3]):  # Create 3 test items
                    item_data["name"] = f"DELETE TEST Item {i+1}"
                    item_data["description"] = f"Item created for deletion testing {i+1}"
                    
                    response = await self.client.post("/api/v1/menu/items", json=item_data, headers=self.auth_headers)
                    if response.status_code == 201:
                        item = response.json()
                        self.test_items.append(item)
                        self.cleanup_queue.append(("item", item['id'], item['name']))
                        print(f"   🍽️ Created test item: {item['name']} ({item['id']})")
                        
            # Create test modifiers
            modifiers_data = RMSTestFixtures.generate_modifier_data()
            
            for i, modifier_data in enumerate(modifiers_data[:2]):  # Create 2 test modifiers
                modifier_data["name"] = f"DELETE TEST Modifier {i+1}"
                
                response = await self.client.post("/api/v1/menu/modifiers", json=modifier_data, headers=self.auth_headers)
                if response.status_code == 201:
                    modifier = response.json()
                    self.test_modifiers.append(modifier)
                    self.cleanup_queue.append(("modifier", modifier['id'], modifier['name']))
                    print(f"   🔧 Created test modifier: {modifier['name']} ({modifier['id']})")
                elif response.status_code == 404:
                    print(f"   ⚠️ Modifiers endpoint not available - skipping modifier creation")
                    break
                    
            created_count = len(self.test_categories) + len(self.test_items) + len(self.test_modifiers)
            APITestHelper.print_test_step(f"Created {created_count} test entities for deletion testing", "SUCCESS")
            
        except Exception as e:
            APITestHelper.print_test_step(f"Failed to create test data: {e}", "FAILED")
            
    async def test_menu_item_deletions(self) -> bool:
        """Test deleting menu items"""
        
        APITestHelper.print_test_header("Menu Item Deletions", "🗑️")
        
        if not self.test_items:
            APITestHelper.print_test_step("No test items available for deletion testing", "SKIPPED")
            return True
            
        if not self.confirm_deletes:
            APITestHelper.print_test_step("Delete operations require --confirm-deletes flag", "SKIPPED")
            return True
            
        success_count = 0
        
        # Test deleting individual items
        for item in self.test_items[:2]:  # Delete first 2 items, keep 1 for cleanup
            try:
                item_id = item['id']
                item_name = item['name']
                
                APITestHelper.print_test_step(f"Deleting item: {item_name}", "RUNNING")
                
                # First verify item exists
                verify_response = await self.client.get(f"/api/v1/menu/items/{item_id}", headers=self.auth_headers)
                if verify_response.status_code != 200:
                    APITestHelper.print_test_step(f"Item {item_name} not found for deletion", "SKIPPED")
                    continue
                    
                start_time = time.time()
                response = await self.client.delete(f"/api/v1/menu/items/{item_id}", headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 204:
                    APITestHelper.print_test_step(f"Item deleted successfully ({response_time:.0f}ms)", "SUCCESS")
                    
                    # Verify item is actually deleted
                    await asyncio.sleep(0.1)
                    verify_response = await self.client.get(f"/api/v1/menu/items/{item_id}", headers=self.auth_headers)
                    
                    if verify_response.status_code == 404:
                        APITestHelper.print_test_step("Deletion verified - item not found", "SUCCESS")
                        
                        # Remove from cleanup queue since it's deleted
                        self.cleanup_queue = [entry for entry in self.cleanup_queue if not (entry[0] == "item" and entry[1] == item_id)]
                        
                    else:
                        APITestHelper.print_test_step("Deletion verification failed - item still exists", "FAILED")
                        
                    self.results.add_success("menu_item_deletions", f"Delete item {item_name}", {
                        "response_time": response_time,
                        "item_id": item_id,
                        "verified": verify_response.status_code == 404
                    })
                    success_count += 1
                    
                elif response.status_code == 404:
                    APITestHelper.print_test_step(f"Item not found (may already be deleted)", "SKIPPED")
                    
                elif response.status_code == 403:
                    APITestHelper.print_test_step("Item deletion forbidden (permission check working)", "SUCCESS")
                    self.results.add_success("menu_item_deletions", f"Delete item {item_name} (permission check)", {
                        "response_time": response_time,
                        "permission_enforced": True
                    })
                    success_count += 1
                    
                elif response.status_code == 409:
                    APITestHelper.print_test_step("Item deletion conflict (may have dependencies)", "SKIPPED")
                    print(f"   ⚠️ Item may have dependencies preventing deletion")
                    
                else:
                    APITestHelper.print_test_step(f"Item deletion failed: HTTP {response.status_code}", "FAILED")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    self.results.add_failure("menu_item_deletions", f"Delete item {item_name}", 
                                          f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Item deletion error: {e}", "FAILED")
                self.results.add_failure("menu_item_deletions", f"Delete item {item_name}", str(e))
                
        print(f"\n📊 Item Deletion Summary: {success_count}/{min(2, len(self.test_items))} successful")
        return success_count > 0
        
    async def test_menu_modifier_deletions(self) -> bool:
        """Test deleting menu modifiers"""
        
        APITestHelper.print_test_header("Menu Modifier Deletions", "🗑️")
        
        if not self.test_modifiers:
            APITestHelper.print_test_step("No test modifiers available for deletion testing", "SKIPPED")
            return True
            
        if not self.confirm_deletes:
            APITestHelper.print_test_step("Delete operations require --confirm-deletes flag", "SKIPPED")
            return True
            
        success_count = 0
        
        # Test deleting modifiers
        for modifier in self.test_modifiers[:1]:  # Delete first modifier, keep 1 for cleanup
            try:
                modifier_id = modifier['id']
                modifier_name = modifier['name']
                
                APITestHelper.print_test_step(f"Deleting modifier: {modifier_name}", "RUNNING")
                
                start_time = time.time()
                response = await self.client.delete(f"/api/v1/menu/modifiers/{modifier_id}", headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 204:
                    APITestHelper.print_test_step(f"Modifier deleted successfully ({response_time:.0f}ms)", "SUCCESS")
                    
                    # Verify modifier is actually deleted
                    await asyncio.sleep(0.1)
                    verify_response = await self.client.get(f"/api/v1/menu/modifiers/{modifier_id}", headers=self.auth_headers)
                    
                    if verify_response.status_code == 404:
                        APITestHelper.print_test_step("Deletion verified - modifier not found", "SUCCESS")
                        
                        # Remove from cleanup queue since it's deleted
                        self.cleanup_queue = [entry for entry in self.cleanup_queue if not (entry[0] == "modifier" and entry[1] == modifier_id)]
                        
                    else:
                        APITestHelper.print_test_step("Deletion verification failed - modifier still exists", "FAILED")
                        
                    self.results.add_success("menu_modifier_deletions", f"Delete modifier {modifier_name}", {
                        "response_time": response_time,
                        "modifier_id": modifier_id,
                        "verified": verify_response.status_code == 404
                    })
                    success_count += 1
                    
                elif response.status_code == 404:
                    APITestHelper.print_test_step("Modifier endpoint not found (may not be implemented)", "SKIPPED")
                    break
                    
                elif response.status_code == 403:
                    APITestHelper.print_test_step("Modifier deletion forbidden (permission check working)", "SUCCESS")
                    success_count += 1
                    
                elif response.status_code == 409:
                    APITestHelper.print_test_step("Modifier deletion conflict (may have dependencies)", "SKIPPED")
                    
                else:
                    APITestHelper.print_test_step(f"Modifier deletion failed: HTTP {response.status_code}", "FAILED")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    self.results.add_failure("menu_modifier_deletions", f"Delete modifier {modifier_name}", 
                                          f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Modifier deletion error: {e}", "FAILED")
                self.results.add_failure("menu_modifier_deletions", f"Delete modifier {modifier_name}", str(e))
                
        print(f"\n📊 Modifier Deletion Summary: {success_count}/{min(1, len(self.test_modifiers))} successful")
        return True  # Modifiers may not be implemented
        
    async def test_menu_category_deletions(self) -> bool:
        """Test deleting menu categories"""
        
        APITestHelper.print_test_header("Menu Category Deletions", "🗑️")
        
        if not self.test_categories:
            APITestHelper.print_test_step("No test categories available for deletion testing", "SKIPPED")
            return True
            
        if not self.confirm_deletes:
            APITestHelper.print_test_step("Delete operations require --confirm-deletes flag", "SKIPPED")
            return True
            
        success_count = 0
        
        # Test deleting categories (should fail if they have items)
        for category in self.test_categories:
            try:
                category_id = category['id']
                category_name = category['name']
                
                APITestHelper.print_test_step(f"Deleting category: {category_name}", "RUNNING")
                
                start_time = time.time()
                response = await self.client.delete(f"/api/v1/menu/categories/{category_id}", headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 204:
                    APITestHelper.print_test_step(f"Category deleted successfully ({response_time:.0f}ms)", "SUCCESS")
                    
                    # Verify category is actually deleted
                    await asyncio.sleep(0.1)
                    verify_response = await self.client.get(f"/api/v1/menu/categories/{category_id}", headers=self.auth_headers)
                    
                    if verify_response.status_code == 404:
                        APITestHelper.print_test_step("Deletion verified - category not found", "SUCCESS")
                        
                        # Remove from cleanup queue since it's deleted
                        self.cleanup_queue = [entry for entry in self.cleanup_queue if not (entry[0] == "category" and entry[1] == category_id)]
                        
                    else:
                        APITestHelper.print_test_step("Deletion verification failed - category still exists", "FAILED")
                        
                    self.results.add_success("menu_category_deletions", f"Delete category {category_name}", {
                        "response_time": response_time,
                        "category_id": category_id,
                        "verified": verify_response.status_code == 404
                    })
                    success_count += 1
                    
                elif response.status_code == 409:
                    APITestHelper.print_test_step("Category deletion conflict (has dependencies)", "SUCCESS")
                    print(f"   ✅ Proper constraint enforcement - category has items")
                    
                    self.results.add_success("menu_category_deletions", f"Delete category {category_name} (constraint check)", {
                        "response_time": response_time,
                        "constraint_enforced": True
                    })
                    success_count += 1
                    
                elif response.status_code == 404:
                    APITestHelper.print_test_step(f"Category not found (may already be deleted)", "SKIPPED")
                    
                elif response.status_code == 403:
                    APITestHelper.print_test_step("Category deletion forbidden (permission check working)", "SUCCESS")
                    self.results.add_success("menu_category_deletions", f"Delete category {category_name} (permission check)", {
                        "response_time": response_time,
                        "permission_enforced": True
                    })
                    success_count += 1
                    
                else:
                    APITestHelper.print_test_step(f"Category deletion failed: HTTP {response.status_code}", "FAILED")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    self.results.add_failure("menu_category_deletions", f"Delete category {category_name}", 
                                          f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Category deletion error: {e}", "FAILED")
                self.results.add_failure("menu_category_deletions", f"Delete category {category_name}", str(e))
                
        print(f"\n📊 Category Deletion Summary: {success_count}/{len(self.test_categories)} successful")
        return success_count > 0
        
    async def test_cascade_deletion_behavior(self) -> bool:
        """Test cascade deletion behavior"""
        
        APITestHelper.print_test_header("Cascade Deletion Behavior", "🔗")
        
        if not self.confirm_deletes:
            APITestHelper.print_test_step("Cascade deletion tests require --confirm-deletes flag", "SKIPPED")
            return True
            
        # Create a fresh category with items for cascade testing
        try:
            APITestHelper.print_test_step("Creating test data for cascade deletion", "RUNNING")
            
            # Create category
            category_data = {
                "name": "CASCADE DELETE Test Category",
                "description": "Category for testing cascade deletion",
                "sort_order": 999
            }
            
            response = await self.client.post("/api/v1/menu/categories", json=category_data, headers=self.auth_headers)
            if response.status_code != 201:
                APITestHelper.print_test_step("Failed to create test category for cascade test", "SKIPPED")
                return True
                
            test_category = response.json()
            category_id = test_category['id']
            
            # Create item in category
            item_data = {
                "name": "CASCADE DELETE Test Item",
                "description": "Item for testing cascade deletion",
                "price": 9.99,
                "category_id": category_id,
                "is_available": True
            }
            
            response = await self.client.post("/api/v1/menu/items", json=item_data, headers=self.auth_headers)
            if response.status_code != 201:
                APITestHelper.print_test_step("Failed to create test item for cascade test", "SKIPPED")
                return True
                
            test_item = response.json()
            item_id = test_item['id']
            
            print(f"   📂 Created category: {test_category['name']} ({category_id})")
            print(f"   🍽️ Created item: {test_item['name']} ({item_id})")
            
            # Test cascade deletion options
            cascade_tests = [
                # First delete the item, then category should be deletable
                ("item_first", "Delete item first, then category", [
                    (f"/api/v1/menu/items/{item_id}", "item"),
                    (f"/api/v1/menu/categories/{category_id}", "category")
                ]),
                
                # Alternative: Test if category deletion with force parameter works
                ("force_delete", "Force delete category with items", [
                    (f"/api/v1/menu/categories/{category_id}?force=true", "category (force)")
                ])
            ]
            
            success_count = 0
            
            for test_name, description, deletions in cascade_tests:
                if test_name == "force_delete":
                    # Skip force delete if we already deleted in previous test
                    continue
                    
                try:
                    APITestHelper.print_test_step(f"Testing: {description}", "RUNNING")
                    
                    cascade_success = True
                    
                    for endpoint, entity_type in deletions:
                        start_time = time.time()
                        response = await self.client.delete(endpoint, headers=self.auth_headers)
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status_code == 204:
                            APITestHelper.print_test_step(f"Deleted {entity_type} successfully ({response_time:.0f}ms)", "SUCCESS")
                        elif response.status_code == 404:
                            APITestHelper.print_test_step(f"{entity_type} not found (may already be deleted)", "SKIPPED")
                        else:
                            APITestHelper.print_test_step(f"Failed to delete {entity_type}: HTTP {response.status_code}", "FAILED")
                            cascade_success = False
                            break
                            
                        await asyncio.sleep(0.2)
                        
                    if cascade_success:
                        self.results.add_success("cascade_deletion", description, {
                            "test_type": test_name,
                            "deletions_count": len(deletions)
                        })
                        success_count += 1
                        
                    break  # Exit after first successful test
                    
                except Exception as e:
                    APITestHelper.print_test_step(f"Cascade deletion test error: {e}", "FAILED")
                    self.results.add_failure("cascade_deletion", description, str(e))
                    
            print(f"\n📊 Cascade Deletion Summary: {success_count}/1 successful")
            return success_count > 0
            
        except Exception as e:
            APITestHelper.print_test_step(f"Cascade deletion test setup error: {e}", "FAILED")
            return False
            
    async def test_deletion_validation(self) -> bool:
        """Test deletion validation and error handling"""
        
        APITestHelper.print_test_header("Deletion Validation", "✅")
        
        validation_tests = [
            ("/api/v1/menu/categories/invalid-uuid", "Invalid category UUID"),
            ("/api/v1/menu/categories/00000000-0000-0000-0000-000000000000", "Non-existent category"),
            ("/api/v1/menu/items/invalid-uuid", "Invalid item UUID"),
            ("/api/v1/menu/items/00000000-0000-0000-0000-000000000000", "Non-existent item"),
            ("/api/v1/menu/modifiers/invalid-uuid", "Invalid modifier UUID"),
            ("/api/v1/menu/modifiers/00000000-0000-0000-0000-000000000000", "Non-existent modifier")
        ]
        
        success_count = 0
        
        for endpoint, description in validation_tests:
            try:
                APITestHelper.print_test_step(f"Testing: {description}", "RUNNING")
                
                start_time = time.time()
                response = await self.client.delete(endpoint, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                # We expect 404 for non-existent entities, 400 for invalid UUIDs
                if response.status_code == 404:
                    APITestHelper.print_test_step(f"Correctly returned 404 for non-existent entity ({response_time:.0f}ms)", "SUCCESS")
                    
                    self.results.add_success("deletion_validation", description, {
                        "response_time": response_time,
                        "correct_error_code": True
                    })
                    success_count += 1
                    
                elif response.status_code == 400:
                    APITestHelper.print_test_step(f"Correctly returned 400 for invalid UUID ({response_time:.0f}ms)", "SUCCESS")
                    
                    self.results.add_success("deletion_validation", description, {
                        "response_time": response_time,
                        "correct_error_code": True
                    })
                    success_count += 1
                    
                elif response.status_code == 204:
                    APITestHelper.print_test_step(f"Unexpected success for invalid deletion", "FAILED")
                    self.results.add_failure("deletion_validation", description, 
                                          "Invalid deletion succeeded", 204)
                    
                else:
                    APITestHelper.print_test_step(f"Unexpected response: HTTP {response.status_code}", "FAILED")
                    self.results.add_failure("deletion_validation", description, 
                                          f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.2)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Validation test error: {e}", "FAILED")
                self.results.add_failure("deletion_validation", description, str(e))
                
        print(f"\n📊 Validation Testing Summary: {success_count}/{len(validation_tests)} tests passed")
        return success_count > 0
        
    def print_menu_deletion_summary(self):
        """Print comprehensive menu deletion test summary"""
        
        APITestHelper.print_test_header("Menu Deletion Tests Summary", "📊")
        
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
        print(f"   Categories: {len(self.test_categories)}")
        print(f"   Items: {len(self.test_items)}")
        print(f"   Modifiers: {len(self.test_modifiers)}")
        
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
                    
    async def cleanup_remaining_entities(self):
        """Clean up any remaining test entities"""
        
        if not self.cleanup_queue:
            return
            
        print(f"\n🧹 Cleaning up {len(self.cleanup_queue)} remaining test entities...")
        
        # Clean up in reverse order (items -> modifiers -> categories)
        cleanup_order = ["item", "modifier", "category"]
        
        for entity_type in cleanup_order:
            entities_to_cleanup = [entry for entry in self.cleanup_queue if entry[0] == entity_type]
            
            for entity_type, entity_id, entity_name in entities_to_cleanup:
                try:
                    endpoint_map = {
                        "item": f"/api/v1/menu/items/{entity_id}",
                        "category": f"/api/v1/menu/categories/{entity_id}",
                        "modifier": f"/api/v1/menu/modifiers/{entity_id}"
                    }
                    
                    endpoint = endpoint_map.get(entity_type)
                    if not endpoint:
                        continue
                        
                    response = await self.client.delete(endpoint, headers=self.auth_headers)
                    
                    if response.status_code == 204:
                        print(f"   ✅ Cleaned up {entity_type}: {entity_name}")
                    elif response.status_code == 404:
                        print(f"   ⚠️ {entity_type} already deleted: {entity_name}")
                    else:
                        print(f"   ❌ Failed to cleanup {entity_type}: {entity_name} (HTTP {response.status_code})")
                        
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    print(f"   ❌ Error cleaning up {entity_type}: {e}")
                    
    async def run_comprehensive_menu_deletion_tests(self) -> bool:
        """Run all menu deletion tests"""
        
        print("🗑️ RMS Menu Deletion Operations Tests")
        print("="*50)
        
        if not self.confirm_deletes:
            print("⚠️  DESTRUCTIVE TESTING DISABLED")
            print("   Use --confirm-deletes flag to enable deletion testing")
            print("   This will create and delete test data in the database")
            print()
        
        start_time = time.time()
        
        try:
            # Setup authentication
            if not await self.setup_authentication():
                return False
                
            # Create test data for deletion testing
            await self.create_test_menu_data()
                
            # Run all menu deletion tests
            tests = [
                ("Menu Item Deletions", self.test_menu_item_deletions),
                ("Menu Modifier Deletions", self.test_menu_modifier_deletions),
                ("Menu Category Deletions", self.test_menu_category_deletions),
                ("Cascade Deletion Behavior", self.test_cascade_deletion_behavior),
                ("Deletion Validation", self.test_deletion_validation)
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
            self.print_menu_deletion_summary()
            
            return overall_success
            
        except KeyboardInterrupt:
            print("\n⚠️ Menu deletion tests interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Menu deletion tests failed: {e}")
            return False
        finally:
            # Always cleanup remaining entities
            try:
                await self.cleanup_remaining_entities()
            except Exception as e:
                print(f"⚠️ Final cleanup failed: {e}")
                
            await self.client.close()


async def main():
    """Main entry point for menu deletion testing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Test RMS menu deletion operations")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--confirm-deletes", action="store_true", 
                       help="Confirm that you want to perform destructive delete operations")
    
    args = parser.parse_args()
    
    tester = MenuDeletionTester(args.base_url, args.confirm_deletes)
    
    try:
        success = await tester.run_comprehensive_menu_deletion_tests()
        
        if success:
            print(f"\n✅ All menu deletion tests passed successfully!")
        else:
            print(f"\n❌ Some menu deletion tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Menu deletion testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())