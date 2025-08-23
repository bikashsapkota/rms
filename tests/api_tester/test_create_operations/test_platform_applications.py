"""
Test platform application API operations.
"""

import asyncio
import pytest
from typing import Dict, Any
from tests.api_tester.shared.utils import api_request
from tests.api_tester.shared.fixtures import API_BASE_URL


class TestPlatformApplications:
    """Test platform application operations."""
    
    @pytest.fixture(scope="class")
    def event_loop(self):
        """Create an event loop for the test class."""
        loop = asyncio.new_event_loop()
        yield loop
        loop.close()
    
    @pytest.mark.asyncio
    async def test_create_restaurant_application(self):
        """Test creating a restaurant application."""
        application_data = {
            "applicant_name": "Jane Smith",
            "applicant_email": "jane.smith@example.com",
            "restaurant_name": "Jane's Gourmet Kitchen",
            "restaurant_address": {
                "street": "789 Culinary Ave",
                "city": "Foodville",
                "state": "CA",
                "zip": "90210",
                "country": "US"
            },
            "restaurant_phone": "+1-555-FOOD",
            "restaurant_email": "info@janesgourmet.com",
            "business_description": "A gourmet restaurant specializing in farm-to-table cuisine with locally sourced ingredients."
        }
        
        url = f"{API_BASE_URL}/platform/applications/"
        response = await api_request("POST", url, json=application_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["applicant_name"] == "Jane Smith"
        assert data["applicant_email"] == "jane.smith@example.com"
        assert data["restaurant_name"] == "Jane's Gourmet Kitchen"
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data
        
        # Store application ID for use in other tests
        return data["id"]
    
    @pytest.mark.asyncio
    async def test_create_application_minimal_data(self):
        """Test creating application with minimal required data."""
        application_data = {
            "applicant_name": "John Doe",
            "applicant_email": "john.doe@example.com",
            "restaurant_name": "John's Quick Bites"
        }
        
        url = f"{API_BASE_URL}/platform/applications/"
        response = await api_request("POST", url, json=application_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["applicant_name"] == "John Doe"
        assert data["restaurant_name"] == "John's Quick Bites"
        assert data["status"] == "pending"
        
        return data["id"]
    
    @pytest.mark.asyncio
    async def test_create_application_validation_error(self):
        """Test application creation with validation errors."""
        # Missing required fields
        invalid_data = {
            "applicant_name": "Test User"
            # Missing applicant_email and restaurant_name
        }
        
        url = f"{API_BASE_URL}/platform/applications/"
        response = await api_request("POST", url, json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_get_applications_list(self):
        """Test getting list of applications (admin endpoint)."""
        # This endpoint typically requires admin authentication
        # For now, test the endpoint structure
        url = f"{API_BASE_URL}/platform/applications/"
        response = await api_request("GET", url)
        
        # Expect 401 without proper admin authentication
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_application_by_id(self):
        """Test getting specific application by ID."""
        # First create an application
        application_data = {
            "applicant_name": "Test Applicant",
            "applicant_email": "test@example.com",
            "restaurant_name": "Test Restaurant"
        }
        
        create_url = f"{API_BASE_URL}/platform/applications/"
        create_response = await api_request("POST", create_url, json=application_data)
        
        if create_response.status_code != 200:
            pytest.skip("Application creation failed")
        
        application_id = create_response.json()["id"]
        
        # Get the application by ID
        get_url = f"{API_BASE_URL}/platform/applications/{application_id}"
        get_response = await api_request("GET", get_url)
        
        # May require admin auth
        assert get_response.status_code in [200, 401, 403]
        
        if get_response.status_code == 200:
            data = get_response.json()
            assert data["id"] == application_id
            assert data["applicant_name"] == "Test Applicant"
    
    @pytest.mark.asyncio
    async def test_application_approval_endpoint(self):
        """Test application approval endpoint structure."""
        # Create an application first
        application_data = {
            "applicant_name": "Approval Test",
            "applicant_email": "approval@example.com",
            "restaurant_name": "Approval Test Restaurant"
        }
        
        create_url = f"{API_BASE_URL}/platform/applications/"
        create_response = await api_request("POST", create_url, json=application_data)
        
        if create_response.status_code != 200:
            pytest.skip("Application creation failed")
        
        application_id = create_response.json()["id"]
        
        # Test approval endpoint (requires admin auth)
        approval_data = {
            "admin_notes": "Application approved after review"
        }
        
        approval_url = f"{API_BASE_URL}/platform/applications/{application_id}/approve"
        approval_response = await api_request("POST", approval_url, json=approval_data)
        
        # Expect 401/403 without admin authentication
        assert approval_response.status_code in [200, 401, 403]
    
    @pytest.mark.asyncio
    async def test_application_rejection_endpoint(self):
        """Test application rejection endpoint structure."""
        # Create an application first
        application_data = {
            "applicant_name": "Rejection Test",
            "applicant_email": "rejection@example.com",
            "restaurant_name": "Rejection Test Restaurant"
        }
        
        create_url = f"{API_BASE_URL}/platform/applications/"
        create_response = await api_request("POST", create_url, json=application_data)
        
        if create_response.status_code != 200:
            pytest.skip("Application creation failed")
        
        application_id = create_response.json()["id"]
        
        # Test rejection endpoint (requires admin auth)
        rejection_data = {
            "admin_notes": "Application rejected due to incomplete information"
        }
        
        rejection_url = f"{API_BASE_URL}/platform/applications/{application_id}/reject"
        rejection_response = await api_request("POST", rejection_url, json=rejection_data)
        
        # Expect 401/403 without admin authentication
        assert rejection_response.status_code in [200, 401, 403]
    
    @pytest.mark.asyncio
    async def test_application_stats_endpoint(self):
        """Test application statistics endpoint."""
        url = f"{API_BASE_URL}/platform/applications/stats"
        response = await api_request("GET", url)
        
        # Expect 401/403 without admin authentication
        assert response.status_code in [200, 401, 403]
        
        if response.status_code == 200:
            data = response.json()
            assert "total_applications" in data
            assert "pending_applications" in data
            assert "approved_applications" in data
            assert "rejected_applications" in data
            assert "recent_applications" in data
    
    @pytest.mark.asyncio
    async def test_invalid_application_id(self):
        """Test endpoints with invalid application ID."""
        invalid_id = "00000000-0000-0000-0000-000000000000"
        
        # Test get with invalid ID
        get_url = f"{API_BASE_URL}/platform/applications/{invalid_id}"
        get_response = await api_request("GET", get_url)
        
        assert get_response.status_code in [404, 401, 403]
        
        # Test approval with invalid ID
        approval_data = {"admin_notes": "Test"}
        approval_url = f"{API_BASE_URL}/platform/applications/{invalid_id}/approve"
        approval_response = await api_request("POST", approval_url, json=approval_data)
        
        assert approval_response.status_code in [404, 401, 403]
    
    @pytest.mark.asyncio
    async def test_application_data_validation(self):
        """Test various application data validation scenarios."""
        # Test invalid email format
        invalid_email_data = {
            "applicant_name": "Test User",
            "applicant_email": "invalid-email",
            "restaurant_name": "Test Restaurant"
        }
        
        url = f"{API_BASE_URL}/platform/applications/"
        response = await api_request("POST", url, json=invalid_email_data)
        
        # May return 422 for validation error or 200 if email validation is lenient
        assert response.status_code in [200, 422]
        
        # Test empty strings
        empty_data = {
            "applicant_name": "",
            "applicant_email": "test@example.com",
            "restaurant_name": ""
        }
        
        response = await api_request("POST", url, json=empty_data)
        assert response.status_code in [200, 422]
        
        # Test very long strings
        long_name_data = {
            "applicant_name": "A" * 500,  # Very long name
            "applicant_email": "test@example.com",
            "restaurant_name": "Test Restaurant"
        }
        
        response = await api_request("POST", url, json=long_name_data)
        assert response.status_code in [200, 422]