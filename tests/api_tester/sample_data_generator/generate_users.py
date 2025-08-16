#!/usr/bin/env python3
"""
Generate Users Test Data

Creates realistic user accounts for RMS API testing.
Creates users with different roles: admin, manager, staff.
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


class UserDataGenerator:
    """Generates user test data via API calls"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.created_users = []
        self.available_restaurants = []
        
    async def load_available_restaurants(self):
        """Load available restaurants to assign users to"""
        
        try:
            headers = await get_auth_headers(self.client)
            if not headers:
                print("❌ Failed to authenticate - cannot load restaurants")
                return
                
            response = await self.client.get("/api/v1/restaurants", headers=headers)
            
            if response.status_code == 200:
                restaurants = response.json()
                if isinstance(restaurants, list):
                    self.available_restaurants = restaurants
                elif isinstance(restaurants, dict) and 'items' in restaurants:
                    self.available_restaurants = restaurants['items']
                    
                print(f"📋 Found {len(self.available_restaurants)} restaurants for user assignment")
                
                for restaurant in self.available_restaurants:
                    print(f"   • {restaurant['name']} (ID: {restaurant['id']})")
                    
            else:
                print(f"⚠️  Could not load restaurants: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error loading restaurants: {e}")
            
    async def generate_user(self, role: str = "staff", restaurant_id: str = None) -> dict:
        """Generate a single user"""
        
        try:
            # Get authentication headers
            headers = await get_auth_headers(self.client)
            if not headers:
                print("❌ Failed to authenticate - cannot create users")
                return None
                
            # Select restaurant if not provided
            if not restaurant_id and self.available_restaurants:
                import random
                restaurant = random.choice(self.available_restaurants)
                restaurant_id = restaurant['id']
                restaurant_name = restaurant['name']
            else:
                restaurant_name = "Unknown Restaurant"
                
            # Generate user data
            user_data = RMSTestFixtures.generate_user_data("placeholder_org", restaurant_id, role)
            
            # For API creation, we need to set the password field, not password_hash
            user_data["password"] = "secure_test_password"
            if "password_hash" in user_data:
                del user_data["password_hash"]
                
            # Add restaurant_id if available
            if restaurant_id:
                user_data["restaurant_id"] = restaurant_id
                
            print(f"👤 Creating {role} user: {user_data['full_name']}")
            print(f"   Email: {user_data['email']}")
            print(f"   Restaurant: {restaurant_name}")
            
            # Create user via API
            response = await self.client.post("/api/v1/users", json=user_data, headers=headers)
            
            if response.status_code == 201:
                user_response = response.json()
                self.created_users.append(user_response)
                
                print(f"✅ User created successfully:")
                print(f"   ID: {user_response['id']}")
                print(f"   Email: {user_response['email']}")
                print(f"   Role: {user_response['role']}")
                print(f"   Organization: {user_response.get('organization_id', 'N/A')}")
                
                return user_response
                
            elif response.status_code == 404:
                print("⚠️  User creation endpoint not found - this may be expected in Phase 1")
                print("    Users might be created through restaurant setup process")
                return None
                
            elif response.status_code == 409:
                print(f"⚠️  User with email {user_data['email']} already exists")
                return None
                
            else:
                print(f"❌ Failed to create user: HTTP {response.status_code}")
                if response.json_data:
                    print(f"   Error: {response.json_data}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating user: {e}")
            return None
            
    async def generate_users_for_restaurant(self, restaurant_id: str, restaurant_name: str) -> list:
        """Generate a complete set of users for a restaurant"""
        
        print(f"\n🏢 Generating users for restaurant: {restaurant_name}")
        
        users = []
        user_roles = [
            {"role": "admin", "count": 1},
            {"role": "manager", "count": 1}, 
            {"role": "staff", "count": 3}
        ]
        
        for role_config in user_roles:
            role = role_config["role"]
            count = role_config["count"]
            
            print(f"\n👥 Creating {count} {role}(s)...")
            
            for i in range(count):
                user = await self.generate_user(role, restaurant_id)
                if user:
                    users.append(user)
                    
                # Small delay between user creations
                await asyncio.sleep(0.3)
                
        return users
        
    async def generate_multiple_users(self) -> list:
        """Generate users for all available restaurants"""
        
        if not self.available_restaurants:
            print("❌ No restaurants available for user creation")
            return []
            
        all_users = []
        
        # Generate users for each restaurant
        for restaurant in self.available_restaurants:
            restaurant_id = restaurant['id']
            restaurant_name = restaurant['name']
            
            users = await self.generate_users_for_restaurant(restaurant_id, restaurant_name)
            all_users.extend(users)
            
        return all_users
        
    async def verify_user_data(self, user_id: str) -> bool:
        """Verify user was created correctly by fetching it"""
        
        try:
            headers = await get_auth_headers(self.client)
            if not headers:
                return False
                
            response = await self.client.get(f"/api/v1/users/{user_id}", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ Verified user: {user_data['full_name']} ({user_data['role']})")
                return APITestHelper.validate_user_response(user_data)
            else:
                print(f"❌ Failed to verify user {user_id}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying user: {e}")
            return False
            
    async def list_all_users(self) -> list:
        """List all users to verify creation"""
        
        try:
            headers = await get_auth_headers(self.client)
            if not headers:
                return []
                
            response = await self.client.get("/api/v1/users", headers=headers)
            
            if response.status_code == 200:
                users = response.json()
                if isinstance(users, list):
                    return users
                elif isinstance(users, dict) and 'items' in users:
                    return users['items']
                else:
                    return []
            else:
                print(f"❌ Failed to list users: HTTP {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error listing users: {e}")
            return []
            
    async def test_user_authentication(self, user_email: str, password: str = "secure_test_password") -> bool:
        """Test if a created user can authenticate"""
        
        try:
            # Test login
            auth_data = {
                "username": user_email,  # FastAPI OAuth2 uses 'username' field
                "password": password
            }
            
            response = await self.client.post("/auth/login", data=auth_data)
            
            if response.status_code == 200:
                print(f"✅ User authentication successful: {user_email}")
                return True
            else:
                print(f"❌ User authentication failed: {user_email} (HTTP {response.status_code})")
                return False
                
        except Exception as e:
            print(f"❌ Error testing user authentication: {e}")
            return False
            
    def print_summary(self):
        """Print generation summary"""
        
        print(f"\n📊 User Generation Summary")
        print(f"{'='*50}")
        print(f"Total Users Created: {len(self.created_users)}")
        
        if self.created_users:
            # Group by role
            by_role = {}
            by_restaurant = {}
            
            for user in self.created_users:
                role = user.get('role', 'Unknown')
                restaurant_id = user.get('restaurant_id', 'Unassigned')
                
                by_role[role] = by_role.get(role, 0) + 1
                by_restaurant[restaurant_id] = by_restaurant.get(restaurant_id, 0) + 1
                
            print(f"\nBy Role:")
            for role, count in by_role.items():
                print(f"  {role.title()}: {count}")
                
            print(f"\nBy Restaurant:")
            for restaurant_id, count in by_restaurant.items():
                # Find restaurant name
                restaurant_name = "Unknown"
                for restaurant in self.available_restaurants:
                    if restaurant['id'] == restaurant_id:
                        restaurant_name = restaurant['name']
                        break
                        
                print(f"  {restaurant_name}: {count} users")
                
            print(f"\nCreated Users:")
            for user in self.created_users:
                print(f"  • {user['full_name']} ({user['role']})")
                print(f"    Email: {user['email']}")
                print(f"    ID: {user['id']}")
                print()
        else:
            print("❌ No users were created successfully")
            
    async def run_generation(self):
        """Run the complete user generation process"""
        
        print("👥 RMS User Data Generator")
        print("="*50)
        
        try:
            # Load available restaurants first
            await self.load_available_restaurants()
            
            if not self.available_restaurants:
                print("❌ No restaurants found. Please run restaurant generation first.")
                return []
                
            # Generate users
            users = await self.generate_multiple_users()
            
            # Verify a few users
            if users:
                print(f"\n🔍 Verifying user data...")
                for user in users[:3]:  # Verify first 3
                    await self.verify_user_data(user['id'])
                    
                # Test authentication for a few users
                print(f"\n🔐 Testing user authentication...")
                for user in users[:2]:  # Test first 2
                    await self.test_user_authentication(user['email'])
                    
            # List all users to confirm
            print(f"\n📋 Listing all users...")
            all_users = await self.list_all_users()
            if all_users:
                print(f"✅ Found {len(all_users)} total users in system")
            
            # Print summary
            self.print_summary()
            
            return users
            
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
    """Main entry point for user data generation"""
    
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate user test data for RMS")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    generator = UserDataGenerator(args.base_url)
    
    try:
        users = await generator.run_generation()
        
        if users:
            print(f"\n✅ Successfully generated {len(users)} users")
            
            # Save to file for other generators to use
            output_file = Path(__file__).parent / "generated_users.json"
            with open(output_file, 'w') as f:
                json.dump(users, f, indent=2, default=str)
            print(f"📁 User data saved to: {output_file}")
            
        else:
            print("\n⚠️  No users were created - this may be expected in Phase 1")
            print("    Users are typically created through restaurant setup process")
            
    except Exception as e:
        print(f"❌ Generation process failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())