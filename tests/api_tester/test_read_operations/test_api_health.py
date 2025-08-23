#!/usr/bin/env python3
"""
Test API Health and Connectivity

Comprehensive health checks for RMS API endpoints.
Tests connectivity, authentication, and basic API functionality.
"""

import sys
import asyncio
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.api_tester.shared.utils import APITestClient, APITestHelper, TestResults
from tests.api_tester.shared.auth import get_auth_headers, test_authentication_flow


class APIHealthTester:
    """Comprehensive API health and connectivity testing"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.results = TestResults()
        
    async def test_basic_connectivity(self) -> bool:
        """Test basic API server connectivity"""
        
        APITestHelper.print_test_header("Basic API Connectivity", "🌐")
        
        try:
            start_time = time.time()
            response = await self.client.get("/")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code in [200, 404]:  # 404 is OK for root endpoint
                APITestHelper.print_test_step(f"API server is responding ({response_time:.0f}ms)", "SUCCESS")
                self.results.add_success("connectivity", "Basic server connectivity", {
                    "response_time": response_time,
                    "status_code": response.status_code
                })
                return True
            else:
                APITestHelper.print_test_step(f"API server error: HTTP {response.status_code}", "FAILED")
                self.results.add_failure("connectivity", "Basic server connectivity", 
                                       f"HTTP {response.status_code}", response.status_code)
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Cannot connect to API: {e}", "FAILED")
            self.results.add_failure("connectivity", "Basic server connectivity", str(e))
            return False
            
    async def test_health_endpoint(self) -> bool:
        """Test dedicated health endpoint"""
        
        APITestHelper.print_test_header("Health Endpoint", "🏥")
        
        try:
            start_time = time.time()
            response = await self.client.get("/health")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                health_data = response.json()
                
                APITestHelper.print_test_step(f"Health endpoint responding ({response_time:.0f}ms)", "SUCCESS")
                
                # Validate health response structure
                if health_data and isinstance(health_data, dict):
                    status = health_data.get("status", "unknown")
                    APITestHelper.print_test_step(f"Health status: {status}", "SUCCESS")
                    
                    # Print additional health details if available
                    if "version" in health_data:
                        print(f"   🏷️  Version: {health_data['version']}")
                    if "timestamp" in health_data:
                        print(f"   🕒 Timestamp: {health_data['timestamp']}")
                    if "uptime" in health_data:
                        print(f"   ⏱️  Uptime: {health_data['uptime']}")
                        
                else:
                    APITestHelper.print_test_step("Health endpoint returned invalid data", "FAILED")
                    
                self.results.add_success("health", "Health endpoint", {
                    "response_time": response_time,
                    "status": health_data.get("status") if health_data else None,
                    "data": health_data
                })
                return True
                
            else:
                APITestHelper.print_test_step(f"Health endpoint failed: HTTP {response.status_code}", "FAILED")
                self.results.add_failure("health", "Health endpoint", 
                                       f"HTTP {response.status_code}", response.status_code)
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Health endpoint error: {e}", "FAILED")
            self.results.add_failure("health", "Health endpoint", str(e))
            return False
            
    async def test_database_health(self) -> bool:
        """Test database connectivity health"""
        
        APITestHelper.print_test_header("Database Health", "🗄️")
        
        try:
            start_time = time.time()
            response = await self.client.get("/health/db")
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                db_health = response.json()
                
                APITestHelper.print_test_step(f"Database health check passed ({response_time:.0f}ms)", "SUCCESS")
                
                if db_health and isinstance(db_health, dict):
                    db_status = db_health.get("database_status", "unknown")
                    print(f"   📊 Database Status: {db_status}")
                    
                    if "connection_pool" in db_health:
                        pool_info = db_health["connection_pool"]
                        print(f"   🏊 Pool Size: {pool_info.get('size', 'N/A')}")
                        print(f"   🔗 Active Connections: {pool_info.get('active', 'N/A')}")
                        
                self.results.add_success("health", "Database health", {
                    "response_time": response_time,
                    "status": db_health.get("database_status") if db_health else None
                })
                return True
                
            elif response.status_code == 404:
                APITestHelper.print_test_step("Database health endpoint not found (may not be implemented)", "SKIPPED")
                return True  # Not a failure if not implemented
                
            else:
                APITestHelper.print_test_step(f"Database health failed: HTTP {response.status_code}", "FAILED")
                self.results.add_failure("health", "Database health", 
                                       f"HTTP {response.status_code}", response.status_code)
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"Database health error: {e}", "FAILED")
            self.results.add_failure("health", "Database health", str(e))
            return False
            
    async def test_openapi_documentation(self) -> bool:
        """Test OpenAPI documentation availability"""
        
        APITestHelper.print_test_header("API Documentation", "📚")
        
        endpoints_to_test = [
            ("/docs", "Swagger UI"),
            ("/redoc", "ReDoc Documentation"),
            ("/openapi.json", "OpenAPI Schema")
        ]
        
        all_success = True
        
        for endpoint, description in endpoints_to_test:
            try:
                start_time = time.time()
                response = await self.client.get(endpoint)
                response_time = (time.time() - start_time) * 1000
                
                if response.status_code == 200:
                    APITestHelper.print_test_step(f"{description} available ({response_time:.0f}ms)", "SUCCESS")
                    
                    # For OpenAPI schema, validate it's valid JSON
                    if endpoint == "/openapi.json":
                        try:
                            openapi_data = response.json()
                            if openapi_data and "openapi" in openapi_data:
                                version = openapi_data.get("openapi", "unknown")
                                title = openapi_data.get("info", {}).get("title", "Unknown")
                                print(f"   📄 OpenAPI Version: {version}")
                                print(f"   📋 API Title: {title}")
                            else:
                                APITestHelper.print_test_step("Invalid OpenAPI schema", "FAILED")
                                all_success = False
                        except Exception:
                            APITestHelper.print_test_step("OpenAPI schema not valid JSON", "FAILED")
                            all_success = False
                            
                    self.results.add_success("documentation", description, {
                        "endpoint": endpoint,
                        "response_time": response_time
                    })
                    
                else:
                    APITestHelper.print_test_step(f"{description} not available: HTTP {response.status_code}", "FAILED")
                    self.results.add_failure("documentation", description, 
                                           f"HTTP {response.status_code}", response.status_code)
                    all_success = False
                    
                # Small delay between requests
                await asyncio.sleep(0.1)
                
            except Exception as e:
                APITestHelper.print_test_step(f"{description} error: {e}", "FAILED")
                self.results.add_failure("documentation", description, str(e))
                all_success = False
                
        return all_success
        
    async def test_authentication_endpoints(self) -> bool:
        """Test authentication endpoint availability and basic functionality"""
        
        APITestHelper.print_test_header("Authentication Endpoints", "🔐")
        
        # Test authentication flow
        auth_success = await test_authentication_flow(self.client)
        
        if auth_success:
            self.results.add_success("authentication", "Authentication flow", {
                "login_endpoint": "/auth/login",
                "user_info_endpoint": "/auth/me"
            })
        else:
            self.results.add_failure("authentication", "Authentication flow", 
                                   "Authentication test failed")
            
        # Test individual auth endpoints
        auth_endpoints = [
            "/auth/login",
            "/auth/logout", 
            "/auth/refresh",
            "/auth/me"
        ]
        
        headers = await get_auth_headers(self.client)
        endpoint_success = True
        
        for endpoint in auth_endpoints:
            try:
                # For most endpoints, we expect 405 (Method Not Allowed) for GET requests
                response = await self.client.get(endpoint)
                
                if response.status_code in [200, 401, 405]:  # Expected responses
                    APITestHelper.print_test_step(f"Auth endpoint {endpoint} exists", "SUCCESS")
                    self.results.add_success("authentication", f"Endpoint {endpoint}", {
                        "endpoint": endpoint,
                        "status_code": response.status_code
                    })
                else:
                    APITestHelper.print_test_step(f"Auth endpoint {endpoint} unexpected response: {response.status_code}", "FAILED")
                    self.results.add_failure("authentication", f"Endpoint {endpoint}", 
                                           f"HTTP {response.status_code}", response.status_code)
                    endpoint_success = False
                    
                await asyncio.sleep(0.1)
                
            except Exception as e:
                APITestHelper.print_test_step(f"Auth endpoint {endpoint} error: {e}", "FAILED")
                self.results.add_failure("authentication", f"Endpoint {endpoint}", str(e))
                endpoint_success = False
                
        return auth_success and endpoint_success
        
    async def test_cors_headers(self) -> bool:
        """Test CORS headers are properly configured"""
        
        APITestHelper.print_test_header("CORS Configuration", "🌍")
        
        try:
            # Test preflight request
            response = await self.client.get("/health")
            
            if response.status_code == 200:
                headers = response.headers
                
                # Check for CORS headers
                cors_headers = {
                    "Access-Control-Allow-Origin": headers.get("access-control-allow-origin"),
                    "Access-Control-Allow-Methods": headers.get("access-control-allow-methods"),
                    "Access-Control-Allow-Headers": headers.get("access-control-allow-headers")
                }
                
                cors_configured = any(value for value in cors_headers.values())
                
                if cors_configured:
                    APITestHelper.print_test_step("CORS headers detected", "SUCCESS")
                    for header, value in cors_headers.items():
                        if value:
                            print(f"   {header}: {value}")
                            
                    self.results.add_success("cors", "CORS configuration", cors_headers)
                else:
                    APITestHelper.print_test_step("No CORS headers found (may be intentional)", "SKIPPED")
                    
                return True
                
            else:
                APITestHelper.print_test_step("Cannot test CORS due to health endpoint failure", "FAILED")
                return False
                
        except Exception as e:
            APITestHelper.print_test_step(f"CORS test error: {e}", "FAILED")
            self.results.add_failure("cors", "CORS configuration", str(e))
            return False
            
    async def test_response_times(self) -> bool:
        """Test API response time performance"""
        
        APITestHelper.print_test_header("Response Time Performance", "⚡")
        
        test_endpoints = [
            "/health",
            "/docs",
            "/openapi.json"
        ]
        
        all_times = []
        performance_issues = []
        
        for endpoint in test_endpoints:
            try:
                # Test multiple times for average
                times = []
                for _ in range(3):
                    start_time = time.time()
                    response = await self.client.get(endpoint)
                    response_time = (time.time() - start_time) * 1000
                    
                    if response.status_code in [200, 404]:
                        times.append(response_time)
                        
                    await asyncio.sleep(0.1)
                
                if times:
                    avg_time = sum(times) / len(times)
                    min_time = min(times)
                    max_time = max(times)
                    
                    all_times.extend(times)
                    
                    # Performance thresholds
                    if avg_time > 2000:  # 2 seconds
                        status = "FAILED"
                        performance_issues.append(f"{endpoint}: {avg_time:.0f}ms")
                    elif avg_time > 1000:  # 1 second
                        status = "WARNING"
                    else:
                        status = "SUCCESS"
                        
                    APITestHelper.print_test_step(
                        f"{endpoint}: avg {avg_time:.0f}ms (min: {min_time:.0f}ms, max: {max_time:.0f}ms)", 
                        status
                    )
                    
                    self.results.add_success("performance", f"Response time {endpoint}", {
                        "endpoint": endpoint,
                        "average_ms": avg_time,
                        "min_ms": min_time,
                        "max_ms": max_time
                    })
                    
            except Exception as e:
                APITestHelper.print_test_step(f"Performance test failed for {endpoint}: {e}", "FAILED")
                self.results.add_failure("performance", f"Response time {endpoint}", str(e))
                
        # Overall performance summary\n        if all_times:\n            overall_avg = sum(all_times) / len(all_times)\n            print(f\"\\n📊 Overall Performance Summary:\")\n            print(f\"   Average Response Time: {overall_avg:.0f}ms\")\n            print(f\"   Fastest Response: {min(all_times):.0f}ms\")\n            print(f\"   Slowest Response: {max(all_times):.0f}ms\")\n            \n            if performance_issues:\n                print(f\"\\n⚠️  Performance Issues Detected:\")\n                for issue in performance_issues:\n                    print(f\"   • {issue}\")\n                return False\n            else:\n                print(f\"   ✅ All endpoints responding within acceptable limits\")\n                return True\n        else:\n            return False\n            \n    def print_health_summary(self):\n        \"\"\"Print comprehensive health test summary\"\"\"\n        \n        APITestHelper.print_test_header(\"Health Test Summary\", \"📊\")\n        \n        print(f\"Total Tests: {self.results.total_tests}\")\n        print(f\"Passed: {self.results.passed_tests}\")\n        print(f\"Failed: {self.results.failed_tests}\")\n        print(f\"Success Rate: {self.results.success_rate:.1f}%\")\n        \n        # Group results by category\n        categories = {}\n        for result in self.results.results:\n            category = result.category\n            if category not in categories:\n                categories[category] = {\"passed\": 0, \"failed\": 0}\n                \n            if result.success:\n                categories[category][\"passed\"] += 1\n            else:\n                categories[category][\"failed\"] += 1\n                \n        print(f\"\\n📋 Results by Category:\")\n        for category, stats in categories.items():\n            total = stats[\"passed\"] + stats[\"failed\"]\n            rate = (stats[\"passed\"] / total) * 100 if total > 0 else 0\n            print(f\"   {category.title()}: {stats['passed']}/{total} ({rate:.1f}%)\")\n            \n        # Show failures if any\n        if self.results.failed_tests > 0:\n            print(f\"\\n❌ Failed Tests:\")\n            for result in self.results.results:\n                if not result.success:\n                    print(f\"   • {result.category}: {result.test_name} - {result.error_message}\")\n                    \n        # Performance summary\n        perf_results = [r for r in self.results.results if r.category == \"performance\" and r.response_time > 0]\n        if perf_results:\n            avg_response_time = sum(r.response_time for r in perf_results) / len(perf_results)\n            print(f\"\\n⚡ Average Response Time: {avg_response_time:.0f}ms\")\n            \n    async def run_comprehensive_health_tests(self) -> bool:\n        \"\"\"Run all health tests\"\"\"\n        \n        print(\"🏥 RMS API Health & Connectivity Tests\")\n        print(\"=\"*50)\n        \n        start_time = time.time()\n        \n        try:\n            # Run all health tests\n            tests = [\n                (\"Basic Connectivity\", self.test_basic_connectivity),\n                (\"Health Endpoint\", self.test_health_endpoint), \n                (\"Database Health\", self.test_database_health),\n                (\"API Documentation\", self.test_openapi_documentation),\n                (\"Authentication\", self.test_authentication_endpoints),\n                (\"CORS Configuration\", self.test_cors_headers),\n                (\"Response Times\", self.test_response_times)\n            ]\n            \n            overall_success = True\n            \n            for test_name, test_func in tests:\n                try:\n                    success = await test_func()\n                    if not success:\n                        overall_success = False\n                        \n                except Exception as e:\n                    APITestHelper.print_test_step(f\"{test_name} failed with error: {e}\", \"FAILED\")\n                    self.results.add_failure(\"general\", test_name, str(e))\n                    overall_success = False\n                    \n                # Small delay between test categories\n                await asyncio.sleep(0.5)\n                \n            # Calculate execution time\n            self.results.execution_time = time.time() - start_time\n            \n            # Print summary\n            self.print_health_summary()\n            \n            return overall_success\n            \n        except KeyboardInterrupt:\n            print(\"\\n⚠️  Health tests interrupted by user\")\n            return False\n        except Exception as e:\n            print(f\"\\n❌ Health tests failed: {e}\")\n            return False\n        finally:\n            await self.client.close()\n\n\nasync def main():\n    \"\"\"Main entry point for API health testing\"\"\"\n    \n    import argparse\n    \n    parser = argparse.ArgumentParser(description=\"Test RMS API health and connectivity\")\n    parser.add_argument(\"--base-url\", default=\"http://localhost:8000\", help=\"API base URL\")\n    \n    args = parser.parse_args()\n    \n    tester = APIHealthTester(args.base_url)\n    \n    try:\n        success = await tester.run_comprehensive_health_tests()\n        \n        if success:\n            print(f\"\\n✅ All health tests passed successfully!\")\n            print(f\"   API is healthy and ready for comprehensive testing\")\n        else:\n            print(f\"\\n❌ Some health tests failed\")\n            print(f\"   Review the issues above before running full test suite\")\n            sys.exit(1)\n            \n    except Exception as e:\n        print(f\"❌ Health testing failed: {e}\")\n        sys.exit(1)\n\n\nif __name__ == \"__main__\":\n    asyncio.run(main())"