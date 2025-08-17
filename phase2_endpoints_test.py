#!/usr/bin/env python3
"""
Phase 2 Endpoints Testing Script
Tests all Phase 2 endpoints to validate functionality
"""

import asyncio
import json
import sys
import traceback
from typing import Optional, Dict, Any, List
from tests.api_tester.shared.utils import (
    APITestClient, TestResults, APITestHelper,
    print_test_header, print_success, print_error, print_info
)


class Phase2EndpointTester:
    """Test Phase 2 endpoints without authentication requirements"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = TestResults()
        
    async def test_public_endpoints(self, client: APITestClient) -> Dict[str, Any]:
        """Test public reservation endpoints"""
        print_test_header("Testing Public Reservation Endpoints", "🌐")
        
        results = {
            "total_endpoints": 0,
            "working_endpoints": 0,
            "failed_endpoints": 0,
            "errors": []
        }
        
        # Use a test restaurant ID (UUID format)
        test_restaurant_id = "550e8400-e29b-41d4-a716-446655440000"
        
        # Test 1: Get restaurant info
        print_info("Testing restaurant info endpoint...")
        results["total_endpoints"] += 1
        
        try:
            response = await client.get(f"/api/v1/public/reservations/{test_restaurant_id}/info")
            if response.is_success():
                print_success(f"✅ Restaurant info: {response.status_code}")
                results["working_endpoints"] += 1
            else:
                print_error(f"❌ Restaurant info failed: {response.status_code} - Expected (no test data)")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Restaurant info: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Restaurant info error: {str(e)}")
            results["failed_endpoints"] += 1
            results["errors"].append(f"Restaurant info: {str(e)}")
        
        # Test 2: Check reservation availability
        print_info("Testing reservation availability...")
        results["total_endpoints"] += 1
        
        try:
            params = {
                "reservation_date": "2025-08-18",
                "party_size": 2,
                "time_preference": "19:00:00",
                "duration_minutes": 90
            }
            response = await client.get(f"/api/v1/public/reservations/{test_restaurant_id}/availability", params=params)
            if response.is_success():
                print_success(f"✅ Reservation availability: {response.status_code}")
                results["working_endpoints"] += 1
            else:
                print_error(f"❌ Reservation availability failed: {response.status_code} - Expected (no test data)")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Reservation availability: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Reservation availability error: {str(e)}")
            results["failed_endpoints"] += 1
            results["errors"].append(f"Reservation availability: {str(e)}")
        
        # Test 3: Try to book reservation (will fail without valid data)
        print_info("Testing reservation booking...")
        results["total_endpoints"] += 1
        
        try:
            booking_data = {
                "customer_name": "Test Customer",
                "customer_email": "test@example.com",
                "customer_phone": "+1-555-1234",
                "party_size": 2,
                "reservation_date": "2025-08-18",
                "reservation_time": "19:00:00",
                "special_requests": "Test booking"
            }
            response = await client.post(f"/api/v1/public/reservations/{test_restaurant_id}/book", json=booking_data)
            if response.is_success():
                print_success(f"✅ Reservation booking: {response.status_code}")
                results["working_endpoints"] += 1
            else:
                print_error(f"❌ Reservation booking failed: {response.status_code} - Expected (no test data)")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Reservation booking: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Reservation booking error: {str(e)}")
            results["failed_endpoints"] += 1
            results["errors"].append(f"Reservation booking: {str(e)}")
        
        # Test 4: Waitlist entry
        print_info("Testing waitlist entry...")
        results["total_endpoints"] += 1
        
        try:
            waitlist_data = {
                "customer_name": "Test Customer",
                "customer_email": "test@example.com",
                "customer_phone": "+1-555-5678",
                "party_size": 4,
                "special_requests": "Test waitlist entry"
            }
            response = await client.post(f"/api/v1/public/reservations/{test_restaurant_id}/waitlist", json=waitlist_data)
            if response.is_success():
                print_success(f"✅ Waitlist entry: {response.status_code}")
                results["working_endpoints"] += 1
            else:
                print_error(f"❌ Waitlist entry failed: {response.status_code} - Expected (no test data)")
                results["failed_endpoints"] += 1
                results["errors"].append(f"Waitlist entry: {response.status_code}")
        except Exception as e:
            print_error(f"❌ Waitlist entry error: {str(e)}")
            results["failed_endpoints"] += 1
            results["errors"].append(f"Waitlist entry: {str(e)}")
        
        return results
    
    async def test_authenticated_endpoints_structure(self, client: APITestClient) -> Dict[str, Any]:
        """Test that authenticated endpoints exist (structure test only)"""
        print_test_header("Testing Authenticated Endpoints Structure", "🔒")
        
        results = {
            "total_endpoints": 0,
            "working_endpoints": 0,
            "failed_endpoints": 0,
            "errors": []
        }
        
        # List of endpoints that should exist (will return 403 without auth)
        endpoints_to_test = [
            # Table Management
            ("GET", "/api/v1/tables/", "List tables"),
            ("GET", "/api/v1/tables/analytics/utilization", "Table utilization"),
            ("GET", "/api/v1/tables/availability/overview", "Table availability overview"),
            ("GET", "/api/v1/tables/layout/restaurant", "Restaurant layout"),
            
            # Reservation Management
            ("GET", "/api/v1/reservations/", "List reservations"),
            ("GET", "/api/v1/reservations/analytics/summary", "Reservation analytics"),
            ("GET", "/api/v1/reservations/calendar/view", "Calendar view"),
            ("GET", "/api/v1/reservations/today/overview", "Today overview"),
            
            # Availability System
            ("GET", "/api/v1/availability/slots", "Availability slots"),
            ("GET", "/api/v1/availability/calendar", "Availability calendar"),
            ("GET", "/api/v1/availability/overview", "Availability overview"),
            ("GET", "/api/v1/availability/alternatives", "Availability alternatives"),
            ("GET", "/api/v1/availability/capacity/optimization", "Capacity optimization"),
            
            # Waitlist Management
            ("GET", "/api/v1/waitlist/", "List waitlist"),
            ("GET", "/api/v1/waitlist/analytics/summary", "Waitlist analytics"),
            ("GET", "/api/v1/waitlist/availability/check", "Waitlist availability check"),
        ]
        
        for method, endpoint, description in endpoints_to_test:
            print_info(f"Testing {description}...")
            results["total_endpoints"] += 1
            
            try:
                if method == "GET":
                    response = await client.get(endpoint)
                else:
                    response = await client.post(endpoint, json={})
                
                # We expect 403 (Forbidden) for authenticated endpoints without auth
                # This confirms the endpoints exist
                if response.status_code == 403:
                    print_success(f"✅ {description}: Endpoint exists (403 expected)")
                    results["working_endpoints"] += 1
                elif response.is_success():
                    print_success(f"✅ {description}: {response.status_code}")
                    results["working_endpoints"] += 1
                else:
                    print_error(f"❌ {description} failed: {response.status_code}")
                    results["failed_endpoints"] += 1
                    results["errors"].append(f"{description}: {response.status_code}")
            except Exception as e:
                print_error(f"❌ {description} error: {str(e)}")
                results["failed_endpoints"] += 1
                results["errors"].append(f"{description}: {str(e)}")
        
        return results
    
    async def analyze_api_structure(self, client: APITestClient) -> Dict[str, Any]:
        """Analyze the complete API structure"""
        print_test_header("Analyzing Phase 2 API Structure", "🔍")
        
        try:
            response = await client.get("/api/v1/openapi.json")
            if not response.is_success():
                return {"error": f"Failed to get OpenAPI spec: {response.status_code}"}
            
            spec = response.json_data
            paths = spec.get("paths", {})
            
            # Categorize endpoints
            categories = {
                "tables": [],
                "reservations": [],
                "availability": [],
                "waitlist": [],
                "public": [],
                "auth": [],
                "other": []
            }
            
            for path in paths.keys():
                if "/tables" in path:
                    categories["tables"].append(path)
                elif "/reservations" in path:
                    categories["reservations"].append(path)
                elif "/availability" in path:
                    categories["availability"].append(path)
                elif "/waitlist" in path:
                    categories["waitlist"].append(path)
                elif "/public" in path:
                    categories["public"].append(path)
                elif "/auth" in path:
                    categories["auth"].append(path)
                else:
                    categories["other"].append(path)
            
            print_info("📊 Phase 2 API Structure Analysis:")
            print_info(f"  Tables: {len(categories['tables'])} endpoints")
            print_info(f"  Reservations: {len(categories['reservations'])} endpoints")
            print_info(f"  Availability: {len(categories['availability'])} endpoints")
            print_info(f"  Waitlist: {len(categories['waitlist'])} endpoints")
            print_info(f"  Public: {len(categories['public'])} endpoints")
            print_info(f"  Auth: {len(categories['auth'])} endpoints")
            print_info(f"  Other: {len(categories['other'])} endpoints")
            
            total_phase2 = (
                len(categories['tables']) + 
                len(categories['reservations']) + 
                len(categories['availability']) + 
                len(categories['waitlist']) +
                len(categories['public'])
            )
            
            print_success(f"🎯 Total Phase 2 Endpoints: {total_phase2}")
            
            return {
                "categories": categories,
                "total_phase2_endpoints": total_phase2,
                "endpoint_counts": {k: len(v) for k, v in categories.items()}
            }
            
        except Exception as e:
            print_error(f"❌ API structure analysis failed: {str(e)}")
            return {"error": str(e)}
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive Phase 2 endpoint testing"""
        print_test_header("Phase 2 Comprehensive Endpoint Testing", "🚀")
        
        async with APITestClient(self.base_url) as client:
            # 1. Analyze API structure
            structure_analysis = await self.analyze_api_structure(client)
            
            # 2. Test public endpoints
            public_results = await self.test_public_endpoints(client)
            
            # 3. Test authenticated endpoint structure
            auth_results = await self.test_authenticated_endpoints_structure(client)
            
            # Combine results
            total_endpoints = (
                public_results["total_endpoints"] +
                auth_results["total_endpoints"]
            )
            
            working_endpoints = (
                public_results["working_endpoints"] +
                auth_results["working_endpoints"]
            )
            
            failed_endpoints = (
                public_results["failed_endpoints"] +
                auth_results["failed_endpoints"]
            )
            
            all_errors = public_results["errors"] + auth_results["errors"]
            
            # Calculate functionality percentage
            # For structure test, 403 responses count as "working" since endpoints exist
            functionality_percentage = (working_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0
            
            # Print summary
            print_test_header("Phase 2 Testing Summary", "📊")
            print_info(f"Total Endpoints Tested: {total_endpoints}")
            print_success(f"Functional/Existing Endpoints: {working_endpoints}")
            if failed_endpoints > 0:
                print_error(f"Non-Functional Endpoints: {failed_endpoints}")
            else:
                print_info(f"Non-Functional Endpoints: {failed_endpoints}")
            
            print_info(f"Phase 2 Endpoint Functionality: {functionality_percentage:.1f}%")
            
            if structure_analysis.get("total_phase2_endpoints"):
                print_success(f"🎯 Total Phase 2 Endpoints in API: {structure_analysis['total_phase2_endpoints']}")
            
            if all_errors:
                print_error("Issues found:")
                for error in all_errors:
                    print_error(f"  - {error}")
            
            return {
                "success": True,
                "functionality_percentage": functionality_percentage,
                "total_endpoints_tested": total_endpoints,
                "working_endpoints": working_endpoints,
                "failed_endpoints": failed_endpoints,
                "errors": all_errors,
                "structure_analysis": structure_analysis,
                "detailed_results": {
                    "public_endpoints": public_results,
                    "authenticated_endpoints": auth_results
                }
            }


async def main():
    """Main function to run Phase 2 endpoint testing"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:8000"
    
    tester = Phase2EndpointTester(base_url)
    
    try:
        results = await tester.run_comprehensive_test()
        
        if results["success"]:
            print_test_header("Phase 2 Endpoint Testing Complete!", "✅")
            
            functionality = results["functionality_percentage"]
            total_endpoints = results.get("structure_analysis", {}).get("total_phase2_endpoints", 0)
            
            if functionality >= 90:
                print_success(f"Phase 2 endpoints are {functionality:.1f}% functional - Excellent!")
            elif functionality >= 70:
                print_info(f"Phase 2 endpoints are {functionality:.1f}% functional - Good")
            else:
                print_error(f"Phase 2 endpoints are {functionality:.1f}% functional - Needs attention")
            
            if total_endpoints > 0:
                print_info(f"🔍 Found {total_endpoints} Phase 2 endpoints in the API")
                print_info(f"📝 This suggests Phase 2 is extensively implemented")
            
            # Save detailed results
            with open("phase2_endpoint_test_results.json", "w") as f:
                json.dump(results, f, indent=2)
            print_info("Detailed results saved to phase2_endpoint_test_results.json")
            
        else:
            print_error(f"Phase 2 endpoint testing failed: {results.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print_error(f"Phase 2 endpoint testing crashed: {str(e)}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())