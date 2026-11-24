# Autor: Carsten Ostlender & Daniel Balbach, 2026
# TODO: Unit Tests
# Chunking in eigene Datei auslagern, um die Logik zu trennen und die Lesbarkeit zu verbessern.
# DB und Chunking trennen
import logging
import sys
from enum import StrEnum
from pathlib import Path

import psycopg
from chonkie import (
    Chunk,
    LateChunker,
    RecursiveChunker,
    SemanticChunker,
    SentenceChunker,
    TokenChunker,
)
from psycopg import sql
from sentence_transformers import SentenceTransformer
from sqlalchemy import Engine, create_engine, text
from sqlalchemy import text as sql_text
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from rag_project.config import get_settings
from rag_project.database.document import ProcessedDocument
from rag_project.database.metadata import Metadata
from rag_project.database.models import (
    Base,
    ChunkingRun,
    Document,
    MetaData,
)
from rag_project.database.models import (
    Chunk as ChunkModel,
)
from rag_project.database.process_pdf import process_pdf

logger = logging.getLogger(__name__)
# In Connect Funktion?
settings = get_settings()

# TODO remove
url = URL.create(
    "postgresql+psycopg",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=int(settings.db_port),
    database=settings.db_name,
)

engine = create_engine(url, pool_pre_ping=True)


class ChunkingStrategy(StrEnum):
    FIXED_SIZE = "fixed_size"
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"
    LATE = "late"
    SENTENCE = "sentence"


token_count = 35
threshold_length = 0.65


def get_database_url_from_config() -> URL:
    return URL.create(
        "postgresql+psycopg",
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=int(settings.db_port),
        database=settings.db_name,
    )


def insert_document_into_database(
    session: Session,
    document_name: str,
    document: ProcessedDocument,
    strategy: ChunkingStrategy,
    chunks: list[Chunk],
) -> None:
    # Check nonsensical and empty inputs
    if not document_name.strip():
        raise ValueError("Dokumentname darf nicht leer sein.")

    if document is None:
        raise ValueError("Dokument muss verhanden sein.")

    if document.content is None or document.metadata is None:
        raise ValueError("Kein Dokumentinhalt oder Metadaten vorhanden.")

    if not isinstance(strategy, ChunkingStrategy):
        raise ValueError("Strategie muss vorhanden  sein.")

    # Save Document
    db_document = Document(
        filename=document_name,
        content=document.content,
        original_file=document.original_file,
        metadata_record=MetaData(
            title=document.metadata.title,
            author=document.metadata.author,
            subject=document.metadata.subject,
            keywords=document.metadata.keywords,
            pdf_created_at=document.metadata.pdf_created_at,
            page_count=document.metadata.page_count,
            file_size_bytes=document.metadata.file_size_bytes,
        ),
    )
    session.add(db_document)
    session.flush()

    # Save ChunkingRun
    chunking_run = ChunkingRun(
        document_id=db_document.id,
        strategy=strategy.value,
        parameters={},
        embedding_model=settings.embedding_model,
    )
    session.add(chunking_run)
    session.flush()

    # Save Chunks
    for i, chunk in enumerate(chunks):
        db_chunk = ChunkModel(
            run_id=chunking_run.id,
            chunk_index=i,
            content=chunk.text,
            token_count=chunk.token_count,
            embedding=list(chunk.embedding) if chunk.embedding is not None else None,
        )
        session.add(db_chunk)

    logger.debug("Insert successful!")


def insert_document(
    session: Session, document_name: str, document: ProcessedDocument, strategy: ChunkingStrategy
) -> None:

    # Unsinnige und leere Eingaben abfangen
    if not document_name.strip():
        raise ValueError("Dokumentname darf nicht leer sein.")

    if document is None:
        raise ValueError("Dokument muss verhanden sein.")

    if document.content is None or document.metadata is None:
        raise ValueError("Kein Dokumentinhalt oder Metadaten vorhanden.")

    if not isinstance(strategy, ChunkingStrategy):
        raise ValueError("Strategie muss vorhanden  sein.")

    # creating a cursor object
    content = document.content

    # Chunking Strategie auswählen
    chunks = chunk_text(content, strategy)
    # insert_into_database(document_name, document, strategy, chunks, embedding_model)
    insert_document_into_database(session, document_name, document, strategy, chunks)


