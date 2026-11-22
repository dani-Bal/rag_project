"""Application configuration loaded from environment variables."""

from pathlib import Path

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings for the application scaffold."""

    vector_length: PositiveInt = Field(description="Number of elements in the vector")
    app_name: str = "rag-project"
    debug: bool = False

    db_host: str = Field("localhost", validation_alias="DB_HOST")
    db_port: int = Field(5432, validation_alias="DB_PORT")
    db_name: str = Field(validation_alias="DB_NAME")
    db_user: str = Field(validation_alias="DB_USER")
    db_password: str = Field(validation_alias="DB_PASSWORD")

    embedding_model: str = Field(
        default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        validation_alias="EMBEDDING_MODEL",
    )
    upload_dir: Path = Path("data/local/uploads")
    max_file_size: int = 20 * 1024 * 1024  # 20 MB

    model_config = SettingsConfigDict(
        env_prefix="RAG_PROJECT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    llm_provider_url: str = Field(
        default="https://chat-ai.academiccloud.de/v1/",
        validation_alias="LLM_PROVIDER_URL",
    )

    llm_api_key: str = Field(
        default="",
    )

    llm_model_name: str = Field(
        default="gpt-3.5-turbo",
    )


def get_settings() -> Settings:
    """Return application settings loaded from the current environment."""
    return Settings()  # pyright: ignore[reportCallIssue]
