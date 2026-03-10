from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to this file (ai-tutor-backend/app/config.py → ai-tutor-backend/.env)
# This works regardless of the working directory the server is launched from.
_ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        env_ignore_empty=True,   # treat empty env vars as unset → fall back to .env file values
    )

    # Application
    app_env: str = "development"
    app_port: int = 8000
    app_secret_key: str = "change-me-in-production"
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:5173"

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "ai_tutor"

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Anthropic
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"
    anthropic_max_tokens: int = 800

    # Piston (code execution)
    piston_url: str = "http://localhost:2000"
    piston_run_timeout: int = 3000      # ms — Piston's default server max is 3000
    piston_compile_timeout: int = 10000 # ms — compile step limit (Java etc.)

    # JWT
    jwt_secret_key: str = "change-me"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # OAuth (Phase 2)
    google_client_id: str = ""
    google_client_secret: str = ""
    github_client_id: str = ""
    github_client_secret: str = ""

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


settings = Settings()
