from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    environment: str = "development"
    database_path: str = "data/health.db"

    telegram_bot_token: str | None = None
    telegram_allowed_chat_id: int | None = None
    telegram_webhook_secret: str | None = None

    openai_api_key: str | None = None
    openai_model: str = "gpt-5.6-luna"

    garmin_client_id: str | None = None
    garmin_client_secret: str | None = None
    garmin_redirect_uri: str = "http://localhost:8000/garmin/callback"


@lru_cache
def get_settings() -> Settings:
    return Settings()

