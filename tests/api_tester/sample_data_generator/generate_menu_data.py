#!/usr/bin/env python3
"""
Generate Menu Data

Creates realistic menu categories, items, and modifiers for RMS API testing.
Adapts menu content based on restaurant cuisine type.
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


class MenuDataGenerator:
    """Generates menu test data via API calls"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = APITestClient(base_url)
        self.created_categories = []
        self.created_items = []
        self.created_modifiers = []
        self.available_restaurants = []
        
    async def load_available_restaurants(self):
        """Load available restaurants to create menus for"""
        
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
                    
                print(f"📋 Found {len(self.available_restaurants)} restaurants for menu creation")
                
                for restaurant in self.available_restaurants:
                    cuisine = restaurant.get('settings', {}).get('cuisine_type', 'american')
                    print(f"   • {restaurant['name']} ({cuisine.title()} cuisine)")
                    
            else:
                print(f"⚠️  Could not load restaurants: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error loading restaurants: {e}")
            
    async def generate_menu_category(self, category_data: dict) -> dict:
        """Generate a single menu category"""
        
        try:
            # Get authentication headers
            headers = await get_auth_headers(self.client)
            if not headers:
                print("❌ Failed to authenticate - cannot create menu category")
                return None
                
            print(f"📂 Creating menu category: {category_data['name']}")
            
            # Create category via API
            response = await self.client.post("/api/v1/menu/categories", json=category_data, headers=headers)
            
            if response.status_code == 201:
                category_response = response.json()
                self.created_categories.append(category_response)
                
                print(f"✅ Category created successfully:")
                print(f"   ID: {category_response['id']}")
                print(f"   Name: {category_response['name']}")
                print(f"   Sort Order: {category_response['sort_order']}")
                
                return category_response
                
            else:
                print(f"❌ Failed to create category: HTTP {response.status_code}")
                if response.json_data:
                    print(f"   Error: {response.json_data}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating category: {e}")
            return None
            
    async def generate_menu_item(self, item_data: dict) -> dict:
        """Generate a single menu item"""
        
        try:
            # Get authentication headers
            headers = await get_auth_headers(self.client)
            if not headers:
                print("❌ Failed to authenticate - cannot create menu item")
                return None
                
            print(f"🍽️  Creating menu item: {item_data['name']} (${item_data['price']})")
            
            # Create item via API
            response = await self.client.post("/api/v1/menu/items", json=item_data, headers=headers)
            
            if response.status_code == 201:
                item_response = response.json()
                self.created_items.append(item_response)
                
                print(f"✅ Item created successfully:")
                print(f"   ID: {item_response['id']}")
                print(f"   Name: {item_response['name']}")
                print(f"   Price: ${item_response['price']}")
                print(f"   Category: {item_response.get('category_id', 'N/A')}")
                
                return item_response
                
            else:
                print(f"❌ Failed to create item: HTTP {response.status_code}")
                if response.json_data:
                    print(f"   Error: {response.json_data}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating item: {e}")
            return None
            
    async def generate_modifier(self, modifier_data: dict) -> dict:
        """Generate a single modifier"""
        
        try:
            # Get authentication headers
            headers = await get_auth_headers(self.client)
            if not headers:
                print("❌ Failed to authenticate - cannot create modifier")
                return None
                
            print(f"🔧 Creating modifier: {modifier_data['name']} (${modifier_data['price_adjustment']})")
            
            # Create modifier via API
            response = await self.client.post("/api/v1/menu/modifiers", json=modifier_data, headers=headers)
            
            if response.status_code == 201:
                modifier_response = response.json()
                self.created_modifiers.append(modifier_response)
                
                print(f"✅ Modifier created successfully:")
                print(f"   ID: {modifier_response['id']}")
                print(f"   Name: {modifier_response['name']}")
                print(f"   Type: {modifier_response['type']}")
                print(f"   Price Adjustment: ${modifier_response['price_adjustment']}")
                
                return modifier_response
                
            elif response.status_code == 404:
                print("⚠️  Modifier endpoint not found - modifiers may not be implemented yet")
                return None
                
            else:
                print(f"❌ Failed to create modifier: HTTP {response.status_code}")
                if response.json_data:
                    print(f"   Error: {response.json_data}")
                return None
                
        except Exception as e:
            print(f"❌ Error creating modifier: {e}")
            return None
            
    async def generate_menu_for_restaurant(self, restaurant: dict) -> dict:
        """Generate a complete menu for a specific restaurant"""
        
        restaurant_id = restaurant['id']
        restaurant_name = restaurant['name']
        cuisine_type = restaurant.get('settings', {}).get('cuisine_type', 'american')
        
        print(f"\n🍽️  Generating {cuisine_type.title()} menu for: {restaurant_name}")
        print("="*60)
        
        # Generate categories first
        categories_data = RMSTestFixtures.generate_menu_category_data(cuisine_type)
        created_categories = []
        
        print(f"\n📂 Creating {len(categories_data)} menu categories...")
        
        for category_data in categories_data:
            category = await self.generate_menu_category(category_data)
            if category:
                created_categories.append(category)\n                \n            # Small delay between category creations\n            await asyncio.sleep(0.2)\n            \n        # Generate items for each category\n        created_items = []\n        \n        for category in created_categories:\n            category_id = category['id']\n            category_name = category['name']\n            \n            print(f\"\\n🍽️  Creating items for category: {category_name}\")\n            \n            # Generate items for this category\n            items_data = RMSTestFixtures.generate_menu_items_data(category_id, category_name, cuisine_type)\n            \n            for item_data in items_data:\n                item = await self.generate_menu_item(item_data)\n                if item:\n                    created_items.append(item)\n                    \n                # Small delay between item creations\n                await asyncio.sleep(0.1)\n                \n        # Generate modifiers (if supported)\n        created_modifiers = []\n        modifiers_data = RMSTestFixtures.generate_modifier_data()\n        \n        print(f\"\\n🔧 Creating {len(modifiers_data)} modifiers...\")\n        \n        for modifier_data in modifiers_data[:5]:  # Create first 5 modifiers\n            modifier = await self.generate_modifier(modifier_data)\n            if modifier:\n                created_modifiers.append(modifier)\n                \n            # Small delay between modifier creations\n            await asyncio.sleep(0.1)\n            \n        menu_summary = {\n            \"restaurant_id\": restaurant_id,\n            \"restaurant_name\": restaurant_name,\n            \"cuisine_type\": cuisine_type,\n            \"categories\": created_categories,\n            \"items\": created_items,\n            \"modifiers\": created_modifiers,\n            \"totals\": {\n                \"categories\": len(created_categories),\n                \"items\": len(created_items),\n                \"modifiers\": len(created_modifiers)\n            }\n        }\n        \n        print(f\"\\n📊 Menu creation summary for {restaurant_name}:\")\n        print(f\"   Categories: {len(created_categories)}\")\n        print(f\"   Items: {len(created_items)}\")\n        print(f\"   Modifiers: {len(created_modifiers)}\")\n        \n        return menu_summary\n        \n    async def generate_menus_for_all_restaurants(self) -> list:\n        \"\"\"Generate menus for all available restaurants\"\"\"\n        \n        if not self.available_restaurants:\n            print(\"❌ No restaurants available for menu creation\")\n            return []\n            \n        all_menus = []\n        \n        for restaurant in self.available_restaurants:\n            try:\n                menu = await self.generate_menu_for_restaurant(restaurant)\n                if menu:\n                    all_menus.append(menu)\n                    \n                # Delay between restaurants\n                await asyncio.sleep(1.0)\n                \n            except Exception as e:\n                print(f\"❌ Failed to create menu for {restaurant['name']}: {e}\")\n                \n        return all_menus\n        \n    async def verify_menu_data(self, restaurant_id: str) -> bool:\n        \"\"\"Verify menu was created correctly by fetching categories and items\"\"\"\n        \n        try:\n            headers = await get_auth_headers(self.client)\n            if not headers:\n                return False\n                \n            # Check categories\n            response = await self.client.get(\"/api/v1/menu/categories\", headers=headers)\n            if response.status_code == 200:\n                categories = response.json()\n                if isinstance(categories, list):\n                    category_count = len(categories)\n                elif isinstance(categories, dict) and 'items' in categories:\n                    category_count = len(categories['items'])\n                else:\n                    category_count = 0\n                    \n                print(f\"✅ Verified {category_count} menu categories\")\n                \n            # Check items\n            response = await self.client.get(\"/api/v1/menu/items\", headers=headers)\n            if response.status_code == 200:\n                items = response.json()\n                if isinstance(items, list):\n                    item_count = len(items)\n                elif isinstance(items, dict) and 'items' in items:\n                    item_count = len(items['items'])\n                else:\n                    item_count = 0\n                    \n                print(f\"✅ Verified {item_count} menu items\")\n                \n                return True\n                \n            else:\n                print(f\"❌ Failed to verify menu data: HTTP {response.status_code}\")\n                return False\n                \n        except Exception as e:\n            print(f\"❌ Error verifying menu data: {e}\")\n            return False\n            \n    def print_summary(self):\n        \"\"\"Print generation summary\"\"\"\n        \n        print(f\"\\n📊 Menu Generation Summary\")\n        print(f\"{'='*50}\")\n        print(f\"Total Categories Created: {len(self.created_categories)}\")\n        print(f\"Total Items Created: {len(self.created_items)}\")\n        print(f\"Total Modifiers Created: {len(self.created_modifiers)}\")\n        \n        if self.created_categories:\n            print(f\"\\nCategories by Restaurant:\")\n            restaurant_categories = {}\n            \n            for category in self.created_categories:\n                # Find restaurant name\n                restaurant_name = \"Unknown\"\n                for restaurant in self.available_restaurants:\n                    if restaurant['id'] == category.get('restaurant_id'):\n                        restaurant_name = restaurant['name']\n                        break\n                        \n                if restaurant_name not in restaurant_categories:\n                    restaurant_categories[restaurant_name] = []\n                restaurant_categories[restaurant_name].append(category['name'])\n                \n            for restaurant_name, categories in restaurant_categories.items():\n                print(f\"  {restaurant_name}: {', '.join(categories)}\")\n                \n        if self.created_items:\n            print(f\"\\nItems by Price Range:\")\n            price_ranges = {\"Under $10\": 0, \"$10-$20\": 0, \"Over $20\": 0}\n            \n            for item in self.created_items:\n                price = float(item.get('price', 0))\n                if price < 10:\n                    price_ranges[\"Under $10\"] += 1\n                elif price <= 20:\n                    price_ranges[\"$10-$20\"] += 1\n                else:\n                    price_ranges[\"Over $20\"] += 1\n                    \n            for price_range, count in price_ranges.items():\n                print(f\"  {price_range}: {count} items\")\n                \n    async def run_generation(self):\n        \"\"\"Run the complete menu generation process\"\"\"\n        \n        print(\"🍽️  RMS Menu Data Generator\")\n        print(\"=\"*50)\n        \n        try:\n            # Load available restaurants first\n            await self.load_available_restaurants()\n            \n            if not self.available_restaurants:\n                print(\"❌ No restaurants found. Please run restaurant generation first.\")\n                return []\n                \n            # Generate menus\n            menus = await self.generate_menus_for_all_restaurants()\n            \n            # Verify menu data\n            if menus:\n                print(f\"\\n🔍 Verifying menu data...\")\n                for menu in menus[:1]:  # Verify first restaurant\n                    await self.verify_menu_data(menu['restaurant_id'])\n                    \n            # Print summary\n            self.print_summary()\n            \n            return menus\n            \n        except KeyboardInterrupt:\n            print(\"\\n⚠️  Generation interrupted by user\")\n            return []\n        except Exception as e:\n            print(f\"\\n❌ Generation failed: {e}\")\n            return []\n        finally:\n            # Close the client\n            await self.client.close()\n\n\nasync def main():\n    \"\"\"Main entry point for menu data generation\"\"\"\n    \n    import argparse\n    \n    parser = argparse.ArgumentParser(description=\"Generate menu test data for RMS\")\n    parser.add_argument(\"--base-url\", default=\"http://localhost:8000\", help=\"API base URL\")\n    \n    args = parser.parse_args()\n    \n    generator = MenuDataGenerator(args.base_url)\n    \n    try:\n        menus = await generator.run_generation()\n        \n        if menus:\n            total_categories = sum(menu['totals']['categories'] for menu in menus)\n            total_items = sum(menu['totals']['items'] for menu in menus)\n            total_modifiers = sum(menu['totals']['modifiers'] for menu in menus)\n            \n            print(f\"\\n✅ Successfully generated menus for {len(menus)} restaurants\")\n            print(f\"   Total Categories: {total_categories}\")\n            print(f\"   Total Items: {total_items}\")\n            print(f\"   Total Modifiers: {total_modifiers}\")\n            \n            # Save to file for other generators to use\n            output_file = Path(__file__).parent / \"generated_menus.json\"\n            with open(output_file, 'w') as f:\n                json.dump(menus, f, indent=2, default=str)\n            print(f\"📁 Menu data saved to: {output_file}\")\n            \n        else:\n            print(\"\\n❌ No menus were created successfully\")\n            sys.exit(1)\n            \n    except Exception as e:\n        print(f\"❌ Generation process failed: {e}\")\n        sys.exit(1)\n\n\nif __name__ == \"__main__\":\n    asyncio.run(main())"