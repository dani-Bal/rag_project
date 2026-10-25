# Architecture

This repository starts with minimal scaffolding for a Retrieval-Augmented Generation system.

- `graph/` will contain LangGraph orchestration, graph construction, state, and nodes.
- `retrieval/` will contain retrieval, vector database access, filtering, and reranking.
- `ingestion/` will contain loading, parsing, chunking, metadata extraction, and indexing.
- `llm/` will contain model initialization, provider integrations, and prompt templates.
- `config.py` contains centralized, typed application settings.

Keep orchestration separate from business logic. Graph nodes should have one responsibility, and
external API calls should be isolated. Retrieval and ingestion should not depend unnecessarily on
LangGraph. Model names, chunk settings, and retrieval parameters should be configurable. Add
dependencies and abstractions only when implementation requires them.
