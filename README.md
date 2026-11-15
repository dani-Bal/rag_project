# RAG Project

This repository is the starting point for a student-built Retrieval-Augmented Generation (RAG)
system. It currently contains repository infrastructure and a small application scaffold; the RAG
workflow will be added incrementally.

## Project Structure

```
rag_project/
├── compose.yml                 # Main Docker Compose configuration
├── docker/Dockerfile.backend   # Backend (FastAPI) Dockerfile
├── docker/Dockerfile.frontend  # Frontend (Streamlit) Dockerfile
├── README.md                   # This file
├── src/
├──── backend/
│       └── main.py                 # FastAPI application
├──── frontend/
│       └── main.py                 # Streamlit application
├── data/                       # Document storage and test data
└── scripts/                    # Utility scripts
```

## Technology

Python 3.13, `uv`, Ruff, Pyright, Pytest, `pre-commit`, and `pydantic-settings`.

## Setup

Install Python 3.13 and [uv](https://docs.astral.sh/uv/), then run:

```bash
uv sync --group dev
cp .env.example .env
```

Keep real credentials in `.env`; never commit them.

Run the scaffold with `uv run python -m rag_project.main`.

## Docker Compose

The project includes Docker Compose configuration for running the backend and frontend services. To build and start follow these steps:
1. Install Docker and Docker Compose
2. Use terminal commands to build and start the application

### 1 Platform-specific Docker Setup

- **Windows:** [Install Docker Desktop for Windows](https://docs.docker.com/desktop/install/windows-install/)
- **Linux:** [Install Docker Engine for Linux](https://docs.docker.com/engine/install/)
- **macOS:** [Install Docker Desktop for macOS](https://docs.docker.com/desktop/install/mac-install/)

### 2 Terminal Commands
```bash
# Build and start services
docker compose up --build

# Start services (after initial build)
docker compose up

# Start services detached
docker compose up -d

# Stop containers
docker compose stop

# Stop services and delete containers
docker compose down

# View logs
docker compose logs -f
```

Ensure Docker Compose is available (v2+). Verify with `docker compose version`.

## Frontend URL
http://localhost:8501

## Backend URL
http://localhost:8000/doc

## Ollama Webui URL
http://localhost:8080

## Checks

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run pyright
uv run pre-commit install
uv run pre-commit run --all-files
```

Coverage can be generated with:

```bash
uv run pytest tests/unit/ --cov=rag_project --cov-report=term-missing --cov-report=xml
```

## Local CPU-only Ollama

Start the bounded Ollama service with:

```bash
docker compose -f docker-compose.ollama.yml up -d
docker exec rag-project-ollama ollama pull qwen2.5:3b
docker exec rag-project-ollama ollama pull nomic-embed-text
```

The Compose file caps Ollama at 16 GiB RAM and six CPUs. The default assumes an
eight-core host, leaving two cores for the host OS; set `OLLAMA_CPUS` to your
host CPU count minus two when that differs. To use it from either RAG script,
set `OPENAI_BASE_URL=http://localhost:11434/v1`, any non-empty
`OPENAI_API_KEY`, `CHAT_MODEL=openai:qwen2.5:3b`, and
`EMBEDDING_MODEL=nomic-embed-text`.

For CPU-only interactive RAG, `qwen2.5:3b` is the practical starting point:
it leaves headroom for the application and gives much better latency than a
7B/8B model. Use `qwen2.5:7b` only if answer quality matters more than speed;
it will fit under the memory cap in a quantized Ollama build but will be slower.
`nomic-embed-text` is a local embedding model, so the Qdrant collection must
use its vector dimension (768) rather than the 1536 dimensions used by
`text-embedding-3-small`.

## Repository structure

- `src/rag_project/`: installable application package and future RAG modules.
- `tests/`: unit and future integration tests.
- `evaluation/`: future datasets and RAG quality evaluations.
- `docs/`: [development environment](docs/ENTWICKLUNGSUMGEBUNG.md),
  [architecture](docs/ARCHITECTURE.md), [coding guidelines](docs/CODING_GUIDELINES.md), and
  [contributing](docs/CONTRIBUTING.md) documentation.
- `.github/`: CI, Dependabot, and issue/pull-request templates.
