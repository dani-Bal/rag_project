"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings for the application scaffold."""

    app_name: str = "rag-project"
    debug: bool = False

    upload_dir: Path = Path("data/local/uploads")
    max_file_size: int = 20 * 1024 * 1024  # 20 MB

    model_config = SettingsConfigDict(
        env_prefix="RAG_PROJECT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """Return application settings loaded from the current environment."""

    return Settings()
