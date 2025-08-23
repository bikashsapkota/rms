"""
API tests for availability checking and waitlist management endpoints.
"""

import asyncio
import aiohttp
from datetime import date, time, timedelta
from typing import Dict, Any
from tests.api_tester.shared.auth import authenticate_user
from tests.api_tester.shared.utils import print_test_header, print_success, print_error


class AvailabilityAndWaitlistTester:
    """Test availability and waitlist management API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.headers = {"Content-Type": "application/json"}
        
    async def run_all_tests(self):
        """Run all availability and waitlist tests."""
        print_test_header("Availability & Waitlist Management API Tests")
        
        async with aiohttp.ClientSession() as session:
            # Authenticate first
            access_token = await authenticate_user(session, self.api_base)
            if not access_token:
                print_error("Authentication failed - cannot run availability tests")
                return False
            
            self.headers["Authorization"] = f"Bearer {access_token}"
            
            # Create test tables first
            table_ids = await self.create_test_tables(session)
            if not table_ids:
                print_error("Failed to create test tables - cannot run availability tests")
                return False
            
            # Run test sequence
            test_results = []
            
            # Availability tests
            test_results.append(await self.test_check_availability(session))
            test_results.append(await self.test_availability_calendar(session))
            test_results.append(await self.test_find_alternatives(session))
            test_results.append(await self.test_capacity_optimization(session))
            test_results.append(await self.test_availability_overview(session))
            
            # Waitlist tests
            test_results.append(await self.test_add_to_waitlist(session))
            test_results.append(await self.test_get_waitlist(session))
            
            if hasattr(self, 'created_waitlist_id'):
                test_results.append(await self.test_get_waitlist_entry(session))
                test_results.append(await self.test_update_waitlist_entry(session))
                test_results.append(await self.test_notify_waitlist_customer(session))
                test_results.append(await self.test_waitlist_availability_check(session))
                test_results.append(await self.test_waitlist_analytics(session))
                
                # Cleanup waitlist entry
                test_results.append(await self.test_remove_from_waitlist(session))
            
            # Cleanup test tables
            await self.cleanup_test_tables(session, table_ids)
            
            # Summary
            passed = sum(test_results)
            total = len(test_results)
            print(f"\nAvailability & Waitlist Tests Summary: {passed}/{total} passed")
            
            return passed == total
    
    async def create_test_tables(self, session: aiohttp.ClientSession) -> list:
        """Create test tables for availability tests."""
        table_ids = []
        
        for i in range(3):
            table_data = {
                "table_number": f"T_AVAIL_{i+1}",
                "capacity": 4,
                "location": "test_dining",
            }
            
            try:
                async with session.post(
                    f"{self.api_base}/tables/",
                    json=table_data,
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        table_ids.append(data["id"])
            except Exception:
                pass
        
        return table_ids
    
    async def cleanup_test_tables(self, session: aiohttp.ClientSession, table_ids: list):
        """Clean up test tables."""
        for table_id in table_ids:
            try:
                async with session.delete(
                    f"{self.api_base}/tables/{table_id}",
                    headers=self.headers
                ) as response:
                    pass
            except Exception:
                pass
    
    async def test_check_availability(self, session: aiohttp.ClientSession) -> bool:
        """Test checking availability for a specific date and party size."""
        print("\n🔍 Testing availability checking...")
        
        tomorrow = date.today() + timedelta(days=1)
        
        try:
            async with session.get(
                f"{self.api_base}/availability/slots"
                f"?reservation_date={tomorrow.isoformat()}"
                f"&party_size=2"
                f"&time_preference=19:00:00"
                f"&duration_minutes=90",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    availability = await response.json()
                    print_success("Availability check completed successfully")
                    print(f"  📅 Date: {availability['date']}")
                    print(f"  👥 Party Size: {availability['party_size']}")
                    print(f"  ⏰ Available Slots: {len(availability['available_slots'])}")
                    print(f"  💡 Recommendations: {len(availability['recommendations'])}")
                    print(f"  🚫 Fully Booked: {availability['is_fully_booked']}")
                    
                    if availability['available_slots']:
                        print("  📋 Sample slots:")
                        for slot in availability['available_slots'][:3]:
                            print(f"    🕐 {slot['time']}: {slot['available_tables']} tables available")
                    
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Availability check failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Availability check request failed: {e}")
            return False
    
    async def test_availability_calendar(self, session: aiohttp.ClientSession) -> bool:
        """Test getting availability calendar."""
        print("\n📅 Testing availability calendar...")
        
        today = date.today()
        
        try:
            async with session.get(
                f"{self.api_base}/availability/calendar?year={today.year}&month={today.month}",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    calendar = await response.json()
                    print_success("Availability calendar retrieved successfully")
                    print(f"  📅 Year: {calendar['year']}, Month: {calendar['month']}")
                    print(f"  📊 Days in month: {len(calendar['days'])}")
                    
                    # Count available days
                    available_days = sum(1 for day in calendar['days'] if day['is_open'])
                    print(f"  ✅ Available days: {available_days}")
                    
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Availability calendar failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Availability calendar request failed: {e}")
            return False
    
    async def test_find_alternatives(self, session: aiohttp.ClientSession) -> bool:
        """Test finding alternative time slots."""
        print("\n🔄 Testing alternative slot finding...")
        
        tomorrow = date.today() + timedelta(days=1)
        
        try:
            async with session.get(
                f"{self.api_base}/availability/alternatives"
                f"?preferred_date={tomorrow.isoformat()}"
                f"&preferred_time=19:00:00"
                f"&party_size=4"
                f"&duration_minutes=90",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    alternatives = await response.json()
                    print_success(f"Found {len(alternatives)} alternative slots")
                    
                    for i, slot in enumerate(alternatives[:3]):
                        print(f"  {i+1}. 🕐 {slot['time']}: {slot['available_tables']} tables")
                    
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Alternative slots failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Alternative slots request failed: {e}")
            return False
    
    async def test_capacity_optimization(self, session: aiohttp.ClientSession) -> bool:
        """Test capacity optimization suggestions."""
        print("\n📊 Testing capacity optimization...")
        
        today = date.today()
        
        try:
            async with session.get(
                f"{self.api_base}/availability/capacity/optimization?target_date={today.isoformat()}",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    optimization = await response.json()
                    print_success("Capacity optimization retrieved successfully")
                    print(f"  📅 Date: {optimization['date']}")
                    print(f"  📊 Occupancy Rate: {optimization['current_occupancy_rate']}%")
                    print(f"  🕐 Peak Hours: {len(optimization['peak_hours'])}")
                    print(f"  💡 Suggestions: {len(optimization['suggested_improvements'])}")
                    print(f"  📝 Recommendations: {len(optimization['recommended_actions'])}")
                    
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Capacity optimization failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Capacity optimization request failed: {e}")
            return False
    
    async def test_availability_overview(self, session: aiohttp.ClientSession) -> bool:
        """Test availability overview for date range."""
        print("\n📈 Testing availability overview...")
        
        start_date = date.today()
        end_date = start_date + timedelta(days=7)
        
        try:
            async with session.get(
                f"{self.api_base}/availability/overview"
                f"?start_date={start_date.isoformat()}"
                f"&end_date={end_date.isoformat()}",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    overview = await response.json()
                    print_success("Availability overview retrieved successfully")
                    print(f"  📅 Period: {overview['period']['start_date']} to {overview['period']['end_date']}")
                    print(f"  📊 Total Days: {overview['summary']['total_days']}")
                    print(f"  ✅ Available Days: {overview['summary']['available_days']}")
                    print(f"  🚫 Fully Booked Days: {overview['summary']['fully_booked_days']}")
                    
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Availability overview failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Availability overview request failed: {e}")
            return False
    
    async def test_add_to_waitlist(self, session: aiohttp.ClientSession) -> bool:
        """Test adding a customer to the waitlist."""
        print("\n📝 Testing waitlist addition...")
        
        tomorrow = date.today() + timedelta(days=1)
        waitlist_data = {
            "customer_name": "Jane Smith",
            "customer_phone": "+1987654321",
            "customer_email": "jane@example.com",
            "party_size": 6,
            "preferred_date": tomorrow.isoformat(),
            "preferred_time": "19:00:00",
            "notes": "Special anniversary dinner"
        }
        
        try:
            async with session.post(
                f"{self.api_base}/waitlist/",
                json=waitlist_data,
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    self.created_waitlist_id = data["id"]
                    print_success(f"Customer added to waitlist: {data['customer_name']}")
                    print(f"  👥 Party Size: {data['party_size']}")
                    print(f"  📅 Preferred Date: {data['preferred_date']}")
                    print(f"  🕐 Preferred Time: {data['preferred_time']}")
                    print(f"  📊 Priority Score: {data['priority_score']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Waitlist addition failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Waitlist addition request failed: {e}")
            return False
    
    async def test_get_waitlist(self, session: aiohttp.ClientSession) -> bool:
        """Test getting the current waitlist."""
        print("\n📋 Testing waitlist retrieval...")
        
        try:
            async with session.get(
                f"{self.api_base}/waitlist/",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    waitlist = await response.json()
                    print_success(f"Retrieved {len(waitlist)} waitlist entries")
                    
                    for entry in waitlist:
                        print(f"  👤 {entry['customer_name']}: {entry['party_size']} people ({entry['status']})")
                        print(f"    📊 Priority: {entry['priority_score']}")
                    
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Waitlist retrieval failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Waitlist retrieval request failed: {e}")
            return False
    
    async def test_get_waitlist_entry(self, session: aiohttp.ClientSession) -> bool:
        """Test getting a specific waitlist entry."""
        print("\n🔍 Testing waitlist entry details...")
        
        try:
            async with session.get(
                f"{self.api_base}/waitlist/{self.created_waitlist_id}",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    entry = await response.json()
                    print_success("Waitlist entry details retrieved successfully")
                    print(f"  👤 Customer: {entry['customer_name']}")
                    print(f"  📞 Phone: {entry['customer_phone']}")
                    print(f"  👥 Party Size: {entry['party_size']}")
                    print(f"  📊 Status: {entry['status']}")
                    print(f"  📝 Notes: {entry['notes']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Waitlist entry details failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Waitlist entry details request failed: {e}")
            return False
    
    async def test_update_waitlist_entry(self, session: aiohttp.ClientSession) -> bool:
        """Test updating a waitlist entry."""
        print("\n✏️ Testing waitlist entry update...")
        
        update_data = {
            "party_size": 4,
            "notes": "Updated: Reduced party size due to cancellation"
        }
        
        try:
            async with session.put(
                f"{self.api_base}/waitlist/{self.created_waitlist_id}",
                json=update_data,
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    entry = await response.json()
                    print_success("Waitlist entry updated successfully")
                    print(f"  👥 New Party Size: {entry['party_size']}")
                    print(f"  📝 Updated Notes: {entry['notes']}")
                    print(f"  📊 New Priority Score: {entry['priority_score']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Waitlist entry update failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Waitlist entry update request failed: {e}")
            return False
    
    async def test_notify_waitlist_customer(self, session: aiohttp.ClientSession) -> bool:
        """Test notifying a waitlist customer."""
        print("\n📢 Testing waitlist customer notification...")
        
        notify_data = {
            "message": "Table available for your party",
            "available_time": "19:30:00"
        }
        
        try:
            async with session.put(
                f"{self.api_base}/waitlist/{self.created_waitlist_id}/notify",
                json=notify_data,
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    entry = await response.json()
                    print_success(f"Customer notified - Status: {entry['status']}")
                    print(f"  📝 Notes updated with notification details")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Customer notification failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Customer notification request failed: {e}")
            return False
    
    async def test_waitlist_availability_check(self, session: aiohttp.ClientSession) -> bool:
        """Test checking availability for waitlist customers."""
        print("\n🔍 Testing waitlist availability check...")
        
        try:
            async with session.get(
                f"{self.api_base}/waitlist/availability/check",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    suggestions = await response.json()
                    print_success(f"Found {suggestions['total_suggestions']} notification suggestions")
                    
                    for suggestion in suggestions['notification_suggestions'][:2]:
                        customer = suggestion['waitlist_entry']['customer_name']
                        slot_time = suggestion['suggested_slot']['time']
                        match_quality = suggestion['match_quality']
                        print(f"  👤 {customer}: {slot_time} ({match_quality} match)")
                    
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Waitlist availability check failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Waitlist availability check request failed: {e}")
            return False
    
    async def test_waitlist_analytics(self, session: aiohttp.ClientSession) -> bool:
        """Test getting waitlist analytics."""
        print("\n📈 Testing waitlist analytics...")
        
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        try:
            async with session.get(
                f"{self.api_base}/waitlist/analytics/summary"
                f"?start_date={start_date.isoformat()}"
                f"&end_date={end_date.isoformat()}",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    analytics = await response.json()
                    print_success("Waitlist analytics retrieved successfully")
                    print(f"  📊 Total Entries: {analytics['total_waitlist_entries']}")
                    print(f"  🎯 Current Active: {analytics['current_active_waitlist']}")
                    print(f"  ✅ Conversion Rate: {analytics['conversion_rate']}%")
                    print(f"  👥 Average Party Size: {analytics['average_party_size']}")
                    print(f"  🪑 Seated Customers: {analytics['seated_customers']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Waitlist analytics failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Waitlist analytics request failed: {e}")
            return False
    
    async def test_remove_from_waitlist(self, session: aiohttp.ClientSession) -> bool:
        """Test removing a customer from the waitlist."""
        print("\n🗑️ Testing waitlist removal...")
        
        try:
            async with session.delete(
                f"{self.api_base}/waitlist/{self.created_waitlist_id}",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print_success(f"Customer removed from waitlist: {result['message']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Waitlist removal failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Waitlist removal request failed: {e}")
            return False


async def main():
    """Run availability and waitlist tests."""
    tester = AvailabilityAndWaitlistTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())