#!/usr/bin/env python3
"""
Generate Restaurants Test Data

Creates realistic restaurant data for RMS API testing.
Works with the Phase 1 restaurant setup process that auto-creates organizations.
"""

import sys
import asyncio
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.api_tester.shared.utils import APITestClient, APITestHelper
from tests.api_tester.shared.auth import get_auth_headers
from tests.api_tester.shared.fixtures import RMSTestFixtures


class RestaurantDataGenerator:
    """Generates restaurant test data via API calls"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.created_restaurants = []
        self.created_organizations = []  # Track auto-created organizations
        
    async def generate_restaurant(self, location_suffix: str = "") -> dict:
        """Generate a single restaurant (which auto-creates organization in Phase 1)"""
        
        try:
            # Get authentication headers
            headers = await get_auth_headers(self.client)
            if not headers:
                print("❌ Failed to authenticate - cannot create restaurants")
                return None
                
            # Generate restaurant data (without organization_id for Phase 1)
            restaurant_data = RMSTestFixtures.generate_restaurant_data("placeholder", location_suffix)
            
            # Remove organization_id for Phase 1 auto-creation
            if "organization_id" in restaurant_data:
                del restaurant_data["organization_id"]
                
            print(f"🍽️  Creating restaurant: {restaurant_data['name']}")
            print(f"   Cuisine: {restaurant_data['settings']['cuisine_type']}")
            print(f"   Location: {restaurant_data['address']['city']}, {restaurant_data['address']['state']}")
            
            # Try restaurant creation endpoint
            response = await self.client.post("/api/v1/restaurants", json=restaurant_data, headers=headers)
            
            if response.status_code == 201:
                restaurant_response = response.json()
                self.created_restaurants.append(restaurant_response)
                
                print(f"✅ Restaurant created successfully:")
                print(f"   Restaurant ID: {restaurant_response['id']}")
                print(f"   Name: {restaurant_response['name']}")
                print(f"   Organization ID: {restaurant_response.get('organization_id', 'N/A')}")
                
                return restaurant_response
                
            elif response.status_code == 404:
                # Try setup endpoint (Phase 1 pattern)
                print("🔄 Trying restaurant setup endpoint...")
                
                setup_data = {
                    "restaurant": restaurant_data,
                    "admin_user": {
                        "email": f"admin@{restaurant_data['name'].lower().replace(' ', '').replace('location', '')}.com",
                        "full_name": "Restaurant Admin",
                        "password": "admin_password_123"
                    }
                }
                
                response = await self.client.post("/api/v1/setup/restaurant", json=setup_data, headers=headers)
                
                if response.status_code == 201:
                    setup_response = response.json()
                    
                    # Extract restaurant and organization info
                    restaurant_info = setup_response.get("restaurant", setup_response)
                    org_info = setup_response.get("organization")
                    
                    self.created_restaurants.append(restaurant_info)
                    if org_info:
                        self.created_organizations.append(org_info)
                    
                    print(f"✅ Restaurant setup completed successfully:")
                    print(f"   Restaurant ID: {restaurant_info['id']}")
                    print(f"   Name: {restaurant_info['name']}")
                    if org_info:
                        print(f"   Organization: {org_info['name']} ({org_info['id']})")
                    
                    return restaurant_info
                else:
                    print(f"❌ Restaurant setup failed: HTTP {response.status_code}")
                    if response.json_data:
                        print(f"   Error: {response.json_data}")
                    return None
                    
            else:
                print(f"❌ Failed to create restaurant: HTTP {response.status_code}")
                if response.json_data:
                    print(f"   Error: {response.json_data}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating restaurant: {e}")
            return None
            
    async def generate_multiple_restaurants(self, count: int = 4) -> list:
        """Generate multiple restaurants with different characteristics"""
        
        restaurant_types = [
            "Downtown",
            "Mall", 
            "Suburban",
            "Waterfront",
            "Historic District",
            "Business District"
        ]
        
        all_restaurants = []
        
        print(f"\n🏗️  Generating {count} restaurants")
        
        for i in range(count):
            location_type = restaurant_types[i % len(restaurant_types)]
            suffix = f"{location_type} {i+1}"
            
            restaurant = await self.generate_restaurant(suffix)
            if restaurant:
                all_restaurants.append(restaurant)
                
            # Add small delay between creations
            await asyncio.sleep(0.5)
                    
        return all_restaurants
        
    async def verify_restaurant_data(self, restaurant_id: str) -> bool:
        """Verify restaurant was created correctly by fetching it"""
        
        try:
            headers = await get_auth_headers(self.client)
            if not headers:
                return False
                
            response = await self.client.get(f"/api/v1/restaurants/{restaurant_id}", headers=headers)
            
            if response.status_code == 200:
                restaurant_data = response.json()
                print(f"✅ Verified restaurant: {restaurant_data['name']}")
                return APITestHelper.validate_restaurant_response(restaurant_data)
            else:
                print(f"❌ Failed to verify restaurant {restaurant_id}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying restaurant: {e}")
            return False
            
    async def list_all_restaurants(self) -> list:
        """List all restaurants to verify creation"""
        
        try:
            headers = await get_auth_headers(self.client)
            if not headers:
                return []
                
            response = await self.client.get("/api/v1/restaurants", headers=headers)
            
            if response.status_code == 200:
                restaurants = response.json()
                if isinstance(restaurants, list):
                    return restaurants
                elif isinstance(restaurants, dict) and 'items' in restaurants:
                    return restaurants['items']
                else:
                    return []
            else:
                print(f"❌ Failed to list restaurants: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error listing restaurants: {e}")
            return []
            
    def print_summary(self):
        """Print generation summary"""
        
        print(f"\n📊 Restaurant Generation Summary")
        print(f"{'='*50}")
        print(f"Total Restaurants Created: {len(self.created_restaurants)}")
        print(f"Total Organizations Auto-Created: {len(self.created_organizations)}")
        
        if self.created_restaurants:
            print(f"\nCreated Restaurants:")
            for restaurant in self.created_restaurants:
                settings = restaurant.get('settings', {})
                cuisine = settings.get('cuisine_type', 'Unknown')
                price_range = settings.get('price_range', 'Unknown')
                
                print(f"  • {restaurant['name']}")
                print(f"    ID: {restaurant['id']}")
                print(f"    Cuisine: {cuisine.title()}")
                print(f"    Price Range: {price_range.title()}")
                if restaurant.get('organization_id'):
                    print(f"    Organization: {restaurant['organization_id']}")
                print()
                
        if self.created_organizations:
            print(f"Auto-Created Organizations:")
            for org in self.created_organizations:
                print(f"  • {org['name']} ({org.get('organization_type', 'Unknown')})")
                print(f"    ID: {org['id']}")
                print()
        else:
            print("ℹ️  Organizations were auto-created (not tracked in response)")
            
    async def run_generation(self, count: int = 4):
        """Run the complete restaurant generation process"""
        
        print("🍽️  RMS Restaurant Data Generator")
        print("="*50)
        
        try:
            # Generate restaurants
            restaurants = await self.generate_multiple_restaurants(count)
            
            # Verify a few restaurants
            if restaurants:
                print(f"\n🔍 Verifying restaurant data...")
                for restaurant in restaurants[:2]:  # Verify first 2
                    await self.verify_restaurant_data(restaurant['id'])
                    
            # List all restaurants to confirm
            print(f"\n📋 Listing all restaurants...")
            all_restaurants = await self.list_all_restaurants()
            if all_restaurants:
                print(f"✅ Found {len(all_restaurants)} total restaurants in system")
            
            # Print summary
            self.print_summary()
            
            return restaurants
            
        except KeyboardInterrupt:
            print("\n⚠️  Generation interrupted by user")
            return []
        except Exception as e:
            print(f"\n❌ Generation failed: {e}")
            return []
        finally:
            # Close the client
            await self.client.close()


async def main():
    """Main entry point for restaurant data generation"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate restaurant test data for RMS")
    parser.add_argument("--count", type=int, default=4, help="Number of restaurants to create")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    generator = RestaurantDataGenerator(args.base_url)
    
    try:
        restaurants = await generator.run_generation(args.count)
        
        if restaurants:
            print(f"\n✅ Successfully generated {len(restaurants)} restaurants")
            
            # Save to file for other generators to use
            output_file = Path(__file__).parent / "generated_restaurants.json"
            with open(output_file, 'w') as f:
                json.dump(restaurants, f, indent=2, default=str)
            print(f"📁 Restaurant data saved to: {output_file}")
            
        else:
            print("\n❌ No restaurants were created successfully")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Generation process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())