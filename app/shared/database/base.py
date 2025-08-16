from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class TimestampMixin(SQLModel):
    """Mixin for timestamp fields."""
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        sa_column_kwargs={"onupdate": datetime.utcnow},
        nullable=False,
    )


class TenantMixin(SQLModel):
    """Mixin for multi-tenant fields."""
    organization_id: UUID = Field(foreign_key="organizations.id", index=True)
    

class RestaurantTenantMixin(TenantMixin):
    """Mixin for restaurant-level tenant fields."""
    restaurant_id: UUID = Field(foreign_key="restaurants.id", index=True)


class BaseModel(TimestampMixin):
    """Base model with UUID primary key and timestamps."""
    id: UUID = Field(default_factory=uuid4, primary_key=True)


class TenantBaseModel(BaseModel, TenantMixin):
    """Base model for organization-level tenant resources."""
    pass


class RestaurantTenantBaseModel(BaseModel, RestaurantTenantMixin):
    """Base model for restaurant-level tenant resources."""
    pass