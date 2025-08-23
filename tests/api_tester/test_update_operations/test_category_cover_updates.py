"""
Test category cover image update operations.
"""

import asyncio
import pytest
from typing import Dict, Any
from tests.api_tester.shared.utils import api_request
from tests.api_tester.shared.auth import get_auth_headers
from tests.api_tester.shared.fixtures import API_BASE_URL


class TestCategoryCoverUpdates:
    """Test category cover image update operations."""
    
    @pytest.fixture(scope="class")
    def event_loop(self):
        """Create an event loop for the test class."""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()
    
    @pytest.fixture(scope="class")
    async def auth_setup(self):
        """Setup authentication for tests."""
        # Use existing test user credentials
        auth_data = {
            "username": "admin@testpizza.com",
            "password": "testpassword123"
        }
        
        response = await api_request("POST", f"{API_BASE_URL}/auth/login", json=auth_data)
        
        if response.status_code != 200:
            pytest.skip("Authentication failed - requires setup")
        
        token_data = response.json()
        return {
            "headers": get_auth_headers(token_data["access_token"]),
            "organization_id": token_data["user"]["organization_id"],
            "restaurant_id": token_data["user"]["restaurant_id"]
        }
    
    @pytest.fixture(scope="class")
    async def test_category(self, auth_setup):
        """Create a test category for cover image tests."""
        category_data = {
            "name": "Cover Image Test Category",
            "description": "Category for testing cover images",
            "sort_order": 99
        }
        
        url = f"{API_BASE_URL}/categories/"
        response = await api_request(
            "POST", 
            url, 
            json=category_data, 
            headers=auth_setup["headers"]
        )
        
        if response.status_code != 200:
            pytest.skip("Category creation failed")
        
        category = response.json()
        yield category
        
        # Cleanup - delete the category
        delete_url = f"{API_BASE_URL}/categories/{category['id']}"
        await api_request("DELETE", delete_url, headers=auth_setup["headers"])
    
    @pytest.fixture(scope="class")
    async def test_menu_item(self, auth_setup, test_category):
        """Create a test menu item with an image for cover tests."""
        item_data = {
            "name": "Cover Image Test Item",
            "description": "Item for testing category cover images",
            "price": 12.99,
            "category_id": test_category["id"],
            "image_url": "https://example.com/images/test-item.jpg"
        }
        
        url = f"{API_BASE_URL}/items/"
        response = await api_request(
            "POST", 
            url, 
            json=item_data, 
            headers=auth_setup["headers"]
        )
        
        if response.status_code != 200:
            pytest.skip("Menu item creation failed")
        
        item = response.json()
        yield item
        
        # Cleanup - delete the item
        delete_url = f"{API_BASE_URL}/items/{item['id']}"
        await api_request("DELETE", delete_url, headers=auth_setup["headers"])
    
    @pytest.mark.asyncio
    async def test_update_category_cover_directly(self, auth_setup, test_category):
        """Test updating category cover image directly."""
        cover_image_url = "https://example.com/images/category-cover.jpg"
        
        update_data = {
            "cover_image_url": cover_image_url
        }
        
        url = f"{API_BASE_URL}/categories/{test_category['id']}"
        response = await api_request(
            "PUT", 
            url, 
            json=update_data, 
            headers=auth_setup["headers"]
        )
        
        assert response.status_code == 200
        updated_category = response.json()
        
        assert updated_category["cover_image_url"] == cover_image_url
        assert updated_category["name"] == test_category["name"]  # Other fields unchanged
    
    @pytest.mark.asyncio
    async def test_set_item_as_category_cover(self, auth_setup, test_category, test_menu_item):
        """Test setting a menu item's image as category cover."""
        url = f"{API_BASE_URL}/items/{test_menu_item['id']}/set-as-category-cover"
        response = await api_request("PUT", url, headers=auth_setup["headers"])
        
        assert response.status_code == 200
        result = response.json()
        
        assert "message" in result
        assert "category_id" in result
        assert result["category_id"] == test_category["id"]
        
        # Verify the category was updated
        category_url = f"{API_BASE_URL}/categories/{test_category['id']}"
        category_response = await api_request("GET", category_url, headers=auth_setup["headers"])
        
        assert category_response.status_code == 200
        updated_category = category_response.json()
        
        assert updated_category["cover_image_url"] == test_menu_item["image_url"]
    
    @pytest.mark.asyncio
    async def test_set_cover_item_without_image(self, auth_setup, test_category):
        """Test setting an item without image as category cover."""
        # Create an item without image
        item_data = {
            "name": "No Image Item",
            "description": "Item without image",
            "price": 8.99,
            "category_id": test_category["id"]
            # No image_url
        }
        
        create_url = f"{API_BASE_URL}/items/"
        create_response = await api_request(
            "POST", 
            create_url, 
            json=item_data, 
            headers=auth_setup["headers"]
        )
        
        if create_response.status_code != 200:
            pytest.skip("Item creation failed")
        
        item = create_response.json()
        item_id = item["id"]
        
        try:
            # Try to set as cover
            cover_url = f"{API_BASE_URL}/items/{item_id}/set-as-category-cover"
            cover_response = await api_request("PUT", cover_url, headers=auth_setup["headers"])
            
            # Should fail because item has no image
            assert cover_response.status_code == 400  # Bad request
            
        finally:
            # Cleanup
            delete_url = f"{API_BASE_URL}/items/{item_id}"
            await api_request("DELETE", delete_url, headers=auth_setup["headers"])
    
    @pytest.mark.asyncio
    async def test_set_cover_nonexistent_item(self, auth_setup):
        """Test setting cover with non-existent item ID."""
        fake_item_id = "00000000-0000-0000-0000-000000000000"
        
        url = f"{API_BASE_URL}/items/{fake_item_id}/set-as-category-cover"
        response = await api_request("PUT", url, headers=auth_setup["headers"])
        
        assert response.status_code == 404  # Not found
    
    @pytest.mark.asyncio
    async def test_remove_category_cover(self, auth_setup, test_category):
        """Test removing category cover image."""
        # First set a cover image
        cover_image_url = "https://example.com/images/temp-cover.jpg"
        
        set_data = {
            "cover_image_url": cover_image_url
        }
        
        set_url = f"{API_BASE_URL}/categories/{test_category['id']}"
        set_response = await api_request(
            "PUT", 
            set_url, 
            json=set_data, 
            headers=auth_setup["headers"]
        )
        
        assert set_response.status_code == 200
        
        # Now remove the cover image
        remove_data = {
            "cover_image_url": None
        }
        
        remove_response = await api_request(
            "PUT", 
            set_url, 
            json=remove_data, 
            headers=auth_setup["headers"]
        )
        
        assert remove_response.status_code == 200
        updated_category = remove_response.json()
        
        assert updated_category["cover_image_url"] is None
    
    @pytest.mark.asyncio
    async def test_category_cover_in_list_response(self, auth_setup, test_category):
        """Test that cover image appears in category list response."""
        # Set a cover image
        cover_image_url = "https://example.com/images/list-test-cover.jpg"
        
        update_data = {
            "cover_image_url": cover_image_url
        }
        
        update_url = f"{API_BASE_URL}/categories/{test_category['id']}"
        await api_request(
            "PUT", 
            update_url, 
            json=update_data, 
            headers=auth_setup["headers"]
        )
        
        # Get categories list
        list_url = f"{API_BASE_URL}/categories/"
        list_response = await api_request("GET", list_url, headers=auth_setup["headers"])
        
        assert list_response.status_code == 200
        categories = list_response.json()
        
        # Find our test category
        test_cat = next(
            (cat for cat in categories if cat["id"] == test_category["id"]), 
            None
        )
        
        assert test_cat is not None
        assert test_cat["cover_image_url"] == cover_image_url
    
    @pytest.mark.asyncio
    async def test_category_cover_url_validation(self, auth_setup, test_category):
        """Test category cover URL validation."""
        # Test various URL formats
        valid_urls = [
            "https://example.com/image.jpg",
            "http://example.com/image.png",
            "https://cdn.example.com/path/to/image.webp",
        ]
        
        for url in valid_urls:
            update_data = {"cover_image_url": url}
            
            update_url = f"{API_BASE_URL}/categories/{test_category['id']}"
            response = await api_request(
                "PUT", 
                update_url, 
                json=update_data, 
                headers=auth_setup["headers"]
            )
            
            assert response.status_code == 200
            updated_category = response.json()
            assert updated_category["cover_image_url"] == url
    
    @pytest.mark.asyncio
    async def test_category_cover_unauthorized(self, test_category):
        """Test category cover update without authentication."""
        update_data = {
            "cover_image_url": "https://example.com/unauthorized.jpg"
        }
        
        url = f"{API_BASE_URL}/categories/{test_category['id']}"
        response = await api_request("PUT", url, json=update_data)
        
        assert response.status_code == 401  # Unauthorized
    
    @pytest.mark.asyncio
    async def test_set_cover_unauthorized(self, test_menu_item):
        """Test setting item as cover without authentication."""
        url = f"{API_BASE_URL}/items/{test_menu_item['id']}/set-as-category-cover"
        response = await api_request("PUT", url)
        
        assert response.status_code == 401  # Unauthorized