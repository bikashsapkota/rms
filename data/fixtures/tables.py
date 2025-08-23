"""
Sample table data for testing and development.
"""

from typing import List, Dict, Any


def get_sample_tables() -> List[Dict[str, Any]]:
    """Get sample table data for restaurant setup."""
    return [
        {
            "table_number": "T01",
            "capacity": 2,
            "location": "main_dining",
            "coordinates": {"x": 100, "y": 100},
            "status": "available",
            "is_active": True,
        },
        {
            "table_number": "T02", 
            "capacity": 4,
            "location": "main_dining",
            "coordinates": {"x": 200, "y": 100},
            "status": "available",
            "is_active": True,
        },
        {
            "table_number": "T03",
            "capacity": 4,
            "location": "main_dining", 
            "coordinates": {"x": 300, "y": 100},
            "status": "available",
            "is_active": True,
        },
        {
            "table_number": "T04",
            "capacity": 6,
            "location": "main_dining",
            "coordinates": {"x": 400, "y": 100},
            "status": "available",
            "is_active": True,
        },
        {
            "table_number": "T05",
            "capacity": 8,
            "location": "main_dining",
            "coordinates": {"x": 500, "y": 100},
            "status": "available",
            "is_active": True,
        },
        {
            "table_number": "P01",
            "capacity": 4,
            "location": "patio",
            "coordinates": {"x": 100, "y": 300},
            "status": "available",
            "is_active": True,
        },
        {
            "table_number": "P02",
            "capacity": 4,
            "location": "patio",
            "coordinates": {"x": 200, "y": 300},
            "status": "available",
            "is_active": True,
        },
        {
            "table_number": "P03",
            "capacity": 6,
            "location": "patio",
            "coordinates": {"x": 300, "y": 300},
            "status": "available",
            "is_active": True,
        },
        {
            "table_number": "VIP01",
            "capacity": 10,
            "location": "private",
            "coordinates": {"x": 600, "y": 200},
            "status": "available",
            "is_active": True,
        },
        {
            "table_number": "BAR01",
            "capacity": 2,
            "location": "bar",
            "coordinates": {"x": 50, "y": 200},
            "status": "available",
            "is_active": True,
        },
        {
            "table_number": "BAR02",
            "capacity": 2,
            "location": "bar",
            "coordinates": {"x": 75, "y": 200},
            "status": "available",
            "is_active": True,
        },
        {
            "table_number": "BAR03",
            "capacity": 4,
            "location": "bar",
            "coordinates": {"x": 100, "y": 200},
            "status": "available",
            "is_active": True,
        },
    ]


def get_restaurant_layout_settings() -> Dict[str, Any]:
    """Get default restaurant layout settings."""
    return {
        "floor_plan": {
            "width": 800,
            "height": 500,
            "scale": "1:100",
        },
        "zones": {
            "main_dining": {
                "name": "Main Dining Area",
                "color": "#e3f2fd",
                "description": "Primary dining area with standard tables",
            },
            "patio": {
                "name": "Outdoor Patio",
                "color": "#e8f5e8",
                "description": "Outdoor seating area",
            },
            "private": {
                "name": "Private Dining",
                "color": "#fff3e0",
                "description": "Private rooms for special events",
            },
            "bar": {
                "name": "Bar Area",
                "color": "#fce4ec",
                "description": "Bar seating and high tables",
            },
        },
        "operating_hours": {
            "monday": {"open": "11:00", "close": "22:00"},
            "tuesday": {"open": "11:00", "close": "22:00"},
            "wednesday": {"open": "11:00", "close": "22:00"},
            "thursday": {"open": "11:00", "close": "22:00"},
            "friday": {"open": "11:00", "close": "23:00"},
            "saturday": {"open": "10:00", "close": "23:00"},
            "sunday": {"open": "10:00", "close": "21:00"},
        },
        "reservation_settings": {
            "min_advance_hours": 1,
            "max_advance_days": 30,
            "default_duration_minutes": 90,
            "buffer_time_minutes": 15,
            "max_party_size": 12,
            "allow_walk_ins": True,
        },
    }