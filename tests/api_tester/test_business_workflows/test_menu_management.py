#!/usr/bin/env python3
"""
Test Menu Management Workflow

Comprehensive end-to-end testing of menu management operations.
Tests the complete lifecycle of menu creation, updates, and management.
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


class MenuManagementWorkflow:
    """End-to-end menu management workflow testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.results = TestResults()
        self.auth_headers = None
        
        # Menu workflow state
        self.menu_data = {
            "categories": [],
            "items": [],
            "seasonal_items": [],
            "daily_specials": [],
            "total_revenue": 0
        }
        
    async def setup_authentication(self) -> bool:
        """Setup authentication for menu workflow testing"""
        
        self.auth_headers = await get_auth_headers(self.client)
        if not self.auth_headers:
            APITestHelper.print_test_step("Authentication failed - cannot run menu workflow", "FAILED")
            return False
            
        APITestHelper.print_test_step("Authentication successful", "SUCCESS")
        return True
        
    async def test_comprehensive_menu_creation(self) -> bool:
        """Test Phase 1: Comprehensive menu creation"""
        
        APITestHelper.print_test_header("Phase 1: Comprehensive Menu Creation", "🍽️")
        
        try:
            # Create a complete restaurant menu structure
            menu_structure = {
                "Breakfast": [
                    {"name": "Pancakes Deluxe", "price": 12.99, "description": "Fluffy pancakes with maple syrup"},
                    {"name": "Eggs Benedict", "price": 14.99, "description": "English muffin with poached eggs and hollandaise"},
                    {"name": "Breakfast Burrito", "price": 11.99, "description": "Scrambled eggs, bacon, cheese, and potatoes"}
                ],
                "Lunch": [
                    {"name": "Caesar Salad", "price": 10.99, "description": "Crisp romaine with Caesar dressing"},
                    {"name": "Club Sandwich", "price": 13.99, "description": "Triple-decker with turkey, bacon, and avocado"},
                    {"name": "Soup of the Day", "price": 8.99, "description": "Chef's daily soup creation"}
                ],
                "Dinner": [
                    {"name": "Grilled Salmon", "price": 22.99, "description": "Atlantic salmon with lemon herb sauce"},
                    {"name": "Ribeye Steak", "price": 28.99, "description": "12oz ribeye with garlic mashed potatoes"},
                    {"name": "Vegetarian Pasta", "price": 16.99, "description": "Fresh pasta with seasonal vegetables"}
                ],
                "Desserts": [
                    {"name": "Chocolate Cake", "price": 7.99, "description": "Rich chocolate cake with berry compote"},
                    {"name": "Tiramisu", "price": 8.99, "description": "Classic Italian dessert"},
                    {"name": "Ice Cream Sundae", "price": 6.99, "description": "Vanilla ice cream with choice of toppings"}
                ]
            }
            
            total_categories = len(menu_structure)
            total_items = sum(len(items) for items in menu_structure.values())
            
            APITestHelper.print_test_step(f"Creating {total_categories} categories with {total_items} items", "RUNNING")
            
            categories_created = 0
            items_created = 0
            
            for sort_order, (category_name, items) in enumerate(menu_structure.items(), 1):
                # Create category
                category_data = {
                    "name": category_name,
                    "description": f"Our selection of {category_name.lower()} dishes",
                    "sort_order": sort_order
                }
                
                start_time = time.time()
                response = await self.client.post("/api/v1/menu/categories", 
                                                json=category_data, headers=self.auth_headers)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 201:
                    category = response.json()
                    self.menu_data["categories"].append(category)
                    categories_created += 1
                    
                    print(f"   ✅ Created category: {category_name} ({response_time:.0f}ms)")
                    
                    # Create items for this category
                    for item_data in items:
                        item_data["category_id"] = category["id"]
                        item_data["is_available"] = True
                        
                        item_start_time = time.time()
                        item_response = await self.client.post("/api/v1/menu/items", 
                                                             json=item_data, headers=self.auth_headers)
                        item_response_time = (time.time() - item_start_time) * 1000
                        
                        if item_response.status_code == 201:
                            item = item_response.json()
                            self.menu_data["items"].append(item)
                            items_created += 1
                            
                            print(f"      ✅ Created item: {item_data['name']} - ${item_data['price']} ({item_response_time:.0f}ms)")
                        else:
                            print(f"      ❌ Failed to create item: {item_data['name']}")
                            
                        await asyncio.sleep(0.05)  # Small delay between items
                        
                elif response.status_code == 409:
                    print(f"   ⚠️ Category already exists: {category_name}")
                else:
                    print(f"   ❌ Failed to create category: {category_name}")
                    
                await asyncio.sleep(0.1)  # Small delay between categories
                
            success_rate = (categories_created + items_created) / (total_categories + total_items)
            
            if success_rate >= 0.8:  # 80% success rate
                APITestHelper.print_test_step(f"Menu creation successful: {categories_created} categories, {items_created} items", "SUCCESS")
                
                self.results.add_success("menu_workflow", "Comprehensive menu creation", {
                    "categories_created": categories_created,
                    "items_created": items_created,
                    "success_rate": success_rate
                })
                
                return True
            else:
                APITestHelper.print_test_step(f"Menu creation incomplete: {success_rate:.1%} success rate", "FAILED")
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Menu creation error: {e}", "FAILED")
            self.results.add_failure("menu_workflow", "Comprehensive menu creation", str(e))
            return False
            
    async def test_dynamic_pricing_updates(self) -> bool:
        """Test Phase 2: Dynamic pricing and availability updates"""
        
        APITestHelper.print_test_header("Phase 2: Dynamic Pricing & Availability", "💰")
        
        if not self.menu_data["items"]:
            APITestHelper.print_test_step("No menu items available for pricing updates", "SKIPPED")
            return True
            
        try:
            # Simulate various pricing and availability scenarios
            pricing_scenarios = [
                ("Happy Hour Discount", 0.8, True),    # 20% discount
                ("Peak Hour Premium", 1.15, True),     # 15% premium
                ("Out of Stock", 1.0, False),          # Temporarily unavailable
                ("Special Promotion", 0.75, True),     # 25% discount
                ("Regular Price", 1.0, True)           # Back to normal
            ]
            
            updates_successful = 0
            total_updates = 0
            
            for scenario_name, price_multiplier, availability in pricing_scenarios:
                APITestHelper.print_test_step(f"Applying scenario: {scenario_name}", "RUNNING")
                
                # Apply to a subset of items
                items_to_update = self.menu_data["items"][:3]  # Update first 3 items
                
                for item in items_to_update:
                    total_updates += 1
                    original_price = float(item.get("price", 0))
                    new_price = round(original_price * price_multiplier, 2)
                    
                    update_data = {
                        "price": new_price,
                        "is_available": availability
                    }
                    
                    try:
                        start_time = time.time()
                        response = await self.client.patch(f"/api/v1/menu/items/{item['id']}", 
                                                         json=update_data, headers=self.auth_headers)
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status_code == 200:
                            updated_item = response.json()
                            
                            # Verify the update
                            if (abs(float(updated_item["price"]) - new_price) < 0.01 and 
                                updated_item["is_available"] == availability):
                                updates_successful += 1
                                
                                status = "available" if availability else "unavailable"
                                print(f"      ✅ {item['name']}: ${original_price} → ${new_price} ({status}) ({response_time:.0f}ms)")
                            else:
                                print(f"      ❌ {item['name']}: Update verification failed")
                                
                        else:
                            print(f"      ❌ {item['name']}: Update failed (HTTP {response.status_code})")
                            
                    except Exception as e:
                        print(f"      ❌ {item['name']}: Update error - {e}")
                        
                    await asyncio.sleep(0.05)
                    
                await asyncio.sleep(0.2)  # Delay between scenarios
                
            success_rate = updates_successful / total_updates if total_updates > 0 else 0
            
            if success_rate >= 0.8:
                APITestHelper.print_test_step(f"Pricing updates successful: {updates_successful}/{total_updates}", "SUCCESS")
                
                self.results.add_success("menu_workflow", "Dynamic pricing updates", {
                    "updates_successful": updates_successful,
                    "total_updates": total_updates,
                    "success_rate": success_rate
                })
                
                return True
            else:
                APITestHelper.print_test_step(f"Pricing updates incomplete: {success_rate:.1%} success rate", "FAILED")
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Pricing updates error: {e}", "FAILED")
            self.results.add_failure("menu_workflow", "Dynamic pricing updates", str(e))
            return False
            
    async def test_seasonal_menu_management(self) -> bool:
        """Test Phase 3: Seasonal menu management"""
        
        APITestHelper.print_test_header("Phase 3: Seasonal Menu Management", "🍂")
        
        try:
            # Create seasonal items
            seasonal_items = [
                {
                    "name": "Pumpkin Spice Latte",
                    "description": "Seasonal fall beverage with pumpkin and spices",
                    "price": 5.99,
                    "seasonal": True,
                    "season": "fall"
                },
                {
                    "name": "Summer Berry Salad",
                    "description": "Fresh mixed berries with mint and honey",
                    "price": 9.99,
                    "seasonal": True,
                    "season": "summer"
                },
                {
                    "name": "Winter Comfort Soup",
                    "description": "Hearty beef and vegetable soup",
                    "price": 8.99,
                    "seasonal": True,
                    "season": "winter"
                }
            ]
            
            # Find a category to add seasonal items to
            target_category = None
            if self.menu_data["categories"]:
                target_category = self.menu_data["categories"][0]  # Use first category
                
            if not target_category:
                APITestHelper.print_test_step("No categories available for seasonal items", "SKIPPED")
                return True
                
            APITestHelper.print_test_step("Creating seasonal menu items", "RUNNING")
            
            seasonal_created = 0
            
            for seasonal_item in seasonal_items:
                seasonal_item["category_id"] = target_category["id"]
                seasonal_item["is_available"] = True
                
                try:
                    start_time = time.time()
                    response = await self.client.post("/api/v1/menu/items", 
                                                    json=seasonal_item, headers=self.auth_headers)
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 201:
                        item = response.json()
                        self.menu_data["seasonal_items"].append(item)
                        seasonal_created += 1
                        
                        print(f"   ✅ Created seasonal item: {seasonal_item['name']} ({seasonal_item['season']}) ({response_time:.0f}ms)")
                        
                    elif response.status_code == 409:
                        print(f"   ⚠️ Seasonal item already exists: {seasonal_item['name']}")
                        seasonal_created += 1  # Count as success
                        
                    else:
                        print(f"   ❌ Failed to create seasonal item: {seasonal_item['name']}")
                        
                except Exception as e:
                    print(f"   ❌ Error creating seasonal item: {e}")
                    
                await asyncio.sleep(0.1)
                
            # Test seasonal item management - temporarily disable out-of-season items
            APITestHelper.print_test_step("Managing seasonal availability", "RUNNING")
            
            availability_updates = 0
            
            for item in self.menu_data["seasonal_items"]:
                # Simulate disabling winter items (out of season)
                if item.get("season") == "winter":
                    try:
                        update_data = {"is_available": False}
                        response = await self.client.patch(f"/api/v1/menu/items/{item['id']}", 
                                                         json=update_data, headers=self.auth_headers)
                        
                        if response.status_code == 200:
                            availability_updates += 1
                            print(f"   ✅ Disabled out-of-season item: {item['name']}")
                        else:
                            print(f"   ❌ Failed to disable item: {item['name']}")
                            
                    except Exception as e:
                        print(f"   ❌ Error updating availability: {e}")
                        
            if seasonal_created >= 2:  # At least 2 seasonal items created
                APITestHelper.print_test_step(f"Seasonal menu management successful", "SUCCESS")
                
                self.results.add_success("menu_workflow", "Seasonal menu management", {
                    "seasonal_items_created": seasonal_created,
                    "availability_updates": availability_updates
                })
                
                return True
            else:
                APITestHelper.print_test_step("Seasonal menu management incomplete", "FAILED")
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Seasonal menu management error: {e}", "FAILED")
            self.results.add_failure("menu_workflow", "Seasonal menu management", str(e))
            return False
            
    async def test_menu_analytics_simulation(self) -> bool:
        """Test Phase 4: Menu analytics and performance simulation"""
        
        APITestHelper.print_test_header("Phase 4: Menu Analytics Simulation", "📊")
        
        if not self.menu_data["items"]:
            APITestHelper.print_test_step("No menu items available for analytics", "SKIPPED")
            return True
            
        try:
            # Simulate menu performance analytics
            APITestHelper.print_test_step("Generating menu performance analytics", "RUNNING")
            
            total_items = len(self.menu_data["items"])
            categories = len(self.menu_data["categories"])
            
            # Calculate simulated metrics
            analytics = {
                "total_menu_items": total_items,
                "total_categories": categories,
                "seasonal_items": len(self.menu_data["seasonal_items"]),
                "average_price": 0,
                "price_range": {"min": float('inf'), "max": 0},
                "category_distribution": {},
                "availability_rate": 0
            }
            
            # Calculate price metrics
            available_items = 0
            total_price = 0
            
            for item in self.menu_data["items"]:
                price = float(item.get("price", 0))
                total_price += price
                
                # Update price range
                analytics["price_range"]["min"] = min(analytics["price_range"]["min"], price)
                analytics["price_range"]["max"] = max(analytics["price_range"]["max"], price)
                
                # Count available items
                if item.get("is_available", True):
                    available_items += 1
                    
            if total_items > 0:
                analytics["average_price"] = round(total_price / total_items, 2)
                analytics["availability_rate"] = round((available_items / total_items) * 100, 1)
                
            # Category distribution
            for category in self.menu_data["categories"]:
                category_items = [item for item in self.menu_data["items"] 
                                if item.get("category_id") == category["id"]]
                analytics["category_distribution"][category["name"]] = len(category_items)
                
            # Simulate revenue calculation
            simulated_daily_orders = total_items * 2  # Assume 2 orders per item per day
            analytics["estimated_daily_revenue"] = round(analytics["average_price"] * simulated_daily_orders, 2)
            
            # Display analytics
            print(f"   📊 Menu Analytics:")
            print(f"      Total Items: {analytics['total_menu_items']}")
            print(f"      Categories: {analytics['total_categories']}")
            print(f"      Seasonal Items: {analytics['seasonal_items']}")
            print(f"      Average Price: ${analytics['average_price']}")
            print(f"      Price Range: ${analytics['price_range']['min']:.2f} - ${analytics['price_range']['max']:.2f}")
            print(f"      Availability Rate: {analytics['availability_rate']}%")
            print(f"      Est. Daily Revenue: ${analytics['estimated_daily_revenue']}")
            
            print(f"\n   📈 Category Distribution:")
            for category, count in analytics["category_distribution"].items():
                percentage = round((count / total_items) * 100, 1) if total_items > 0 else 0
                print(f"      {category}: {count} items ({percentage}%)")
                
            # Validate analytics quality
            quality_checks = {
                "has_multiple_categories": categories >= 3,
                "reasonable_price_range": analytics["price_range"]["max"] - analytics["price_range"]["min"] > 5,
                "good_availability": analytics["availability_rate"] >= 80,
                "balanced_menu": all(count >= 2 for count in analytics["category_distribution"].values())
            }
            
            passed_checks = sum(quality_checks.values())
            total_checks = len(quality_checks)
            
            if passed_checks >= total_checks - 1:  # Allow one failing check
                APITestHelper.print_test_step(f"Menu analytics validation successful ({passed_checks}/{total_checks})", "SUCCESS")
                
                self.results.add_success("menu_workflow", "Menu analytics simulation", {
                    "total_items": total_items,
                    "categories": categories,
                    "average_price": analytics["average_price"],
                    "availability_rate": analytics["availability_rate"],
                    "quality_score": passed_checks / total_checks
                })
                
                return True
            else:
                APITestHelper.print_test_step(f"Menu analytics validation incomplete ({passed_checks}/{total_checks})", "FAILED")
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Menu analytics error: {e}", "FAILED")
            self.results.add_failure("menu_workflow", "Menu analytics simulation", str(e))
            return False
            
    async def test_public_menu_optimization(self) -> bool:
        """Test Phase 5: Public menu optimization and testing"""
        
        APITestHelper.print_test_header("Phase 5: Public Menu Optimization", "🌐")
        
        try:
            # Test public menu access and optimization
            APITestHelper.print_test_step("Testing public menu performance", "RUNNING")
            
            # Simulate multiple public menu requests
            response_times = []
            successful_requests = 0
            total_requests = 5
            
            for i in range(total_requests):
                try:
                    start_time = time.time()
                    response = await self.client.get("/api/v1/menu/public?restaurant_id=test-restaurant")
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code == 200:
                        successful_requests += 1
                        response_times.append(response_time)
                        
                        if i == 0:  # Analyze first response
                            menu_data = response.json()
                            categories_count = len(menu_data.get("categories", []))
                            items_count = sum(len(cat.get("items", [])) for cat in menu_data.get("categories", []))
                            
                            print(f"   🌐 Public Menu Structure:")
                            print(f"      Categories: {categories_count}")
                            print(f"      Total Items: {items_count}")
                            print(f"      Response Time: {response_time:.0f}ms")
                            
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    print(f"   ❌ Public menu request {i+1} failed: {e}")
                    
            # Analyze performance
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
                min_response_time = min(response_times)
                max_response_time = max(response_times)
                
                print(f"\n   ⚡ Performance Analysis:")
                print(f"      Successful Requests: {successful_requests}/{total_requests}")
                print(f"      Average Response Time: {avg_response_time:.0f}ms")
                print(f"      Min Response Time: {min_response_time:.0f}ms")
                print(f"      Max Response Time: {max_response_time:.0f}ms")
                
                # Performance thresholds
                performance_good = (
                    successful_requests >= total_requests * 0.8 and  # 80% success rate
                    avg_response_time <= 500  # Under 500ms average
                )
                
                if performance_good:
                    APITestHelper.print_test_step("Public menu optimization successful", "SUCCESS")
                    
                    self.results.add_success("menu_workflow", "Public menu optimization", {
                        "successful_requests": successful_requests,
                        "total_requests": total_requests,
                        "avg_response_time": avg_response_time,
                        "performance_good": True
                    })
                    
                    return True
                else:
                    APITestHelper.print_test_step("Public menu performance needs optimization", "FAILED")
                    return False
            else:
                APITestHelper.print_test_step("No successful public menu responses", "FAILED")
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Public menu optimization error: {e}", "FAILED")
            self.results.add_failure("menu_workflow", "Public menu optimization", str(e))
            return False
            
    def print_workflow_summary(self):
        """Print comprehensive menu workflow summary"""
        
        APITestHelper.print_test_header("Menu Management Workflow Summary", "📊")
        
        print(f"Total Tests: {self.results.total_tests}")
        print(f"Passed: {self.results.passed_tests}")
        print(f"Failed: {self.results.failed_tests}")
        print(f"Success Rate: {self.results.success_rate:.1f}%")
        
        # Menu statistics
        print(f"\n🍽️ Menu Statistics:")
        print(f"   Categories Created: {len(self.menu_data['categories'])}")
        print(f"   Regular Items: {len(self.menu_data['items'])}")
        print(f"   Seasonal Items: {len(self.menu_data['seasonal_items'])}")
        print(f"   Total Menu Items: {len(self.menu_data['items']) + len(self.menu_data['seasonal_items'])}")
        
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
                    print(f"   • {result.test_name} - {result.error_message}")
                    
    async def run_complete_menu_workflow(self) -> bool:
        """Run the complete menu management workflow"""
        
        print("🍽️ RMS Menu Management Workflow")
        print("="*50)
        print("End-to-end testing of complete menu lifecycle management")
        print()
        
        start_time = time.time()
        
        try:
            # Setup authentication
            if not await self.setup_authentication():
                return False
                
            # Run all workflow phases
            workflow_phases = [
                ("Comprehensive Menu Creation", self.test_comprehensive_menu_creation),
                ("Dynamic Pricing Updates", self.test_dynamic_pricing_updates),
                ("Seasonal Menu Management", self.test_seasonal_menu_management),
                ("Menu Analytics Simulation", self.test_menu_analytics_simulation),
                ("Public Menu Optimization", self.test_public_menu_optimization)
            ]
            
            overall_success = True
            completed_phases = 0
            
            for phase_name, phase_func in workflow_phases:
                try:
                    print(f"\n{'='*20} {phase_name} {'='*20}")
                    success = await phase_func()
                    
                    if success:
                        completed_phases += 1
                    else:
                        overall_success = False
                        # Continue with remaining phases
                        
                except Exception as e:
                    APITestHelper.print_test_step(f"{phase_name} failed with error: {e}", "FAILED")
                    self.results.add_failure("menu_workflow", phase_name, str(e))
                    overall_success = False
                    
                # Small delay between phases
                await asyncio.sleep(0.5)
                
            # Calculate execution time
            self.results.execution_time = time.time() - start_time
            
            # Print summary
            self.print_workflow_summary()
            
            print(f"\n🎯 Workflow Results:")
            print(f"   Completed Phases: {completed_phases}/{len(workflow_phases)}")
            print(f"   Overall Success: {'✅' if overall_success else '❌'}")
            print(f"   Execution Time: {self.results.execution_time:.2f} seconds")
            
            return overall_success
            
        except KeyboardInterrupt:
            print("\n⚠️ Menu workflow interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Menu workflow failed: {e}")
            return False
        finally:
            await self.client.close()


async def main():
    """Main entry point for menu management workflow testing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Test RMS menu management workflow")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    workflow = MenuManagementWorkflow(args.base_url)
    
    try:
        success = await workflow.run_complete_menu_workflow()
        
        if success:
            print(f"\n🎉 Menu management workflow completed successfully!")
            print(f"   Complete menu lifecycle operations are working correctly")
        else:
            print(f"\n⚠️ Menu management workflow had some issues")
            print(f"   Review the results above for details")
            
    except Exception as e:
        print(f"❌ Menu workflow testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())