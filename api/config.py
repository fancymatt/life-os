"""
API Configuration

Handles environment variables and path configuration for Docker deployment.
Supports volume mounting for presets and output directories.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """API Settings with Docker volume support"""

    # API Configuration
    api_title: str = "AI-Studio API"
    api_version: str = "1.0.0"
    api_description: str = "API for AI-powered image analysis and generation"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    reload: bool = False  # Set to True for development

    # CORS Configuration
    cors_origins: list = []  # Will be populated in __init__
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: list = ["*"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set CORS origins based on environment
        cors_env = os.getenv("CORS_ORIGINS", "")
        if cors_env:
            # Parse from environment (comma-separated or JSON array)
            if cors_env.startswith("["):
                import json
                self.cors_origins = json.loads(cors_env)
            else:
                self.cors_origins = [origin.strip() for origin in cors_env.split(",")]
        else:
            # Default origins based on environment
            if os.getenv("DOCKER_ENV"):
                # Production/Docker: Allow localhost and production domains
                self.cors_origins = [
                    "http://localhost:3000",
                    "http://localhost:8000",
                    "http://127.0.0.1:3000",
                    "http://127.0.0.1:8000",
                    "http://os.fcy.sh",
                    "https://os.fcy.sh",
                ]
            else:
                # Development: Allow localhost on various ports
                self.cors_origins = [
                    "http://localhost:3000",
                    "http://localhost:8000",
                    "http://localhost:5173",  # Vite default
                    "http://127.0.0.1:3000",
                    "http://127.0.0.1:8000",
                    "http://127.0.0.1:5173",
                ]

    # Path Configuration (Docker volume support)
    base_dir: Path = Path("/app" if os.getenv("DOCKER_ENV") else os.getcwd())
    presets_dir: Path = base_dir / "presets"
    output_dir: Path = base_dir / "output"
    cache_dir: Path = base_dir / "cache"
    upload_dir: Path = base_dir / "uploads"
    characters_dir: Path = base_dir / "data" / "characters"

    # API Keys (from environment)
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds

    # File Upload
    max_upload_size: int = 10 * 1024 * 1024  # 10MB
    allowed_extensions: set = {".jpg", ".jpeg", ".png", ".webp"}

    # Job Configuration
    job_retention_hours: int = 24  # Keep job results for 24 hours
    job_storage_backend: str = os.getenv("JOB_STORAGE_BACKEND", "redis")  # "redis" or "memory"
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    # Database Configuration
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://lifeos:lifeos_dev_password@localhost:5432/lifeos"
    )

    # Authentication Configuration
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION_USE_STRONG_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24  # 24 hours
    jwt_refresh_token_expire_days: int = 30  # 30 days
    require_authentication: bool = os.getenv("REQUIRE_AUTH", "true").lower() == "true"

    # Background Jobs (if using Celery)
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

    class Config:
        env_file = ".env"
        case_sensitive = False

    def ensure_directories(self):
        """Ensure all required directories exist"""
        for dir_path in [self.presets_dir, self.output_dir, self.cache_dir, self.upload_dir, self.characters_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def get_preset_categories(self) -> list:
        """Get list of preset categories"""
        return [
            "outfits",
            "visual_styles",
            "art_styles",
            "hair_styles",
            "hair_colors",
            "makeup",
            "expressions",
            "accessories"
        ]


# Global settings instance
settings = Settings()
settings.ensure_directories()
