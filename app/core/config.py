"""Application configuration."""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "Task API"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Storage (future: will be replaced with database)
    STORAGE_TYPE: str = "memory"  # memory, database, etc.
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()