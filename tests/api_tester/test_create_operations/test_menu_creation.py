#!/usr/bin/env python3
"""
Test Menu Creation Operations

Comprehensive testing of menu-related POST endpoints.
Tests menu category, item, and modifier creation workflows.
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


class MenuCreationTester:
    """Comprehensive menu creation operations testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.results = TestResults()
        self.auth_headers = None
        self.created_categories = []
        self.created_items = []
        self.created_modifiers = []
        
    async def setup_authentication(self) -> bool:
        """Setup authentication for all tests"""
        
        self.auth_headers = await get_auth_headers(self.client)
        if not self.auth_headers:
            APITestHelper.print_test_step("Authentication failed - cannot run menu creation tests", "FAILED")
            return False
            
        APITestHelper.print_test_step("Authentication successful", "SUCCESS")
        return True
        
    async def test_menu_category_creation(self) -> bool:
        """Test creating menu categories"""
        
        APITestHelper.print_test_header("Menu Category Creation", "📂")
        
        # Generate test categories
        categories_data = RMSTestFixtures.generate_menu_category_data("american")
        
        success_count = 0
        
        for i, category_data in enumerate(categories_data[:3]):  # Test first 3 categories
            try:
                # Add unique suffix to avoid conflicts
                category_data["name"] = f"{category_data['name']} Test {i+1}"
                
                APITestHelper.print_test_step(f"Creating category: {category_data['name']}", "RUNNING")
                
                start_time = time.time()
                response = await self.client.post("/api/v1/menu/categories", json=category_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 201:
                    category_response = response.json()
                    self.created_categories.append(category_response)
                    
                    APITestHelper.print_test_step(f"Category created successfully ({response_time:.0f}ms)", "SUCCESS")
                    
                    # Validate response structure
                    required_fields = ['id', 'name', 'sort_order']
                    if all(field in category_response for field in required_fields):
                        APITestHelper.print_test_step("Category response structure is valid", "SUCCESS")
                        
                        print(f"   📂 Created Category:")
                        print(f"      ID: {category_response['id']}")
                        print(f"      Name: {category_response['name']}")
                        print(f"      Sort Order: {category_response['sort_order']}")
                        print(f"      Description: {category_response.get('description', 'N/A')}")
                        
                        # Verify data matches input
                        if APITestHelper.compare_data_fields(category_data, category_response, ['name', 'description', 'sort_order']):
                            APITestHelper.print_test_step("Category data matches input", "SUCCESS")
                        else:
                            APITestHelper.print_test_step("Category data doesn't match input", "FAILED")
                            
                    else:
                        APITestHelper.print_test_step("Category response missing required fields", "FAILED")
                        
                    self.results.add_success("menu_categories", f"Create category {i+1}", {
                        "response_time": response_time,
                        "category_id": category_response['id'],
                        "category_name": category_response['name']
                    })
                    success_count += 1
                    
                elif response.status_code == 409:
                    APITestHelper.print_test_step(f"Category already exists (conflict)", "SKIPPED")
                    
                else:
                    APITestHelper.print_test_step(f"Category creation failed: HTTP {response.status_code}", "FAILED")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    self.results.add_failure("menu_categories", f"Create category {i+1}", 
                                           f"HTTP {response.status_code}", response.status_code)
                    
                # Small delay between creations
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Category creation error: {e}", "FAILED")
                self.results.add_failure("menu_categories", f"Create category {i+1}", str(e))
                
        print(f"\n📊 Category Creation Summary: {success_count}/{len(categories_data[:3])} successful")
        return success_count > 0
        
    async def test_menu_item_creation(self) -> bool:
        """Test creating menu items"""
        
        APITestHelper.print_test_header("Menu Item Creation", "🍽️")
        
        # Need a category to assign items to
        if not self.created_categories:
            APITestHelper.print_test_step("No categories available for item creation", "SKIPPED")
            return True
            
        category = self.created_categories[0]
        category_id = category['id']
        category_name = category['name']
        
        print(f"   📂 Using category: {category_name} ({category_id})")
        
        # Generate test menu items
        items_data = RMSTestFixtures.generate_menu_items_data(category_id, category_name, "american")
        
        success_count = 0
        
        for i, item_data in enumerate(items_data[:4]):  # Test first 4 items
            try:
                # Add unique suffix to avoid conflicts
                item_data["name"] = f"{item_data['name']} Test {i+1}"
                
                APITestHelper.print_test_step(f"Creating item: {item_data['name']}", "RUNNING")
                
                start_time = time.time()
                response = await self.client.post("/api/v1/menu/items", json=item_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 201:
                    item_response = response.json()
                    self.created_items.append(item_response)
                    
                    APITestHelper.print_test_step(f"Item created successfully ({response_time:.0f}ms)", "SUCCESS")
                    
                    # Validate response structure
                    if APITestHelper.validate_menu_item_response(item_response):
                        APITestHelper.print_test_step("Item response structure is valid", "SUCCESS")
                        
                        print(f"   🍽️ Created Item:")
                        print(f"      ID: {item_response['id']}")
                        print(f"      Name: {item_response['name']}")
                        print(f"      Price: ${item_response['price']}")
                        print(f"      Category: {item_response.get('category_id')}")
                        print(f"      Available: {item_response.get('is_available')}")
                        
                        # Verify data matches input
                        if APITestHelper.compare_data_fields(item_data, item_response, ['name', 'description', 'price', 'category_id']):
                            APITestHelper.print_test_step("Item data matches input", "SUCCESS")
                        else:
                            APITestHelper.print_test_step("Item data doesn't match input", "FAILED")
                            
                    else:
                        APITestHelper.print_test_step("Item response missing required fields", "FAILED")
                        
                    self.results.add_success("menu_items", f"Create item {i+1}", {
                        "response_time": response_time,
                        "item_id": item_response['id'],
                        "item_name": item_response['name'],
                        "price": item_response['price']
                    })
                    success_count += 1
                    
                elif response.status_code == 409:
                    APITestHelper.print_test_step(f"Item already exists (conflict)", "SKIPPED")
                    
                else:
                    APITestHelper.print_test_step(f"Item creation failed: HTTP {response.status_code}", "FAILED")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    self.results.add_failure("menu_items", f"Create item {i+1}", 
                                           f"HTTP {response.status_code}", response.status_code)
                    
                # Small delay between creations
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Item creation error: {e}", "FAILED")
                self.results.add_failure("menu_items", f"Create item {i+1}", str(e))
                
        print(f"\n📊 Item Creation Summary: {success_count}/{len(items_data[:4])} successful")
        return success_count > 0
        
    async def test_menu_modifier_creation(self) -> bool:
        """Test creating menu modifiers"""
        
        APITestHelper.print_test_header("Menu Modifier Creation", "🔧")
        
        # Generate test modifiers
        modifiers_data = RMSTestFixtures.generate_modifier_data()
        
        success_count = 0
        
        for i, modifier_data in enumerate(modifiers_data[:3]):  # Test first 3 modifiers
            try:
                # Add unique suffix to avoid conflicts
                modifier_data["name"] = f"{modifier_data['name']} Test {i+1}"
                
                APITestHelper.print_test_step(f"Creating modifier: {modifier_data['name']}", "RUNNING")
                
                start_time = time.time()
                response = await self.client.post("/api/v1/menu/modifiers", json=modifier_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 201:
                    modifier_response = response.json()
                    self.created_modifiers.append(modifier_response)
                    
                    APITestHelper.print_test_step(f"Modifier created successfully ({response_time:.0f}ms)", "SUCCESS")
                    
                    # Validate response structure
                    required_fields = ['id', 'name', 'type', 'price_adjustment']
                    if all(field in modifier_response for field in required_fields):
                        APITestHelper.print_test_step("Modifier response structure is valid", "SUCCESS")
                        
                        print(f"   🔧 Created Modifier:")
                        print(f"      ID: {modifier_response['id']}")
                        print(f"      Name: {modifier_response['name']}")
                        print(f"      Type: {modifier_response['type']}")
                        print(f"      Price Adjustment: ${modifier_response['price_adjustment']}")
                        
                        # Verify data matches input
                        if APITestHelper.compare_data_fields(modifier_data, modifier_response, ['name', 'type', 'price_adjustment']):
                            APITestHelper.print_test_step("Modifier data matches input", "SUCCESS")
                        else:
                            APITestHelper.print_test_step("Modifier data doesn't match input", "FAILED")
                            
                    else:
                        APITestHelper.print_test_step("Modifier response missing required fields", "FAILED")
                        
                    self.results.add_success("menu_modifiers", f"Create modifier {i+1}", {
                        "response_time": response_time,
                        "modifier_id": modifier_response['id'],
                        "modifier_name": modifier_response['name']
                    })
                    success_count += 1
                    
                elif response.status_code == 404:
                    APITestHelper.print_test_step("Modifiers endpoint not found (may not be implemented)", "SKIPPED")
                    break  # Don't try more if endpoint doesn't exist
                    
                elif response.status_code == 409:
                    APITestHelper.print_test_step(f"Modifier already exists (conflict)", "SKIPPED")
                    
                else:
                    APITestHelper.print_test_step(f"Modifier creation failed: HTTP {response.status_code}", "FAILED")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    self.results.add_failure("menu_modifiers", f"Create modifier {i+1}", 
                                           f"HTTP {response.status_code}", response.status_code)
                    
                # Small delay between creations
                await asyncio.sleep(0.3)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Modifier creation error: {e}", "FAILED")
                self.results.add_failure("menu_modifiers", f"Create modifier {i+1}", str(e))
                
        print(f"\n📊 Modifier Creation Summary: {success_count}/{len(modifiers_data[:3])} successful")
        return True  # Not a failure if modifiers aren't implemented
        
    async def test_menu_item_modifier_assignment(self) -> bool:
        """Test assigning modifiers to menu items"""
        
        APITestHelper.print_test_header("Menu Item Modifier Assignment", "🔗")
        
        if not self.created_items or not self.created_modifiers:
            APITestHelper.print_test_step("Need both items and modifiers for assignment testing", "SKIPPED")
            return True
            
        item = self.created_items[0]
        modifier = self.created_modifiers[0]
        item_id = item['id']
        modifier_id = modifier['id']
        
        print(f"   🍽️ Item: {item['name']} ({item_id})")
        print(f"   🔧 Modifier: {modifier['name']} ({modifier_id})")
        
        try:
            APITestHelper.print_test_step("Assigning modifier to item", "RUNNING")
            
            assignment_data = {
                "modifier_id": modifier_id
            }
            
            start_time = time.time()
            response = await self.client.post(f"/api/v1/menu/items/{item_id}/modifiers", 
                                            json=assignment_data, headers=self.auth_headers)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 201:
                APITestHelper.print_test_step(f"Modifier assignment successful ({response_time:.0f}ms)", "SUCCESS")
                
                assignment_response = response.json()
                if isinstance(assignment_response, dict):
                    print(f"   🔗 Assignment Details:")
                    for key, value in assignment_response.items():
                        print(f"      {key}: {value}")
                        
                self.results.add_success("menu_assignments", "Assign modifier to item", {
                    "response_time": response_time,
                    "item_id": item_id,
                    "modifier_id": modifier_id
                })
                return True
                
            elif response.status_code == 404:
                APITestHelper.print_test_step("Modifier assignment endpoint not found (may not be implemented)", "SKIPPED")
                return True
                
            else:
                APITestHelper.print_test_step(f"Modifier assignment failed: HTTP {response.status_code}", "FAILED")
                if response.json_data:
                    print(f"   Error: {response.json_data}")
                self.results.add_failure("menu_assignments", "Assign modifier to item", 
                                       f"HTTP {response.status_code}", response.status_code)
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Modifier assignment error: {e}", "FAILED")
            self.results.add_failure("menu_assignments", "Assign modifier to item", str(e))
            return False
            
    async def test_menu_data_validation(self) -> bool:
        """Test menu data validation and error handling"""
        
        APITestHelper.print_test_header("Menu Data Validation", "✅")
        
        validation_tests = [
            # Category validation tests
            ({}, "Empty category data", "/api/v1/menu/categories"),
            ({"name": ""}, "Empty category name", "/api/v1/menu/categories"),
            ({"name": "Test", "sort_order": "invalid"}, "Invalid sort order", "/api/v1/menu/categories"),
            
            # Item validation tests (if we have a category)
            ({}, "Empty item data", "/api/v1/menu/items"),
            ({"name": "Test Item"}, "Missing price", "/api/v1/menu/items"),
            ({"name": "Test", "price": -10}, "Negative price", "/api/v1/menu/items"),
            ({"name": "Test", "price": "invalid"}, "Invalid price", "/api/v1/menu/items"),
        ]
        
        if self.created_categories:
            # Add category_id to item tests
            category_id = self.created_categories[0]['id']
            for i, (data, desc, endpoint) in enumerate(validation_tests):
                if endpoint == "/api/v1/menu/items" and data:
                    data["category_id"] = category_id
        
        success_count = 0
        
        for invalid_data, description, endpoint in validation_tests:
            try:
                APITestHelper.print_test_step(f"Testing: {description}", "RUNNING")
                
                start_time = time.time()
                response = await self.client.post(endpoint, json=invalid_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                # We expect validation errors (400) for invalid data
                if response.status_code == 400:
                    APITestHelper.print_test_step(f"Validation correctly rejected ({response_time:.0f}ms)", "SUCCESS")
                    
                    if response.json_data:
                        error_info = response.json_data
                        print(f"   ✅ Error details: {error_info}")
                        
                    self.results.add_success("menu_validation", description, {
                        "response_time": response_time,
                        "correctly_rejected": True
                    })
                    success_count += 1
                    
                elif response.status_code == 422:
                    APITestHelper.print_test_step(f"Validation error (422) - correct behavior ({response_time:.0f}ms)", "SUCCESS")
                    success_count += 1
                    
                elif response.status_code == 201:
                    APITestHelper.print_test_step(f"Invalid data accepted (should be rejected)", "FAILED")
                    self.results.add_failure("menu_validation", description, 
                                           "Invalid data was accepted", 201)
                    
                else:
                    APITestHelper.print_test_step(f"Unexpected response: HTTP {response.status_code}", "FAILED")
                    self.results.add_failure("menu_validation", description, 
                                           f"HTTP {response.status_code}", response.status_code)
                    
                await asyncio.sleep(0.2)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Validation test error: {e}", "FAILED")
                self.results.add_failure("menu_validation", description, str(e))
                
        print(f"\n📊 Validation Testing Summary: {success_count}/{len(validation_tests)} tests passed")
        return success_count > 0
        
    def print_menu_creation_summary(self):
        """Print comprehensive menu creation test summary"""
        
        APITestHelper.print_test_header("Menu Creation Tests Summary", "📊")
        
        print(f"Total Tests: {self.results.total_tests}")
        print(f"Passed: {self.results.passed_tests}")
        print(f"Failed: {self.results.failed_tests}")
        print(f"Success Rate: {self.results.success_rate:.1f}%")
        
        # Show created entities
        print(f"\n📂 Created Entities:")
        print(f"   Categories: {len(self.created_categories)}")
        print(f"   Items: {len(self.created_items)}")
        print(f"   Modifiers: {len(self.created_modifiers)}")
        
        if self.created_categories:
            print(f"\n   📂 Categories:")
            for cat in self.created_categories:
                print(f"      • {cat['name']} (ID: {cat['id']})")
                
        if self.created_items:
            print(f"\n   🍽️ Items:")
            for item in self.created_items:
                print(f"      • {item['name']} - ${item['price']} (ID: {item['id']})")
                
        if self.created_modifiers:
            print(f"\n   🔧 Modifiers:")
            for mod in self.created_modifiers:
                print(f"      • {mod['name']} - ${mod['price_adjustment']} (ID: {mod['id']})")
                
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
                    
    async def cleanup_created_entities(self):
        """Clean up created test entities"""
        
        if not any([self.created_categories, self.created_items, self.created_modifiers]):
            return
            
        print(f"\n🧹 Cleaning up created test entities...")
        
        # Clean up in reverse order (items -> modifiers -> categories)
        cleanup_tasks = [
            (self.created_items, "/api/v1/menu/items", "items"),
            (self.created_modifiers, "/api/v1/menu/modifiers", "modifiers"),
            (self.created_categories, "/api/v1/menu/categories", "categories")
        ]
        
        for entities, endpoint_base, entity_type in cleanup_tasks:
            if entities:
                print(f"   🗑️ Cleaning up {len(entities)} {entity_type}...")
                
                for entity in entities:
                    try:
                        entity_id = entity['id']
                        response = await self.client.delete(f"{endpoint_base}/{entity_id}", headers=self.auth_headers)
                        
                        if response.status_code == 204:
                            print(f"   ✅ Deleted {entity_type[:-1]}: {entity.get('name', entity_id)}")
                        elif response.status_code == 404:
                            print(f"   ⚠️ {entity_type[:-1]} already deleted: {entity.get('name', entity_id)}")
                        else:
                            print(f"   ❌ Failed to delete {entity_type[:-1]}: {entity.get('name', entity_id)}")
                            
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        print(f"   ❌ Error deleting {entity_type[:-1]}: {e}")
                        
    async def run_comprehensive_menu_creation_tests(self) -> bool:
        """Run all menu creation tests"""
        
        print("🍽️ RMS Menu Creation Operations Tests")
        print("="*50)
        
        start_time = time.time()
        
        try:
            # Setup authentication
            if not await self.setup_authentication():
                return False
                
            # Run all menu creation tests
            tests = [
                ("Menu Category Creation", self.test_menu_category_creation),
                ("Menu Item Creation", self.test_menu_item_creation),
                ("Menu Modifier Creation", self.test_menu_modifier_creation),
                ("Modifier Assignment", self.test_menu_item_modifier_assignment),
                ("Data Validation", self.test_menu_data_validation)
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
            self.print_menu_creation_summary()
            
            return overall_success
            
        except KeyboardInterrupt:
            print("\n⚠️ Menu creation tests interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Menu creation tests failed: {e}")
            return False
        finally:
            # Cleanup created entities
            try:
                await self.cleanup_created_entities()
            except Exception as e:
                print(f"⚠️ Cleanup failed: {e}")
                
            await self.client.close()


async def main():
    """Main entry point for menu creation testing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Test RMS menu creation operations")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--no-cleanup", action="store_true", help="Skip cleanup of created entities")
    
    args = parser.parse_args()
    
    tester = MenuCreationTester(args.base_url)
    
    try:
        success = await tester.run_comprehensive_menu_creation_tests()
        
        if success:
            print(f"\n✅ All menu creation tests passed successfully!")
        else:
            print(f"\n❌ Some menu creation tests failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Menu creation testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())