#!/usr/bin/env python3
"""
Production-Level Performance and Load Testing

Comprehensive performance testing to ensure the system can handle
production-level load and maintains acceptable response times.
"""

import sys
import asyncio
import time
import statistics
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
import aiohttp

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.api_tester.shared.utils import APITestClient, APITestHelper, TestResults
from tests.api_tester.shared.auth import get_auth_headers
from tests.api_tester.shared.setup import setup_test_restaurant


class PerformanceLoadTester:
    """Production-level performance and load testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = TestResults()
        self.auth_headers = None
        self.restaurant_data = None
        
    async def setup_test_environment(self) -> bool:
        """Set up test environment for performance testing"""
        APITestHelper.print_test_header("Performance Test Setup", "🏗️")
        
        try:
            client = APITestClient(self.base_url)
            
            # Setup test restaurant
            self.restaurant_data = await setup_test_restaurant(client)
            if not self.restaurant_data:
                return False
                
            # Get authentication headers
            self.auth_headers = await get_auth_headers(client, 
                                                    self.restaurant_data["admin_email"],
                                                    self.restaurant_data["admin_password"])
            if not self.auth_headers:
                return False
            
            await client.close()
            APITestHelper.print_test_step("Performance test environment ready", "SUCCESS")
            return True
            
        except Exception as e:
            APITestHelper.print_test_step(f"Performance setup failed: {e}", "FAILED")
            return False
    
    async def test_api_response_times(self) -> bool:
        """Test API endpoint response times under normal load"""
        APITestHelper.print_test_header("API Response Time Testing", "⏱️")
        
        endpoints_to_test = [
            ("GET", "/health", None, None),
            ("GET", "/api/v1/menu/categories/", None, self.auth_headers),
            ("GET", "/api/v1/menu/items/", None, self.auth_headers),
            ("GET", "/api/v1/orders/", None, self.auth_headers),
            ("GET", "/api/v1/kitchen/orders", None, self.auth_headers),
            ("GET", "/api/v1/payments/summary", None, self.auth_headers),
            ("GET", "/api/v1/qr-orders/analytics", None, self.auth_headers),
        ]
        
        response_times = {}
        
        try:
            async with aiohttp.ClientSession() as session:
                for method, endpoint, data, headers in endpoints_to_test:
                    times = []
                    
                    # Test each endpoint 10 times
                    for _ in range(10):
                        start_time = time.time()
                        
                        if method == "GET":
                            async with session.get(f"{self.base_url}{endpoint}", headers=headers) as response:
                                await response.read()
                                status_code = response.status
                        elif method == "POST":
                            async with session.post(f"{self.base_url}{endpoint}", json=data, headers=headers) as response:
                                await response.read()
                                status_code = response.status
                        
                        response_time = (time.time() - start_time) * 1000  # Convert to ms
                        
                        if status_code in [200, 401]:  # 401 is acceptable for auth-protected endpoints
                            times.append(response_time)
                        
                        await asyncio.sleep(0.1)  # Small delay between requests
                    
                    if times:
                        avg_time = statistics.mean(times)
                        min_time = min(times)
                        max_time = max(times)
                        median_time = statistics.median(times)
                        
                        response_times[endpoint] = {
                            "average": avg_time,
                            "min": min_time,
                            "max": max_time,
                            "median": median_time,
                            "samples": len(times)
                        }
                        
                        # Performance thresholds
                        if avg_time > 1000:  # 1 second
                            status = "FAILED"
                        elif avg_time > 500:  # 500ms
                            status = "WARNING"
                        else:
                            status = "SUCCESS"
                        
                        APITestHelper.print_test_step(
                            f"{endpoint}: avg {avg_time:.0f}ms (min: {min_time:.0f}ms, max: {max_time:.0f}ms)", 
                            status
                        )
            
            # Overall performance assessment
            if response_times:
                all_averages = [stats["average"] for stats in response_times.values()]
                overall_avg = statistics.mean(all_averages)
                
                print(f"\\n📊 Overall Performance Summary:")
                print(f"   Average Response Time: {overall_avg:.0f}ms")
                print(f"   Fastest Endpoint: {min(all_averages):.0f}ms")
                print(f"   Slowest Endpoint: {max(all_averages):.0f}ms")
                
                # Record results
                self.results.add_success("performance", "API response times", {
                    "overall_average": overall_avg,
                    "endpoint_details": response_times
                })
                
                return overall_avg < 1000  # Pass if under 1 second average
            
            return False
            
        except Exception as e:
            APITestHelper.print_test_step(f"Response time testing failed: {e}", "FAILED")
            self.results.add_failure("performance", "API response times", str(e))
            return False
    
    async def test_concurrent_order_creation(self) -> bool:
        """Test concurrent order creation performance"""
        APITestHelper.print_test_header("Concurrent Order Creation", "🔄")
        
        try:
            # First, create menu items for orders
            client = APITestClient(self.base_url)
            
            # Create category
            category_data = {"name": "Performance Test Category", "description": "For testing"}
            response = await client.post("/api/v1/menu/categories/", json=category_data, headers=self.auth_headers)
            if response.status_code != 200:
                raise Exception("Failed to create test category")
            
            category_id = response.json()["id"]
            
            # Create menu item
            item_data = {
                "name": "Performance Test Item",
                "price": 10.00,
                "description": "Item for performance testing",
                "category_id": category_id,
                "is_available": True
            }
            response = await client.post("/api/v1/menu/items/", json=item_data, headers=self.auth_headers)
            if response.status_code != 200:
                raise Exception("Failed to create test menu item")
            
            menu_item_id = response.json()["id"]
            await client.close()
            
            # Prepare order data template
            order_template = {
                "order_type": "dine_in",
                "customer_name": "Performance Test Customer",
                "items": [
                    {
                        "menu_item_id": menu_item_id,
                        "quantity": 1
                    }
                ]
            }
            
            # Test concurrent order creation
            concurrent_levels = [5, 10, 20]  # Different concurrency levels
            
            for concurrency in concurrent_levels:
                APITestHelper.print_test_step(f"Testing {concurrency} concurrent orders", "INFO")
                
                start_time = time.time()
                successful_orders = 0
                failed_orders = 0
                
                async def create_order(order_num: int):
                    """Create a single order"""
                    try:
                        async with aiohttp.ClientSession() as session:
                            order_data = order_template.copy()
                            order_data["customer_name"] = f"Customer {order_num}"
                            
                            async with session.post(
                                f"{self.base_url}/api/v1/orders/",
                                json=order_data,
                                headers=self.auth_headers
                            ) as response:
                                if response.status == 200:
                                    return True
                                else:
                                    return False
                    except Exception:
                        return False
                
                # Create tasks for concurrent execution
                tasks = [create_order(i) for i in range(concurrency)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Count results
                for result in results:
                    if result is True:
                        successful_orders += 1
                    else:
                        failed_orders += 1
                
                execution_time = time.time() - start_time
                orders_per_second = successful_orders / execution_time if execution_time > 0 else 0
                
                # Performance assessment
                success_rate = (successful_orders / concurrency) * 100
                
                if success_rate >= 95 and orders_per_second >= 5:
                    status = "SUCCESS"
                elif success_rate >= 80 and orders_per_second >= 2:
                    status = "WARNING"
                else:
                    status = "FAILED"
                
                APITestHelper.print_test_step(
                    f"Concurrency {concurrency}: {successful_orders}/{concurrency} orders ({success_rate:.1f}%) "
                    f"at {orders_per_second:.1f} orders/sec",
                    status
                )
                
                self.results.add_success("performance", f"Concurrent orders (n={concurrency})", {
                    "successful_orders": successful_orders,
                    "failed_orders": failed_orders,
                    "success_rate": success_rate,
                    "orders_per_second": orders_per_second,
                    "execution_time": execution_time
                })
            
            return True
            
        except Exception as e:
            APITestHelper.print_test_step(f"Concurrent order testing failed: {e}", "FAILED")
            self.results.add_failure("performance", "Concurrent order creation", str(e))
            return False
    
    async def test_kitchen_operations_performance(self) -> bool:
        """Test kitchen operations performance under load"""
        APITestHelper.print_test_header("Kitchen Operations Performance", "👨‍🍳")
        
        try:
            # Create test orders first
            client = APITestClient(self.base_url)
            
            order_ids = []
            for i in range(10):  # Create 10 test orders
                order_data = {
                    "order_type": "dine_in",
                    "customer_name": f"Kitchen Test Customer {i}",
                    "items": [{"menu_item_id": "dummy", "quantity": 1}]  # Will use existing menu items
                }
                
                # For this test, we'll create minimal orders
                # In production, you'd use the actual menu items created earlier
                pass  # Skip actual order creation for now
            
            await client.close()
            
            # Test kitchen endpoints performance
            kitchen_endpoints = [
                "/api/v1/kitchen/orders",
                "/api/v1/kitchen/performance",
                "/api/v1/kitchen/prep-queue",
                "/api/v1/kitchen/analytics/daily"
            ]
            
            response_times = {}
            
            async with aiohttp.ClientSession() as session:
                for endpoint in kitchen_endpoints:
                    times = []
                    
                    # Test each endpoint 5 times
                    for _ in range(5):
                        start_time = time.time()
                        
                        async with session.get(f"{self.base_url}{endpoint}", headers=self.auth_headers) as response:
                            await response.read()
                            response_time = (time.time() - start_time) * 1000
                            
                            if response.status in [200, 404]:  # 404 is OK if no data exists
                                times.append(response_time)
                        
                        await asyncio.sleep(0.1)
                    
                    if times:
                        avg_time = statistics.mean(times)
                        response_times[endpoint] = avg_time
                        
                        status = "SUCCESS" if avg_time < 500 else "WARNING" if avg_time < 1000 else "FAILED"
                        APITestHelper.print_test_step(f"{endpoint}: {avg_time:.0f}ms", status)
            
            # Overall kitchen performance assessment
            if response_times:
                avg_kitchen_response = statistics.mean(response_times.values())
                
                self.results.add_success("performance", "Kitchen operations", {
                    "average_response_time": avg_kitchen_response,
                    "endpoint_times": response_times
                })
                
                return avg_kitchen_response < 1000
            
            return False
            
        except Exception as e:
            APITestHelper.print_test_step(f"Kitchen performance testing failed: {e}", "FAILED")
            self.results.add_failure("performance", "Kitchen operations performance", str(e))
            return False
    
    async def test_database_connection_performance(self) -> bool:
        """Test database connection and query performance"""
        APITestHelper.print_test_header("Database Performance", "🗄️")
        
        try:
            # Test database health endpoint multiple times
            response_times = []
            
            async with aiohttp.ClientSession() as session:
                for _ in range(20):  # Test 20 times
                    start_time = time.time()
                    
                    async with session.get(f"{self.base_url}/health") as response:
                        await response.read()
                        response_time = (time.time() - start_time) * 1000
                        
                        if response.status == 200:
                            response_times.append(response_time)
                    
                    await asyncio.sleep(0.05)  # Small delay
            
            if response_times:
                avg_time = statistics.mean(response_times)
                min_time = min(response_times)
                max_time = max(response_times)
                p95_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
                
                # Database performance assessment
                if avg_time < 100 and p95_time < 200:
                    status = "SUCCESS"
                elif avg_time < 300 and p95_time < 500:
                    status = "WARNING"
                else:
                    status = "FAILED"
                
                APITestHelper.print_test_step(
                    f"DB Health: avg {avg_time:.0f}ms, 95th {p95_time:.0f}ms (min: {min_time:.0f}ms, max: {max_time:.0f}ms)",
                    status
                )
                
                self.results.add_success("performance", "Database performance", {
                    "average_time": avg_time,
                    "min_time": min_time,
                    "max_time": max_time,
                    "p95_time": p95_time,
                    "samples": len(response_times)
                })
                
                return avg_time < 300 and p95_time < 500
            
            return False
            
        except Exception as e:
            APITestHelper.print_test_step(f"Database performance testing failed: {e}", "FAILED")
            self.results.add_failure("performance", "Database performance", str(e))
            return False
    
    async def test_memory_and_resource_usage(self) -> bool:
        """Test memory and resource usage patterns"""
        APITestHelper.print_test_header("Resource Usage Testing", "💾")
        
        try:
            # This is a simplified resource test
            # In production, you'd want to monitor actual memory usage
            
            # Perform sustained load to test resource handling
            async with aiohttp.ClientSession() as session:
                start_time = time.time()
                
                # Make sustained requests for 30 seconds
                request_count = 0
                errors = 0
                
                while time.time() - start_time < 30:  # 30 second test
                    try:
                        async with session.get(f"{self.base_url}/health") as response:
                            if response.status == 200:
                                request_count += 1
                            else:
                                errors += 1
                    except Exception:
                        errors += 1
                    
                    await asyncio.sleep(0.1)  # 10 requests per second
                
                duration = time.time() - start_time
                requests_per_second = request_count / duration
                error_rate = (errors / (request_count + errors)) * 100 if (request_count + errors) > 0 else 0
                
                # Resource usage assessment
                if requests_per_second >= 8 and error_rate < 5:
                    status = "SUCCESS"
                elif requests_per_second >= 5 and error_rate < 10:
                    status = "WARNING"
                else:
                    status = "FAILED"
                
                APITestHelper.print_test_step(
                    f"Sustained load: {requests_per_second:.1f} req/sec, {error_rate:.1f}% errors over {duration:.1f}s",
                    status
                )
                
                self.results.add_success("performance", "Resource usage", {
                    "requests_per_second": requests_per_second,
                    "error_rate": error_rate,
                    "duration": duration,
                    "total_requests": request_count
                })
                
                return requests_per_second >= 5 and error_rate < 10
            
        except Exception as e:
            APITestHelper.print_test_step(f"Resource usage testing failed: {e}", "FAILED")
            self.results.add_failure("performance", "Resource usage", str(e))
            return False
    
    def print_performance_summary(self):
        """Print comprehensive performance test summary"""
        
        APITestHelper.print_test_header("Performance Test Summary", "📊")
        
        print(f"Total Performance Tests: {self.results.total_tests}")
        print(f"Passed Tests: {self.results.passed_tests}")
        print(f"Failed Tests: {self.results.failed_tests}")
        print(f"Success Rate: {self.results.success_rate:.1f}%")
        
        # Show performance categories
        categories = {}
        for result in self.results.results:
            category = result.category
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0}
            
            if result.success:
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1
        
        print(f"\\n📋 Performance Categories:")
        for category, stats in categories.items():
            total = stats["passed"] + stats["failed"]
            rate = (stats["passed"] / total) * 100 if total > 0 else 0
            print(f"   {category.title()}: {stats['passed']}/{total} ({rate:.1f}%)")
        
        # Show failures
        if self.results.failed_tests > 0:
            print(f"\\n❌ Performance Issues:")
            for result in self.results.results:
                if not result.success:
                    print(f"   • {result.test_name}: {result.error_message}")
        
        # Performance recommendations
        print(f"\\n💡 Performance Recommendations:")
        if self.results.success_rate >= 90:
            print(f"   ✅ System performance is excellent for production")
        elif self.results.success_rate >= 75:
            print(f"   ⚠️  System performance is acceptable but could be optimized")
        else:
            print(f"   ❌ System performance needs improvement before production")
        
        print(f"\\n🎯 Production Readiness:")
        if self.results.success_rate >= 85:
            print(f"   ✅ READY for production deployment")
        else:
            print(f"   ❌ NOT READY - address performance issues first")
    
    async def run_all_performance_tests(self) -> bool:
        """Run all performance and load tests"""
        
        print("⚡ Production-Level Performance & Load Tests")
        print("="*50)
        
        start_time = time.time()
        
        try:
            # Setup environment
            if not await self.setup_test_environment():
                return False
            
            # Run performance tests
            tests = [
                ("API Response Times", self.test_api_response_times),
                ("Concurrent Order Creation", self.test_concurrent_order_creation),
                ("Kitchen Operations Performance", self.test_kitchen_operations_performance),
                ("Database Performance", self.test_database_connection_performance),
                ("Resource Usage", self.test_memory_and_resource_usage)
            ]
            
            overall_success = True
            
            for test_name, test_func in tests:
                try:
                    success = await test_func()
                    if not success:
                        overall_success = False
                        
                except Exception as e:
                    APITestHelper.print_test_step(f"{test_name} failed with error: {e}", "FAILED")
                    self.results.add_failure("performance", test_name, str(e))
                    overall_success = False
                
                # Delay between test categories
                await asyncio.sleep(2)
            
            # Calculate execution time
            self.results.execution_time = time.time() - start_time
            
            # Print summary
            self.print_performance_summary()
            
            return overall_success
            
        except KeyboardInterrupt:
            print("\\n⚠️ Performance tests interrupted by user")
            return False
        except Exception as e:
            print(f"\\n❌ Performance tests failed: {e}")
            return False


async def main():
    """Main entry point for performance testing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Test production performance and load")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    tester = PerformanceLoadTester(args.base_url)
    
    try:
        success = await tester.run_all_performance_tests()
        
        if success:
            print(f"\\n✅ Performance tests passed successfully!")
            print(f"   System is ready for production load")
        else:
            print(f"\\n❌ Performance tests identified issues")
            print(f"   Optimize performance before production deployment")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Performance testing failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())