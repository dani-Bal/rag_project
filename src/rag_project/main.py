"""Application entry point for the initial project scaffold."""

import logging

from rag_project.config import get_settings

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the application scaffold."""

    settings = get_settings()
    logger.info("Starting %s (debug=%s)", settings.app_name, settings.debug)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
