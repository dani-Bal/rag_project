"""Create the local database schema and ingest one PDF into the chunks table."""

# KI generiertes File
import argparse
from pathlib import Path

import psycopg
from openai import OpenAI
from psycopg import sql
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from rag_project.config import get_settings
from rag_project.database.database import ChunkingStrategy, chunk_text
from rag_project.database.models import Base, DocumentChunk
from rag_project.database.process_pdf import process_pdf


def ensure_database(database_url: str) -> None:
    """Create the configured database if it does not already exist."""
    target = make_url(database_url)
    database_name = target.database
    if not database_name:
        raise ValueError("DATABASE_URL must include a database name")

    maintenance_url = target.set(database="postgres").render_as_string(hide_password=False)
    with psycopg.connect(maintenance_url, autocommit=True) as connection:
        exists = connection.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (database_name,)
        ).fetchone()
        if exists is None:
            connection.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))


def seed_documents(pdf_path: Path) -> int:
    """Bootstrap the schema and insert embedded chunks from a PDF.

    Returns:
        Number of inserted chunks.
    """
    settings = get_settings()
    ensure_database(settings.database_url)
    engine = create_engine(settings.database_url)

    # The extension must exist before SQLAlchemy creates the VECTOR column.
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)

    document = process_pdf(pdf_path.read_bytes())
    chunks = chunk_text(document.content, ChunkingStrategy.FIXED_SIZE)
    if not chunks:
        return 0

    embedding_client = OpenAI(base_url=settings.llm_provider_url, api_key="ollama")
    embedding_response = embedding_client.embeddings.create(
        model=settings.embedding_model_name,
        input=[chunk.text for chunk in chunks],
    )
    embeddings = {item.index: item.embedding for item in embedding_response.data}
    if any(len(embedding) != settings.vector_length for embedding in embeddings.values()):
        raise ValueError(
            f"Embedding size does not match configured vector length ({settings.vector_length})"
        )

    with Session(engine) as session:
        session.add_all(
            [
                DocumentChunk(
                    content=chunk.text,
                    embedding=embeddings[index],
                    run_id=1,
                    chunk_index=index,
                    token_count=chunk.token_count,
                )
                for index, chunk in enumerate(chunks)
            ]
        )
        session.commit()

        sample = session.scalar(select(DocumentChunk).order_by(DocumentChunk.id.desc()).limit(1))
        if sample is None or not sample.content or not sample.embedding:
            raise RuntimeError("Could not read back an embedded DocumentChunk")

    return len(chunks)


def main() -> None:
    """Run the PDF bootstrap command."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf_path", type=Path, help="Path to the PDF file to ingest")
    args = parser.parse_args()

    inserted = seed_documents(args.pdf_path)
    print(f"Inserted {inserted} chunks from {args.pdf_path}")


if __name__ == "__main__":
    main()
