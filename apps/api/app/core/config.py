"""
Application configuration using Pydantic Settings.
All settings can be overridden via environment variables.
"""
from functools import lru_cache
from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "cat-now-me API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, validation_alias="DEBUG")
    ENVIRONMENT: str = Field(default="development", validation_alias="ENVIRONMENT")
    
    # API
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        validation_alias="CORS_ORIGINS"
    )
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/cat_now_me",
        validation_alias="DATABASE_URL"
    )
    DATABASE_ECHO: bool = Field(default=False, validation_alias="DATABASE_ECHO")
    
    # Vector Database
    CHROMA_HOST: str = Field(default="localhost", validation_alias="CHROMA_HOST")
    CHROMA_PORT: int = Field(default=8001, validation_alias="CHROMA_PORT")
    CHROMA_COLLECTION: str = Field(default="documents", validation_alias="CHROMA_COLLECTION")
    
    # Ollama
    OLLAMA_BASE_URL: str = Field(default="http://localhost:11434", validation_alias="OLLAMA_BASE_URL")
    OLLAMA_DEFAULT_MODEL: str = Field(default="codellama:13b-instruct", validation_alias="OLLAMA_DEFAULT_MODEL")
    OLLAMA_TIMEOUT: int = Field(default=120, validation_alias="OLLAMA_TIMEOUT")
    
    # Available Models
    OLLAMA_MODELS: List[str] = Field(
        default=["codellama:13b-instruct", "deepseek-coder:6.7b", "llama3.1:8b", "phi3:mini"],
        validation_alias="OLLAMA_MODELS"
    )
    
    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production-min-32-chars",
        validation_alias="SECRET_KEY"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Redis (for caching, rate limiting, Celery)
    REDIS_URL: str = Field(default="redis://localhost:6379/0", validation_alias="REDIS_URL")
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="json", validation_alias="LOG_FORMAT")  # json or console
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = Field(default=100, validation_alias="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=60, validation_alias="RATE_LIMIT_WINDOW")  # seconds
    
    # File Upload
    MAX_FILE_SIZE: int = Field(default=10 * 1024 * 1024, validation_alias="MAX_FILE_SIZE")  # 10MB
    UPLOAD_DIR: str = Field(default="./uploads", validation_alias="UPLOAD_DIR")
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("OLLAMA_MODELS", mode="before")
    @classmethod
    def parse_ollama_models(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [model.strip() for model in v.split(",")]
        return v


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()