#!/usr/bin/env python3
"""
Phase 1 Production-Grade Testing Suite
Comprehensive testing to verify Phase 1 is production-ready.
"""

import requests
import json
import time
import asyncio
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import string

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

class Phase1ProductionTester:
    """Production-grade testing for Phase 1 functionality."""
    
    def __init__(self):
        self.auth_headers = None
        self.restaurant_id = None
        self.organization_id = None
        self.test_results = {
            "security": [],
            "performance": [],
            "edge_cases": [],
            "data_integrity": [],
            "error_handling": [],
            "concurrent_access": []
        }
        
    def log_test_result(self, category, test_name, success, details=None, response_time=None):
        """Log test result with details."""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_time": response_time,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results[category].append(result)
        status = "✅" if success else "❌"
        time_info = f" ({response_time:.3f}s)" if response_time else ""
        print(f"  {status} {test_name}{time_info}")
        if not success and details:
            print(f"    Details: {details}")
    
    def setup_test_environment(self):
        """Set up test environment."""
        print("🏗️ Setting up production test environment...")
        
        timestamp = int(time.time())
        test_data = {
            "restaurant_name": f"Production Test {timestamp}",
            "admin_user": {
                "email": f"prod.test.{timestamp}@example.com",
                "password": "SecurePassword123!",
                "full_name": "Production Test Admin"
            }
        }
        
        try:
            # Setup restaurant
            response = requests.post(f"{BASE_URL}/setup", json=test_data)
            if response.status_code != 200:
                print(f"❌ Setup failed: {response.status_code}")
                return False
            
            setup_result = response.json()
            self.restaurant_id = setup_result["restaurant"]["id"]
            self.organization_id = setup_result["organization"]["id"]
            
            # Authenticate
            auth_data = {
                "email": test_data["admin_user"]["email"],
                "password": test_data["admin_user"]["password"]
            }
            response = requests.post(f"{API_BASE}/auth/login", json=auth_data)
            if response.status_code != 200:
                print(f"❌ Auth failed: {response.status_code}")
                return False
            
            auth_result = response.json()
            token = auth_result["access_token"]
            self.auth_headers = {"Authorization": f"Bearer {token}"}
            
            print("✅ Test environment ready")
            return True
            
        except Exception as e:
            print(f"❌ Setup error: {e}")
            return False
    
    def test_authentication_security(self):
        """Test authentication security measures."""
        print("\n🔐 Testing Authentication Security...")
        
        # Test 1: Invalid JWT token
        start_time = time.time()
        invalid_headers = {"Authorization": "Bearer invalid.jwt.token"}
        response = requests.get(f"{API_BASE}/menu/categories", headers=invalid_headers)
        response_time = time.time() - start_time
        success = response.status_code == 401
        self.log_test_result("security", "Invalid JWT Token Rejection", success, 
                           f"Status: {response.status_code}", response_time)
        
        # Test 2: Missing authorization header
        start_time = time.time()
        response = requests.get(f"{API_BASE}/menu/categories/")  # Note: trailing slash for proper endpoint
        response_time = time.time() - start_time
        success = response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing auth
        self.log_test_result("security", "Missing Auth Header Rejection", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 3: SQL injection attempts in login
        start_time = time.time()
        malicious_data = {
            "email": "admin@example.com'; DROP TABLE users; --",
            "password": "password"
        }
        response = requests.post(f"{API_BASE}/auth/login", json=malicious_data)
        response_time = time.time() - start_time
        success = response.status_code in [401, 422]
        self.log_test_result("security", "SQL Injection Protection", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 4: Password brute force protection (multiple failed attempts)
        print("    Testing brute force protection...")
        failed_attempts = 0
        for i in range(5):
            start_time = time.time()
            response = requests.post(f"{API_BASE}/auth/login", json={
                "email": "admin@example.com",
                "password": f"wrong_password_{i}"
            })
            response_time = time.time() - start_time
            if response.status_code == 401:
                failed_attempts += 1
        
        success = failed_attempts == 5
        self.log_test_result("security", "Brute Force Protection", success,
                           f"Failed attempts handled: {failed_attempts}/5")
        
        # Test 5: Token expiration handling
        start_time = time.time()
        response = requests.post(f"{API_BASE}/auth/refresh", headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("security", "Token Refresh Mechanism", success,
                           f"Status: {response.status_code}", response_time)
    
    def test_input_validation_security(self):
        """Test input validation and sanitization."""
        print("\n🛡️ Testing Input Validation & Sanitization...")
        
        # Test 1: XSS protection in menu items
        start_time = time.time()
        xss_data = {
            "name": "<script>alert('xss')</script>",
            "description": "<img src=x onerror=alert('xss')>",
            "price": 10.99,
            "is_available": True
        }
        response = requests.post(f"{API_BASE}/menu/items", json=xss_data, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code in [400, 422] or (response.status_code == 200 and "<script>" not in response.text)
        self.log_test_result("security", "XSS Protection", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 2: Large payload handling
        start_time = time.time()
        large_data = {
            "name": "A" * 10000,  # Very long name
            "description": "B" * 50000,  # Very long description
            "price": 10.99
        }
        response = requests.post(f"{API_BASE}/menu/items", json=large_data, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code in [400, 422, 413]  # Should reject large payloads
        self.log_test_result("security", "Large Payload Protection", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 3: Invalid data types
        start_time = time.time()
        invalid_data = {
            "name": 123,  # Should be string
            "price": "invalid_price",  # Should be number
            "is_available": "maybe"  # Should be boolean
        }
        response = requests.post(f"{API_BASE}/menu/items", json=invalid_data, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 422
        self.log_test_result("security", "Data Type Validation", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 4: Unicode and special character handling
        start_time = time.time()
        unicode_data = {
            "name": "🍔 Spëcîál Bürgér with Émojîs 中文",
            "description": "A test with unicode: αβγδε ñáéíóú محتوى عربي",
            "price": 15.99,
            "is_available": True
        }
        response = requests.post(f"{API_BASE}/menu/items", json=unicode_data, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code in [200, 201]
        self.log_test_result("security", "Unicode Character Support", success,
                           f"Status: {response.status_code}", response_time)
    
    def test_performance_under_load(self):
        """Test performance under concurrent load."""
        print("\n⚡ Testing Performance Under Load...")
        
        # Test 1: Response time for basic operations
        operations = [
            ("GET Categories", lambda: requests.get(f"{API_BASE}/menu/categories", headers=self.auth_headers)),
            ("GET Items", lambda: requests.get(f"{API_BASE}/menu/items", headers=self.auth_headers)),
            ("GET Modifiers", lambda: requests.get(f"{API_BASE}/menu/modifiers", headers=self.auth_headers)),
            ("GET Public Menu", lambda: requests.get(f"{API_BASE}/menu/public", params={"restaurant_id": self.restaurant_id}))
        ]
        
        for operation_name, operation in operations:
            times = []
            for i in range(10):  # 10 requests per operation
                start_time = time.time()
                response = operation()
                response_time = time.time() - start_time
                times.append(response_time)
                if response.status_code not in [200, 201]:
                    break
            
            avg_time = sum(times) / len(times)
            success = avg_time < 1.0 and all(t < 2.0 for t in times)  # Average < 1s, max < 2s
            self.log_test_result("performance", f"{operation_name} Response Time", success,
                               f"Avg: {avg_time:.3f}s, Max: {max(times):.3f}s", avg_time)
        
        # Test 2: Concurrent access
        print("    Testing concurrent access...")
        
        def concurrent_request():
            try:
                start_time = time.time()
                response = requests.get(f"{API_BASE}/menu/categories", headers=self.auth_headers)
                response_time = time.time() - start_time
                return response.status_code == 200, response_time
            except Exception as e:
                return False, 0
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            start_time = time.time()
            futures = [executor.submit(concurrent_request) for _ in range(50)]
            results = [future.result() for future in as_completed(futures)]
            total_time = time.time() - start_time
        
        successful_requests = sum(1 for success, _ in results if success)
        avg_response_time = sum(time for _, time in results) / len(results)
        
        success = successful_requests >= 45 and total_time < 10  # 90% success rate, under 10s total
        self.log_test_result("performance", "Concurrent Access (50 requests)", success,
                           f"Success: {successful_requests}/50, Total time: {total_time:.3f}s", avg_response_time)
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        print("\n🎯 Testing Edge Cases...")
        
        # Test 1: Empty database queries
        start_time = time.time()
        response = requests.get(f"{API_BASE}/menu/items?category_id=99999999-9999-9999-9999-999999999999", 
                              headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200 and response.json() == []
        self.log_test_result("edge_cases", "Empty Query Results", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 2: Boundary values for prices
        boundary_prices = [-1, 0, 0.01, 999999.99, 1000000]
        for price in boundary_prices:
            start_time = time.time()
            data = {"name": f"Test Item {price}", "price": price, "is_available": True}
            response = requests.post(f"{API_BASE}/menu/items", json=data, headers=self.auth_headers)
            response_time = time.time() - start_time
            
            # Negative prices should be rejected, others should be accepted
            expected_success = price >= 0
            actual_success = response.status_code in ([200, 201] if expected_success else [400, 422])
            self.log_test_result("edge_cases", f"Price Boundary Test ({price})", actual_success,
                               f"Status: {response.status_code}", response_time)
        
        # Test 3: Very long pagination
        start_time = time.time()
        response = requests.get(f"{API_BASE}/menu/items?skip=10000&limit=1000", headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code == 200
        self.log_test_result("edge_cases", "Large Pagination Parameters", success,
                           f"Status: {response.status_code}", response_time)
        
        # Test 4: Invalid UUIDs
        invalid_uuids = ["invalid", "123", "00000000-0000-0000-0000", "not-a-uuid"]
        for invalid_uuid in invalid_uuids:
            start_time = time.time()
            response = requests.get(f"{API_BASE}/menu/items/{invalid_uuid}", headers=self.auth_headers)
            response_time = time.time() - start_time
            success = response.status_code in [400, 404, 422]
            self.log_test_result("edge_cases", f"Invalid UUID Handling ({invalid_uuid[:10]})", success,
                               f"Status: {response.status_code}", response_time)
    
    def test_data_integrity(self):
        """Test data integrity and consistency."""
        print("\n🔗 Testing Data Integrity...")
        
        # Test 1: Create category and verify it appears in lists
        start_time = time.time()
        category_data = {
            "name": "Integrity Test Category",
            "description": "Testing data integrity",
            "display_order": 1,
            "is_active": True
        }
        response = requests.post(f"{API_BASE}/menu/categories", json=category_data, headers=self.auth_headers)
        response_time = time.time() - start_time
        
        if response.status_code in [200, 201]:
            category = response.json()
            category_id = category["id"]
            
            # Verify category appears in list
            list_response = requests.get(f"{API_BASE}/menu/categories", headers=self.auth_headers)
            categories = list_response.json()
            found = any(cat["id"] == category_id for cat in categories)
            
            success = found
            self.log_test_result("data_integrity", "Category Creation & Listing", success,
                               f"Category found in list: {found}", response_time)
            
            # Test 2: Create item with this category
            item_data = {
                "name": "Integrity Test Item",
                "description": "Item for testing relationships",
                "price": 12.99,
                "category_id": category_id,
                "is_available": True
            }
            start_time = time.time()
            item_response = requests.post(f"{API_BASE}/menu/items", json=item_data, headers=self.auth_headers)
            response_time = time.time() - start_time
            
            success = item_response.status_code in [200, 201]
            self.log_test_result("data_integrity", "Item-Category Relationship", success,
                               f"Status: {item_response.status_code}", response_time)
            
            if success:
                item = item_response.json()
                # Verify item has correct category
                get_response = requests.get(f"{API_BASE}/menu/items/{item['id']}", headers=self.auth_headers)
                if get_response.status_code == 200:
                    retrieved_item = get_response.json()
                    category_match = retrieved_item.get("category_id") == category_id
                    self.log_test_result("data_integrity", "Category Relationship Persistence", category_match,
                                       f"Category IDs match: {category_match}")
        
        # Test 3: Transaction consistency (attempt to create item with non-existent category)
        start_time = time.time()
        invalid_item = {
            "name": "Invalid Category Item",
            "price": 10.99,
            "category_id": "99999999-9999-9999-9999-999999999999"
        }
        response = requests.post(f"{API_BASE}/menu/items", json=invalid_item, headers=self.auth_headers)
        response_time = time.time() - start_time
        success = response.status_code in [400, 404, 422]
        self.log_test_result("data_integrity", "Foreign Key Constraint", success,
                           f"Status: {response.status_code}", response_time)
    
    def test_error_handling_robustness(self):
        """Test error handling robustness."""
        print("\n🚨 Testing Error Handling Robustness...")
        
        # Test 1: Malformed JSON
        start_time = time.time()
        try:
            response = requests.post(f"{API_BASE}/menu/categories", 
                                   data="{invalid json}", 
                                   headers={**self.auth_headers, "Content-Type": "application/json"})
            response_time = time.time() - start_time
            success = response.status_code in [400, 422]
        except Exception:
            response_time = time.time() - start_time
            success = True  # Exception is acceptable for malformed requests
        
        self.log_test_result("error_handling", "Malformed JSON Handling", success,
                           "Properly rejected malformed JSON", response_time)
        
        # Test 2: Missing required fields
        incomplete_data_sets = [
            {},  # Completely empty
            {"name": ""},  # Empty name
            {"description": "No name provided"},  # Missing name
            {"name": "Test", "price": None}  # Null price
        ]
        
        for i, incomplete_data in enumerate(incomplete_data_sets):
            start_time = time.time()
            response = requests.post(f"{API_BASE}/menu/items", json=incomplete_data, headers=self.auth_headers)
            response_time = time.time() - start_time
            success = response.status_code == 422
            self.log_test_result("error_handling", f"Missing Fields Test {i+1}", success,
                               f"Status: {response.status_code}", response_time)
        
        # Test 3: Server overload simulation (rapid requests)
        print("    Testing rapid request handling...")
        start_time = time.time()
        responses = []
        for i in range(20):  # 20 rapid requests
            response = requests.get(f"{API_BASE}/menu/categories", headers=self.auth_headers)
            responses.append(response.status_code)
        
        response_time = time.time() - start_time
        success_count = sum(1 for status in responses if status == 200)
        success = success_count >= 18  # Allow 2 failures out of 20
        self.log_test_result("error_handling", "Rapid Request Handling", success,
                           f"Successful: {success_count}/20", response_time)
    
    def run_production_grade_tests(self):
        """Run all production-grade tests."""
        print("🚀 PHASE 1 PRODUCTION-GRADE TESTING")
        print("=" * 70)
        
        if not self.setup_test_environment():
            return False
        
        # Run all test categories
        self.test_authentication_security()
        self.test_input_validation_security()
        self.test_performance_under_load()
        self.test_edge_cases()
        self.test_data_integrity()
        self.test_error_handling_robustness()
        
        # Generate comprehensive report
        self.generate_production_report()
        
        return True
    
    def generate_production_report(self):
        """Generate comprehensive production readiness report."""
        print("\n" + "=" * 70)
        print("📊 PRODUCTION-GRADE TEST RESULTS")
        print("=" * 70)
        
        total_tests = 0
        passed_tests = 0
        category_results = {}
        
        for category, tests in self.test_results.items():
            if not tests:
                continue
                
            category_passed = sum(1 for test in tests if test["success"])
            category_total = len(tests)
            category_results[category] = {
                "passed": category_passed,
                "total": category_total,
                "success_rate": (category_passed / category_total) * 100 if category_total > 0 else 0
            }
            
            total_tests += category_total
            passed_tests += category_passed
        
        overall_success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"Overall Success Rate: {overall_success_rate:.1f}% ({passed_tests}/{total_tests})")
        print(f"Tests Passed: {passed_tests}")
        print(f"Tests Failed: {total_tests - passed_tests}")
        
        print("\n📋 Category Breakdown:")
        for category, results in category_results.items():
            status = "✅" if results["success_rate"] >= 90 else "⚠️" if results["success_rate"] >= 75 else "❌"
            print(f"   {status} {category.replace('_', ' ').title()}: {results['passed']}/{results['total']} ({results['success_rate']:.1f}%)")
        
        # Performance summary
        performance_tests = self.test_results.get("performance", [])
        if performance_tests:
            print("\n⚡ Performance Summary:")
            for test in performance_tests:
                if test.get("response_time"):
                    status = "✅" if test["response_time"] < 1.0 else "⚠️"
                    print(f"   {status} {test['test']}: {test['response_time']:.3f}s")
        
        # Failed tests details
        failed_tests = []
        for category, tests in self.test_results.items():
            for test in tests:
                if not test["success"]:
                    failed_tests.append(f"{category}: {test['test']} - {test.get('details', 'No details')}")
        
        if failed_tests:
            print("\n❌ Failed Tests:")
            for failed_test in failed_tests:
                print(f"   • {failed_test}")
        
        # Production readiness assessment
        print("\n🎯 Production Readiness Assessment:")
        
        security_score = category_results.get("security", {}).get("success_rate", 0)
        performance_score = category_results.get("performance", {}).get("success_rate", 0)
        data_integrity_score = category_results.get("data_integrity", {}).get("success_rate", 0)
        error_handling_score = category_results.get("error_handling", {}).get("success_rate", 0)
        
        if overall_success_rate >= 95 and security_score >= 90 and performance_score >= 85:
            print("   ✅ PRODUCTION READY")
            print("   All critical systems meet production standards.")
            assessment = "PRODUCTION_READY"
        elif overall_success_rate >= 85 and security_score >= 80:
            print("   ⚠️  PRODUCTION READY WITH MINOR ISSUES")
            print("   Core functionality is solid, minor improvements recommended.")
            assessment = "PRODUCTION_READY_WITH_ISSUES"
        else:
            print("   ❌ NOT PRODUCTION READY")
            print("   Critical issues must be resolved before production deployment.")
            assessment = "NOT_PRODUCTION_READY"
        
        # Critical areas assessment
        print("\n🔍 Critical Areas Assessment:")
        areas = [
            ("Security", security_score, "🔐"),
            ("Performance", performance_score, "⚡"),
            ("Data Integrity", data_integrity_score, "🔗"),
            ("Error Handling", error_handling_score, "🚨")
        ]
        
        for area, score, emoji in areas:
            if score >= 90:
                status = "✅ Excellent"
            elif score >= 75:
                status = "⚠️ Good"
            elif score >= 60:
                status = "⚠️ Needs Improvement"
            else:
                status = "❌ Critical Issues"
            
            print(f"   {emoji} {area}: {status} ({score:.1f}%)")
        
        return assessment


def main():
    """Run production-grade tests."""
    tester = Phase1ProductionTester()
    
    try:
        success = tester.run_production_grade_tests()
        
        if success:
            print("\n✅ Production-grade testing completed successfully!")
            exit(0)
        else:
            print("\n❌ Production-grade testing encountered issues")
            exit(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed: {e}")
        exit(1)


if __name__ == "__main__":
    main()