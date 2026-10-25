"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings for the application scaffold."""

    app_name: str = "rag-project"
    debug: bool = False

    model_config = SettingsConfigDict(
        env_prefix="RAG_PROJECT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """Return application settings loaded from the current environment."""

    return Settings()
