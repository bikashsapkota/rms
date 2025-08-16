"""
Sample menu item data for development and testing.
"""

from typing import List, Dict, Any
from decimal import Decimal

# Menu items for Pizza Palace restaurants
PIZZA_PALACE_ITEMS: List[Dict[str, Any]] = [
    # Appetizers
    {
        "name": "Garlic Bread",
        "description": "Fresh baked bread with garlic butter and herbs",
        "price": Decimal("6.99"),
        "category_name": "Appetizers",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1573821663912-6df460f9c684?w=400",
    },
    {
        "name": "Mozzarella Sticks",
        "description": "Breaded mozzarella served with marinara sauce",
        "price": Decimal("8.99"),
        "category_name": "Appetizers",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1541745537411-b8046dc6d66c?w=400",
    },
    {
        "name": "Buffalo Wings",
        "description": "Spicy chicken wings with ranch dipping sauce",
        "price": Decimal("11.99"),
        "category_name": "Appetizers",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1567620832903-9fc6debc209f?w=400",
    },
    
    # Pizza
    {
        "name": "Margherita Pizza",
        "description": "Fresh mozzarella, tomato sauce, and basil",
        "price": Decimal("15.99"),
        "category_name": "Pizza",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?w=400",
    },
    {
        "name": "Pepperoni Pizza",
        "description": "Classic pepperoni with mozzarella cheese",
        "price": Decimal("17.99"),
        "category_name": "Pizza",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400",
    },
    {
        "name": "Supreme Pizza",
        "description": "Pepperoni, sausage, peppers, onions, and mushrooms",
        "price": Decimal("21.99"),
        "category_name": "Pizza",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=400",
    },
    {
        "name": "Hawaiian Pizza",
        "description": "Ham, pineapple, and mozzarella cheese",
        "price": Decimal("18.99"),
        "category_name": "Pizza",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1565299507177-b0ac66763828?w=400",
    },
    
    # Pasta
    {
        "name": "Spaghetti Bolognese",
        "description": "Classic meat sauce with parmesan cheese",
        "price": Decimal("14.99"),
        "category_name": "Pasta",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1621996346565-e3dbc353d2e5?w=400",
    },
    {
        "name": "Fettuccine Alfredo",
        "description": "Rich cream sauce with parmesan cheese",
        "price": Decimal("13.99"),
        "category_name": "Pasta",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1621047894440-8edc8dc1d672?w=400",
    },
    {
        "name": "Chicken Penne",
        "description": "Grilled chicken with penne pasta in marinara sauce",
        "price": Decimal("16.99"),
        "category_name": "Pasta",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1621996346565-e3dbc353d2e5?w=400",
    },
    
    # Salads
    {
        "name": "Caesar Salad",
        "description": "Romaine lettuce, croutons, parmesan, and Caesar dressing",
        "price": Decimal("9.99"),
        "category_name": "Salads",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1546793665-c74683f339c1?w=400",
    },
    {
        "name": "Greek Salad",
        "description": "Mixed greens, olives, feta cheese, and Greek dressing",
        "price": Decimal("11.99"),
        "category_name": "Salads",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400",
    },
    
    # Desserts
    {
        "name": "Tiramisu",
        "description": "Classic Italian dessert with coffee and mascarpone",
        "price": Decimal("7.99"),
        "category_name": "Desserts",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?w=400",
    },
    {
        "name": "Chocolate Lava Cake",
        "description": "Warm chocolate cake with molten center",
        "price": Decimal("8.99"),
        "category_name": "Desserts",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400",
    },
    
    # Beverages
    {
        "name": "Coca-Cola",
        "description": "Classic soft drink",
        "price": Decimal("2.99"),
        "category_name": "Beverages",
        "is_available": True,
    },
    {
        "name": "Italian Soda",
        "description": "Sparkling water with flavor syrup",
        "price": Decimal("3.99"),
        "category_name": "Beverages",
        "is_available": True,
    },
]

