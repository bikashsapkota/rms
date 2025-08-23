#!/usr/bin/env python3
"""
Production-Level Test Suite Runner

Comprehensive test runner for Phase 3 production readiness verification.
Runs unit tests, API tests, workflow tests, and performance tests.
"""

import sys
import asyncio
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from tests.api_tester.shared.utils import APITestHelper


class ProductionTestRunner:
    """Production test suite orchestrator"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = {
            "unit_tests": {"passed": False, "details": None},
            "api_health": {"passed": False, "details": None},
            "workflow_tests": {"passed": False, "details": None},
            "performance_tests": {"passed": False, "details": None},
            "overall": {"passed": False, "start_time": None, "end_time": None}
        }
    
    def print_header(self):
        """Print production test suite header"""
        print("🚀 RMS Production-Level Test Suite")
        print("="*50)
        print(f"Target API: {self.base_url}")
        print(f"Test Scope: Phase 3 Order Management System")
        print(f"Start Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
    
    async def check_server_availability(self) -> bool:
        """Check if the API server is running and accessible"""
        APITestHelper.print_test_header("Server Availability Check", "🔍")
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/health", timeout=10) as response:
                    if response.status == 200:
                        health_data = await response.json()
                        APITestHelper.print_test_step("API server is running and healthy", "SUCCESS")
                        
                        if isinstance(health_data, dict) and "status" in health_data:
                            print(f"   Server Status: {health_data.get('status', 'unknown')}")
                        
                        return True
                    else:
                        APITestHelper.print_test_step(f"API server returned HTTP {response.status}", "FAILED")
                        return False
                        
        except Exception as e:
            APITestHelper.print_test_step(f"Cannot connect to API server: {e}", "FAILED")
            print(f"\\n❌ Please ensure the API server is running at {self.base_url}")
            print(f"   Start the server with: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
            return False
    
    def run_unit_tests(self) -> bool:
        """Run all unit tests using pytest"""
        APITestHelper.print_test_header("Unit Tests Execution", "🧪")
        
        try:
            # Run pytest with verbose output
            cmd = [
                "python", "-m", "pytest", 
                "tests/unit/",
                "-v",
                "--tb=short",
                "--color=yes"
            ]
            
            print(f"Running command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root)
            
            # Print pytest output
            if result.stdout:
                print("\\nPytest Output:")
                print(result.stdout)
            
            if result.stderr:
                print("\\nPytest Errors:")
                print(result.stderr)
            
            success = result.returncode == 0
            
            if success:
                APITestHelper.print_test_step("Unit tests passed", "SUCCESS")
            else:
                APITestHelper.print_test_step(f"Unit tests failed (exit code: {result.returncode})", "FAILED")
            
            self.results["unit_tests"] = {
                "passed": success,
                "details": {
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            }
            
            return success
            
        except Exception as e:
            APITestHelper.print_test_step(f"Unit test execution failed: {e}", "FAILED")
            self.results["unit_tests"] = {
                "passed": False,
                "details": {"error": str(e)}
            }
            return False
    
    async def run_api_health_tests(self) -> bool:
        """Run API health and connectivity tests"""
        APITestHelper.print_test_header("API Health Tests", "🏥")
        
        try:
            # Import and run health tests
            from tests.api_tester.test_read_operations.test_api_health import APIHealthTester
            
            health_tester = APIHealthTester(self.base_url)
            success = await health_tester.run_comprehensive_health_tests()
            
            self.results["api_health"] = {
                "passed": success,
                "details": {
                    "total_tests": health_tester.results.total_tests,
                    "passed_tests": health_tester.results.passed_tests,
                    "failed_tests": health_tester.results.failed_tests,
                    "success_rate": health_tester.results.success_rate
                }
            }
            
            return success
            
        except Exception as e:
            APITestHelper.print_test_step(f"API health tests failed: {e}", "FAILED")
            self.results["api_health"] = {
                "passed": False,
                "details": {"error": str(e)}
            }
            return False
    
    async def run_workflow_tests(self) -> bool:
        """Run complete workflow tests"""
        APITestHelper.print_test_header("Workflow Tests", "🔄")
        
        try:
            # Import and run workflow tests
            from tests.api_tester.test_production_workflows.test_complete_order_workflow import CompleteOrderWorkflowTester
            
            workflow_tester = CompleteOrderWorkflowTester(self.base_url)
            success = await workflow_tester.run_all_workflow_tests()
            
            self.results["workflow_tests"] = {
                "passed": success,
                "details": {
                    "total_tests": workflow_tester.results.total_tests,
                    "passed_tests": workflow_tester.results.passed_tests,
                    "failed_tests": workflow_tester.results.failed_tests,
                    "success_rate": workflow_tester.results.success_rate,
                    "execution_time": workflow_tester.results.execution_time
                }
            }
            
            return success
            
        except Exception as e:
            APITestHelper.print_test_step(f"Workflow tests failed: {e}", "FAILED")
            self.results["workflow_tests"] = {
                "passed": False,
                "details": {"error": str(e)}
            }
            return False
    
    async def run_performance_tests(self) -> bool:
        """Run performance and load tests"""
        APITestHelper.print_test_header("Performance Tests", "⚡")
        
        try:
            # Import and run performance tests
            from tests.api_tester.test_production_workflows.test_performance_load import PerformanceLoadTester
            
            performance_tester = PerformanceLoadTester(self.base_url)
            success = await performance_tester.run_all_performance_tests()
            
            self.results["performance_tests"] = {
                "passed": success,
                "details": {
                    "total_tests": performance_tester.results.total_tests,
                    "passed_tests": performance_tester.results.passed_tests,
                    "failed_tests": performance_tester.results.failed_tests,
                    "success_rate": performance_tester.results.success_rate,
                    "execution_time": performance_tester.results.execution_time
                }
            }
            
            return success
            
        except Exception as e:
            APITestHelper.print_test_step(f"Performance tests failed: {e}", "FAILED")
            self.results["performance_tests"] = {
                "passed": False,
                "details": {"error": str(e)}
            }
            return False
    
    def print_final_summary(self):
        """Print comprehensive final test summary"""
        
        print("\\n" + "="*60)
        print("🏁 PRODUCTION TEST SUITE FINAL SUMMARY")
        print("="*60)
        
        # Test category results
        categories = [
            ("Unit Tests", "unit_tests", "🧪"),
            ("API Health", "api_health", "🏥"),
            ("Workflow Tests", "workflow_tests", "🔄"),
            ("Performance Tests", "performance_tests", "⚡")
        ]
        
        total_passed = 0
        total_categories = len(categories)
        
        for name, key, emoji in categories:
            result = self.results[key]
            status = "✅ PASSED" if result["passed"] else "❌ FAILED"
            print(f"{emoji} {name}: {status}")
            
            if result["passed"]:
                total_passed += 1
            
            # Show details if available
            if "details" in result and result["details"]:
                details = result["details"]
                if "total_tests" in details:
                    print(f"   Tests: {details['passed_tests']}/{details['total_tests']} " +
                          f"({details['success_rate']:.1f}%)")
                if "execution_time" in details:
                    print(f"   Duration: {details['execution_time']:.2f}s")
        
        # Overall assessment
        print(f"\\n📊 Overall Results:")
        print(f"   Test Categories Passed: {total_passed}/{total_categories}")
        
        overall_success = total_passed == total_categories
        
        if self.results["overall"]["start_time"] and self.results["overall"]["end_time"]:
            total_time = self.results["overall"]["end_time"] - self.results["overall"]["start_time"]
            print(f"   Total Execution Time: {total_time:.2f}s")
        
        # Production readiness assessment
        print(f"\\n🎯 Production Readiness Assessment:")
        
        if overall_success:
            print("   ✅ PRODUCTION READY")
            print("   All test categories passed successfully.")
            print("   The Phase 3 Order Management System is ready for production deployment.")
        elif total_passed >= 3:
            print("   ⚠️  MOSTLY READY")
            print("   Most test categories passed, but some issues remain.")
            print("   Review failed tests and address issues before production deployment.")
        elif total_passed >= 2:
            print("   ⚠️  NEEDS IMPROVEMENT")
            print("   Some critical test categories failed.")
            print("   Significant work needed before production deployment.")
        else:
            print("   ❌ NOT READY")
            print("   Multiple critical test categories failed.")
            print("   Extensive work required before production deployment.")
        
        # Recommendations
        print(f"\\n💡 Recommendations:")
        
        if not self.results["unit_tests"]["passed"]:
            print("   • Fix failing unit tests to ensure code quality")
        
        if not self.results["api_health"]["passed"]:
            print("   • Address API health issues for system stability")
        
        if not self.results["workflow_tests"]["passed"]:
            print("   • Fix workflow issues to ensure feature completeness")
        
        if not self.results["performance_tests"]["passed"]:
            print("   • Optimize performance for production load requirements")
        
        if overall_success:
            print("   • Consider running tests in a staging environment")
            print("   • Set up monitoring and alerting for production")
            print("   • Prepare deployment and rollback procedures")
        
        self.results["overall"]["passed"] = overall_success
        
        print("="*60)
        
        return overall_success
    
    async def run_production_test_suite(self) -> bool:
        """Run the complete production test suite"""
        
        self.results["overall"]["start_time"] = time.time()
        
        self.print_header()
        
        try:
            # Step 1: Check server availability
            if not await self.check_server_availability():
                print("\\n❌ Cannot proceed without API server. Exiting.")
                return False
            
            print("\\n🏃‍♂️ Starting production test execution...")
            
            # Step 2: Run unit tests
            print("\\n" + "-"*40)
            unit_success = self.run_unit_tests()
            
            # Step 3: Run API health tests
            print("\\n" + "-"*40)
            health_success = await self.run_api_health_tests()
            
            # Step 4: Run workflow tests (only if health tests pass)
            print("\\n" + "-"*40)
            if health_success:
                workflow_success = await self.run_workflow_tests()
            else:
                print("⚠️ Skipping workflow tests due to API health failures")
                workflow_success = False
                self.results["workflow_tests"]["passed"] = False
            
            # Step 5: Run performance tests (only if basic tests pass)
            print("\\n" + "-"*40)
            if health_success:
                performance_success = await self.run_performance_tests()
            else:
                print("⚠️ Skipping performance tests due to API health failures")
                performance_success = False
                self.results["performance_tests"]["passed"] = False
            
            self.results["overall"]["end_time"] = time.time()
            
            # Final summary
            overall_success = self.print_final_summary()
            
            return overall_success
            
        except KeyboardInterrupt:
            print("\\n⚠️ Test suite interrupted by user")
            return False
        except Exception as e:
            print(f"\\n❌ Test suite execution failed: {e}")
            return False


async def main():
    """Main entry point for production test suite"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Run production-level test suite for Phase 3")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    parser.add_argument("--api-only", action="store_true", help="Run only API tests")
    parser.add_argument("--workflow-only", action="store_true", help="Run only workflow tests")
    parser.add_argument("--performance-only", action="store_true", help="Run only performance tests")
    
    args = parser.parse_args()
    
    runner = ProductionTestRunner(args.base_url)
    
    try:
        # Handle specific test type requests
        if args.unit_only:
            success = runner.run_unit_tests()
        elif args.api_only:
            success = await runner.run_api_health_tests()
        elif args.workflow_only:
            if await runner.check_server_availability():
                success = await runner.run_workflow_tests()
            else:
                success = False
        elif args.performance_only:
            if await runner.check_server_availability():
                success = await runner.run_performance_tests()
            else:
                success = False
        else:
            # Run complete test suite
            success = await runner.run_production_test_suite()
        
        if success:
            print(f"\\n✅ Test execution completed successfully!")
            sys.exit(0)
        else:
            print(f"\\n❌ Test execution completed with failures!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())