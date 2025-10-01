import os
from functools import lru_cache
from typing import Optional

from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env (if present)
load_dotenv()


class Settings(BaseModel):
    """Application settings loaded from environment variables."""
    app_name: str = "QnA Backend API"
    api_version: str = "1.0.0"
    environment: str = os.getenv("ENVIRONMENT", "development")

    # Security
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "change-this-in-env")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expire_minutes: int = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))

    # Database (SQLite by default)
    sqlalchemy_database_url: str = os.getenv("DATABASE_URL", "sqlite+sqlite:///./qna.db")
    # Note: using sqlite+sqlite for SQLAlchemy 2.0 style URL with sqlite backend in a file relative to working dir.

    # OpenAI
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")

    # CORS
    cors_allow_origins: str = os.getenv("CORS_ALLOW_ORIGINS", "*")  # comma-separated


# PUBLIC_INTERFACE
@lru_cache()
def get_settings() -> Settings:
    """Return cached Settings instance for dependency injection."""
    return Settings()
