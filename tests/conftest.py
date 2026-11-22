"""Shared pytest configuration."""

import os

os.environ.setdefault("RAG_PROJECT_VECTOR_LENGTH", "384")
os.environ.setdefault("RAG_PROJECT_LLM_PROVIDER_URL", "http://localhost:11434")
os.environ.setdefault("RAG_PROJECT_EMBEDDING_MODEL_NAME", "test")
os.environ.setdefault("RAG_PROJECT_LLM_MODEL_NAME", "ollama")
os.environ.setdefault("RAG_PROJECT_DATABASE_URL", "postgresql://test:test@localhost:5432/test")
os.environ.setdefault("DB_NAME", "test")
os.environ.setdefault("DB_USER", "test")
os.environ.setdefault("DB_PASSWORD", "test")
# TODO Alle Variablen sind komplette Platzhalter und sollten später ausgetauscht werden
