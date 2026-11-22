from collections.abc import Iterator
from functools import lru_cache

from openai import OpenAI
from pydantic_ai import Agent
from sqlalchemy import URL, create_engine
from sqlalchemy.orm import Session, sessionmaker

from rag_project.agent.agent import build_agent
from rag_project.agent.tools import retrieve_most_relevant_documents
from rag_project.config import get_settings
from rag_project.database.models import Base


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    settings = get_settings()
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
    return sessionmaker(engine)


def get_session() -> Iterator[Session]:
    factory = get_session_factory()
    with factory() as session:
        yield session


@lru_cache
def get_agent() -> Agent:
    tools = [retrieve_most_relevant_documents]
    return build_agent(tools=tools)


@lru_cache
def get_embedding_client() -> OpenAI:
    settings = get_settings()
    return OpenAI(base_url=settings.llm_provider_url, api_key=settings.llm_api_key)
