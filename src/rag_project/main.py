"""Application entry point for the initial project scaffold."""

import logging

from openai import OpenAI
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker

from rag_project.agent.agent import build_agent
from rag_project.agent.models import AgentContext
from rag_project.agent.tools import retrieve_most_relevant_documents
from rag_project.config import get_settings
from rag_project.database.models import Base

logger = logging.getLogger(__name__)


def main() -> None:
    """Start the application scaffold."""
    settings = get_settings()
    tools = [retrieve_most_relevant_documents]
    agent = build_agent(tools=tools)
    logger.info("Starting %s (debug=%s)", settings.app_name, settings.debug)
    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)

    Session = sessionmaker(engine)
    with Session() as session:
        while True:
            try:
                user_input = input("Enter your question:").strip()
                result = agent.run_sync(
                    user_input,
                    deps=AgentContext(
                        session=session,
                        embedding_client=OpenAI(
                            base_url=settings.llm_provider_url, api_key=settings.llm_api_key
                        ),
                        embedding_model_name=settings.embedding_model,
                    ),
                )
                print("Answer:", result)
            except Exception:
                logger.exception("exception happened!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
