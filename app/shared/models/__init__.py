# Import all models to ensure they're registered with SQLModel
from .organization import Organization
from .restaurant import Restaurant  
from .user import User

__all__ = ["Organization", "Restaurant", "User"]