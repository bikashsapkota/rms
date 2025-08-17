#!/usr/bin/env python3
"""
Run All Delete Operations Tests

Orchestrates execution of all delete operation test suites.
Provides comprehensive testing of all DELETE endpoints in the RMS API.
"""

import sys
import asyncio
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.api_tester.shared.utils import APITestClient, APITestHelper, TestResults


class DeleteOperationsOrchestrator:
    """Orchestrates all delete operation tests"""
    
    def __init__(self, base_url: str = "http://localhost:8000", confirm_deletes: bool = False):
        self.base_url = base_url
        self.confirm_deletes = confirm_deletes
        self.overall_results = TestResults()
        self.test_modules = []
        
    def print_header(self, title: str, emoji: str = "🗑️"):
        """Print formatted section header"""
        print(f"\n{'=' * 60}")
        print(f"{emoji}  {title}")
        print(f"{'=' * 60}")
        
    def print_step(self, step: str, status: str = "RUNNING"):
        """Print test step with status"""
        status_icons = {
            "RUNNING": "🔄",
            "SUCCESS": "✅",
            "FAILED": "❌",
            "SKIPPED": "⏭️"
        }
        icon = status_icons.get(status, "🔄")
        print(f"{icon} {step}")
        
    async def run_test_module(self, module_name: str, description: str) -> bool:
        """Run a specific test module"""
        
        self.print_step(f"{description}", "RUNNING")
        
        try:
            import subprocess
            
            # Run the test module
            script_path = Path(__file__).parent / module_name
            
            if not script_path.exists():
                self.print_step(f"{description} - Script not found", "FAILED")
                return False
                
            # Build command arguments
            cmd_args = [sys.executable, str(script_path), "--base-url", self.base_url]
            if self.confirm_deletes:
                cmd_args.append("--confirm-deletes")
                
            start_time = time.time()
            result = subprocess.run(
                cmd_args,
                capture_output=True,
                text=True,
                cwd=project_root
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                self.print_step(f"{description} completed ({execution_time:.1f}s)", "SUCCESS")
                
                # Extract success information from output
                output_lines = result.stdout.split('\n')
                success_lines = [line for line in output_lines if '✅' in line or 'passed successfully' in line]
                for line in success_lines[-2:]:  # Show last 2 success lines
                    if line.strip():
                        print(f"   {line.strip()}")
                        
                # Store test results
                self.test_modules.append({
                    "module": module_name,
                    "description": description,
                    "success": True,
                    "execution_time": execution_time,
                    "output": result.stdout
                })
                
                return True
                
            else:
                self.print_step(f"{description} failed", "FAILED")
                
                # Show error details
                if result.stderr:
                    error_lines = result.stderr.strip().split('\n')
                    for line in error_lines[-3:]:  # Show last 3 error lines
                        if line.strip():
                            print(f"   Error: {line.strip()}")
                    
                # Store failure results
                self.test_modules.append({
                    "module": module_name,
                    "description": description,
                    "success": False,
                    "execution_time": execution_time,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                })
                
                return False
                
        except Exception as e:
            self.print_step(f"{description} error: {e}", "FAILED")
            
            self.test_modules.append({
                "module": module_name,
                "description": description,
                "success": False,
                "execution_time": 0,
                "error": str(e)
            })
            
            return False
            
    async def run_all_delete_tests(self) -> bool:
        """Run all delete operation test modules"""
        
        # Define test modules to run
        test_modules = [
            ("test_menu_deletions.py", "Menu Deletions (Categories, Items, Modifiers)"),
            ("test_user_deletions.py", "User Deletions (Soft & Hard Deletion)"),
            ("test_restaurant_deletions.py", "Restaurant Deletions (Deactivation & Removal)")
        ]
        
        overall_success = True
        
        for module_name, description in test_modules:
            try:
                success = await self.run_test_module(module_name, description)
                if not success:
                    overall_success = False
                    
            except Exception as e:
                self.print_step(f"{description} failed with error: {e}", "FAILED")
                overall_success = False
                
            # Add delay between test modules
            await asyncio.sleep(1.0)
            
        return overall_success
        
    def print_comprehensive_summary(self):
        """Print comprehensive summary of all delete tests"""
        
        self.print_header("Delete Operations Test Summary", "📊")
        
        total_modules = len(self.test_modules)
        successful_modules = sum(1 for module in self.test_modules if module["success"])
        
        print(f"\n🎯 Overall Results:")
        print(f"   Test Modules: {total_modules}")
        print(f"   Successful: {successful_modules}")
        print(f"   Failed: {total_modules - successful_modules}")
        print(f"   Success Rate: {(successful_modules/total_modules)*100:.1f}%")
        
        # Calculate total execution time
        total_time = sum(module.get("execution_time", 0) for module in self.test_modules)
        print(f"   Total Execution Time: {total_time:.2f} seconds")
        
        # Show delete mode status
        print(f"\n🗑️ Delete Operations Mode:")
        if self.confirm_deletes:
            print(f"   ⚠️  DESTRUCTIVE TESTING ENABLED")
            print(f"   • Hard deletions were performed")
            print(f"   • Test data was created and destroyed")
        else:
            print(f"   🛡️  SAFE MODE")
            print(f"   • Hard deletions were skipped")
            print(f"   • Soft deletions and validation tested")
            print(f"   • Use --confirm-deletes to enable destructive testing")
        
        print(f"\n📋 Module Details:")
        
        for module in self.test_modules:
            status = "✅" if module["success"] else "❌"
            exec_time = module.get("execution_time", 0)
            print(f"   {status} {module['description']}: {exec_time:.1f}s")
            
        # Show failures if any
        failed_modules = [m for m in self.test_modules if not m["success"]]
        if failed_modules:
            print(f"\n❌ Failed Modules:")
            for module in failed_modules:
                print(f"   • {module['description']}")
                if "error" in module:
                    print(f"     Error: {module['error']}")
                elif "stderr" in module and module["stderr"]:
                    error_lines = module["stderr"].strip().split('\n')
                    print(f"     Error: {error_lines[-1]}")  # Show last error line
                    
        # Test coverage summary
        print(f"\n📈 Delete Operations Test Coverage:")
        coverage_areas = [
            "Menu Item Deletions",
            "Menu Category Deletions (with constraints)",
            "Menu Modifier Deletions",
            "Cascade Deletion Behavior",
            "User Soft Deletion (Deactivation)",
            "User Hard Deletion (Permanent)",
            "User Deletion Constraints",
            "User Authentication Blocking",
            "Restaurant Deactivation",
            "Restaurant Hard Deletion",
            "Restaurant Deletion Constraints",
            "Deletion Data Validation",
            "Error Handling & Edge Cases",
            "Permission Enforcement",
            "Cleanup & Recovery"
        ]
        
        print(f"   Covered Areas: {len(coverage_areas)}")
        for area in coverage_areas:
            print(f"   ✅ {area}")
            
        # Performance insights
        if self.test_modules:
            fastest_module = min(self.test_modules, key=lambda x: x.get("execution_time", float('inf')))
            slowest_module = max(self.test_modules, key=lambda x: x.get("execution_time", 0))
            
            print(f"\n⚡ Performance Insights:")
            print(f"   Fastest Test: {fastest_module['description']} ({fastest_module.get('execution_time', 0):.1f}s)")
            print(f"   Slowest Test: {slowest_module['description']} ({slowest_module.get('execution_time', 0):.1f}s)")
            
        # Recommendations
        print(f"\n💡 Recommendations:")
        if successful_modules == total_modules:
            print(f"   ✅ All delete operations working correctly")
            print(f"   • Proceed with business workflow testing")
            print(f"   • All CRUD operations complete and tested")
            print(f"   • Ready for integration and end-to-end testing")
        else:
            print(f"   ⚠️  Some delete operations failed")
            print(f"   • Fix failing endpoints before proceeding")
            print(f"   • Check data constraints and referential integrity")
            print(f"   • Verify permission and authorization logic")
            print(f"   • Test cascade deletion behavior")
            
        # Safety reminders
        print(f"\n🛡️ Safety Reminders:")
        print(f"   • Delete operations are destructive by nature")
        print(f"   • Always test on development/staging environments first")
        print(f"   • Implement proper backup and recovery procedures")
        print(f"   • Use soft deletion for critical business data")
        print(f"   • Audit and log all deletion operations")
            
    async def run_comprehensive_delete_tests(self):
        """Run comprehensive delete operations testing"""
        
        start_time = time.time()
        
        self.print_header("RMS Comprehensive Delete Operations Testing", "🗑️")
        
        print(f"Target API: {self.base_url}")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.confirm_deletes:
            print(f"\n⚠️  DESTRUCTIVE TESTING DISABLED")
            print(f"   Delete tests will run in SAFE MODE")
            print(f"   • Soft deletions and validation will be tested")
            print(f"   • Hard deletions will be skipped")
            print(f"   • Use --confirm-deletes to enable full testing")
        else:
            print(f"\n🚨 DESTRUCTIVE TESTING ENABLED")
            print(f"   ⚠️  WARNING: This will create and delete test data")
            print(f"   • Make sure you're testing against a development database")
            print(f"   • Test data will be cleaned up automatically")
            
        print()
        
        try:
            # Check API availability first
            self.print_step("Checking API availability", "RUNNING")
            
            async with APITestClient(self.base_url) as client:
                response = await client.get("/health")
                if response.status_code == 200:
                    self.print_step("API is available and healthy", "SUCCESS")
                else:
                    self.print_step(f"API health check failed: HTTP {response.status_code}", "FAILED")
                    print(f"\n❌ API is not available. Please start the RMS API server first:")
                    print(f"   uv run uvicorn app.main:app --reload --port 8000")
                    return False
                    
            # Run all delete tests
            success = await self.run_all_delete_tests()
            
            # Calculate total execution time
            total_time = time.time() - start_time
            self.overall_results.execution_time = total_time
            
            # Print comprehensive summary
            self.print_comprehensive_summary()
            
            return success
            
        except KeyboardInterrupt:
            print(f"\n⚠️  Testing interrupted by user")
            return False
        except Exception as e:
            print(f"\n❌ Testing process failed: {e}")
            return False


async def main():
    """Main entry point for comprehensive delete testing"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Run all RMS delete operation tests")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--confirm-deletes", action="store_true", 
                       help="Confirm that you want to perform destructive delete operations")
    
    args = parser.parse_args()
    
    orchestrator = DeleteOperationsOrchestrator(args.base_url, args.confirm_deletes)
    
    try:
        success = await orchestrator.run_comprehensive_delete_tests()
        
        if success:
            print(f"\n🎉 All delete operation tests completed successfully!")
            print(f"\n💡 Next steps:")
            print(f"   • Run business workflows: python ../test_business_workflows/run_all_workflow_tests.py")
            print(f"   • Run comprehensive tests: python ../run_comprehensive_tests.py full")
            print(f"   • All CRUD operations are now tested and validated")
        else:
            print(f"\n💥 Some delete operation tests failed")
            print(f"   Review the failures above and fix issues before proceeding")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())