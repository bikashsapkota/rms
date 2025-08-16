"""
Sample restaurant data for development and testing.
"""

from typing import List, Dict, Any

SAMPLE_RESTAURANTS: List[Dict[str, Any]] = [
    {
        "name": "Pizza Palace Downtown",
        "organization_name": "Pizza Palace Corporation",
        "address": {
            "street": "123 Main Street",
            "city": "Downtown",
            "state": "CA",
            "zip": "90210",
            "country": "US"
        },
        "phone": "+1-555-0123",
        "email": "downtown@pizzapalace.com",
        "settings": {
            "timezone": "America/Los_Angeles",
            "currency": "USD",
            "tax_rate": 8.25,
            "service_fee": 3.0,
            "delivery_radius": 5.0,
            "opening_hours": {
                "monday": {"open": "11:00", "close": "22:00"},
                "tuesday": {"open": "11:00", "close": "22:00"},
                "wednesday": {"open": "11:00", "close": "22:00"},
                "thursday": {"open": "11:00", "close": "22:00"},
                "friday": {"open": "11:00", "close": "23:00"},
                "saturday": {"open": "11:00", "close": "23:00"},
                "sunday": {"open": "12:00", "close": "21:00"}
            }
        },
        "is_active": True,
    },
    {
        "name": "Pizza Palace Mall",
        "organization_name": "Pizza Palace Corporation",
        "address": {
            "street": "456 Shopping Center Blvd",
            "city": "Suburb",
            "state": "CA",
            "zip": "90211",
            "country": "US"
        },
        "phone": "+1-555-0124",
        "email": "mall@pizzapalace.com",
        "settings": {
            "timezone": "America/Los_Angeles",
            "currency": "USD",
            "tax_rate": 8.25,
            "service_fee": 3.0,
            "opening_hours": {
                "monday": {"open": "10:00", "close": "21:00"},
                "tuesday": {"open": "10:00", "close": "21:00"},
                "wednesday": {"open": "10:00", "close": "21:00"},
                "thursday": {"open": "10:00", "close": "21:00"},
                "friday": {"open": "10:00", "close": "22:00"},
                "saturday": {"open": "10:00", "close": "22:00"},
                "sunday": {"open": "11:00", "close": "20:00"}
            }
        },
        "is_active": True,
    },
    {
        "name": "Cozy Corner Bistro",
        "organization_name": "Local Bistro LLC",
        "address": {
            "street": "789 Oak Avenue",
            "city": "Neighborhood",
            "state": "CA",
            "zip": "90212",
            "country": "US"
        },
        "phone": "+1-555-0125",
        "email": "info@cozycornerbistro.com",
        "settings": {
            "timezone": "America/Los_Angeles",
            "currency": "USD",
            "tax_rate": 8.25,
            "opening_hours": {
                "monday": {"closed": True},
                "tuesday": {"open": "17:00", "close": "22:00"},
                "wednesday": {"open": "17:00", "close": "22:00"},
                "thursday": {"open": "17:00", "close": "22:00"},
                "friday": {"open": "17:00", "close": "23:00"},
                "saturday": {"open": "17:00", "close": "23:00"},
                "sunday": {"open": "17:00", "close": "21:00"}
            }
        },
        "is_active": True,
    },
    {
        "name": "Global Burger Express",
        "organization_name": "Global Fast Food Franchise",
        "address": {
            "street": "321 Highway 101",
            "city": "Freeway",
            "state": "CA",
            "zip": "90213",
            "country": "US"
        },
        "phone": "+1-555-0126",
        "email": "freeway@globalburger.com",
        "settings": {
            "timezone": "America/Los_Angeles",
            "currency": "USD",
            "tax_rate": 8.25,
            "service_fee": 2.5,
            "delivery_radius": 3.0,
            "opening_hours": {
                "monday": {"open": "06:00", "close": "23:00"},
                "tuesday": {"open": "06:00", "close": "23:00"},
                "wednesday": {"open": "06:00", "close": "23:00"},
                "thursday": {"open": "06:00", "close": "23:00"},
                "friday": {"open": "06:00", "close": "24:00"},
                "saturday": {"open": "06:00", "close": "24:00"},
                "sunday": {"open": "07:00", "close": "22:00"}
            }
        },
        "is_active": True,
    },
]