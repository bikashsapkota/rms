"""
Sample user data for development and testing.
"""

from typing import List, Dict, Any

SAMPLE_USERS: List[Dict[str, Any]] = [
    # Pizza Palace Corporation Users
    {
        "email": "admin@pizzapalace.com",
        "full_name": "John Smith",
        "role": "admin",
        "password": "admin123!",
        "organization_name": "Pizza Palace Corporation",
        "restaurant_name": None,  # Organization-level admin
        "is_active": True,
    },
    {
        "email": "manager.downtown@pizzapalace.com",
        "full_name": "Sarah Johnson",
        "role": "manager",
        "password": "manager123!",
        "organization_name": "Pizza Palace Corporation",
        "restaurant_name": "Pizza Palace Downtown",
        "is_active": True,
    },
    {
        "email": "staff.downtown@pizzapalace.com",
        "full_name": "Mike Wilson",
        "role": "staff",
        "password": "staff123!",
        "organization_name": "Pizza Palace Corporation",
        "restaurant_name": "Pizza Palace Downtown",
        "is_active": True,
    },
    {
        "email": "manager.mall@pizzapalace.com",
        "full_name": "Emily Davis",
        "role": "manager",
        "password": "manager123!",
        "organization_name": "Pizza Palace Corporation",
        "restaurant_name": "Pizza Palace Mall",
        "is_active": True,
    },
    {
        "email": "staff.mall@pizzapalace.com",
        "full_name": "Alex Brown",
        "role": "staff",
        "password": "staff123!",
        "organization_name": "Pizza Palace Corporation",
        "restaurant_name": "Pizza Palace Mall",
        "is_active": True,
    },
    
    # Local Bistro LLC Users
    {
        "email": "owner@localbistro.com",
        "full_name": "Maria Rodriguez",
        "role": "admin",
        "password": "owner123!",
        "organization_name": "Local Bistro LLC",
        "restaurant_name": "Cozy Corner Bistro",
        "is_active": True,
    },
    {
        "email": "chef@localbistro.com",
        "full_name": "Chef Antoine Dubois",
        "role": "staff",
        "password": "chef123!",
        "organization_name": "Local Bistro LLC",
        "restaurant_name": "Cozy Corner Bistro",
        "is_active": True,
    },
    {
        "email": "server@localbistro.com",
        "full_name": "Lisa Thompson",
        "role": "staff",
        "password": "server123!",
        "organization_name": "Local Bistro LLC",
        "restaurant_name": "Cozy Corner Bistro",
        "is_active": True,
    },
    
    # Global Fast Food Franchise Users
    {
        "email": "regional@globalburger.com",
        "full_name": "David Kim",
        "role": "admin",
        "password": "regional123!",
        "organization_name": "Global Fast Food Franchise",
        "restaurant_name": None,  # Organization-level admin
        "is_active": True,
    },
    {
        "email": "manager@globalburger.com",
        "full_name": "Jennifer Lee",
        "role": "manager",
        "password": "manager123!",
        "organization_name": "Global Fast Food Franchise",
        "restaurant_name": "Global Burger Express",
        "is_active": True,
    },
    {
        "email": "crew@globalburger.com",
        "full_name": "Carlos Martinez",
        "role": "staff",
        "password": "crew123!",
        "organization_name": "Global Fast Food Franchise",
        "restaurant_name": "Global Burger Express",
        "is_active": True,
    },
]