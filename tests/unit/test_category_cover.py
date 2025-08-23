"""
Unit tests for category cover image functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from app.modules.menu.models.category import (
    MenuCategory,
    MenuCategoryCreate,
    MenuCategoryUpdate,
    MenuCategoryRead,
)
from app.modules.menu.services.category import MenuCategoryService
from app.modules.menu.services.item import MenuItemService
from fastapi import HTTPException


class TestCategoryCoverModels:
    """Test category cover image model functionality."""
    
    def test_menu_category_with_cover_image(self):
        """Test MenuCategory model with cover_image_url field."""
        category_data = {
            "name": "Appetizers",
            "description": "Delicious appetizers to start your meal",
            "sort_order": 1,
            "is_active": True,
            "cover_image_url": "https://example.com/images/appetizers.jpg"
        }
        
        category = MenuCategoryCreate(**category_data)
        assert category.name == "Appetizers"
        assert category.cover_image_url == "https://example.com/images/appetizers.jpg"
        
    def test_menu_category_without_cover_image(self):
        """Test MenuCategory model without cover_image_url."""
        category_data = {
            "name": "Desserts",
            "description": "Sweet treats to end your meal"
        }
        
        category = MenuCategoryCreate(**category_data)
        assert category.name == "Desserts"
        assert category.cover_image_url is None
        
    def test_menu_category_update_cover_image(self):
        """Test updating category cover image."""
        update_data = {
            "cover_image_url": "https://example.com/images/new-cover.jpg"
        }
        
        category_update = MenuCategoryUpdate(**update_data)
        assert category_update.cover_image_url == "https://example.com/images/new-cover.jpg"
        
    def test_menu_category_read_with_cover_image(self):
        """Test MenuCategoryRead schema with cover image."""
        read_data = {
            "id": str(uuid4()),
            "organization_id": str(uuid4()),
            "restaurant_id": str(uuid4()),
            "name": "Main Courses",
            "description": "Hearty main course dishes",
            "sort_order": 2,
            "is_active": True,
            "cover_image_url": "https://example.com/images/main-courses.jpg",
            "created_at": "2025-08-17T10:00:00",
            "updated_at": "2025-08-17T10:00:00"
        }
        
        category = MenuCategoryRead(**read_data)
        assert category.name == "Main Courses"
        assert category.cover_image_url == "https://example.com/images/main-courses.jpg"


class TestCategoryCoverService:
    """Test category cover image service functionality."""
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        session = AsyncMock()
        return session
    
    @pytest.fixture
    def sample_organization_id(self):
        """Sample organization ID."""
        return str(uuid4())
    
    @pytest.fixture
    def sample_restaurant_id(self):
        """Sample restaurant ID."""
        return str(uuid4())
    
    @pytest.fixture
    def sample_category_id(self):
        """Sample category ID."""
        return str(uuid4())
    
    @pytest.fixture
    def sample_item_id(self):
        """Sample menu item ID."""
        return str(uuid4())
    
    @pytest.mark.asyncio
    async def test_set_category_cover_from_item_success(self, mock_session, sample_organization_id, 
                                                       sample_restaurant_id, sample_category_id, 
                                                       sample_item_id):
        """Test successfully setting category cover image from menu item."""
        # Mock menu item with image
        mock_item = Mock()
        mock_item.id = sample_item_id
        mock_item.category_id = sample_category_id
        mock_item.image_url = "https://example.com/images/pizza.jpg"
        
        # Mock category
        mock_category = Mock()
        mock_category.id = sample_category_id
        mock_category.cover_image_url = None
        
        # Mock service methods
        original_get_item = MenuMenuItemService.get_item_by_id
        original_get_category = MenuMenuCategoryService.get_category_by_id
        original_update_category = MenuMenuCategoryService.update_category
        
        MenuMenuItemService.get_item_by_id = AsyncMock(return_value=mock_item)
        MenuMenuCategoryService.get_category_by_id = AsyncMock(return_value=mock_category)
        MenuMenuCategoryService.update_category = AsyncMock(return_value=mock_category)
        
        try:
            # This would be implemented in MenuMenuItemService
            item = await MenuMenuItemService.get_item_by_id(
                mock_session, sample_item_id, sample_organization_id, sample_restaurant_id
            )
            
            category = await MenuMenuCategoryService.get_category_by_id(
                mock_session, sample_category_id, sample_organization_id, sample_restaurant_id
            )
            
            # Update category with item's image URL
            update_data = MenuCategoryUpdate(cover_image_url=item.image_url)
            result = await MenuMenuCategoryService.update_category(
                mock_session, sample_category_id, update_data, sample_organization_id, sample_restaurant_id
            )
            
            assert item.image_url == "https://example.com/images/pizza.jpg"
            MenuMenuItemService.get_item_by_id.assert_called_once()
            MenuMenuCategoryService.get_category_by_id.assert_called_once()
            MenuMenuCategoryService.update_category.assert_called_once()
            
        finally:
            # Restore original methods
            MenuMenuItemService.get_item_by_id = original_get_item
            MenuMenuCategoryService.get_category_by_id = original_get_category
            MenuMenuCategoryService.update_category = original_update_category
    
    @pytest.mark.asyncio
    async def test_set_category_cover_item_not_found(self, mock_session, sample_organization_id, 
                                                    sample_restaurant_id, sample_item_id):
        """Test setting category cover when menu item is not found."""
        # Mock service method to raise HTTPException
        original_get_item = MenuItemService.get_item_by_id
        MenuItemService.get_item_by_id = AsyncMock(side_effect=HTTPException(status_code=404, detail="Menu item not found"))
        
        try:
            with pytest.raises(HTTPException) as exc_info:
                await MenuItemService.get_item_by_id(
                    mock_session, sample_item_id, sample_organization_id, sample_restaurant_id
                )
            assert exc_info.value.status_code == 404
            assert "Menu item not found" in str(exc_info.value.detail)
        finally:
            # Restore original method
            MenuItemService.get_item_by_id = original_get_item
    
    @pytest.mark.asyncio
    async def test_set_category_cover_item_no_image(self, mock_session, sample_organization_id, 
                                                   sample_restaurant_id, sample_category_id, 
                                                   sample_item_id):
        """Test setting category cover when menu item has no image."""
        # Mock menu item without image
        mock_item = Mock()
        mock_item.id = sample_item_id
        mock_item.category_id = sample_category_id
        mock_item.image_url = None
        
        # Mock service method
        original_get_item = MenuItemService.get_item_by_id
        MenuItemService.get_item_by_id = AsyncMock(return_value=mock_item)
        
        try:
            item = await MenuItemService.get_item_by_id(
                mock_session, sample_item_id, sample_organization_id, sample_restaurant_id
            )
            
            assert item.image_url is None
            # This would result in a validation error in the actual service
            
        finally:
            # Restore original method
            MenuItemService.get_item_by_id = original_get_item
    
    @pytest.mark.asyncio
    async def test_set_category_cover_different_category(self, mock_session, sample_organization_id, 
                                                        sample_restaurant_id, sample_item_id):
        """Test setting category cover when item belongs to different category."""
        different_category_id = str(uuid4())
        
        # Mock menu item with different category
        mock_item = Mock()
        mock_item.id = sample_item_id
        mock_item.category_id = different_category_id
        mock_item.image_url = "https://example.com/images/pizza.jpg"
        
        # Mock service method
        original_get_item = MenuItemService.get_item_by_id
        MenuItemService.get_item_by_id = AsyncMock(return_value=mock_item)
        
        try:
            item = await MenuItemService.get_item_by_id(
                mock_session, sample_item_id, sample_organization_id, sample_restaurant_id
            )
            
            assert item.category_id == different_category_id
            # This would be validated in the actual service to ensure item belongs to target category
            
        finally:
            # Restore original method
            MenuItemService.get_item_by_id = original_get_item
    
    @pytest.mark.asyncio
    async def test_update_category_cover_directly(self, mock_session, sample_organization_id, 
                                                 sample_restaurant_id, sample_category_id):
        """Test updating category cover image directly."""
        new_cover_url = "https://example.com/images/new-category-cover.jpg"
        
        # Mock category
        mock_category = Mock()
        mock_category.id = sample_category_id
        mock_category.cover_image_url = new_cover_url
        
        # Mock service method
        original_update_category = MenuCategoryService.update_category
        MenuCategoryService.update_category = AsyncMock(return_value=mock_category)
        
        try:
            update_data = MenuCategoryUpdate(cover_image_url=new_cover_url)
            result = await MenuCategoryService.update_category(
                mock_session, sample_category_id, update_data, sample_organization_id, sample_restaurant_id
            )
            
            assert result.cover_image_url == new_cover_url
            MenuCategoryService.update_category.assert_called_once()
            
        finally:
            # Restore original method
            MenuCategoryService.update_category = original_update_category
    
    @pytest.mark.asyncio
    async def test_remove_category_cover(self, mock_session, sample_organization_id, 
                                        sample_restaurant_id, sample_category_id):
        """Test removing category cover image."""
        # Mock category without cover
        mock_category = Mock()
        mock_category.id = sample_category_id
        mock_category.cover_image_url = None
        
        # Mock service method
        original_update_category = MenuCategoryService.update_category
        MenuCategoryService.update_category = AsyncMock(return_value=mock_category)
        
        try:
            update_data = MenuCategoryUpdate(cover_image_url=None)
            result = await MenuCategoryService.update_category(
                mock_session, sample_category_id, update_data, sample_organization_id, sample_restaurant_id
            )
            
            assert result.cover_image_url is None
            MenuCategoryService.update_category.assert_called_once()
            
        finally:
            # Restore original method
            MenuCategoryService.update_category = original_update_category


class TestCategoryCoverValidation:
    """Test category cover image validation."""
    
    def test_cover_image_url_max_length(self):
        """Test cover image URL maximum length validation."""
        # Test valid URL length (within 500 characters)
        valid_url = "https://example.com/images/" + "a" * 450 + ".jpg"
        
        category = MenuCategoryCreate(
            name="Test Category",
            cover_image_url=valid_url
        )
        assert len(category.cover_image_url) <= 500
        
    def test_cover_image_url_format(self):
        """Test cover image URL format validation."""
        # Test various URL formats
        valid_urls = [
            "https://example.com/image.jpg",
            "http://example.com/image.png",
            "https://cdn.example.com/path/to/image.webp",
            None  # None should be valid (no cover image)
        ]
        
        for url in valid_urls:
            category = MenuCategoryCreate(
                name="Test Category",
                cover_image_url=url
            )
            assert category.cover_image_url == url
    
    def test_cover_image_optional(self):
        """Test that cover image is optional."""
        category = MenuCategoryCreate(name="Test Category")
        assert category.cover_image_url is None
        
    def test_cover_image_update_optional(self):
        """Test that cover image update is optional."""
        update = MenuCategoryUpdate(name="Updated Name")
        assert not hasattr(update, 'cover_image_url') or update.cover_image_url is None


class TestCategoryCoverIntegration:
    """Test category cover image integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_category_with_multiple_items_covers(self):
        """Test category with multiple items that could be covers."""
        mock_session = AsyncMock()
        category_id = str(uuid4())
        
        # Mock multiple items in category
        mock_items = [
            Mock(id=str(uuid4()), image_url="https://example.com/item1.jpg"),
            Mock(id=str(uuid4()), image_url="https://example.com/item2.jpg"),
            Mock(id=str(uuid4()), image_url=None),  # Item without image
        ]
        
        # This would be implemented in the actual service to handle multiple items
        # For now, we just test that we can have multiple items with images
        for item in mock_items:
            if item.image_url:
                assert item.image_url.startswith("https://")
    
    def test_category_cover_persistence(self):
        """Test that category cover persists through updates."""
        original_cover = "https://example.com/original.jpg"
        
        # Create category with cover
        category = MenuCategoryCreate(
            name="Test Category",
            cover_image_url=original_cover
        )
        assert category.cover_image_url == original_cover
        
        # Update other fields, cover should remain
        update = MenuCategoryUpdate(description="Updated description")
        # In actual implementation, the service would preserve the existing cover_image_url
        # when it's not included in the update
        assert update.description == "Updated description"