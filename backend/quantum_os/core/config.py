from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn, Field
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "QuantumOS"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    
    # API
    API_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: List[str] = ["*"]
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Database
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://quantumos:quantumos123@localhost:5432/quantumos"
    )
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 40
    
    # Redis
    REDIS_URL: RedisDsn = Field(default="redis://localhost:6379")
    REDIS_MAX_CONNECTIONS: int = 50
    
    # Security
    # SECRET_KEY is required for production/staging, but we allow a fallback for local development.
    SECRET_KEY: Optional[str] = Field(None, min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    def model_post_init(self, __context: object) -> None:
        # Pydantic v2 hook; validate after env loading.
        if self.ENVIRONMENT in (Environment.PRODUCTION, Environment.STAGING):
            if not self.SECRET_KEY:
                raise ValueError("SECRET_KEY is required in production/staging")
        else:
            # Dev/testing fallback (never use in production)
            self.SECRET_KEY = self.SECRET_KEY or "dev-only-insecure-secret-key-change-me"

    
    # Logging
    LOG_FILE: str = "logs/quantumos.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create settings instance
settings = Settings()