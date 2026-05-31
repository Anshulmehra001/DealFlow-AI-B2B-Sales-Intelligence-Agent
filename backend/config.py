"""
Configuration management for DealFlow AI
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings - all optional with safe defaults so app starts without full .env"""

    # Application
    APP_NAME: str = "DealFlow AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Server
    BACKEND_PORT: int = 8000
    FRONTEND_PORT: int = 5173

    # MongoDB - only truly required field
    MONGODB_URI: str = "mongodb://localhost:27017/dealflow_db"
    MONGODB_DATABASE: str = "dealflow_db"
    MONGODB_MAX_POOL_SIZE: int = 10
    MONGODB_MIN_POOL_SIZE: int = 1

    # Google / Gemini - optional, system works without it
    GOOGLE_CLOUD_PROJECT: str = ""
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # Email (Gmail SMTP) - optional, disable if not set
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = ""
    SMTP_FROM_NAME: str = "DealFlow AI"
    EMAIL_DAILY_LIMIT: int = 500

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "http://localhost:8000"]

    # Agent Configuration
    MAX_CONCURRENT_AGENTS: int = 3
    AGENT_TIMEOUT_SECONDS: int = 300
    LEAD_SCORE_THRESHOLD: int = 60

    # Rate Limiting
    API_RATE_LIMIT: int = 100

    # Feature Flags - auto-disable if credentials missing
    ENABLE_EMAIL_SENDING: bool = True
    ENABLE_WEB_SCRAPING: bool = True
    ENABLE_VECTOR_SEARCH: bool = False  # Requires Atlas paid tier

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    @property
    def email_enabled(self) -> bool:
        """Email is only enabled if credentials are configured"""
        return self.ENABLE_EMAIL_SENDING and bool(self.SMTP_USERNAME) and bool(self.SMTP_PASSWORD)

    @property
    def gemini_enabled(self) -> bool:
        """Gemini is only enabled if API key is configured"""
        return bool(self.GEMINI_API_KEY)


# Global settings instance
settings = Settings()


# MongoDB Collections
class Collections:
    LEADS = "leads"
    DEALS = "deals"
    AGENT_ACTIONS = "agent_actions"
    EMAIL_TEMPLATES = "email_templates"
    ANALYTICS = "analytics"


# Deal Stages
class DealStages:
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"

    @classmethod
    def all_stages(cls):
        return [cls.NEW, cls.CONTACTED, cls.QUALIFIED, cls.PROPOSAL,
                cls.NEGOTIATION, cls.CLOSED_WON, cls.CLOSED_LOST]