# Menu items for Bistro
BISTRO_ITEMS: List[Dict[str, Any]] = [
    # Starters
    {
        "name": "Escargot",
        "description": "Traditional French snails in garlic butter",
        "price": Decimal("12.99"),
        "category_name": "Starters",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=400",
    },
    {
        "name": "Foie Gras",
        "description": "Pan-seared duck liver with fig compote",
        "price": Decimal("24.99"),
        "category_name": "Starters",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1544025162-d76694265947?w=400",
    },
    
    # Soup & Salads
    {
        "name": "French Onion Soup",
        "description": "Classic onion soup with gruyere cheese",
        "price": Decimal("8.99"),
        "category_name": "Soup & Salads",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1547826039-bfc35e0f1ea8?w=400",
    },
    {
        "name": "Salade Niçoise",
        "description": "Traditional French salad with tuna and vegetables",
        "price": Decimal("16.99"),
        "category_name": "Soup & Salads",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400",
    },
    
    # Main Courses
    {
        "name": "Coq au Vin",
        "description": "Braised chicken in red wine sauce",
        "price": Decimal("28.99"),
        "category_name": "Main Courses",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=400",
    },
    {
        "name": "Beef Bourguignon",
        "description": "Slow-braised beef in burgundy wine",
        "price": Decimal("32.99"),
        "category_name": "Main Courses",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=400",
    },
    {
        "name": "Duck Confit",
        "description": "Slow-cooked duck leg with garlic potatoes",
        "price": Decimal("29.99"),
        "category_name": "Main Courses",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1598515214211-89d3c73ae83b?w=400",
    },
    
    # Seafood
    {
        "name": "Bouillabaisse",
        "description": "Traditional Provençal fish stew",
        "price": Decimal("34.99"),
        "category_name": "Seafood",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400",
    },
    {
        "name": "Sole Meunière",
        "description": "Pan-fried sole with lemon butter sauce",
        "price": Decimal("26.99"),
        "category_name": "Seafood",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=400",
    },
    
    # Desserts
    {
        "name": "Crème Brûlée",
        "description": "Vanilla custard with caramelized sugar",
        "price": Decimal("9.99"),
        "category_name": "Desserts",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400",
    },
    {
        "name": "Tarte Tatin",
        "description": "Upside-down apple tart with vanilla ice cream",
        "price": Decimal("8.99"),
        "category_name": "Desserts",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1563805042-7684c019e1cb?w=400",
    },
]

# Menu items for Fast Food
FAST_FOOD_ITEMS: List[Dict[str, Any]] = [
    # Burgers
    {
        "name": "Classic Burger",
        "description": "Beef patty with lettuce, tomato, and onion",
        "price": Decimal("5.99"),
        "category_name": "Burgers",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400",
    },
    {
        "name": "Cheeseburger",
        "description": "Classic burger with American cheese",
        "price": Decimal("6.49"),
        "category_name": "Burgers",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400",
    },
    {
        "name": "Double Bacon Burger",
        "description": "Two patties with bacon and cheese",
        "price": Decimal("9.99"),
        "category_name": "Burgers",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400",
    },
    
    # Chicken
    {
        "name": "Crispy Chicken Sandwich",
        "description": "Breaded chicken breast with mayo and lettuce",
        "price": Decimal("6.99"),
        "category_name": "Chicken",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1606755962773-d324e608d3d3?w=400",
    },
    {
        "name": "Chicken Nuggets (10 pc)",
        "description": "Crispy chicken nuggets with dipping sauce",
        "price": Decimal("7.99"),
        "category_name": "Chicken",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1606755962773-d324e608d3d3?w=400",
    },
    
    # Sides
    {
        "name": "French Fries",
        "description": "Crispy golden fries",
        "price": Decimal("2.99"),
        "category_name": "Sides",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400",
    },
    {
        "name": "Onion Rings",
        "description": "Beer-battered onion rings",
        "price": Decimal("3.99"),
        "category_name": "Sides",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?w=400",
    },
    
    # Breakfast
    {
        "name": "Breakfast Burger",
        "description": "Beef patty with egg, cheese, and hash brown",
        "price": Decimal("7.99"),
        "category_name": "Breakfast",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=400",
    },
    {
        "name": "Pancakes (3 stack)",
        "description": "Fluffy pancakes with syrup and butter",
        "price": Decimal("4.99"),
        "category_name": "Breakfast",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1567620832903-9fc6debc209f?w=400",
    },
    
    # Desserts
    {
        "name": "Vanilla Shake",
        "description": "Thick vanilla milkshake",
        "price": Decimal("3.99"),
        "category_name": "Desserts",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1572490122747-3968b75cc699?w=400",
    },
    {
        "name": "Apple Pie",
        "description": "Warm apple pie with cinnamon",
        "price": Decimal("2.99"),
        "category_name": "Desserts",
        "is_available": True,
        "image_url": "https://images.unsplash.com/photo-1621303837174-89787a7d4729?w=400",
    },
    
    # Beverages
    {
        "name": "Soft Drink",
        "description": "Choice of cola, diet cola, or sprite",
        "price": Decimal("1.99"),
        "category_name": "Beverages",
        "is_available": True,
    },
    {
        "name": "Coffee",
        "description": "Fresh brewed coffee",
        "price": Decimal("1.49"),
        "category_name": "Beverages",
        "is_available": True,
    },
]

SAMPLE_ITEMS_BY_RESTAURANT = {
    "Pizza Palace Downtown": PIZZA_PALACE_ITEMS,
    "Pizza Palace Mall": PIZZA_PALACE_ITEMS,
    "Cozy Corner Bistro": BISTRO_ITEMS,
    "Global Burger Express": FAST_FOOD_ITEMS,
}