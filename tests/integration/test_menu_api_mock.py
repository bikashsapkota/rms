"""
Integration tests for menu API endpoints with mocked data.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from decimal import Decimal


class TestMenuCategoriesAPIMocked:
    """Test menu categories API endpoints with mocked services."""

    @patch('app.shared.auth.deps.get_current_user')
    @patch('app.shared.auth.deps.require_admin_or_staff')
    @patch('app.modules.menu.services.category.MenuCategoryService.get_categories')
    def test_list_categories_mocked(self, mock_get_categories, mock_require_auth, mock_get_user, client: TestClient):
        """Test listing menu categories with mocked service."""
        # Mock user
        mock_user = {
            "id": "user-id",
            "role": "admin",
            "organization_id": "org-id",
            "restaurant_id": "restaurant-id"
        }
        
        # Mock categories
        mock_categories = [
            {
                "id": "cat1-id",
                "name": "Pizza",
                "description": "Delicious pizzas",
                "sort_order": 1,
                "is_active": True,
                "organization_id": "org-id",
                "restaurant_id": "restaurant-id"
            },
            {
                "id": "cat2-id", 
                "name": "Drinks",
                "description": "Refreshing beverages",
                "sort_order": 2,
                "is_active": True,
                "organization_id": "org-id",
                "restaurant_id": "restaurant-id"
            }
        ]
        
        mock_get_user.return_value = mock_user
        mock_require_auth.return_value = mock_user
        mock_get_categories.return_value = mock_categories
        
        response = client.get(
            "/api/v1/menu/categories/",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        categories = response.json()
        assert isinstance(categories, list)
        assert len(categories) == 2
        assert categories[0]["name"] == "Pizza"

    @patch('app.shared.auth.deps.get_current_user')
    @patch('app.shared.auth.deps.require_admin')
    @patch('app.modules.menu.services.category.MenuCategoryService.create_category')
    def test_create_category_admin_mocked(self, mock_create_category, mock_require_admin, mock_get_user, client: TestClient):
        """Test creating a category as admin with mocked service."""
        # Mock admin user
        admin_user = {
            "id": "admin-id",
            "role": "admin",
            "organization_id": "org-id",
            "restaurant_id": "restaurant-id"
        }
        
        # Mock created category
        created_category = {
            "id": "new-cat-id",
            "name": "Desserts",
            "description": "Sweet treats",
            "sort_order": 3,
            "is_active": True,
            "organization_id": "org-id",
            "restaurant_id": "restaurant-id"
        }
        
        mock_get_user.return_value = admin_user
        mock_require_admin.return_value = admin_user
        mock_create_category.return_value = created_category
        
        response = client.post(
            "/api/v1/menu/categories/",
            headers={"Authorization": "Bearer admin-token"},
            json={
                "name": "Desserts",
                "description": "Sweet treats",
                "sort_order": 3
            }
        )
        
        assert response.status_code == 200
        category_data = response.json()
        assert category_data["name"] == "Desserts"
        assert category_data["sort_order"] == 3

    def test_create_category_no_auth(self, client: TestClient):
        """Test creating category without authentication."""
        response = client.post(
            "/api/v1/menu/categories/",
            json={
                "name": "Unauthorized Category",
                "description": "Should not be created"
            }
        )
        
        assert response.status_code == 401

    @patch('app.shared.auth.deps.get_current_user')
    @patch('app.shared.auth.deps.require_admin_or_staff')
    @patch('app.modules.menu.services.category.MenuCategoryService.get_category_by_id')
    def test_get_category_by_id_mocked(self, mock_get_category, mock_require_auth, mock_get_user, client: TestClient):
        """Test getting a category by ID with mocked service."""
        mock_user = {"id": "user-id", "role": "admin"}
        mock_category = {
            "id": "cat-id",
            "name": "Pizza",
            "description": "Delicious pizzas",
            "is_active": True,
            "item_count": 5,
            "active_item_count": 4
        }
        
        mock_get_user.return_value = mock_user
        mock_require_auth.return_value = mock_user
        mock_get_category.return_value = mock_category
        
        response = client.get(
            "/api/v1/menu/categories/cat-id",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        category_data = response.json()
        assert category_data["name"] == "Pizza"
        assert "item_count" in category_data

    @patch('app.shared.auth.deps.get_current_user')
    @patch('app.shared.auth.deps.require_admin')
    @patch('app.modules.menu.services.category.MenuCategoryService.update_category')
    def test_update_category_mocked(self, mock_update_category, mock_require_admin, mock_get_user, client: TestClient):
        """Test updating a category with mocked service."""
        mock_user = {"id": "admin-id", "role": "admin"}
        mock_updated_category = {
            "id": "cat-id",
            "name": "Updated Pizza",
            "description": "Updated description",
            "is_active": True
        }
        
        mock_get_user.return_value = mock_user
        mock_require_admin.return_value = mock_user
        mock_update_category.return_value = mock_updated_category
        
        response = client.put(
            "/api/v1/menu/categories/cat-id",
            headers={"Authorization": "Bearer admin-token"},
            json={
                "name": "Updated Pizza",
                "description": "Updated description"
            }
        )
        
        assert response.status_code == 200
        category_data = response.json()
        assert category_data["name"] == "Updated Pizza"


class TestMenuItemsAPIMocked:
    """Test menu items API endpoints with mocked services."""

    @patch('app.shared.auth.deps.get_current_user')
    @patch('app.shared.auth.deps.require_admin_or_staff')
    @patch('app.modules.menu.services.item.MenuItemService.get_items')
    def test_list_items_mocked(self, mock_get_items, mock_require_auth, mock_get_user, client: TestClient):
        """Test listing menu items with mocked service."""
        mock_user = {"id": "user-id", "role": "staff"}
        mock_items = [
            {
                "id": "item1-id",
                "name": "Margherita Pizza",
                "description": "Fresh mozzarella and basil",
                "price": "15.99",
                "category_id": "cat-id",
                "is_available": True
            },
            {
                "id": "item2-id",
                "name": "Pepperoni Pizza", 
                "description": "Classic pepperoni",
                "price": "18.99",
                "category_id": "cat-id",
                "is_available": True
            }
        ]
        
        mock_get_user.return_value = mock_user
        mock_require_auth.return_value = mock_user
        mock_get_items.return_value = mock_items
        
        response = client.get(
            "/api/v1/menu/items/",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        items = response.json()
        assert isinstance(items, list)
        assert len(items) == 2
        assert items[0]["name"] == "Margherita Pizza"

    @patch('app.shared.auth.deps.get_current_user')
    @patch('app.shared.auth.deps.require_admin')
    @patch('app.modules.menu.services.item.MenuItemService.create_item')
    def test_create_item_admin_mocked(self, mock_create_item, mock_require_admin, mock_get_user, client: TestClient):
        """Test creating a menu item as admin with mocked service."""
        mock_user = {"id": "admin-id", "role": "admin"}
        mock_created_item = {
            "id": "new-item-id",
            "name": "New Pizza",
            "description": "A new delicious pizza",
            "price": "20.99",
            "category_id": "cat-id",
            "is_available": True,
            "organization_id": "org-id",
            "restaurant_id": "restaurant-id"
        }
        
        mock_get_user.return_value = mock_user
        mock_require_admin.return_value = mock_user
        mock_create_item.return_value = mock_created_item
        
        response = client.post(
            "/api/v1/menu/items/",
            headers={"Authorization": "Bearer admin-token"},
            json={
                "name": "New Pizza",
                "description": "A new delicious pizza",
                "price": 20.99,
                "category_id": "cat-id"
            }
        )
        
        assert response.status_code == 200
        item_data = response.json()
        assert item_data["name"] == "New Pizza"
        assert item_data["price"] == "20.99"

    def test_create_item_invalid_data(self, client: TestClient):
        """Test creating item with invalid data."""
        response = client.post(
            "/api/v1/menu/items/",
            headers={"Authorization": "Bearer admin-token"},
            json={
                "name": "",  # Invalid empty name
                "price": -5.0,  # Invalid negative price
                "category_id": "cat-id"
            }
        )
        
        assert response.status_code == 422  # Validation error

    @patch('app.shared.auth.deps.get_current_user')
    @patch('app.shared.auth.deps.require_admin_or_staff')
    @patch('app.modules.menu.services.item.MenuItemService.get_item_by_id')
    def test_get_item_by_id_mocked(self, mock_get_item, mock_require_auth, mock_get_user, client: TestClient):
        """Test getting a menu item by ID with mocked service."""
        mock_user = {"id": "user-id", "role": "staff"}
        mock_item = {
            "id": "item-id",
            "name": "Margherita Pizza",
            "description": "Fresh mozzarella and basil",
            "price": "15.99",
            "category_id": "cat-id",
            "category_name": "Pizza",
            "is_available": True
        }
        
        mock_get_user.return_value = mock_user
        mock_require_auth.return_value = mock_user
        mock_get_item.return_value = mock_item
        
        response = client.get(
            "/api/v1/menu/items/item-id",
            headers={"Authorization": "Bearer test-token"}
        )
        
        assert response.status_code == 200
        item_data = response.json()
        assert item_data["name"] == "Margherita Pizza"
        assert "category_name" in item_data

    @patch('app.shared.auth.deps.get_current_user')
    @patch('app.shared.auth.deps.require_admin')
    @patch('app.modules.menu.services.item.MenuItemService.update_item')
    def test_update_item_mocked(self, mock_update_item, mock_require_admin, mock_get_user, client: TestClient):
        """Test updating a menu item with mocked service."""
        mock_user = {"id": "admin-id", "role": "admin"}
        mock_updated_item = {
            "id": "item-id",
            "name": "Updated Pizza",
            "description": "Updated description",
            "price": "19.99",
            "is_available": True
        }
        
        mock_get_user.return_value = mock_user
        mock_require_admin.return_value = mock_user
        mock_update_item.return_value = mock_updated_item
        
        response = client.put(
            "/api/v1/menu/items/item-id",
            headers={"Authorization": "Bearer admin-token"},
            json={
                "name": "Updated Pizza",
                "price": 19.99
            }
        )
        
        assert response.status_code == 200
        item_data = response.json()
        assert item_data["name"] == "Updated Pizza"
        assert item_data["price"] == "19.99"

    @patch('app.shared.auth.deps.get_current_user')
    @patch('app.shared.auth.deps.require_admin_or_staff')
    @patch('app.modules.menu.services.item.MenuItemService.toggle_availability')
    def test_toggle_item_availability_mocked(self, mock_toggle, mock_require_auth, mock_get_user, client: TestClient):
        """Test toggling menu item availability with mocked service."""
        mock_user = {"id": "staff-id", "role": "staff"}
        mock_updated_item = {
            "id": "item-id",
            "name": "Pizza",
            "is_available": False  # Toggled to false
        }
        
        mock_get_user.return_value = mock_user
        mock_require_auth.return_value = mock_user
        mock_toggle.return_value = mock_updated_item
        
        response = client.put(
            "/api/v1/menu/items/item-id/availability",
            headers={"Authorization": "Bearer staff-token"}
        )
        
        assert response.status_code == 200
        item_data = response.json()
        assert item_data["is_available"] is False


class TestPublicMenuAPIMocked:
    """Test public menu API endpoints with mocked services."""

    @patch('app.modules.menu.services.item.MenuItemService.get_public_menu')
    def test_get_public_menu_mocked(self, mock_get_public_menu, client: TestClient):
        """Test getting public menu with mocked service."""
        mock_menu_items = [
            {
                "id": "item1-id",
                "name": "Margherita Pizza",
                "description": "Fresh mozzarella and basil",
                "price": "15.99",
                "category_name": "Pizza",
                "image_url": None
            },
            {
                "id": "item2-id",
                "name": "Caesar Salad",
                "description": "Crisp romaine lettuce",
                "price": "12.99",
                "category_name": "Salads",
                "image_url": "/uploads/caesar.jpg"
            }
        ]
        
        mock_get_public_menu.return_value = mock_menu_items
        
        response = client.get("/api/v1/menu/public?restaurant_id=restaurant-id")
        
        assert response.status_code == 200
        items = response.json()
        assert isinstance(items, list)
        assert len(items) == 2
        assert items[0]["name"] == "Margherita Pizza"
        
        # Check that sensitive fields are not exposed
        for item in items:
            assert "organization_id" not in item
            assert "restaurant_id" not in item

    def test_get_public_menu_missing_restaurant_id(self, client: TestClient):
        """Test getting public menu without restaurant_id parameter."""
        response = client.get("/api/v1/menu/public")
        
        assert response.status_code == 422  # Validation error

    @patch('app.modules.menu.services.item.MenuItemService.get_public_menu')
    def test_get_public_menu_empty_result(self, mock_get_public_menu, client: TestClient):
        """Test getting public menu when no items available."""
        mock_get_public_menu.return_value = []
        
        response = client.get("/api/v1/menu/public?restaurant_id=restaurant-id")
        
        assert response.status_code == 200
        items = response.json()
        assert isinstance(items, list)
        assert len(items) == 0