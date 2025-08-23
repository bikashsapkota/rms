"""
API tests for reservation management endpoints.
"""

import asyncio
import aiohttp
from datetime import date, time, timedelta
from typing import Dict, Any
from tests.api_tester.shared.auth import authenticate_user
from tests.api_tester.shared.utils import print_test_header, print_success, print_error


class ReservationManagementTester:
    """Test reservation management API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.headers = {"Content-Type": "application/json"}
        
    async def run_all_tests(self):
        """Run all reservation management tests."""
        print_test_header("Reservation Management API Tests")
        
        async with aiohttp.ClientSession() as session:
            # Authenticate first
            access_token = await authenticate_user(session, self.api_base)
            if not access_token:
                print_error("Authentication failed - cannot run reservation tests")
                return False
            
            self.headers["Authorization"] = f"Bearer {access_token}"
            
            # Create a table first for reservation tests
            table_id = await self.create_test_table(session)
            if not table_id:
                print_error("Failed to create test table - cannot run reservation tests")
                return False
            
            # Run test sequence
            test_results = []
            
            # Test reservation creation
            test_results.append(await self.test_create_reservation(session, table_id))
            
            # Test getting reservations
            test_results.append(await self.test_get_reservations(session))
            
            # Test reservation operations
            if hasattr(self, 'created_reservation_id'):
                test_results.append(await self.test_get_reservation_details(session))
                test_results.append(await self.test_update_reservation(session))
                test_results.append(await self.test_assign_table(session, table_id))
                test_results.append(await self.test_checkin_reservation(session))
                test_results.append(await self.test_reservation_analytics(session))
                test_results.append(await self.test_today_reservations(session))
                test_results.append(await self.test_reservation_calendar(session))
                
                # Test cancellation last
                test_results.append(await self.test_cancel_reservation(session))
            
            # Cleanup
            await self.cleanup_test_table(session, table_id)
            
            # Summary
            passed = sum(test_results)
            total = len(test_results)
            print(f"\nReservation Management Tests Summary: {passed}/{total} passed")
            
            return passed == total
    
    async def create_test_table(self, session: aiohttp.ClientSession) -> str:
        """Create a test table for reservation tests."""
        table_data = {
            "table_number": "T_TEST",
            "capacity": 4,
            "location": "test_area",
        }
        
        try:
            async with session.post(
                f"{self.api_base}/tables/",
                json=table_data,
                headers=self.headers
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data["id"]
        except Exception:
            pass
        return None
    
    async def cleanup_test_table(self, session: aiohttp.ClientSession, table_id: str):
        """Clean up test table."""
        try:
            async with session.delete(
                f"{self.api_base}/tables/{table_id}",
                headers=self.headers
            ) as response:
                pass
        except Exception:
            pass
    
    async def test_create_reservation(self, session: aiohttp.ClientSession, table_id: str) -> bool:
        """Test creating a new reservation."""
        print("\n🔧 Testing reservation creation...")
        
        tomorrow = date.today() + timedelta(days=1)
        reservation_data = {
            "customer_name": "John Doe",
            "customer_phone": "+1234567890",
            "customer_email": "john@example.com",
            "party_size": 2,
            "reservation_date": tomorrow.isoformat(),
            "reservation_time": "19:00:00",
            "duration_minutes": 90,
            "table_id": table_id,
            "special_requests": "Window table preferred",
            "customer_preferences": {"dietary": "vegetarian"}
        }
        
        try:
            async with session.post(
                f"{self.api_base}/reservations/",
                json=reservation_data,
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    self.created_reservation_id = data["id"]
                    print_success(f"Reservation created successfully for {data['customer_name']}")
                    print(f"  📅 Date: {data['reservation_date']}")
                    print(f"  🕐 Time: {data['reservation_time']}")
                    print(f"  👥 Party Size: {data['party_size']}")
                    print(f"  📊 Status: {data['status']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Reservation creation failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Reservation creation request failed: {e}")
            return False
    
    async def test_get_reservations(self, session: aiohttp.ClientSession) -> bool:
        """Test getting all reservations."""
        print("\n📋 Testing reservation listing...")
        
        try:
            async with session.get(
                f"{self.api_base}/reservations/",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    reservations = await response.json()
                    print_success(f"Retrieved {len(reservations)} reservations")
                    
                    for reservation in reservations:
                        table_info = f" (Table {reservation['table_number']})" if reservation['table_number'] else " (No table assigned)"
                        print(f"  📅 {reservation['customer_name']}: {reservation['reservation_date']} {reservation['reservation_time']}{table_info}")
                    
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Reservation listing failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Reservation listing request failed: {e}")
            return False
    
    async def test_get_reservation_details(self, session: aiohttp.ClientSession) -> bool:
        """Test getting reservation details."""
        print("\n🔍 Testing reservation details retrieval...")
        
        try:
            async with session.get(
                f"{self.api_base}/reservations/{self.created_reservation_id}",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    reservation = await response.json()
                    print_success("Reservation details retrieved successfully")
                    print(f"  👤 Customer: {reservation['customer_name']}")
                    print(f"  📞 Phone: {reservation['customer_phone']}")
                    print(f"  👥 Party Size: {reservation['party_size']}")
                    print(f"  📊 Status: {reservation['status']}")
                    print(f"  🪑 Table: {reservation['table_number'] or 'Not assigned'}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Reservation details failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Reservation details request failed: {e}")
            return False
    
    async def test_update_reservation(self, session: aiohttp.ClientSession) -> bool:
        """Test updating a reservation."""
        print("\n✏️ Testing reservation update...")
        
        update_data = {
            "party_size": 4,
            "special_requests": "Birthday celebration - need cake table",
            "customer_preferences": {"dietary": "vegetarian", "occasion": "birthday"}
        }
        
        try:
            async with session.put(
                f"{self.api_base}/reservations/{self.created_reservation_id}",
                json=update_data,
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    reservation = await response.json()
                    print_success("Reservation updated successfully")
                    print(f"  👥 New Party Size: {reservation['party_size']}")
                    print(f"  📝 Special Requests: {reservation['special_requests']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Reservation update failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Reservation update request failed: {e}")
            return False
    
    async def test_assign_table(self, session: aiohttp.ClientSession, table_id: str) -> bool:
        """Test assigning a table to reservation."""
        print("\n🪑 Testing table assignment...")
        
        assign_data = {
            "table_id": table_id
        }
        
        try:
            async with session.post(
                f"{self.api_base}/reservations/{self.created_reservation_id}/seat",
                json=assign_data,
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    reservation = await response.json()
                    print_success("Table assigned successfully")
                    print(f"  🪑 Table ID: {reservation['table_id']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Table assignment failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Table assignment request failed: {e}")
            return False
    
    async def test_checkin_reservation(self, session: aiohttp.ClientSession) -> bool:
        """Test checking in a reservation."""
        print("\n✅ Testing reservation check-in...")
        
        checkin_data = {
            "notes": "Customer arrived on time"
        }
        
        try:
            async with session.post(
                f"{self.api_base}/reservations/{self.created_reservation_id}/checkin",
                json=checkin_data,
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    reservation = await response.json()
                    print_success(f"Customer checked in - Status: {reservation['status']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Reservation check-in failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Reservation check-in request failed: {e}")
            return False
    
    async def test_today_reservations(self, session: aiohttp.ClientSession) -> bool:
        """Test getting today's reservations."""
        print("\n📅 Testing today's reservations...")
        
        try:
            async with session.get(
                f"{self.api_base}/reservations/today/overview",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    overview = await response.json()
                    print_success(f"Today's reservations: {overview['total_reservations']}")
                    print(f"  📅 Date: {overview['date']}")
                    for reservation in overview['reservations']:
                        print(f"    👤 {reservation['customer_name']}: {reservation['reservation_time']} ({reservation['status']})")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Today's reservations failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Today's reservations request failed: {e}")
            return False
    
    async def test_reservation_calendar(self, session: aiohttp.ClientSession) -> bool:
        """Test getting reservation calendar."""
        print("\n📆 Testing reservation calendar...")
        
        today = date.today()
        end_date = today + timedelta(days=7)
        
        try:
            async with session.get(
                f"{self.api_base}/reservations/calendar/view?start_date={today.isoformat()}&end_date={end_date.isoformat()}",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    calendar = await response.json()
                    print_success("Reservation calendar retrieved successfully")
                    print(f"  📅 Period: {calendar['start_date']} to {calendar['end_date']}")
                    
                    reservation_dates = list(calendar['reservations_by_date'].keys())
                    print(f"  📊 Dates with reservations: {len(reservation_dates)}")
                    
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Reservation calendar failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Reservation calendar request failed: {e}")
            return False
    
    async def test_reservation_analytics(self, session: aiohttp.ClientSession) -> bool:
        """Test getting reservation analytics."""
        print("\n📈 Testing reservation analytics...")
        
        start_date = date.today() - timedelta(days=30)
        end_date = date.today()
        
        try:
            async with session.get(
                f"{self.api_base}/reservations/analytics/summary?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    analytics = await response.json()
                    print_success("Reservation analytics retrieved successfully")
                    print(f"  📊 Total Reservations: {analytics['total_reservations']}")
                    print(f"  ✅ Completion Rate: {analytics['completion_rate']}%")
                    print(f"  🚫 No-show Rate: {analytics['no_show_rate']}%")
                    print(f"  👥 Average Party Size: {analytics['average_party_size']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Reservation analytics failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Reservation analytics request failed: {e}")
            return False
    
    async def test_cancel_reservation(self, session: aiohttp.ClientSession) -> bool:
        """Test cancelling a reservation."""
        print("\n❌ Testing reservation cancellation...")
        
        try:
            async with session.delete(
                f"{self.api_base}/reservations/{self.created_reservation_id}",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print_success(f"Reservation cancelled: {result['message']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Reservation cancellation failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Reservation cancellation request failed: {e}")
            return False


async def main():
    """Run reservation management tests."""
    tester = ReservationManagementTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())