"""
Master test runner for all Phase 2 table and reservation management tests.
"""

import asyncio
import time
from tests.api_tester.shared.utils import print_test_header, print_success, print_error
from tests.api_tester.test_phase2_operations.test_table_management import TableManagementTester
from tests.api_tester.test_phase2_operations.test_reservation_management import ReservationManagementTester
from tests.api_tester.test_phase2_operations.test_availability_and_waitlist import AvailabilityAndWaitlistTester
from tests.api_tester.test_phase2_operations.test_public_reservations import PublicReservationTester


async def run_all_phase2_tests():
    """Run all Phase 2 API tests in sequence."""
    print_test_header("Phase 2: Table & Reservation Management - Comprehensive API Tests")
    print("🎯 Testing all table management, reservations, availability, and waitlist endpoints")
    print("=" * 80)
    
    start_time = time.time()
    all_results = []
    
    # Test sequences
    test_suites = [
        ("Table Management", TableManagementTester()),
        ("Reservation Management", ReservationManagementTester()),
        ("Availability & Waitlist", AvailabilityAndWaitlistTester()),
        ("Public Reservations", PublicReservationTester()),
    ]
    
    for suite_name, tester in test_suites:
        print(f"\n{'='*20} {suite_name} Tests {'='*20}")
        try:
            result = await tester.run_all_tests()
            all_results.append((suite_name, result))
            
            if result:
                print_success(f"✅ {suite_name} tests completed successfully")
            else:
                print_error(f"❌ {suite_name} tests had failures")
        except Exception as e:
            print_error(f"❌ {suite_name} tests failed with exception: {e}")
            all_results.append((suite_name, False))
        
        # Brief pause between test suites
        await asyncio.sleep(0.5)
    
    # Final summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*80)
    print_test_header("Phase 2 API Tests - Final Summary")
    
    passed_suites = 0
    total_suites = len(all_results)
    
    for suite_name, result in all_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {suite_name:<25} : {status}")
        if result:
            passed_suites += 1
    
    print(f"\n📊 Test Suite Results: {passed_suites}/{total_suites} suites passed")
    print(f"⏱️  Total execution time: {duration:.2f} seconds")
    
    if passed_suites == total_suites:
        print_success("🎉 All Phase 2 API tests completed successfully!")
        print("\n✨ Phase 2 Implementation Status: COMPLETE ✨")
        print("📋 Covered functionality:")
        print("  • Table management (CRUD operations)")
        print("  • Restaurant layout and floor plan management")
        print("  • Reservation system with advanced scheduling")
        print("  • Real-time availability checking")
        print("  • Intelligent waitlist management")
        print("  • Customer-facing public reservation APIs")
        print("  • Comprehensive analytics and reporting")
        print("  • Multi-tenant isolation and security")
        return True
    else:
        print_error("❌ Some Phase 2 tests failed - please review the logs above")
        return False


async def main():
    """Main entry point for Phase 2 tests."""
    try:
        success = await run_all_phase2_tests()
        if success:
            print("\n🚀 Ready for production deployment!")
        else:
            print("\n🔧 Please fix the failing tests before deployment")
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print_error(f"❌ Test execution failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())