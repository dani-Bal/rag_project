"""Tests for application configuration."""

import logging
from unittest.mock import MagicMock, patch

import pytest
from pydantic_ai import Agent
from sqlalchemy import create_engine

from rag_project.config import Settings


@pytest.fixture(autouse=True)
def mock_database_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mock the database related environment variables.

    Args:
        monkeypatch (pytest.MonkeyPatch): The monkeypatch helper for manipulating the current env.
    """
    monkeypatch.setenv("DB_NAME", "test_database")
    monkeypatch.setenv("DB_USER", "test_user")
    monkeypatch.setenv("DB_PASSWORD", "test_password")


def test_settings_defaults() -> None:
    """Settings provide safe defaults for local development."""
    settings = Settings()  # pyright: ignore[reportCallIssue]

    assert settings.app_name == "rag-project"
    assert settings.debug is False


def test_settings_read_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings read values from the configured environment prefix."""
    monkeypatch.setenv("RAG_PROJECT_APP_NAME", "test-app")
    monkeypatch.setenv("RAG_PROJECT_DEBUG", "true")

    settings = Settings()  # pyright: ignore[reportCallIssue]

    assert settings.app_name == "test-app"
    assert settings.debug is True


@patch("rag_project.main.create_engine")
@patch("rag_project.main.build_agent")
def test_main_logs_startup(
    mocked_agent_factory: MagicMock,
    mocked_db_engine_factory: MagicMock,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The application entry point logs its startup configuration."""
    caplog.set_level(logging.INFO, logger="rag_project.main")
    from rag_project.main import main

    mocked_db_engine_factory.return_value = create_engine("sqlite:///:memory:")
    mocked_agent = MagicMock(spec=Agent)
    mocked_agent_factory.return_value = mocked_agent
    mocked_agent.run_sync.return_value = "Mocked answer by mocked agent"

    with patch("builtins.input") as mocked_input:
        mocked_input.side_effect = KeyboardInterrupt
        with pytest.raises(KeyboardInterrupt):
            main()

    assert "Starting rag-project (debug=False)" in caplog.text
