"""Application entry point for the initial project scaffold."""

import logging

from fastapi import FastAPI
from openai import OpenAI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from rag_project.agent.agent import build_agent
from rag_project.agent.models import AgentContext
from rag_project.agent.tools import retrieve_most_relevant_documents
from rag_project.api.questions import router as questions_router
from rag_project.api.upload import router as upload_router
from rag_project.config import get_settings
from rag_project.database.models import Base

logger = logging.getLogger(__name__)
app = FastAPI(title="RAG Project", version="0.1.0")
app.include_router(upload_router)
app.include_router(questions_router)


def main() -> None:
    """Start the application scaffold."""
    settings = get_settings()
    tools = [retrieve_most_relevant_documents]
    agent = build_agent(tools=tools)
    logger.info("Starting %s (debug=%s)", settings.app_name, settings.debug)

    engine = create_engine(settings.database_url)
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
                            base_url=settings.llm_provider_url,
                            api_key="ollama",
                        ),
                        embedding_model_name=settings.embedding_model_name,
                    ),
                )
                print("Answer:", result)
            except Exception:
                logger.exception("exception happened!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
