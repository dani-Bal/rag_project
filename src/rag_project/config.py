"""Application configuration loaded from environment variables."""

from pydantic import Field, PositiveInt
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed settings for the application scaffold."""

    vector_length: PositiveInt = Field(description="Number of elements in the vector")
    app_name: str = "rag-project"
    debug: bool = False

    model_config = SettingsConfigDict(
        env_prefix="RAG_PROJECT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    llm_provider_url: str
    llm_model_name: str
    database_url: str = Field(description="The url to connect to the database")
    embedding_model_name: str = Field(description="Name of the model used for embedding.")


def get_settings() -> Settings:
    """Return application settings loaded from the current environment."""
    return Settings()  # pyright: ignore[reportCallIssue]
