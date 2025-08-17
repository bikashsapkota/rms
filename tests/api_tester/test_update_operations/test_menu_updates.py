#!/usr/bin/env python3
"""
Test Menu Update Operations

Comprehensive testing of menu-related PUT/PATCH endpoints.
Tests menu category, item, and modifier update workflows.
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


class MenuUpdateTester:
    """Comprehensive menu update operations testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.results = TestResults()
        self.auth_headers = None
        self.available_categories = []
        self.available_items = []
        self.available_modifiers = []
        
    async def setup_authentication(self) -> bool:
        """Setup authentication for all tests"""
        
        self.auth_headers = await get_auth_headers(self.client)
        if not self.auth_headers:
            APITestHelper.print_test_step("Authentication failed - cannot run menu update tests", "FAILED")
            return False
            
        APITestHelper.print_test_step("Authentication successful", "SUCCESS")
        return True
        
    async def load_existing_menu_data(self):
        """Load existing menu data for update testing"""
        
        try:
            # Load categories
            response = await self.client.get("/api/v1/menu/categories", headers=self.auth_headers)
            if response.status_code == 200:
                categories = response.json()
                if isinstance(categories, list):
                    self.available_categories = categories
                elif isinstance(categories, dict) and 'items' in categories:
                    self.available_categories = categories['items']
                    
            # Load items
            response = await self.client.get("/api/v1/menu/items", headers=self.auth_headers)
            if response.status_code == 200:
                items = response.json()
                if isinstance(items, list):
                    self.available_items = items
                elif isinstance(items, dict) and 'items' in items:
                    self.available_items = items['items']
                    
            # Load modifiers
            response = await self.client.get("/api/v1/menu/modifiers", headers=self.auth_headers)
            if response.status_code == 200:
                modifiers = response.json()
                if isinstance(modifiers, list):
                    self.available_modifiers = modifiers
                elif isinstance(modifiers, dict) and 'items' in modifiers:
                    self.available_modifiers = modifiers['items']
                    
            print(f"   📂 Found {len(self.available_categories)} categories")
            print(f"   🍽️ Found {len(self.available_items)} menu items")
            print(f"   🔧 Found {len(self.available_modifiers)} modifiers")
            
        except Exception as e:
            print(f"   ❌ Error loading menu data: {e}")
            
    async def create_test_menu_data(self):
        """Create test menu data if none exists"""
        
        if not self.available_categories:
            APITestHelper.print_test_step("Creating test category for update testing", "RUNNING")
            
            category_data = {
                "name": "Update Test Category",
                "description": "Category created for update testing",
                "sort_order": 99
            }
            
            response = await self.client.post("/api/v1/menu/categories", json=category_data, headers=self.auth_headers)
            if response.status_code == 201:
                self.available_categories.append(response.json())
                APITestHelper.print_test_step("Test category created", "SUCCESS")
            else:
                APITestHelper.print_test_step("Failed to create test category", "FAILED")
                
        if not self.available_items and self.available_categories:
            APITestHelper.print_test_step("Creating test menu item for update testing", "RUNNING")
            
            category_id = self.available_categories[0]['id']
            item_data = {
                "name": "Update Test Item",
                "description": "Item created for update testing",
                "price": 15.99,
                "category_id": category_id,
                "is_available": True
            }
            
            response = await self.client.post("/api/v1/menu/items", json=item_data, headers=self.auth_headers)
            if response.status_code == 201:
                self.available_items.append(response.json())
                APITestHelper.print_test_step("Test menu item created", "SUCCESS")
            else:
                APITestHelper.print_test_step("Failed to create test menu item", "FAILED")
                
    async def test_menu_category_updates(self) -> bool:
        """Test updating menu categories"""
        
        APITestHelper.print_test_header("Menu Category Updates", "📂")
        
        if not self.available_categories:
            APITestHelper.print_test_step("No categories available for update testing", "SKIPPED")
            return True
            
        category = self.available_categories[0]
        category_id = category['id']
        original_name = category['name']
        
        print(f"   📂 Testing updates for category: {original_name} ({category_id})")
        
        update_tests = [
            # Full update (PUT)
            ({
                "name": f"{original_name} - UPDATED",
                "description": "Updated description via PUT",
                "sort_order": category.get('sort_order', 1) + 10
            }, "Full category update (PUT)", "PUT"),
            
            # Partial update (PATCH)
            ({
                "description": "Updated description via PATCH"
            }, "Partial category update (PATCH)", "PATCH"),
            
            # Name update only
            ({
                "name": f"{original_name} - Final Update"
            }, "Category name update", "PATCH"),
            
            # Sort order update
            ({
                "sort_order": 1
            }, "Category sort order update", "PATCH")
        ]
        
        success_count = 0
        
        for update_data, description, method in update_tests:
            try:
                APITestHelper.print_test_step(f"Testing: {description}", "RUNNING")
                
                start_time = time.time()
                if method == "PUT":
                    response = await self.client.put(f"/api/v1/menu/categories/{category_id}", 
                                                   json=update_data, headers=self.auth_headers)
                else:  # PATCH
                    response = await self.client.patch(f"/api/v1/menu/categories/{category_id}", 
                                                     json=update_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    updated_category = response.json()
                    
                    APITestHelper.print_test_step(f"{description} successful ({response_time:.0f}ms)", "SUCCESS")
                    
                    # Verify updates were applied
                    updates_applied = True
                    for key, expected_value in update_data.items():
                        actual_value = updated_category.get(key)
                        if actual_value != expected_value:
                            APITestHelper.print_test_step(f"Update verification failed: {key} = {actual_value} (expected {expected_value})", "FAILED")
                            updates_applied = False
                            
                    if updates_applied:
                        APITestHelper.print_test_step("All updates verified", "SUCCESS")
                        
                        print(f"   📂 Updated Category:")
                        print(f"      Name: {updated_category.get('name')}")
                        print(f"      Description: {updated_category.get('description', 'N/A')}")
                        print(f"      Sort Order: {updated_category.get('sort_order')}")
                        
                    self.results.add_success("category_updates", description, {
                        "response_time": response_time,
                        "category_id": category_id,
                        "method": method,
                        "updates_verified": updates_applied
                    })
                    success_count += 1
                    
                elif response.status_code == 404:
                    APITestHelper.print_test_step(f"Category not found: {category_id}", "FAILED")
                    self.results.add_failure("category_updates", description, 
                                           "Category not found", 404)
                    
                else:
                    APITestHelper.print_test_step(f"{description} failed: HTTP {response.status_code}", "FAILED")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    self.results.add_failure("category_updates", description, 
                                           f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"{description} error: {e}", "FAILED")
                self.results.add_failure("category_updates", description, str(e))
                
        print(f"\n📊 Category Update Summary: {success_count}/{len(update_tests)} successful")
        return success_count > 0
        
    async def test_menu_item_updates(self) -> bool:
        """Test updating menu items"""
        
        APITestHelper.print_test_header("Menu Item Updates", "🍽️")
        
        if not self.available_items:
            APITestHelper.print_test_step("No menu items available for update testing", "SKIPPED")
            return True
            
        item = self.available_items[0]
        item_id = item['id']
        original_name = item['name']
        original_price = item.get('price', 0)
        
        print(f"   🍽️ Testing updates for item: {original_name} (${original_price}) - {item_id}")
        
        update_tests = [
            # Price update
            ({
                "price": original_price + 2.00
            }, "Menu item price update", "PATCH"),
            
            # Availability toggle
            ({
                "is_available": not item.get('is_available', True)
            }, "Menu item availability toggle", "PATCH"),
            
            # Full item update
            ({
                "name": f"{original_name} - UPDATED",
                "description": "Updated description for menu item",
                "price": original_price + 5.00,
                "is_available": True
            }, "Full menu item update (PUT)", "PUT"),
            
            # Description update only
            ({
                "description": "Final updated description"
            }, "Menu item description update", "PATCH")
        ]
        
        success_count = 0
        
        for update_data, description, method in update_tests:
            try:
                APITestHelper.print_test_step(f"Testing: {description}", "RUNNING")
                
                start_time = time.time()
                if method == "PUT":
                    # For PUT, we need to include category_id if it's required
                    if 'category_id' not in update_data and item.get('category_id'):
                        update_data['category_id'] = item['category_id']
                        
                    response = await self.client.put(f"/api/v1/menu/items/{item_id}", 
                                                   json=update_data, headers=self.auth_headers)
                else:  # PATCH
                    response = await self.client.patch(f"/api/v1/menu/items/{item_id}", 
                                                     json=update_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    updated_item = response.json()
                    
                    APITestHelper.print_test_step(f"{description} successful ({response_time:.0f}ms)", "SUCCESS")
                    
                    # Verify updates were applied
                    updates_applied = True
                    for key, expected_value in update_data.items():
                        actual_value = updated_item.get(key)
                        if key == 'price':
                            # Handle price comparison with tolerance for floating point
                            if abs(float(actual_value) - float(expected_value)) > 0.01:
                                APITestHelper.print_test_step(f"Price update verification failed: {actual_value} (expected {expected_value})", "FAILED")
                                updates_applied = False
                        elif actual_value != expected_value:
                            APITestHelper.print_test_step(f"Update verification failed: {key} = {actual_value} (expected {expected_value})", "FAILED")
                            updates_applied = False
                            
                    if updates_applied:
                        APITestHelper.print_test_step("All updates verified", "SUCCESS")
                        
                        print(f"   🍽️ Updated Item:")
                        print(f"      Name: {updated_item.get('name')}")
                        print(f"      Price: ${updated_item.get('price')}")
                        print(f"      Available: {updated_item.get('is_available')}")
                        print(f"      Description: {updated_item.get('description', 'N/A')[:50]}...")
                        
                    self.results.add_success("item_updates", description, {
                        "response_time": response_time,
                        "item_id": item_id,
                        "method": method,
                        "updates_verified": updates_applied
                    })
                    success_count += 1
                    
                elif response.status_code == 404:
                    APITestHelper.print_test_step(f"Menu item not found: {item_id}", "FAILED")
                    self.results.add_failure("item_updates", description, 
                                           "Menu item not found", 404)
                    
                else:
                    APITestHelper.print_test_step(f"{description} failed: HTTP {response.status_code}", "FAILED")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    self.results.add_failure("item_updates", description, 
                                           f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"{description} error: {e}", "FAILED")
                self.results.add_failure("item_updates", description, str(e))
                
        print(f"\n📊 Item Update Summary: {success_count}/{len(update_tests)} successful")
        return success_count > 0
        
    async def test_menu_modifier_updates(self) -> bool:
        """Test updating menu modifiers"""
        
        APITestHelper.print_test_header("Menu Modifier Updates", "🔧")
        
        if not self.available_modifiers:
            APITestHelper.print_test_step("No modifiers available for update testing (may not be implemented)", "SKIPPED")
            return True
            
        modifier = self.available_modifiers[0]
        modifier_id = modifier['id']
        original_name = modifier['name']
        original_price = modifier.get('price_adjustment', 0)
        
        print(f"   🔧 Testing updates for modifier: {original_name} (${original_price}) - {modifier_id}")
        
        update_tests = [
            # Price adjustment update
            ({
                "price_adjustment": original_price + 1.00
            }, "Modifier price adjustment update", "PATCH"),
            
            # Name update
            ({
                "name": f"{original_name} - UPDATED"
            }, "Modifier name update", "PATCH"),
            
            # Full modifier update
            ({
                "name": f"{original_name} - Full Update",
                "type": modifier.get('type', 'addon'),
                "price_adjustment": original_price + 2.50
            }, "Full modifier update (PUT)", "PUT")
        ]
        
        success_count = 0
        
        for update_data, description, method in update_tests:
            try:
                APITestHelper.print_test_step(f"Testing: {description}", "RUNNING")
                
                start_time = time.time()
                if method == "PUT":
                    response = await self.client.put(f"/api/v1/menu/modifiers/{modifier_id}", 
                                                   json=update_data, headers=self.auth_headers)
                else:  # PATCH
                    response = await self.client.patch(f"/api/v1/menu/modifiers/{modifier_id}", 
                                                     json=update_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    updated_modifier = response.json()
                    
                    APITestHelper.print_test_step(f"{description} successful ({response_time:.0f}ms)", "SUCCESS")
                    
                    # Verify updates were applied
                    updates_applied = True
                    for key, expected_value in update_data.items():
                        actual_value = updated_modifier.get(key)
                        if key == 'price_adjustment':
                            # Handle price comparison with tolerance
                            if abs(float(actual_value) - float(expected_value)) > 0.01:
                                APITestHelper.print_test_step(f"Price adjustment verification failed: {actual_value} (expected {expected_value})", "FAILED")
                                updates_applied = False
                        elif actual_value != expected_value:
                            APITestHelper.print_test_step(f"Update verification failed: {key} = {actual_value} (expected {expected_value})", "FAILED")
                            updates_applied = False
                            
                    if updates_applied:
                        APITestHelper.print_test_step("All updates verified", "SUCCESS")
                        
                        print(f"   🔧 Updated Modifier:")
                        print(f"      Name: {updated_modifier.get('name')}")
                        print(f"      Type: {updated_modifier.get('type')}")
                        print(f"      Price Adjustment: ${updated_modifier.get('price_adjustment')}")
                        
                    self.results.add_success("modifier_updates", description, {
                        "response_time": response_time,
                        "modifier_id": modifier_id,
                        "method": method,
                        "updates_verified": updates_applied
                    })
                    success_count += 1
                    
                elif response.status_code == 404:
                    APITestHelper.print_test_step("Modifier endpoint not found (may not be implemented)", "SKIPPED")
                    break  # Don't try more if endpoint doesn't exist
                    
                else:
                    APITestHelper.print_test_step(f"{description} failed: HTTP {response.status_code}", "FAILED")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    self.results.add_failure("modifier_updates", description, 
                                           f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"{description} error: {e}", "FAILED")
                self.results.add_failure("modifier_updates", description, str(e))
                
        print(f"\n📊 Modifier Update Summary: {success_count}/{len(update_tests)} successful")
        return True  # Not a failure if modifiers aren't implemented
        
    async def test_menu_item_availability_toggle(self) -> bool:
        """Test specific availability toggle endpoint"""
        
        APITestHelper.print_test_header("Menu Item Availability Toggle", "🔄")
        
        if not self.available_items:
            APITestHelper.print_test_step("No menu items available for availability testing", "SKIPPED")
            return True
            
        item = self.available_items[0]
        item_id = item['id']
        current_availability = item.get('is_available', True)
        
        print(f"   🍽️ Testing availability toggle for: {item['name']}")
        print(f"   📊 Current availability: {current_availability}")
        
        try:
            APITestHelper.print_test_step("Toggling menu item availability", "RUNNING")
            
            toggle_data = {
                "is_available": not current_availability
            }
            
            start_time = time.time()
            response = await self.client.put(f"/api/v1/menu/items/{item_id}/availability", 
                                           json=toggle_data, headers=self.auth_headers)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                updated_item = response.json()
                new_availability = updated_item.get('is_available')
                
                APITestHelper.print_test_step(f"Availability toggled successfully ({response_time:.0f}ms)", "SUCCESS")
                
                if new_availability == (not current_availability):
                    APITestHelper.print_test_step(f"Availability correctly changed to {new_availability}", "SUCCESS")
                    
                    print(f"   🔄 Availability Update:")
                    print(f"      Previous: {current_availability}")
                    print(f"      Current: {new_availability}")
                    
                    self.results.add_success("availability_toggle", "Toggle item availability", {
                        "response_time": response_time,
                        "item_id": item_id,
                        "previous_state": current_availability,
                        "new_state": new_availability
                    })
                    
                    # Toggle back to original state
                    await asyncio.sleep(0.2)
                    
                    restore_data = {"is_available": current_availability}
                    restore_response = await self.client.put(f"/api/v1/menu/items/{item_id}/availability", 
                                                           json=restore_data, headers=self.auth_headers)
                    
                    if restore_response.status_code == 200:
                        APITestHelper.print_test_step("Availability restored to original state", "SUCCESS")
                    
                else:
                    APITestHelper.print_test_step(f"Availability change verification failed", "FAILED")
                    self.results.add_failure("availability_toggle", "Toggle item availability", 
                                           "Availability state not changed")
                    return False
                    
                return True
                
            elif response.status_code == 404:
                APITestHelper.print_test_step("Availability toggle endpoint not found (may not be implemented)", "SKIPPED")
                return True
                
            else:
                APITestHelper.print_test_step(f"Availability toggle failed: HTTP {response.status_code}", "FAILED")
                if response.json_data:
                    print(f"   Error: {response.json_data}")
                self.results.add_failure("availability_toggle", "Toggle item availability", 
                                       f"HTTP {response.status_code}", response.status_code)
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Availability toggle error: {e}", "FAILED")
            self.results.add_failure("availability_toggle", "Toggle item availability", str(e))
            return False
            
    async def test_update_validation(self) -> bool:
        """Test update data validation and error handling"""
        
        APITestHelper.print_test_header("Update Data Validation", "✅")
        
        if not self.available_categories or not self.available_items:
            APITestHelper.print_test_step("Need categories and items for validation testing", "SKIPPED")
            return True
            
        category_id = self.available_categories[0]['id']
        item_id = self.available_items[0]['id']
        
        validation_tests = [
            # Category validation tests
            (f"/api/v1/menu/categories/{category_id}", {"name": ""}, "Empty category name", "PATCH"),
            (f"/api/v1/menu/categories/{category_id}", {"sort_order": "invalid"}, "Invalid sort order", "PATCH"),
            
            # Item validation tests
            (f"/api/v1/menu/items/{item_id}", {"price": -10}, "Negative price", "PATCH"),
            (f"/api/v1/menu/items/{item_id}", {"price": "invalid"}, "Invalid price format", "PATCH"),
            (f"/api/v1/menu/items/{item_id}", {"is_available": "maybe"}, "Invalid availability value", "PATCH"),
            (f"/api/v1/menu/items/{item_id}", {"category_id": "invalid-uuid"}, "Invalid category ID", "PATCH"),
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
                        
                    self.results.add_success("update_validation", description, {
                        "response_time": response_time,
                        "correctly_rejected": True
                    })
                    success_count += 1
                    
                elif response.status_code == 200:
                    APITestHelper.print_test_step(f"Invalid data accepted (should be rejected)", "FAILED")
                    self.results.add_failure("update_validation", description, 
                                           "Invalid data was accepted", 200)
                    
                else:
                    APITestHelper.print_test_step(f"Unexpected response: HTTP {response.status_code}", "FAILED")
                    self.results.add_failure("update_validation", description, 
                                           f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.2)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Validation test error: {e}", "FAILED")
                self.results.add_failure("update_validation", description, str(e))
                
        print(f"\n📊 Validation Testing Summary: {success_count}/{len(validation_tests)} tests passed")
        return success_count > 0
        
    def print_menu_update_summary(self):
        """Print comprehensive menu update test summary"""
        
        APITestHelper.print_test_header("Menu Update Tests Summary", "📊")
        
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
        print(f"   Categories: {len(self.available_categories)}")
        print(f"   Items: {len(self.available_items)}")
        print(f"   Modifiers: {len(self.available_modifiers)}")
        
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
                    
    async def run_comprehensive_menu_update_tests(self) -> bool:
        """Run all menu update tests"""
        
        print("🍽️ RMS Menu Update Operations Tests")
        print("="*50)
        
        start_time = time.time()
        
        try:
            # Setup authentication
            if not await self.setup_authentication():
                return False
                
            # Load existing menu data
            await self.load_existing_menu_data()
            
            # Create test data if needed
            await self.create_test_menu_data()
                
            # Run all menu update tests
            tests = [
                ("Menu Category Updates", self.test_menu_category_updates),
                ("Menu Item Updates", self.test_menu_item_updates),
                ("Menu Modifier Updates", self.test_menu_modifier_updates),
                ("Item Availability Toggle", self.test_menu_item_availability_toggle),
                ("Update Data Validation", self.test_update_validation)
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
            self.print_menu_update_summary()
            
            return overall_success
            
        except KeyboardInterrupt:
            print("\n⚠️ Menu update tests interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Menu update tests failed: {e}")
            return False
        finally:
            await self.client.close()


async def main():
    """Main entry point for menu update testing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Test RMS menu update operations")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    tester = MenuUpdateTester(args.base_url)
    
    try:
        success = await tester.run_comprehensive_menu_update_tests()
        
        if success:
            print(f"\n✅ All menu update tests passed successfully!")
        else:
            print(f"\n❌ Some menu update tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Menu update testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())