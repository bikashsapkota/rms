"""
Unit tests for API endpoints without database dependency.
"""

import pytest
from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient):
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "unhealthy"]  # May be unhealthy without DB
    assert "version" in data
    assert "timestamp" in data
    assert "database" in data
    assert "services" in data


def test_root_endpoint(client: TestClient):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Restaurant Management System" in data["message"]


def test_openapi_spec(client: TestClient):
    """Test OpenAPI specification endpoint."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    
    spec = response.json()
    assert spec["info"]["title"] == "Restaurant Management System"
    assert "paths" in spec
    
    # Check for expected endpoints
    paths = spec["paths"]
    assert "/api/v1/auth/login" in paths
    assert "/api/v1/menu/public" in paths


def test_docs_endpoint(client: TestClient):
    """Test documentation endpoint."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]