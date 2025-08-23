"""
API tests for table management endpoints.
"""

import asyncio
import aiohttp
from datetime import date, time
from typing import Dict, Any
from tests.api_tester.shared.auth import authenticate_user
from tests.api_tester.shared.utils import print_test_header, print_success, print_error


class TableManagementTester:
    """Test table management API endpoints."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.headers = {"Content-Type": "application/json"}
        
    async def run_all_tests(self):
        """Run all table management tests."""
        print_test_header("Table Management API Tests")
        
        async with aiohttp.ClientSession() as session:
            # Authenticate first
            access_token = await authenticate_user(session, self.api_base)
            if not access_token:
                print_error("Authentication failed - cannot run table tests")
                return False
            
            self.headers["Authorization"] = f"Bearer {access_token}"
            
            # Run test sequence
            test_results = []
            
            # Test table creation
            test_results.append(await self.test_create_table(session))
            
            # Test getting tables
            test_results.append(await self.test_get_tables(session))
            
            # Test table details
            if hasattr(self, 'created_table_id'):
                test_results.append(await self.test_get_table_details(session))
                test_results.append(await self.test_update_table(session))
                test_results.append(await self.test_update_table_status(session))
                test_results.append(await self.test_restaurant_layout(session))
                test_results.append(await self.test_availability_overview(session))
                test_results.append(await self.test_table_analytics(session))
                
                # Test deletion last
                test_results.append(await self.test_delete_table(session))
            
            # Summary
            passed = sum(test_results)
            total = len(test_results)
            print(f"\nTable Management Tests Summary: {passed}/{total} passed")
            
            return passed == total
    
    async def test_create_table(self, session: aiohttp.ClientSession) -> bool:
        """Test creating a new table."""
        print("\n🔧 Testing table creation...")
        
        table_data = {
            "table_number": "T001",
            "capacity": 4,
            "location": "main_dining",
            "coordinates": {"x": 100, "y": 200},
        }
        
        try:
            async with session.post(
                f"{self.api_base}/tables/",
                json=table_data,
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    data = await response.json()
                    self.created_table_id = data["id"]
                    print_success(f"Table created successfully: {data['table_number']}")
                    print(f"  📍 Location: {data['location']}")
                    print(f"  👥 Capacity: {data['capacity']}")
                    print(f"  📊 Status: {data['status']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Table creation failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Table creation request failed: {e}")
            return False
    
    async def test_get_tables(self, session: aiohttp.ClientSession) -> bool:
        """Test getting all tables."""
        print("\n📋 Testing table listing...")
        
        try:
            async with session.get(
                f"{self.api_base}/tables/",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    tables = await response.json()
                    print_success(f"Retrieved {len(tables)} tables")
                    
                    for table in tables:
                        print(f"  🪑 {table['table_number']}: {table['capacity']} seats ({table['status']})")
                    
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Table listing failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Table listing request failed: {e}")
            return False
    
    async def test_get_table_details(self, session: aiohttp.ClientSession) -> bool:
        """Test getting table details."""
        print("\n🔍 Testing table details retrieval...")
        
        try:
            async with session.get(
                f"{self.api_base}/tables/{self.created_table_id}",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    table = await response.json()
                    print_success("Table details retrieved successfully")
                    print(f"  🪑 Table: {table['table_number']}")
                    print(f"  👥 Capacity: {table['capacity']}")
                    print(f"  📊 Status: {table['status']}")
                    print(f"  📈 Active Reservations: {table['active_reservations']}")
                    print(f"  📅 Upcoming Reservations: {table['upcoming_reservations']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Table details failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Table details request failed: {e}")
            return False
    
    async def test_update_table(self, session: aiohttp.ClientSession) -> bool:
        """Test updating a table."""
        print("\n✏️ Testing table update...")
        
        update_data = {
            "capacity": 6,
            "location": "patio",
            "coordinates": {"x": 150, "y": 250},
        }
        
        try:
            async with session.put(
                f"{self.api_base}/tables/{self.created_table_id}",
                json=update_data,
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    table = await response.json()
                    print_success("Table updated successfully")
                    print(f"  👥 New Capacity: {table['capacity']}")
                    print(f"  📍 New Location: {table['location']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Table update failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Table update request failed: {e}")
            return False
    
    async def test_update_table_status(self, session: aiohttp.ClientSession) -> bool:
        """Test updating table status."""
        print("\n🔄 Testing table status update...")
        
        status_data = {
            "status": "maintenance",
            "notes": "Cleaning in progress"
        }
        
        try:
            async with session.put(
                f"{self.api_base}/tables/{self.created_table_id}/status",
                json=status_data,
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    table = await response.json()
                    print_success(f"Table status updated to: {table['status']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Table status update failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Table status update request failed: {e}")
            return False
    
    async def test_restaurant_layout(self, session: aiohttp.ClientSession) -> bool:
        """Test getting restaurant layout."""
        print("\n🏗️ Testing restaurant layout...")
        
        try:
            async with session.get(
                f"{self.api_base}/tables/layout/restaurant",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    layout = await response.json()
                    print_success("Restaurant layout retrieved successfully")
                    print(f"  🪑 Total Tables: {layout['layout_settings']['total_tables']}")
                    print(f"  👥 Total Capacity: {layout['layout_settings']['total_capacity']}")
                    print(f"  📍 Locations: {', '.join(layout['layout_settings']['locations'])}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Restaurant layout failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Restaurant layout request failed: {e}")
            return False
    
    async def test_availability_overview(self, session: aiohttp.ClientSession) -> bool:
        """Test getting availability overview."""
        print("\n📊 Testing availability overview...")
        
        try:
            async with session.get(
                f"{self.api_base}/tables/availability/overview",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    overview = await response.json()
                    print_success("Availability overview retrieved successfully")
                    print(f"  🪑 Total Tables: {overview['total_tables']}")
                    print(f"  👥 Total Capacity: {overview['total_capacity']}")
                    print(f"  ✅ Available: {overview['available_tables']}")
                    print(f"  🚫 Occupied: {overview['occupied_tables']}")
                    print(f"  📅 Reserved: {overview['reserved_tables']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Availability overview failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Availability overview request failed: {e}")
            return False
    
    async def test_table_analytics(self, session: aiohttp.ClientSession) -> bool:
        """Test getting table analytics."""
        print("\n📈 Testing table analytics...")
        
        try:
            async with session.get(
                f"{self.api_base}/tables/analytics/utilization?days_back=30",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    analytics = await response.json()
                    print_success("Table analytics retrieved successfully")
                    print(f"  🪑 Total Tables: {analytics['total_tables']}")
                    print(f"  📅 Recent Reservations: {analytics['recent_reservations']}")
                    print(f"  📊 Utilization Rate: {analytics['utilization_rate']}%")
                    print(f"  📝 Recommendations: {len(analytics['recommendations'])}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Table analytics failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Table analytics request failed: {e}")
            return False
    
    async def test_delete_table(self, session: aiohttp.ClientSession) -> bool:
        """Test deleting a table."""
        print("\n🗑️ Testing table deletion...")
        
        try:
            async with session.delete(
                f"{self.api_base}/tables/{self.created_table_id}",
                headers=self.headers
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    print_success(f"Table deleted: {result['message']}")
                    return True
                else:
                    error_data = await response.json()
                    print_error(f"Table deletion failed: {error_data.get('detail', 'Unknown error')}")
                    return False
                    
        except Exception as e:
            print_error(f"Table deletion request failed: {e}")
            return False


async def main():
    """Run table management tests."""
    tester = TableManagementTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())