"""
RMS API Test Fixtures and Sample Data Generation

Provides realistic test data for comprehensive API testing.
Includes organizations, restaurants, users, menus, and business scenarios.
"""

import uuid
from typing import Dict, List, Any
from decimal import Decimal
import random


class RMSTestFixtures:
    """Centralized test data fixtures for RMS API testing"""
    
    @staticmethod
    def generate_organization_data(org_type: str = "independent") -> Dict[str, Any]:
        """Generate realistic organization data"""
        
        org_templates = {
            "independent": {
                "names": [
                    "Bella Vista Restaurant",
                    "The Golden Spoon",
                    "Ocean Breeze Dining",
                    "Mountain View Bistro",
                    "Urban Kitchen"
                ],
                "subscription_tier": "basic"
            },
            "chain": {
                "names": [
                    "Pizza Palace Chain",
                    "Burger Kingdom",
                    "Taco Express",
                    "Pasta World",
                    "Sushi Station"
                ],
                "subscription_tier": "professional"
            },
            "franchise": {
                "names": [
                    "Global Eats Franchise",
                    "International Dining Co",
                    "World Kitchen Franchise",
                    "Metro Food Group",
                    "Premier Restaurant Network"
                ],
                "subscription_tier": "enterprise"
            }
        }
        
        template = org_templates.get(org_type, org_templates["independent"])
        name = random.choice(template["names"])
        
        return {
            "name": name,
            "organization_type": org_type,
            "subscription_tier": template["subscription_tier"],
            "billing_email": f"billing@{name.lower().replace(' ', '').replace('restaurant', '').replace('chain', '').replace('franchise', '')}.com",
            "is_active": True
        }
    
    @staticmethod
    def generate_restaurant_data(organization_id: str, location_suffix: str = "") -> Dict[str, Any]:
        """Generate realistic restaurant data"""
        
        restaurant_templates = [
            {
                "name": f"Downtown Location {location_suffix}",
                "cuisine": "american",
                "price_range": "medium",
                "address": {
                    "street": "123 Main Street",
                    "city": "Downtown",
                    "state": "CA",
                    "zip_code": "90210",
                    "country": "US"
                }
            },
            {
                "name": f"Mall Location {location_suffix}",
                "cuisine": "italian",
                "price_range": "high",
                "address": {
                    "street": "456 Shopping Center Blvd",
                    "city": "Mall Plaza",
                    "state": "NY",
                    "zip_code": "10001",
                    "country": "US"
                }
            },
            {
                "name": f"Suburban Location {location_suffix}",
                "cuisine": "mexican",
                "price_range": "low",
                "address": {
                    "street": "789 Suburban Ave",
                    "city": "Suburbia",
                    "state": "TX",
                    "zip_code": "75001",
                    "country": "US"
                }
            }
        ]
        
        template = random.choice(restaurant_templates)
        
        return {
            "name": template["name"],
            "address": template["address"],
            "phone": f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}",
            "email": f"contact@{template['name'].lower().replace(' ', '').replace('location', '')}.com",
            "settings": {
                "cuisine_type": template["cuisine"],
                "price_range": template["price_range"],
                "accepts_reservations": True,
                "delivery_available": random.choice([True, False]),
                "takeout_available": True,
                "hours": {
                    "monday": {"open": "11:00", "close": "22:00"},
                    "tuesday": {"open": "11:00", "close": "22:00"},
                    "wednesday": {"open": "11:00", "close": "22:00"},
                    "thursday": {"open": "11:00", "close": "22:00"},
                    "friday": {"open": "11:00", "close": "23:00"},
                    "saturday": {"open": "10:00", "close": "23:00"},
                    "sunday": {"open": "10:00", "close": "21:00"}
                }
            },
            "is_active": True
        }
    
    @staticmethod
    def generate_user_data(organization_id: str, restaurant_id: str = None, role: str = "staff") -> Dict[str, Any]:
        """Generate realistic user data"""
        
        first_names = ["John", "Jane", "Michael", "Sarah", "David", "Emily", "Chris", "Amanda", "Robert", "Lisa"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        full_name = f"{first_name} {last_name}"
        
        # Generate email based on role and name
        email_prefix = f"{first_name.lower()}.{last_name.lower()}"
        if role == "admin":
            email = f"{email_prefix}+admin@testrestaurant.com"
        elif role == "manager":
            email = f"{email_prefix}+manager@testrestaurant.com"
        else:
            email = f"{email_prefix}@testrestaurant.com"
        
        return {
            "email": email,
            "full_name": full_name,
            "role": role,
            "password_hash": "hashed_password_placeholder",  # Will be properly hashed by API
            "is_active": True
        }
    
    @staticmethod
    def generate_menu_category_data(cuisine_type: str = "american") -> List[Dict[str, Any]]:
        """Generate realistic menu categories based on cuisine type"""
        
        category_templates = {
            "american": [
                {"name": "Appetizers", "description": "Start your meal with our delicious appetizers", "sort_order": 1},
                {"name": "Burgers & Sandwiches", "description": "Juicy burgers and hearty sandwiches", "sort_order": 2},
                {"name": "Main Courses", "description": "Hearty American classics", "sort_order": 3},
                {"name": "Salads", "description": "Fresh and healthy salad options", "sort_order": 4},
                {"name": "Desserts", "description": "Sweet endings to your meal", "sort_order": 5},
                {"name": "Beverages", "description": "Refreshing drinks and specialty beverages", "sort_order": 6}
            ],
            "italian": [
                {"name": "Antipasti", "description": "Traditional Italian starters", "sort_order": 1},
                {"name": "Pasta", "description": "Homemade pasta dishes", "sort_order": 2},
                {"name": "Pizza", "description": "Wood-fired pizzas with authentic toppings", "sort_order": 3},
                {"name": "Secondi Piatti", "description": "Main courses featuring meat and seafood", "sort_order": 4},
                {"name": "Dolci", "description": "Traditional Italian desserts", "sort_order": 5},
                {"name": "Vini e Bevande", "description": "Italian wines and beverages", "sort_order": 6}
            ],
            "mexican": [
                {"name": "Antojitos", "description": "Mexican appetizers and small plates", "sort_order": 1},
                {"name": "Tacos", "description": "Authentic tacos with various fillings", "sort_order": 2},
                {"name": "Burritos & Quesadillas", "description": "Hearty wrapped and grilled specialties", "sort_order": 3},
                {"name": "Platos Principales", "description": "Traditional Mexican main dishes", "sort_order": 4},
                {"name": "Postres", "description": "Sweet Mexican desserts", "sort_order": 5},
                {"name": "Bebidas", "description": "Mexican beverages and aguas frescas", "sort_order": 6}
            ]
        }
        
        categories = category_templates.get(cuisine_type, category_templates["american"])
        
        # Add is_active to each category
        for category in categories:
            category["is_active"] = True
            
        return categories
    
    @staticmethod
    def generate_menu_items_data(category_id: str, category_name: str, cuisine_type: str = "american") -> List[Dict[str, Any]]:
        """Generate realistic menu items for a specific category"""
        
        menu_items_templates = {
            "american": {
                "Appetizers": [
                    {"name": "Buffalo Wings", "description": "Spicy buffalo wings served with ranch dressing", "price": 12.99},
                    {"name": "Loaded Potato Skins", "description": "Crispy potato skins with bacon, cheese, and sour cream", "price": 9.99},
                    {"name": "Onion Rings", "description": "Beer-battered onion rings with chipotle mayo", "price": 8.99},
                    {"name": "Spinach Artichoke Dip", "description": "Creamy dip served with tortilla chips", "price": 10.99}
                ],
                "Burgers & Sandwiches": [
                    {"name": "Classic Cheeseburger", "description": "1/3 lb beef patty with cheese, lettuce, tomato, onion", "price": 14.99},
                    {"name": "BBQ Bacon Burger", "description": "Burger with BBQ sauce, bacon, and onion rings", "price": 16.99},
                    {"name": "Grilled Chicken Sandwich", "description": "Marinated chicken breast with avocado", "price": 13.99},
                    {"name": "Fish Sandwich", "description": "Beer-battered cod with tartar sauce", "price": 15.99}
                ],
                "Main Courses": [
                    {"name": "Grilled Salmon", "description": "Atlantic salmon with lemon herb butter", "price": 22.99},
                    {"name": "Ribeye Steak", "description": "12oz ribeye cooked to perfection", "price": 28.99},
                    {"name": "BBQ Ribs", "description": "Full rack of baby back ribs", "price": 24.99},
                    {"name": "Chicken Parmesan", "description": "Breaded chicken with marinara and mozzarella", "price": 18.99}
                ]
            },
            "italian": {
                "Antipasti": [
                    {"name": "Bruschetta Trio", "description": "Three types of bruschetta with fresh toppings", "price": 11.99},
                    {"name": "Antipasto Platter", "description": "Cured meats, cheeses, olives, and roasted peppers", "price": 16.99},
                    {"name": "Calamari Fritti", "description": "Crispy fried squid with marinara sauce", "price": 13.99},
                    {"name": "Caprese Salad", "description": "Fresh mozzarella, tomatoes, and basil", "price": 12.99}
                ],
                "Pasta": [
                    {"name": "Spaghetti Carbonara", "description": "Classic carbonara with pancetta and egg", "price": 16.99},
                    {"name": "Fettuccine Alfredo", "description": "Rich and creamy alfredo sauce", "price": 15.99},
                    {"name": "Penne Arrabbiata", "description": "Spicy tomato sauce with garlic and herbs", "price": 14.99},
                    {"name": "Lasagna della Casa", "description": "Traditional meat lasagna with three cheeses", "price": 18.99}
                ],
                "Pizza": [
                    {"name": "Margherita", "description": "Tomato, mozzarella, and fresh basil", "price": 14.99},
                    {"name": "Pepperoni", "description": "Classic pepperoni with mozzarella", "price": 16.99},
                    {"name": "Quattro Stagioni", "description": "Four seasons with artichokes, ham, mushrooms, olives", "price": 19.99},
                    {"name": "Prosciutto e Funghi", "description": "Prosciutto, mushrooms, and arugula", "price": 21.99}
                ]
            },
            "mexican": {
                "Antojitos": [
                    {"name": "Guacamole & Chips", "description": "Fresh avocado dip with crispy tortilla chips", "price": 8.99},
                    {"name": "Queso Fundido", "description": "Melted cheese with chorizo and peppers", "price": 10.99},
                    {"name": "Nachos Supremos", "description": "Loaded nachos with beans, cheese, jalapeños", "price": 12.99},
                    {"name": "Jalapeño Poppers", "description": "Breaded jalapeños stuffed with cream cheese", "price": 9.99}
                ],
                "Tacos": [
                    {"name": "Carne Asada Tacos", "description": "Grilled steak with onions and cilantro", "price": 3.99},
                    {"name": "Al Pastor Tacos", "description": "Marinated pork with pineapple", "price": 3.75},
                    {"name": "Fish Tacos", "description": "Grilled fish with cabbage slaw", "price": 4.25},
                    {"name": "Carnitas Tacos", "description": "Slow-cooked pork with lime and onions", "price": 3.50}
                ],
                "Burritos & Quesadillas": [
                    {"name": "California Burrito", "description": "Carne asada, fries, cheese, and guacamole", "price": 13.99},
                    {"name": "Chicken Quesadilla", "description": "Grilled chicken with cheese and peppers", "price": 11.99},
                    {"name": "Bean & Rice Burrito", "description": "Vegetarian burrito with black beans", "price": 9.99},
                    {"name": "Steak Quesadilla", "description": "Grilled steak with cheese and onions", "price": 13.99}
                ]
            }
        }
        
        # Get items for the category, fallback to American appetizers if not found
        cuisine_items = menu_items_templates.get(cuisine_type, menu_items_templates["american"])
        items = cuisine_items.get(category_name, cuisine_items.get("Appetizers", []))
        
        # Add common fields to each item
        for item in items:
            item.update({
                "category_id": category_id,
                "is_available": True,
                "image_url": None
            })
            
        return items
    
    @staticmethod
    def generate_modifier_data() -> List[Dict[str, Any]]:
        """Generate realistic menu modifiers"""
        
        modifiers = [
            {"name": "Extra Cheese", "modifier_type": "addon", "price_adjustment": 1.50},
            {"name": "Extra Bacon", "modifier_type": "addon", "price_adjustment": 2.00},
            {"name": "Avocado", "modifier_type": "addon", "price_adjustment": 1.75},
            {"name": "No Onions", "modifier_type": "substitution", "price_adjustment": 0.00},
            {"name": "No Tomatoes", "modifier_type": "substitution", "price_adjustment": 0.00},
            {"name": "Extra Spicy", "modifier_type": "preparation", "price_adjustment": 0.00},
            {"name": "Well Done", "modifier_type": "preparation", "price_adjustment": 0.00},
            {"name": "Large Size", "modifier_type": "size", "price_adjustment": 3.00},
            {"name": "Small Size", "modifier_type": "size", "price_adjustment": -2.00},
            {"name": "Gluten Free Bun", "modifier_type": "substitution", "price_adjustment": 1.00}
        ]
        
        # Add is_active to each modifier
        for modifier in modifiers:
            modifier["is_active"] = True
            
        return modifiers
    
    @staticmethod
    def generate_complete_restaurant_setup() -> Dict[str, Any]:
        """Generate a complete restaurant setup with organization, restaurant, users, and menu"""
        
        # Generate organization
        org_type = random.choice(["independent", "chain", "franchise"])
        organization = RMSTestFixtures.generate_organization_data(org_type)
        
        # Generate restaurant
        restaurant = RMSTestFixtures.generate_restaurant_data("org_placeholder", "Main")
        cuisine_type = restaurant["settings"]["cuisine_type"]
        
        # Generate users with different roles
        users = [
            RMSTestFixtures.generate_user_data("org_placeholder", "rest_placeholder", "admin"),
            RMSTestFixtures.generate_user_data("org_placeholder", "rest_placeholder", "manager"),
            RMSTestFixtures.generate_user_data("org_placeholder", "rest_placeholder", "staff"),
            RMSTestFixtures.generate_user_data("org_placeholder", "rest_placeholder", "staff")
        ]
        
        # Generate menu categories
        menu_categories = RMSTestFixtures.generate_menu_category_data(cuisine_type)
        
        # Generate menu items for each category
        menu_items = []
        for category in menu_categories:
            category_items = RMSTestFixtures.generate_menu_items_data(
                "cat_placeholder", 
                category["name"], 
                cuisine_type
            )
            menu_items.extend(category_items)
        
        # Generate modifiers
        modifiers = RMSTestFixtures.generate_modifier_data()
        
        return {
            "organization": organization,
            "restaurant": restaurant,
            "users": users,
            "menu_categories": menu_categories,
            "menu_items": menu_items,
            "modifiers": modifiers,
            "metadata": {
                "cuisine_type": cuisine_type,
                "organization_type": org_type,
                "total_categories": len(menu_categories),
                "total_items": len(menu_items),
                "total_users": len(users)
            }
        }
    
    @staticmethod
    def generate_test_scenarios() -> List[Dict[str, Any]]:
        """Generate multiple test scenarios for comprehensive testing"""
        
        scenarios = []
        
        # Independent restaurant scenarios
        for i in range(2):
            scenario = RMSTestFixtures.generate_complete_restaurant_setup()
            scenario["scenario_name"] = f"Independent Restaurant {i+1}"
            scenarios.append(scenario)
        
        # Chain restaurant scenario
        chain_scenario = RMSTestFixtures.generate_complete_restaurant_setup()
        chain_scenario["organization"]["organization_type"] = "chain"
        chain_scenario["organization"]["subscription_tier"] = "professional"
        chain_scenario["scenario_name"] = "Chain Restaurant Network"
        scenarios.append(chain_scenario)
        
        # Franchise scenario
        franchise_scenario = RMSTestFixtures.generate_complete_restaurant_setup()
        franchise_scenario["organization"]["organization_type"] = "franchise"
        franchise_scenario["organization"]["subscription_tier"] = "enterprise"
        franchise_scenario["scenario_name"] = "Franchise Operation"
        scenarios.append(franchise_scenario)
        
        return scenarios
    
    @staticmethod
    def get_test_admin_credentials() -> Dict[str, str]:
        """Get default test admin credentials"""
        return {
            "email": "admin@testrestaurant.com",
            "password": "secure_test_password"
        }
    
    @staticmethod
    def get_test_credentials_by_role(role: str) -> Dict[str, str]:
        """Get test credentials for specific role"""
        credentials = {
            "admin": {"email": "admin@testrestaurant.com", "password": "secure_test_password"},
            "manager": {"email": "manager@testrestaurant.com", "password": "manager_password"},
            "staff": {"email": "staff@testrestaurant.com", "password": "staff_password"}
        }
        
        return credentials.get(role, credentials["admin"])


# Convenience functions for quick data generation
def quick_organization(org_type: str = "independent") -> Dict[str, Any]:
    """Quick organization data generation"""
    return RMSTestFixtures.generate_organization_data(org_type)


def quick_restaurant(org_id: str, suffix: str = "") -> Dict[str, Any]:
    """Quick restaurant data generation"""
    return RMSTestFixtures.generate_restaurant_data(org_id, suffix)


def quick_user(org_id: str, rest_id: str = None, role: str = "staff") -> Dict[str, Any]:
    """Quick user data generation"""
    return RMSTestFixtures.generate_user_data(org_id, rest_id, role)


def quick_menu_setup(cuisine_type: str = "american") -> Dict[str, Any]:
    """Quick menu setup with categories and items"""
    categories = RMSTestFixtures.generate_menu_category_data(cuisine_type)
    items = []
    
    for category in categories:
        category_items = RMSTestFixtures.generate_menu_items_data(
            "placeholder_id", 
            category["name"], 
            cuisine_type
        )
        items.extend(category_items)
    
    return {
        "categories": categories,
        "items": items,
        "modifiers": RMSTestFixtures.generate_modifier_data()
    }