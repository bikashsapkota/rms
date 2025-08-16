"""
Sample menu category data for development and testing.
"""

from typing import List, Dict, Any

# Categories for Pizza Palace restaurants
PIZZA_PALACE_CATEGORIES: List[Dict[str, Any]] = [
    {
        "name": "Appetizers",
        "description": "Start your meal with our delicious appetizers",
        "sort_order": 1,
        "is_active": True,
    },
    {
        "name": "Pizza",
        "description": "Our signature wood-fired pizzas made with fresh ingredients",
        "sort_order": 2,
        "is_active": True,
    },
    {
        "name": "Pasta",
        "description": "Traditional Italian pasta dishes",
        "sort_order": 3,
        "is_active": True,
    },
    {
        "name": "Salads",
        "description": "Fresh and healthy salad options",
        "sort_order": 4,
        "is_active": True,
    },
    {
        "name": "Desserts",
        "description": "Sweet treats to end your meal",
        "sort_order": 5,
        "is_active": True,
    },
    {
        "name": "Beverages",
        "description": "Refreshing drinks and specialty beverages",
        "sort_order": 6,
        "is_active": True,
    },
]

# Categories for Bistro
BISTRO_CATEGORIES: List[Dict[str, Any]] = [
    {
        "name": "Starters",
        "description": "Elegant appetizers to begin your dining experience",
        "sort_order": 1,
        "is_active": True,
    },
    {
        "name": "Soup & Salads",
        "description": "Fresh soups and artisanal salads",
        "sort_order": 2,
        "is_active": True,
    },
    {
        "name": "Main Courses",
        "description": "Chef's signature entrees",
        "sort_order": 3,
        "is_active": True,
    },
    {
        "name": "Seafood",
        "description": "Fresh catches and ocean delicacies",
        "sort_order": 4,
        "is_active": True,
    },
    {
        "name": "Desserts",
        "description": "Artisanal desserts crafted in-house",
        "sort_order": 5,
        "is_active": True,
    },
    {
        "name": "Wine & Cocktails",
        "description": "Curated wine selection and craft cocktails",
        "sort_order": 6,
        "is_active": True,
    },
]

# Categories for Fast Food
FAST_FOOD_CATEGORIES: List[Dict[str, Any]] = [
    {
        "name": "Burgers",
        "description": "Flame-grilled burgers made to order",
        "sort_order": 1,
        "is_active": True,
    },
    {
        "name": "Chicken",
        "description": "Crispy chicken sandwiches and nuggets",
        "sort_order": 2,
        "is_active": True,
    },
    {
        "name": "Sides",
        "description": "Fries, onion rings, and more",
        "sort_order": 3,
        "is_active": True,
    },
    {
        "name": "Breakfast",
        "description": "All-day breakfast menu",
        "sort_order": 4,
        "is_active": True,
    },
    {
        "name": "Desserts",
        "description": "Shakes, pies, and sweet treats",
        "sort_order": 5,
        "is_active": True,
    },
    {
        "name": "Beverages",
        "description": "Soft drinks, coffee, and more",
        "sort_order": 6,
        "is_active": True,
    },
]

SAMPLE_CATEGORIES_BY_RESTAURANT = {
    "Pizza Palace Downtown": PIZZA_PALACE_CATEGORIES,
    "Pizza Palace Mall": PIZZA_PALACE_CATEGORIES,
    "Cozy Corner Bistro": BISTRO_CATEGORIES,
    "Global Burger Express": FAST_FOOD_CATEGORIES,
}