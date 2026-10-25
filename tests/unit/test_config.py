"""Tests for application configuration."""

import logging

import pytest

from rag_project.config import Settings
from rag_project.main import main


def test_settings_defaults() -> None:
    """Settings provide safe defaults for local development."""

    settings = Settings()

    assert settings.app_name == "rag-project"
    assert settings.debug is False


def test_settings_read_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Settings read values from the configured environment prefix."""

    monkeypatch.setenv("RAG_PROJECT_APP_NAME", "test-app")
    monkeypatch.setenv("RAG_PROJECT_DEBUG", "true")

    settings = Settings()

    assert settings.app_name == "test-app"
    assert settings.debug is True


def test_main_logs_startup(caplog: pytest.LogCaptureFixture) -> None:
    """The application entry point logs its startup configuration."""

    caplog.set_level(logging.INFO, logger="rag_project.main")

    main()

    assert "Starting rag-project (debug=False)" in caplog.text