def chunk_text(content: str, strategy: ChunkingStrategy) -> list[Chunk]:
    if not content.strip():
        raise ValueError("Inhalt darf nicht leer sein.")

    if not isinstance(strategy, ChunkingStrategy):
        raise ValueError("Strategie muss vorhanden  sein.")

    chunks = []
    # Chunking Strategie auswählen
    try:
        match strategy:
            case ChunkingStrategy.FIXED_SIZE:
                chunker = TokenChunker(tokenizer="word", chunk_size=token_count, chunk_overlap=5)
                chunks = chunker.chunk(content)
                print("Fixed size strategy")
            case ChunkingStrategy.SENTENCE:
                chunker = SentenceChunker(tokenizer="word", chunk_size=token_count)
                chunks = chunker.chunk(content)
                print("Sentence strategy")
            case ChunkingStrategy.RECURSIVE:
                chunker = RecursiveChunker(tokenizer="word", chunk_size=token_count)
                chunks = chunker.chunk(content)
                print("Recursive strategy")
            case ChunkingStrategy.SEMANTIC:
                settings = get_settings()
                embedding_model = settings.embedding_model
                chunker = SemanticChunker(
                    embedding_model=embedding_model,
                    chunk_size=token_count,
                    threshold=threshold_length,
                )
                chunks = chunker.chunk(content)
                print("Semantic strategy")
            case ChunkingStrategy.LATE:
                settings = get_settings()
                embedding_model = settings.embedding_model
                chunker = LateChunker(embedding_model=embedding_model, chunk_size=token_count)
                chunks = chunker.chunk(content)
                print("Late strategy")
            case _:
                raise Exception("Bitte geben Sie eine gültige Strategie an.")

    except Exception:
        raise

    # Fehlende Embeddings erzeugen
    ###Verloren gegangen beim Merging. Mit KI erzeugt.
    missing_chunks = [chunk for chunk in chunks if chunk.embedding is None]

    if missing_chunks:
        settings = get_settings()
        model = SentenceTransformer(settings.embedding_model)

        embeddings = model.encode(
            [chunk.text for chunk in missing_chunks],
            convert_to_numpy=True,
        )

        for chunk, embedding in zip(missing_chunks, embeddings, strict=True):
            chunk.embedding = embedding
    ###Ende KI-Block
    return chunks


# KI Generiert Verbindung testen
def test_connection() -> None:
    try:
        with engine.connect() as connection:
            result = connection.execute(sql_text("SELECT current_database(), version()")).one()

            print("Verbindung erfolgreich!")
            print("Datenbank:", result[0])
            print("PostgreSQL:", result[1])

    except SQLAlchemyError as error:
        print("Datenbankverbindung fehlgeschlagen:", error)


# TODO add call in main entrypoint
def bootstrap_database(engine: Engine) -> None:
    """
    Create all tables in the database if they are not existing yet.

    Args:
        engine (Engine): The engine connected to the database where the
            tables should be created.
    """

    from rag_project.database.metadata import Metadata  # noqa: F401, F811
    from rag_project.database.models import (
        Base,  # noqa: F811
        ChunkingRun,  # noqa: F401, F811
        Document,  # noqa: F401, F811
        MetaData,  # noqa: F401, F811
    )
    from rag_project.database.models import (
        Chunk as ChunkModel,  # noqa: F401
    )

    Base.metadata.create_all(engine)


def ensure_database(database_url: str | URL) -> None:
    """Create the configured database if it does not already exist."""
    target = make_url(database_url) if isinstance(database_url, str) else database_url
    database_name = target.database
    if not database_name:
        raise ValueError("DATABASE_URL must include a database name")

    maintenance_url = target.set(database="postgres", drivername="postgresql").render_as_string(
        hide_password=False
    )
    with psycopg.connect(maintenance_url, autocommit=True) as connection:
        exists = connection.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (database_name,)
        ).fetchone()
        if exists is None:
            connection.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))


def seed_documents(src_folder: Path) -> None:
    """Bootstrap the schema and insert embedded chunks from a PDF."""
    if not src_folder.is_dir():
        raise ValueError(f"Given path is not a directory: {src_folder}")
    database_url = get_database_url_from_config()
    ensure_database(database_url)
    engine = create_engine(database_url)

    # The extension must exist before SQLAlchemy creates the VECTOR column.
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(engine)
    num_docs_inserted = 0
    with Session(engine) as session, session.begin():
        for src_doc_path in src_folder.glob("*.pdf"):
            logger.debug(f"Processing document: {src_doc_path.name}")
            pdf_data = Path(src_doc_path).read_bytes()
            processed_doc = process_pdf(pdf_data)
            insert_document(
                session=session,
                document_name=src_doc_path.name,
                document=processed_doc,
                strategy=ChunkingStrategy.FIXED_SIZE,
            )
            num_docs_inserted += 1
            logger.info(f"Document inserted: {src_doc_path.name}")
    logger.info(f"Inserted {num_docs_inserted} documents.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError(
            "Bitte einen PDF-Dateipfad angeben. Syntax: rag_project.database.database Dateipfad."
        )

    filepath = sys.argv[1]

    # test_connection()
    meta1 = Metadata(
        title=None,
        author=None,
        subject=None,
        keywords=None,
        pdf_created_at=None,
        page_count=None,
        file_size_bytes=None,
    )

    with Session(engine) as session, session.begin():
        pdf_data = Path(filepath).read_bytes()
        doc1 = process_pdf(pdf_data)
        insert_document(session, filepath, doc1, ChunkingStrategy.FIXED_SIZE)
    # insert_document("", None, None)
    # insert_document("test3.pdf", text, ChunkingStrategy.SEMANTIC)
    # insert_document("test3.pdf", text, ChunkingStrategy.SENTENCE)
    # insert_document("test3.pdf", text, ChunkingStrategy.RECURSIVE)
    # insert_document("test3.pdf", text, ChunkingStrategy.LATE)
