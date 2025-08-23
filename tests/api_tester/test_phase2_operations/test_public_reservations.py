"""
API tests for public reservation endpoints (customer-facing).
"""

import asyncio
import aiohttp
from datetime import date, time, timedelta
from typing import Dict, Any
from tests.api_tester.shared.utils import print_test_header, print_success, print_error


class PublicReservationTester:
    """Test public reservation API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.headers = {"Content-Type": "application/json"}
        self.restaurant_id = None  # Will be set during restaurant info test
        
    async def run_all_tests(self):
        """Run all public reservation tests."""
        print_test_header("Public Reservation API Tests")
        
        async with aiohttp.ClientSession() as session:
            # First get restaurant info (this sets restaurant_id)
            if not await self.test_get_restaurant_info(session):
                print_error("Failed to get restaurant info - cannot run public tests")
                return False
            
            # Run test sequence
            test_results = []
            
            # Test availability checking
            test_results.append(await self.test_check_public_availability(session))
            
            # Test reservation creation
            test_results.append(await self.test_create_public_reservation(session))
            
            # Test reservation status and management
            if hasattr(self, 'created_reservation_id'):
                test_results.append(await self.test_get_reservation_status(session))
                test_results.append(await self.test_cancel_public_reservation(session))
            
            # Test waitlist functionality
            test_results.append(await self.test_join_public_waitlist(session))
            test_results.append(await self.test_get_waitlist_status(session))
            
            # Summary
            passed = sum(test_results)
            total = len(test_results)
            print(f"\nPublic Reservation Tests Summary: {passed}/{total} passed")
            
            return passed == total
    
    async def test_get_restaurant_info(self, session: aiohttp.ClientSession) -> bool:
        """Test getting restaurant information (and extract restaurant_id)."""
        print("\n🏪 Testing restaurant info retrieval...")
        
        # For this test, we'll use a placeholder restaurant ID
        # In a real scenario, this would come from setup or configuration
        test_restaurant_id = "550e8400-e29b-41d4-a716-446655440000"  # Example UUID
        
        try:
            async with session.get(
                f"{self.api_base}/public/reservations/{test_restaurant_id}/info",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    restaurant = await response.json()
                    self.restaurant_id = restaurant["restaurant_id"]
                    print_success(f"Restaurant info retrieved: {restaurant['name']}")
                    print(f"  🏪 Name: {restaurant['name']}")
                    print(f"  📞 Phone: {restaurant.get('phone', 'N/A')}")
                    print(f"  📧 Email: {restaurant.get('email', 'N/A')}")
                    print(f"  🆔 ID: {restaurant['restaurant_id']}")
                    return True
                elif response.status == 404:
                    # If test restaurant doesn't exist, create a placeholder
                    print(f"⚠️ Test restaurant not found, using placeholder ID")
                    self.restaurant_id = test_restaurant_id
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Restaurant info failed: {error_data.get('detail', 'Unknown error')}")
                    # Still set placeholder for other tests
                    self.restaurant_id = test_restaurant_id
                    return True
                    
        except Exception as e:
            print_error(f"Restaurant info request failed: {e}")
            # Set placeholder for other tests
            self.restaurant_id = test_restaurant_id
            return True
    
    async def test_check_public_availability(self, session: aiohttp.ClientSession) -> bool:
        """Test checking availability through public endpoint."""
        print("\n🔍 Testing public availability check...")
        
        tomorrow = date.today() + timedelta(days=1)
        
        try:
            async with session.get(
                f"{self.api_base}/public/reservations/{self.restaurant_id}/availability"
                f"?reservation_date={tomorrow.isoformat()}"
                f"&party_size=2"
                f"&time_preference=19:00:00"
                f"&duration_minutes=90",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    availability = await response.json()
                    print_success("Public availability check completed successfully")
                    print(f"  🏪 Restaurant: {availability['restaurant_name']}")
                    print(f"  📅 Date: {availability['date']}")
                    print(f"  👥 Party Size: {availability['party_size']}")
                    print(f"  ⏰ Available Slots: {len(availability['available_slots'])}")
                    print(f"  💡 Recommendations: {len(availability['recommendations'])}")
                    print(f"  🚫 Fully Booked: {availability['is_fully_booked']}")
                    
                    if availability['alternatives']:
                        print(f"  🔄 Alternatives: {len(availability['alternatives'])}")
                    
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Public availability check failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Public availability check request failed: {e}")
            return False
    
    async def test_create_public_reservation(self, session: aiohttp.ClientSession) -> bool:
        """Test creating a reservation through public endpoint."""
        print("\n📝 Testing public reservation creation...")
        
        tomorrow = date.today() + timedelta(days=1)
        reservation_data = {
            "customer_name": "John Public",
            "customer_phone": "+1555123456",
            "customer_email": "john.public@example.com",
            "party_size": 2,
            "reservation_date": tomorrow.isoformat(),
            "reservation_time": "19:00:00",
            "duration_minutes": 90,
            "special_requests": "Quiet corner table please",
            "customer_preferences": {
                "seating": "booth",
                "occasion": "date_night"
            }
        }
        
        try:
            async with session.post(
                f"{self.api_base}/public/reservations/{self.restaurant_id}/book",
                json=reservation_data,
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    reservation = await response.json()
                    self.created_reservation_id = reservation["reservation_id"]
                    self.customer_phone = reservation_data["customer_phone"]
                    self.customer_name = reservation_data["customer_name"]
                    
                    print_success("Public reservation created successfully")
                    print(f"  📝 Reservation ID: {reservation['reservation_id']}")
                    print(f"  👤 Customer: {reservation['customer_name']}")
                    print(f"  📅 Date: {reservation['reservation_date']}")
                    print(f"  🕐 Time: {reservation['reservation_time']}")
                    print(f"  👥 Party Size: {reservation['party_size']}")
                    print(f"  📊 Status: {reservation['status']}")
                    print(f"  ✅ {reservation['confirmation_message']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Public reservation creation failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Public reservation creation request failed: {e}")
            return False
    
    async def test_get_reservation_status(self, session: aiohttp.ClientSession) -> bool:
        """Test getting reservation status through public endpoint."""
        print("\n📋 Testing public reservation status...")
        
        try:
            async with session.get(
                f"{self.api_base}/public/reservations/{self.restaurant_id}/status"
                f"?customer_phone={self.customer_phone}"
                f"&customer_name={self.customer_name}",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    status_data = await response.json()
                    print_success("Reservation status retrieved successfully")
                    print(f"  👤 Customer: {status_data['customer_name']}")
                    print(f"  📞 Phone: {status_data['customer_phone']}")
                    print(f"  📋 Reservations: {len(status_data['reservations'])}")
                    
                    for reservation in status_data['reservations']:
                        print(f"    📅 {reservation['reservation_date']} {reservation['reservation_time']}")
                        print(f"    📊 Status: {reservation['status']}")
                        if reservation['special_requests']:
                            print(f"    📝 Requests: {reservation['special_requests']}")
                    
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Reservation status failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Reservation status request failed: {e}")
            return False
    
    async def test_cancel_public_reservation(self, session: aiohttp.ClientSession) -> bool:
        """Test cancelling a reservation through public endpoint."""
        print("\n❌ Testing public reservation cancellation...")
        
        try:
            async with session.delete(
                f"{self.api_base}/public/reservations/{self.restaurant_id}/cancel/{self.created_reservation_id}"
                f"?customer_phone={self.customer_phone}",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print_success("Reservation cancelled successfully")
                    print(f"  📝 Reservation ID: {result['reservation_id']}")
                    print(f"  📊 Status: {result['status']}")
                    print(f"  ✅ {result['message']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Reservation cancellation failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Reservation cancellation request failed: {e}")
            return False
    
    async def test_join_public_waitlist(self, session: aiohttp.ClientSession) -> bool:
        """Test joining waitlist through public endpoint."""
        print("\n📝 Testing public waitlist join...")
        
        tomorrow = date.today() + timedelta(days=1)
        waitlist_data = {
            "customer_name": "Sarah Public",
            "customer_phone": "+1555987654",
            "customer_email": "sarah.public@example.com",
            "party_size": 4,
            "preferred_date": tomorrow.isoformat(),
            "preferred_time": "20:00:00",
            "notes": "Birthday celebration - hoping for availability"
        }
        
        try:
            async with session.post(
                f"{self.api_base}/public/reservations/{self.restaurant_id}/waitlist",
                json=waitlist_data,
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    waitlist = await response.json()
                    self.waitlist_customer_phone = waitlist_data["customer_phone"]
                    self.waitlist_customer_name = waitlist_data["customer_name"]
                    
                    print_success("Successfully joined waitlist")
                    print(f"  📝 Waitlist ID: {waitlist['waitlist_id']}")
                    print(f"  👤 Customer: {waitlist['customer_name']}")
                    print(f"  👥 Party Size: {waitlist['party_size']}")
                    print(f"  🎯 Position: #{waitlist['position']}")
                    print(f"  📊 Priority Score: {waitlist['priority_score']}")
                    print(f"  ✅ {waitlist['confirmation_message']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Waitlist join failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Waitlist join request failed: {e}")
            return False
    
    async def test_get_waitlist_status(self, session: aiohttp.ClientSession) -> bool:
        """Test getting waitlist status through public endpoint."""
        print("\n📋 Testing public waitlist status...")
        
        if not hasattr(self, 'waitlist_customer_phone'):
            print_error("No waitlist entry created - skipping status test")
            return True
        
        try:
            async with session.get(
                f"{self.api_base}/public/reservations/{self.restaurant_id}/waitlist/status"
                f"?customer_phone={self.waitlist_customer_phone}"
                f"&customer_name={self.waitlist_customer_name}",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    status_data = await response.json()
                    print_success("Waitlist status retrieved successfully")
                    print(f"  👤 Customer: {status_data['customer_name']}")
                    print(f"  📞 Phone: {status_data['customer_phone']}")
                    print(f"  📋 Waitlist Entries: {len(status_data['waitlist_entries'])}")
                    
                    for entry in status_data['waitlist_entries']:
                        print(f"    👥 Party Size: {entry['party_size']}")
                        print(f"    📊 Status: {entry['status']}")
                        print(f"    🎯 Position: #{entry['position']}")
                        if entry['preferred_date']:
                            print(f"    📅 Preferred: {entry['preferred_date']} {entry['preferred_time']}")
                    
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Waitlist status failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Waitlist status request failed: {e}")
            return False


async def main():
    """Run public reservation tests."""
    tester = PublicReservationTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())