"""
Integration tests for setup API endpoints.
"""

import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient


class TestSetupAPI:
    """Test setup API endpoints."""

    def test_health_check_endpoint(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "version" in data
        assert "timestamp" in data
        assert "database" in data
        assert "services" in data
        
        # Check services
        services = data["services"]
        assert "authentication" in services
        assert "menu_management" in services
        assert "user_management" in services
        assert "file_upload" in services

    def test_root_endpoint_updated(self, client: TestClient):
        """Test that root endpoint shows Phase 1 information."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert "phase" in data
        assert "Phase 1" in data["phase"]

    @patch('app.core.setup.RestaurantSetupService.create_restaurant_setup')
    def test_restaurant_setup_success(self, mock_setup, client: TestClient):
        """Test successful restaurant setup."""
        # Mock setup service response
        mock_setup.return_value = {
            "organization": {
                "id": "org-123",
                "name": "Test Restaurant Organization",
                "type": "independent"
            },
            "restaurant": {
                "id": "rest-123",
                "name": "Test Restaurant",
                "organization_id": "org-123"
            },
            "admin_user": {
                "id": "user-123",
                "email": "admin@test.com",
                "full_name": "Test Admin",
                "role": "admin"
            }
        }
        
        # Test data
        setup_data = {
            "restaurant_name": "Test Restaurant",
            "address": {
                "street": "123 Main St",
                "city": "Test City",
                "state": "TS",
                "zip": "12345"
            },
            "phone": "+1-555-0123",
            "email": "info@test.com",
            "settings": {"timezone": "America/New_York"},
            "admin_user": {
                "email": "admin@test.com",
                "full_name": "Test Admin",
                "password": "securepassword123"
            }
        }
        
        response = client.post("/setup", json=setup_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data
        assert "organization" in data
        assert "restaurant" in data
        assert "admin_user" in data
        assert "next_steps" in data
        
        # Verify organization data
        org = data["organization"]
        assert org["name"] == "Test Restaurant Organization"
        assert org["type"] == "independent"
        
        # Verify restaurant data
        restaurant = data["restaurant"]
        assert restaurant["name"] == "Test Restaurant"
        assert restaurant["organization_id"] == "org-123"
        
        # Verify admin user data
        admin = data["admin_user"]
        assert admin["email"] == "admin@test.com"
        assert admin["role"] == "admin"
        
        # Verify next steps provided
        assert len(data["next_steps"]) > 0
        assert any("menu" in step.lower() for step in data["next_steps"])

    def test_restaurant_setup_invalid_data(self, client: TestClient):
        """Test restaurant setup with invalid data."""
        # Missing required fields
        setup_data = {
            "restaurant_name": "",  # Empty name
            "admin_user": {
                "email": "invalid-email",  # Invalid email
                "full_name": "Test Admin",
                "password": "short"  # Too short password
            }
        }
        
        response = client.post("/setup", json=setup_data)
        assert response.status_code == 422  # Validation error

    def test_restaurant_setup_missing_admin(self, client: TestClient):
        """Test restaurant setup without admin user."""
        setup_data = {
            "restaurant_name": "Test Restaurant"
            # Missing admin_user
        }
        
        response = client.post("/setup", json=setup_data)
        assert response.status_code == 422  # Validation error

    @patch('app.core.setup.RestaurantSetupService.create_restaurant_setup')
    def test_restaurant_setup_service_error(self, mock_setup, client: TestClient):
        """Test restaurant setup when service throws error."""
        # Mock service to raise exception
        mock_setup.side_effect = Exception("Database connection failed")
        
        setup_data = {
            "restaurant_name": "Test Restaurant",
            "admin_user": {
                "email": "admin@test.com",
                "full_name": "Test Admin",
                "password": "securepassword123"
            }
        }
        
        response = client.post("/setup", json=setup_data)
        
        assert response.status_code == 500
        assert "setup failed" in response.json()["detail"].lower()

    def test_restaurant_setup_minimal_data(self, client: TestClient):
        """Test restaurant setup with minimal required data."""
        with patch('app.core.setup.RestaurantSetupService.create_restaurant_setup') as mock_setup:
            mock_setup.return_value = {
                "organization": {
                    "id": "org-123",
                    "name": "Minimal Restaurant Organization",
                    "type": "independent"
                },
                "restaurant": {
                    "id": "rest-123",
                    "name": "Minimal Restaurant",
                    "organization_id": "org-123"
                },
                "admin_user": {
                    "id": "user-123",
                    "email": "admin@minimal.com",
                    "full_name": "Minimal Admin",
                    "role": "admin"
                }
            }
            
            setup_data = {
                "restaurant_name": "Minimal Restaurant",
                "admin_user": {
                    "email": "admin@minimal.com",
                    "full_name": "Minimal Admin",
                    "password": "password123"
                }
            }
            
            response = client.post("/setup", json=setup_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["restaurant"]["name"] == "Minimal Restaurant"


class TestPhase1Endpoints:
    """Test that all Phase 1 required endpoints are available."""

    def test_all_required_auth_endpoints(self, client: TestClient):
        """Test that all Phase 1 auth endpoints exist."""
        auth_endpoints = [
            ("POST", "/api/v1/auth/login"),
            ("POST", "/api/v1/auth/logout"),
            ("POST", "/api/v1/auth/refresh"),
            ("GET", "/api/v1/auth/me"),
            ("GET", "/api/v1/users/"),
            ("POST", "/api/v1/users/"),
            ("PUT", "/api/v1/users/test-id"),
        ]
        
        for method, endpoint in auth_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "PUT":
                response = client.put(endpoint, json={})
            
            # We expect 401/422 errors (unauthorized/validation) but not 404 (not found)
            assert response.status_code != 404, f"{method} {endpoint} should exist"

    def test_all_required_menu_endpoints(self, client: TestClient):
        """Test that all Phase 1 menu endpoints exist."""
        menu_endpoints = [
            ("GET", "/api/v1/menu/categories/"),
            ("POST", "/api/v1/menu/categories/"),
            ("GET", "/api/v1/menu/categories/test-id"),
            ("PUT", "/api/v1/menu/categories/test-id"),
            ("DELETE", "/api/v1/menu/categories/test-id"),
            ("GET", "/api/v1/menu/items/"),
            ("POST", "/api/v1/menu/items/"),
            ("GET", "/api/v1/menu/items/test-id"),
            ("PUT", "/api/v1/menu/items/test-id"),
            ("DELETE", "/api/v1/menu/items/test-id"),
            ("PUT", "/api/v1/menu/items/test-id/availability"),
            ("POST", "/api/v1/menu/items/test-id/image"),
            ("GET", "/api/v1/menu/public"),
        ]
        
        for method, endpoint in menu_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            elif method == "PUT":
                response = client.put(endpoint, json={})
            elif method == "DELETE":
                response = client.delete(endpoint)
            
            # We expect 401/422 errors but not 404 (not found)
            assert response.status_code != 404, f"{method} {endpoint} should exist"

    def test_phase1_endpoint_count(self, client: TestClient):
        """Test that we have at least the required 20 Phase 1 endpoints."""
        response = client.get("/api/v1/openapi.json")
        assert response.status_code == 200
        
        openapi_spec = response.json()
        paths = openapi_spec.get("paths", {})
        
        # Count actual API endpoints (excluding health/root)
        api_endpoints = [path for path in paths.keys() if path.startswith("/api/v1/")]
        
        # Phase 1 requires 20 API endpoints minimum
        assert len(api_endpoints) >= 20, f"Expected at least 20 API endpoints, got {len(api_endpoints)}"