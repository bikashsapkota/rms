from typing import List
from pydantic import AnyHttpUrl, EmailStr, field_validator, ConfigDict
from pydantic_settings import BaseSettings
from pathlib import Path
import os


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Restaurant Management System"
    PROJECT_VERSION: str = "0.1.0"
    VERSION: str = "0.1.0"  # Alias for PROJECT_VERSION
    DEBUG: bool = False
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://rms_user:rms_pass@localhost:5432/rms_dev"
    TEST_DATABASE_URL: str = "postgresql://rms_user:rms_pass@localhost:5432/rms_test"
    
    # JWT Configuration
    SECRET_KEY: str = "your-super-secret-jwt-key-for-testing-only"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120
    
    # File Upload Configuration
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5_242_880  # 5MB
    MAX_UPLOAD_SIZE: int = 5_242_880  # Alias for tests
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "gif", "webp"]  # For tests
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = True
    REDIS_TTL_DEFAULT: int = 300  # 5 minutes default TTL
    REDIS_TTL_TABLES: int = 600   # 10 minutes for table data
    REDIS_TTL_AVAILABILITY: int = 60  # 1 minute for availability (changes frequently)
    REDIS_TTL_RESERVATIONS: int = 300  # 5 minutes for reservations
    REDIS_TTL_RESTAURANT_INFO: int = 1800  # 30 minutes for restaurant info (rarely changes)
    
    # Frontend URL for QR code generation
    FRONTEND_URL: str = "http://localhost:3000"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",  # Vite default
    ]
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                # Handle JSON list format
                import json
                return json.loads(v)
            else:
                # Handle comma-separated string
                return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(f"Invalid CORS origins format: {v}")
    
    # Phase 1: Default tenant configuration
    DEFAULT_ORGANIZATION_NAME: str = "Default Restaurant Organization"
    DEFAULT_RESTAURANT_NAME: str = "My Restaurant"
    
    # Paths
    @property
    def upload_path(self) -> Path:
        path = Path(self.UPLOAD_DIR)
        path.mkdir(exist_ok=True)
        return path
    
    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",
        frozen=True
    )


# Global settings instance
settings = Settings()