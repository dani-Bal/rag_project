import logging
import os
from pathlib import Path

import uvicorn
from sqlalchemy import URL, create_engine

from rag_project.agent.agent import build_agent
from rag_project.agent.tools import retrieve_most_relevant_documents
from rag_project.api.build import build_app
from rag_project.config import get_settings
from rag_project.database.database import bootstrap_database, seed_documents

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logging.basicConfig(level="INFO")
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
    bootstrap_database(engine=engine)
    if src_docs_dir := os.getenv("RAG_PROJECT_SEED_DOCUMENTS_DIR"):
        seed_documents(src_folder=Path(src_docs_dir))
    app = build_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)
