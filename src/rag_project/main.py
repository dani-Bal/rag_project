"""Application entry point for the initial project scaffold."""

import logging

from fastapi import FastAPI

from rag_project.api.upload import router as upload_router
from rag_project.config import get_settings

logger = logging.getLogger(__name__)
app = FastAPI(title="RAG Project", version="0.1.0")
app.include_router(upload_router)


def main() -> None:
    """Start the application scaffold."""

    settings = get_settings()
    logger.info("Starting %s (debug=%s)", settings.app_name, settings.debug)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
