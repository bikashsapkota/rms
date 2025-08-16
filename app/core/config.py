from typing import List
from pydantic import AnyHttpUrl, EmailStr, validator
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
    DEBUG: bool = True
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://rms_user:rms_pass@localhost:5432/rms_dev"
    TEST_DATABASE_URL: str = "postgresql://rms_user:rms_pass@localhost:5432/rms_test"
    
    # JWT Configuration
    SECRET_KEY: str = "your-super-secret-jwt-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload Configuration
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5_242_880  # 5MB
    ALLOWED_IMAGE_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",  # Vite default
    ]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Phase 1: Default tenant configuration
    DEFAULT_ORGANIZATION_NAME: str = "Default Restaurant Organization"
    DEFAULT_RESTAURANT_NAME: str = "My Restaurant"
    
    # Paths
    @property
    def upload_path(self) -> Path:
        path = Path(self.UPLOAD_DIR)
        path.mkdir(exist_ok=True)
        return path
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()