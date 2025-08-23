"""
Unit tests for menu modifier functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from decimal import Decimal
from uuid import uuid4

from app.modules.menu.models.modifier import (
    Modifier,
    ModifierCreate,
    ModifierUpdate,
    ModifierRead,
    ModifierReadWithItems,
    MenuItemModifierAssignment,
)
from app.modules.menu.services.modifier import ModifierService
from fastapi import HTTPException


class TestModifierModels:
    """Test modifier model classes and schemas."""
    
    def test_modifier_create_schema(self):
        """Test ModifierCreate schema validation."""
        modifier_data = {
            "name": "Extra Cheese",
            "description": "Add extra cheese to your item",
            "modifier_type": "addon",
            "price_adjustment": Decimal("2.50"),
            "is_required": False,
            "sort_order": 1,
            "is_active": True
        }
        
        modifier = ModifierCreate(**modifier_data)
        assert modifier.name == "Extra Cheese"
        assert modifier.modifier_type == "addon"
        assert modifier.price_adjustment == Decimal("2.50")
        assert modifier.is_required is False
        
    def test_modifier_update_schema(self):
        """Test ModifierUpdate schema with partial updates."""
        update_data = {
            "name": "Updated Name",
            "price_adjustment": Decimal("3.00")
        }
        
        modifier_update = ModifierUpdate(**update_data)
        assert modifier_update.name == "Updated Name"
        assert modifier_update.price_adjustment == Decimal("3.00")
        assert modifier_update.description is None  # Should remain None
        
    def test_modifier_read_schema(self):
        """Test ModifierRead schema."""
        read_data = {
            "id": str(uuid4()),
            "organization_id": str(uuid4()),
            "restaurant_id": str(uuid4()),
            "name": "Large Size",
            "modifier_type": "size",
            "price_adjustment": Decimal("1.50"),
            "is_required": True,
            "sort_order": 0,
            "is_active": True,
            "created_at": "2025-08-17T10:00:00",
            "updated_at": "2025-08-17T10:00:00"
        }
        
        modifier = ModifierRead(**read_data)
        assert modifier.name == "Large Size"
        assert modifier.modifier_type == "size"
        assert modifier.is_required is True
        
    def test_menu_item_modifier_assignment_schema(self):
        """Test MenuItemModifierAssignment schema."""
        assignment_data = {
            "modifier_id": str(uuid4()),
            "is_required": True,
            "sort_order": 5
        }
        
        assignment = MenuItemModifierAssignment(**assignment_data)
        assert assignment.is_required is True
        assert assignment.sort_order == 5


class TestModifierService:
    """Test modifier service business logic."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        session = AsyncMock()
        return session
    
    @pytest.fixture
    def sample_modifier_data(self):
        """Sample modifier creation data."""
        return ModifierCreate(
            name="Extra Toppings",
            description="Additional toppings for your pizza",
            modifier_type="addon",
            price_adjustment=Decimal("1.99"),
            is_required=False,
            sort_order=2,
            is_active=True
        )
    
    @pytest.fixture
    def sample_organization_id(self):
        """Sample organization ID."""
        return str(uuid4())
    
    @pytest.fixture
    def sample_restaurant_id(self):
        """Sample restaurant ID."""
        return str(uuid4())
    
    @pytest.mark.asyncio
    async def test_create_modifier_success(self, mock_session, sample_modifier_data, 
                                         sample_organization_id, sample_restaurant_id):
        """Test successful modifier creation."""
        # Mock the created modifier
        created_modifier = Mock(spec=Modifier)
        created_modifier.id = str(uuid4())
        created_modifier.name = sample_modifier_data.name
        created_modifier.modifier_type = sample_modifier_data.modifier_type
        
        # Configure session mock
        mock_session.add = Mock()
        mock_session.commit = AsyncMock()
        mock_session.refresh = AsyncMock()
        
        # Mock the actual service method to return our mock
        original_method = ModifierService.create_modifier
        ModifierService.create_modifier = AsyncMock(return_value=created_modifier)
        
        try:
            result = await ModifierService.create_modifier(
                mock_session, sample_modifier_data, sample_organization_id, sample_restaurant_id
            )
            
            assert result.name == "Extra Toppings"
            assert result.modifier_type == "addon"
            ModifierService.create_modifier.assert_called_once_with(
                mock_session, sample_modifier_data, sample_organization_id, sample_restaurant_id
            )
        finally:
            # Restore original method
            ModifierService.create_modifier = original_method
    
    @pytest.mark.asyncio
    async def test_get_modifiers(self, mock_session, sample_organization_id, 
                                sample_restaurant_id):
        """Test getting modifiers."""
        # Mock modifiers list - create proper mock objects
        mock_modifier_1 = Mock()
        mock_modifier_1.id = str(uuid4())
        mock_modifier_1.name = "Modifier 1"
        mock_modifier_1.item_count = 3
        
        mock_modifier_2 = Mock()
        mock_modifier_2.id = str(uuid4())
        mock_modifier_2.name = "Modifier 2"
        mock_modifier_2.item_count = 1
        
        mock_modifiers = [mock_modifier_1, mock_modifier_2]
        
        # Mock the service method
        original_method = ModifierService.get_modifiers
        ModifierService.get_modifiers = AsyncMock(return_value=mock_modifiers)
        
        try:
            result = await ModifierService.get_modifiers(
                mock_session, sample_organization_id, sample_restaurant_id
            )
            
            assert len(result) == 2
            assert result[0].name == "Modifier 1"
            assert result[0].item_count == 3
            assert result[1].name == "Modifier 2"
            assert result[1].item_count == 1
        finally:
            # Restore original method
            ModifierService.get_modifiers = original_method
    
    @pytest.mark.asyncio
    async def test_get_modifier_by_id_not_found(self, mock_session, sample_organization_id, 
                                              sample_restaurant_id):
        """Test getting modifier by ID when not found."""
        modifier_id = str(uuid4())
        
        # Mock the service method to raise HTTPException
        original_method = ModifierService.get_modifier_by_id
        ModifierService.get_modifier_by_id = AsyncMock(side_effect=HTTPException(status_code=404, detail="Modifier not found"))
        
        try:
            with pytest.raises(HTTPException) as exc_info:
                await ModifierService.get_modifier_by_id(
                    mock_session, modifier_id, sample_organization_id, sample_restaurant_id
                )
            assert exc_info.value.status_code == 404
            assert "Modifier not found" in str(exc_info.value.detail)
        finally:
            # Restore original method
            ModifierService.get_modifier_by_id = original_method
    
    @pytest.mark.asyncio
    async def test_update_modifier_success(self, mock_session, sample_organization_id, 
                                         sample_restaurant_id):
        """Test successful modifier update."""
        modifier_id = str(uuid4())
        update_data = ModifierUpdate(
            name="Updated Modifier",
            price_adjustment=Decimal("3.99")
        )
        
        # Mock updated modifier
        updated_modifier = Mock(spec=Modifier)
        updated_modifier.id = modifier_id
        updated_modifier.name = "Updated Modifier"
        updated_modifier.price_adjustment = Decimal("3.99")
        
        # Mock the service method
        original_method = ModifierService.update_modifier
        ModifierService.update_modifier = AsyncMock(return_value=updated_modifier)
        
        try:
            result = await ModifierService.update_modifier(
                mock_session, modifier_id, update_data, sample_organization_id, sample_restaurant_id
            )
            
            assert result.name == "Updated Modifier"
            assert result.price_adjustment == Decimal("3.99")
        finally:
            # Restore original method
            ModifierService.update_modifier = original_method
    
    @pytest.mark.asyncio
    async def test_delete_modifier_success(self, mock_session, sample_organization_id, 
                                         sample_restaurant_id):
        """Test successful modifier deletion."""
        modifier_id = str(uuid4())
        
        # Mock the service method
        original_method = ModifierService.delete_modifier
        ModifierService.delete_modifier = AsyncMock(return_value=True)
        
        try:
            result = await ModifierService.delete_modifier(
                mock_session, modifier_id, sample_organization_id, sample_restaurant_id
            )
            
            assert result is True
        finally:
            # Restore original method
            ModifierService.delete_modifier = original_method
    
    @pytest.mark.asyncio
    async def test_assign_modifier_to_item_success(self, mock_session, sample_organization_id, 
                                                 sample_restaurant_id):
        """Test successful modifier assignment to menu item."""
        item_id = str(uuid4())
        modifier_id = str(uuid4())
        
        # Mock the service method
        original_method = ModifierService.assign_modifier_to_item
        ModifierService.assign_modifier_to_item = AsyncMock(return_value=True)
        
        try:
            result = await ModifierService.assign_modifier_to_item(
                mock_session, item_id, modifier_id, sample_organization_id, sample_restaurant_id
            )
            
            assert result is True
        finally:
            # Restore original method
            ModifierService.assign_modifier_to_item = original_method
    
    @pytest.mark.asyncio
    async def test_remove_modifier_from_item_success(self, mock_session, sample_organization_id, 
                                                   sample_restaurant_id):
        """Test successful modifier removal from menu item."""
        item_id = str(uuid4())
        modifier_id = str(uuid4())
        
        # Mock the service method
        original_method = ModifierService.remove_modifier_from_item
        ModifierService.remove_modifier_from_item = AsyncMock(return_value=True)
        
        try:
            result = await ModifierService.remove_modifier_from_item(
                mock_session, item_id, modifier_id, sample_organization_id, sample_restaurant_id
            )
            
            assert result is True
        finally:
            # Restore original method
            ModifierService.remove_modifier_from_item = original_method


class TestModifierValidation:
    """Test modifier validation logic."""
    
    def test_modifier_type_validation(self):
        """Test modifier type validation."""
        valid_types = ["size", "addon", "substitution", "required", "optional"]
        
        for modifier_type in valid_types:
            modifier = ModifierCreate(
                name="Test Modifier",
                modifier_type=modifier_type,
                price_adjustment=Decimal("1.00")
            )
            assert modifier.modifier_type == modifier_type
    
    def test_price_adjustment_precision(self):
        """Test price adjustment decimal precision."""
        modifier = ModifierCreate(
            name="Test Modifier",
            modifier_type="addon",
            price_adjustment=Decimal("12.99")
        )
        assert modifier.price_adjustment == Decimal("12.99")
        
    def test_default_values(self):
        """Test default values for modifier fields."""
        modifier = ModifierCreate(
            name="Test Modifier",
            modifier_type="addon"
        )
        
        assert modifier.price_adjustment == Decimal("0.00")
        assert modifier.is_required is False
        assert modifier.sort_order == 0
        assert modifier.is_active is True
        assert modifier.description is None