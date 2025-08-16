"""
Sample organization data for development and testing.
"""

from typing import List, Dict, Any

SAMPLE_ORGANIZATIONS: List[Dict[str, Any]] = [
    {
        "name": "Pizza Palace Corporation",
        "organization_type": "chain",
        "subscription_tier": "professional",
        "billing_email": "billing@pizzapalace.com",
        "is_active": True,
    },
    {
        "name": "Local Bistro LLC",
        "organization_type": "independent",
        "subscription_tier": "basic",
        "billing_email": "owner@localbistro.com",
        "is_active": True,
    },
    {
        "name": "Global Fast Food Franchise",
        "organization_type": "franchise",
        "subscription_tier": "enterprise",
        "billing_email": "corporate@globalfastfood.com",
        "is_active": True,
    },
]