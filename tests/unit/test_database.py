"""
Unit tests for database utilities and base models.
"""

import pytest
from datetime import datetime
from app.shared.database.base import TenantBaseModel, RestaurantTenantBaseModel
from sqlmodel import SQLModel, Field


class MockTenantModel(TenantBaseModel, table=True):
    """Test model for tenant base functionality."""
    __tablename__ = "mock_tenant_model"
    
    name: str = Field(max_length=255)


class MockRestaurantTenantModel(RestaurantTenantBaseModel, table=True):
    """Test model for restaurant tenant base functionality."""
    __tablename__ = "mock_restaurant_tenant_model"
    
    name: str = Field(max_length=255)


class TestTenantBaseModel:
    """Test tenant base model functionality."""

    def test_tenant_base_model_fields(self):
        """Test that tenant base model has required fields."""
        model = MockTenantModel(
            name="Test Model",
            organization_id="test-org-id"
        )
        
        assert hasattr(model, 'id')
        assert hasattr(model, 'organization_id')
        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')
        assert hasattr(model, 'is_active')
        
        assert model.organization_id == "test-org-id"
        assert model.is_active is True

    def test_tenant_base_model_timestamps(self):
        """Test that timestamps are properly set."""
        model = MockTenantModel(
            name="Test Model",
            organization_id="test-org-id"
        )
        
        # Check that timestamps are datetime objects
        assert isinstance(model.created_at, datetime)
        assert isinstance(model.updated_at, datetime)
        
        # Check that created_at and updated_at are close to now
        now = datetime.utcnow()
        assert abs((now - model.created_at).total_seconds()) < 1
        assert abs((now - model.updated_at).total_seconds()) < 1

    def test_tenant_base_model_id_generation(self):
        """Test that UUID IDs are generated."""
        model1 = MockTenantModel(
            name="Test Model 1",
            organization_id="test-org-id"
        )
        
        model2 = MockTenantModel(
            name="Test Model 2", 
            organization_id="test-org-id"
        )
        
        assert model1.id is not None
        assert model2.id is not None
        assert model1.id != model2.id
        
        # Check that IDs are valid UUIDs (string format)
        assert len(str(model1.id)) == 36  # UUID string length
        assert '-' in str(model1.id)  # UUID has dashes


class TestRestaurantTenantBaseModel:
    """Test restaurant tenant base model functionality."""

    def test_restaurant_tenant_base_model_fields(self):
        """Test that restaurant tenant base model has required fields."""
        model = MockRestaurantTenantModel(
            name="Test Restaurant Model",
            organization_id="test-org-id",
            restaurant_id="test-restaurant-id"
        )
        
        assert hasattr(model, 'id')
        assert hasattr(model, 'organization_id')
        assert hasattr(model, 'restaurant_id')
        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')
        assert hasattr(model, 'is_active')
        
        assert model.organization_id == "test-org-id"
        assert model.restaurant_id == "test-restaurant-id"
        assert model.is_active is True

    def test_restaurant_tenant_inheritance(self):
        """Test that restaurant tenant model inherits from tenant model."""
        model = MockRestaurantTenantModel(
            name="Test Restaurant Model",
            organization_id="test-org-id",
            restaurant_id="test-restaurant-id"
        )
        
        # Should have all TenantBaseModel fields
        assert hasattr(model, 'organization_id')
        assert hasattr(model, 'created_at')
        assert hasattr(model, 'updated_at')
        assert hasattr(model, 'is_active')
        
        # Plus additional restaurant field
        assert hasattr(model, 'restaurant_id')

    def test_restaurant_tenant_optional_restaurant_id(self):
        """Test that restaurant_id can be None for organization-level records."""
        model = MockRestaurantTenantModel(
            name="Organization-level Model",
            organization_id="test-org-id",
            restaurant_id=None
        )
        
        assert model.organization_id == "test-org-id"
        assert model.restaurant_id is None