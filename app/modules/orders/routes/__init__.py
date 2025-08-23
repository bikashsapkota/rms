"""
Order management API routes.
"""

from .orders import router as orders_router
from .kitchen import router as kitchen_router
from .payments import router as payments_router
from .qr_orders import router as qr_orders_router

__all__ = [
    "orders_router",
    "kitchen_router",
    "payments_router", 
    "qr_orders_router",
]