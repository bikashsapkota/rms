"""
Unit tests for health check endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from app.core.app import app


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_root_endpoint(self):
        """Test root endpoint returns expected data."""
        client = TestClient(app)
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "Restaurant Management System API" in data["message"]

    def test_health_endpoint_success(self):
        """Test health endpoint with healthy database."""
        client = TestClient(app)
        
        with patch('app.modules.setup.routes.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.exec = AsyncMock()
            mock_get_session.return_value = mock_session
            
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert "status" in data
            assert "version" in data
            assert "database" in data

    def test_health_db_endpoint_success(self):
        """Test database health endpoint with successful connection."""
        client = TestClient(app)
        
        with patch('app.modules.setup.routes.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_result = AsyncMock()
            mock_result.first.return_value = 1
            mock_session.exec.return_value = mock_result
            mock_get_session.return_value = mock_session
            
            response = client.get("/health/db")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "healthy"
            assert data["database"] == "connected"
            assert data["connection_test"] == "passed"

    def test_health_db_endpoint_failure(self):
        """Test database health endpoint with connection failure."""
        client = TestClient(app)
        
        with patch('app.modules.setup.routes.get_session') as mock_get_session:
            mock_session = AsyncMock()
            mock_session.exec.side_effect = Exception("Database connection failed")
            mock_get_session.return_value = mock_session
            
            response = client.get("/health/db")
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "unhealthy"
            assert data["database"] == "error"
            assert data["connection_test"] == "failed"
            assert "error" in data