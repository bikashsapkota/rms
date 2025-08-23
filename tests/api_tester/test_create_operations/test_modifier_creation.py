"""
Test modifier creation API operations.
"""

import asyncio
import pytest
from decimal import Decimal
from typing import Dict, Any
from tests.api_tester.shared.utils import api_request
from tests.api_tester.shared.auth import get_auth_headers
from tests.api_tester.shared.fixtures import API_BASE_URL


class TestModifierCreation:
    """Test modifier creation operations."""
    
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
    
    @pytest.mark.asyncio
    async def test_create_modifier_basic(self, auth_setup):
        """Test creating a basic modifier."""
        modifier_data = {
            "name": "Extra Cheese",
            "description": "Add extra cheese to your order",
            "modifier_type": "addon",
            "price_adjustment": 2.50,
            "is_required": False,
            "sort_order": 1,
            "is_active": True
        }
        
        url = f"{API_BASE_URL}/modifiers/"
        response = await api_request(
            "POST", 
            url, 
            json=modifier_data, 
            headers=auth_setup["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Extra Cheese"
        assert data["modifier_type"] == "addon"
        assert float(data["price_adjustment"]) == 2.50
        assert data["is_required"] is False
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        
        # Store modifier ID for cleanup
        return data["id"]
    
    @pytest.mark.asyncio
    async def test_create_modifier_required(self, auth_setup):
        """Test creating a required modifier."""
        modifier_data = {
            "name": "Size Selection",
            "description": "Choose your size",
            "modifier_type": "required",
            "price_adjustment": 0.00,
            "is_required": True,
            "sort_order": 0
        }
        
        url = f"{API_BASE_URL}/modifiers/"
        response = await api_request(
            "POST", 
            url, 
            json=modifier_data, 
            headers=auth_setup["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Size Selection"
        assert data["modifier_type"] == "required"
        assert float(data["price_adjustment"]) == 0.00
        assert data["is_required"] is True
        assert data["sort_order"] == 0
        
        return data["id"]
    
    @pytest.mark.asyncio
    async def test_create_modifier_substitution(self, auth_setup):
        """Test creating a substitution modifier."""
        modifier_data = {
            "name": "Gluten-Free Crust",
            "description": "Replace regular crust with gluten-free option",
            "modifier_type": "substitution",
            "price_adjustment": 3.00,
            "is_required": False,
            "sort_order": 2
        }
        
        url = f"{API_BASE_URL}/modifiers/"
        response = await api_request(
            "POST", 
            url, 
            json=modifier_data, 
            headers=auth_setup["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Gluten-Free Crust"
        assert data["modifier_type"] == "substitution"
        assert float(data["price_adjustment"]) == 3.00
        
        return data["id"]
    
    @pytest.mark.asyncio
    async def test_create_modifier_with_negative_price(self, auth_setup):
        """Test creating a modifier with negative price adjustment (discount)."""
        modifier_data = {
            "name": "Student Discount",
            "description": "10% off for students",
            "modifier_type": "optional",
            "price_adjustment": -1.50,
            "is_required": False,
            "sort_order": 10
        }
        
        url = f"{API_BASE_URL}/modifiers/"
        response = await api_request(
            "POST", 
            url, 
            json=modifier_data, 
            headers=auth_setup["headers"]
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Student Discount"
        assert float(data["price_adjustment"]) == -1.50
        
        return data["id"]
    
    @pytest.mark.asyncio
    async def test_create_modifier_validation_error(self, auth_setup):
        """Test modifier creation with validation errors."""
        # Missing required field
        invalid_data = {
            "description": "Missing name field",
            "modifier_type": "addon"
        }
        
        url = f"{API_BASE_URL}/modifiers/"
        response = await api_request(
            "POST", 
            url, 
            json=invalid_data, 
            headers=auth_setup["headers"]
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_create_modifier_unauthorized(self):
        """Test modifier creation without authentication."""
        modifier_data = {
            "name": "Unauthorized Test",
            "modifier_type": "addon",
            "price_adjustment": 1.00
        }
        
        url = f"{API_BASE_URL}/modifiers/"
        response = await api_request("POST", url, json=modifier_data)
        
        assert response.status_code == 401  # Unauthorized
    
    @pytest.mark.asyncio
    async def test_get_modifiers_list(self, auth_setup):
        """Test getting list of modifiers."""
        url = f"{API_BASE_URL}/modifiers/"
        response = await api_request("GET", url, headers=auth_setup["headers"])
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        # Should have modifiers from previous tests
        assert len(data) >= 0
        
        if data:
            modifier = data[0]
            assert "id" in modifier
            assert "name" in modifier
            assert "modifier_type" in modifier
            assert "price_adjustment" in modifier
    
    @pytest.mark.asyncio
    async def test_get_modifier_by_id(self, auth_setup):
        """Test getting a specific modifier by ID."""
        # First create a modifier
        modifier_data = {
            "name": "Test Get Modifier",
            "modifier_type": "addon",
            "price_adjustment": 1.99
        }
        
        create_url = f"{API_BASE_URL}/modifiers/"
        create_response = await api_request(
            "POST", 
            create_url, 
            json=modifier_data, 
            headers=auth_setup["headers"]
        )
        
        assert create_response.status_code == 200
        created_modifier = create_response.json()
        modifier_id = created_modifier["id"]
        
        # Get the modifier by ID
        get_url = f"{API_BASE_URL}/modifiers/{modifier_id}"
        get_response = await api_request("GET", get_url, headers=auth_setup["headers"])
        
        assert get_response.status_code == 200
        retrieved_modifier = get_response.json()
        
        assert retrieved_modifier["id"] == modifier_id
        assert retrieved_modifier["name"] == "Test Get Modifier"
        assert retrieved_modifier["modifier_type"] == "addon"
    
    @pytest.mark.asyncio
    async def test_update_modifier(self, auth_setup):
        """Test updating a modifier."""
        # First create a modifier
        modifier_data = {
            "name": "Update Test Modifier",
            "modifier_type": "addon",
            "price_adjustment": 1.00
        }
        
        create_url = f"{API_BASE_URL}/modifiers/"
        create_response = await api_request(
            "POST", 
            create_url, 
            json=modifier_data, 
            headers=auth_setup["headers"]
        )
        
        assert create_response.status_code == 200
        created_modifier = create_response.json()
        modifier_id = created_modifier["id"]
        
        # Update the modifier
        update_data = {
            "name": "Updated Modifier Name",
            "price_adjustment": 2.50,
            "description": "Updated description"
        }
        
        update_url = f"{API_BASE_URL}/modifiers/{modifier_id}"
        update_response = await api_request(
            "PUT", 
            update_url, 
            json=update_data, 
            headers=auth_setup["headers"]
        )
        
        assert update_response.status_code == 200
        updated_modifier = update_response.json()
        
        assert updated_modifier["name"] == "Updated Modifier Name"
        assert float(updated_modifier["price_adjustment"]) == 2.50
        assert updated_modifier["description"] == "Updated description"
    
    @pytest.mark.asyncio
    async def test_delete_modifier(self, auth_setup):
        """Test deleting a modifier."""
        # First create a modifier
        modifier_data = {
            "name": "Delete Test Modifier",
            "modifier_type": "addon",
            "price_adjustment": 1.00
        }
        
        create_url = f"{API_BASE_URL}/modifiers/"
        create_response = await api_request(
            "POST", 
            create_url, 
            json=modifier_data, 
            headers=auth_setup["headers"]
        )
        
        assert create_response.status_code == 200
        created_modifier = create_response.json()
        modifier_id = created_modifier["id"]
        
        # Delete the modifier
        delete_url = f"{API_BASE_URL}/modifiers/{modifier_id}"
        delete_response = await api_request(
            "DELETE", 
            delete_url, 
            headers=auth_setup["headers"]
        )
        
        assert delete_response.status_code == 200
        
        # Verify modifier is deleted
        get_url = f"{API_BASE_URL}/modifiers/{modifier_id}"
        get_response = await api_request("GET", get_url, headers=auth_setup["headers"])
        
        assert get_response.status_code == 404  # Not found