"""
Unit tests for application configuration.
"""

import pytest
from unittest.mock import patch
from app.core.config import Settings


class TestSettings:
    """Test application settings configuration."""

    def test_default_settings(self):
        """Test default settings values."""
        with patch.dict('os.environ', {'DEBUG': 'false'}, clear=True):
            settings = Settings()
            
            assert settings.PROJECT_NAME == "Restaurant Management System"
            assert settings.VERSION == "0.1.0"
            assert settings.API_V1_STR == "/api/v1"
            assert settings.DEBUG is False
            assert settings.SECRET_KEY is not None
            assert len(settings.SECRET_KEY) > 0

    def test_environment_override(self):
        """Test that environment variables override defaults."""
        env_vars = {
            "PROJECT_NAME": "Custom RMS",
            "DEBUG": "true",
            "SECRET_KEY": "custom-secret-key",
            "DATABASE_URL": "postgresql://custom:pass@localhost/db"
        }
        
        with patch.dict('os.environ', env_vars, clear=True):
            settings = Settings()
            
            assert settings.PROJECT_NAME == "Custom RMS"
            assert settings.DEBUG is True
            assert settings.SECRET_KEY == "custom-secret-key"
            assert "postgresql://custom:pass@localhost/db" in settings.DATABASE_URL

    def test_cors_origins_string(self):
        """Test CORS origins parsing from string."""
        env_vars = {
            "BACKEND_CORS_ORIGINS": "http://localhost:3000,http://localhost:8080",
            "DEBUG": "false"
        }
        
        with patch.dict('os.environ', env_vars, clear=True):
            settings = Settings()
            
            # CORS origins should be parsed as URLs, so we check the string representation
            cors_origins = [str(origin) for origin in settings.BACKEND_CORS_ORIGINS]
            assert "http://localhost:3000/" in cors_origins
            assert "http://localhost:8080/" in cors_origins

    def test_cors_origins_list(self):
        """Test CORS origins as list."""
        settings = Settings()
        settings.BACKEND_CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8080"]
        
        assert len(settings.BACKEND_CORS_ORIGINS) == 2
        assert "http://localhost:3000" in settings.BACKEND_CORS_ORIGINS

    def test_jwt_settings(self):
        """Test JWT-related settings."""
        settings = Settings()
        
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
        assert settings.ALGORITHM == "HS256"

    def test_database_settings(self):
        """Test database-related settings."""
        with patch.dict('os.environ', {'DEBUG': 'false'}, clear=True):
            settings = Settings()
            
            assert "postgresql" in settings.DATABASE_URL
            assert settings.DATABASE_URL.startswith("postgresql")

    def test_upload_settings(self):
        """Test file upload settings."""
        settings = Settings()
        
        assert settings.UPLOAD_DIR == "uploads"
        assert settings.MAX_UPLOAD_SIZE > 0
        assert len(settings.ALLOWED_EXTENSIONS) > 0
        assert "jpg" in settings.ALLOWED_EXTENSIONS
        assert "png" in settings.ALLOWED_EXTENSIONS

    def test_settings_immutability(self):
        """Test that settings are immutable after creation."""
        with patch.dict('os.environ', {'DEBUG': 'false'}, clear=True):
            settings = Settings()
            original_project_name = settings.PROJECT_NAME
            
            # Pydantic v2 settings are frozen by default
            with pytest.raises(Exception):
                settings.PROJECT_NAME = "Modified Name"
            
            # Original value should remain
            assert settings.PROJECT_NAME == original_project_name