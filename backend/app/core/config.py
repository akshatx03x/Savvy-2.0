import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "LeadSynth AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Allowed CORS origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./lead_gen.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Security
    SECRET_KEY: str = "supersecret_dev_key_change_in_production"

    # AI Config
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    AI_MODEL: str = "gpt-4o-mini"

    # Provider API Credentials
    GOOGLE_MAPS_API_KEY: str = ""
    YELP_API_KEY: str = ""
    B2B_DIRECTORY_API_KEY: str = ""
    OPENSTREETMAP_ENABLED: bool = True

    # Cost Control & Safety Modes
    # Options for LEAD_COST_MODE & AI_COST_MODE: free_only, free_first
    LEAD_COST_MODE: str = "free_only"
    AI_COST_MODE: str = "free_only"

    # Synthetic Data Safety Guard
    # Synthetic generator is strictly for local dev/testing when set to True.
    # Must be False in production! REAL LEADS ONLY.
    ENABLE_SYNTHETIC_DATA: bool = False



    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


settings = Settings()
