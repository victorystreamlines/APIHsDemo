"""Application configuration."""

from __future__ import annotations

import secrets
from pathlib import Path
from typing import Any, Literal

from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings."""

    # Application
    app_name: str = "User Management System"
    debug: bool = False
    version: str = "1.0.0"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: str = secrets.token_urlsafe(32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = "sqlite:///./users.db"
    database_echo: bool = False
    
    # CORS
    backend_cors_origins: list[str] = ["*"]
    
    # API
    api_v1_prefix: str = "/api/v1"
    
    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    
    @validator("backend_cors_origins", pre=True)
    def assemble_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Assemble CORS origins from string or list."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        """Pydantic config."""
        
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent