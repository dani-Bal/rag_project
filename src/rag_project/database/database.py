# Autor: Carsten Ostlender, 2026
# TODO: Unit Tests
# Verbindung aus Datei lesen (verschlüsselt)
# TODO Embedding in datenbank
"""Database operations using SQLAlchemy ORM."""

import sys
from enum import StrEnum
from pathlib import Path
from typing import Optional

from chonkie import (
    Chunk,
    LateChunker,
    RecursiveChunker,
    SemanticChunker,
    SentenceChunker,
    TokenChunker,
)
from sqlalchemy import text

from rag_project.config import get_settings

from .document import Document
from .metadata import Metadata
from .models import (
    Base,
    Chunk as ChunkModel,
    ChunkingRun,
    Document as DocumentModel,
    PDFMetadata,
    get_engine,
    get_session,
)
from .process_pdf import process_pdf


class ChunkingStrategy(StrEnum):
    FIXED_SIZE = "fixed_size"
    RECURSIVE = "recursive"
    SEMANTIC = "semantic"
    LATE = "late"
    SENTENCE = "sentence"


token_count = 35
threshold_length = 0.65

text = (
    "Python ist eine Programmiersprache. Sie wird häufig für KI verwendet. "
    "Machine Learning erkennt Muster in Daten. Neuronale Netze lernen aus Beispielen. "
    "PostgreSQL ist eine relationale Datenbank. Mit pgvector kann man Embeddings speichern. "
    "SQL ermöglicht das Abfragen von Daten. Datenbanken sind für RAG-Systeme wichtig. "
    "Fußball wird von zwei Mannschaften gespielt. Bayern München spielt in der Bundesliga. "
    "Ein Fußballspiel dauert normalerweise 90 Minuten. "
    "Astronomie beschäftigt sich mit Sternen und Planeten. "
    "Die Erde umkreist die Sonne. Der Mond umkreist die Erde."
)


def init_database() -> None:
    """Initialize database tables."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def insert_document(document_name: str, document: Document, strategy: ChunkingStrategy) -> None:
    """Insert a document into the database with chunking.

    Args:
        document_name: Name of the document file
        document: Document object with content and metadata
        strategy: Chunking strategy to use

    Raises:
        ValueError: If inputs are invalid
    """
    # Validate inputs
    if not document_name.strip():
        raise ValueError("Dokumentname darf nicht leer sein.")

    if document is None:
        raise ValueError("Dokument muss verhanden sein.")

    if document.content is None or document.metadata is None:
        raise ValueError("Kein Dokumentinhalt oder Metadaten vorhanden.")

    if not isinstance(strategy, ChunkingStrategy):
        raise ValueError("Strategie muss vorhanden sein.")

    settings = get_settings()
    embedding_model = settings.embedding_model

    # Chunk the content
    chunks = chunk_text(content=document.content, strategy=strategy)

    # Insert into database using ORM
    insert_into_database_orm(
        document_name=document_name,
        document=document,
        strategy=strategy,
        chunks=chunks,
        embedding_model=embedding_model,
    )


def insert_into_database_orm(
    document_name: str,
    document: Document,
    strategy: ChunkingStrategy,
    chunks: list[Chunk],
    embedding_model: str,
) -> None:
    """Insert document data using SQLAlchemy ORM.

    Args:
        document_name: Name of the document file
        document: Document object with content and metadata
        strategy: Chunking strategy
        chunks: List of text chunks
        embedding_model: Name of the embedding model used
    """
    session = get_session()

    try:
        # Insert PDF metadata
        pdf_metadata = PDFMetadata(
            title=document.metadata.title,
            author=document.metadata.author,
            subject=document.metadata.subject,
            keywords=document.metadata.keywords,
            pdf_created_at=document.metadata.pdf_created_at,
            page_count=document.metadata.page_count,
            file_size_bytes=document.metadata.file_size_bytes,
        )
        session.add(pdf_metadata)
        session.flush()  # Get the ID

        # Insert document
        db_document = DocumentModel(
            filename=document_name,
            content=document.content,
            original_file=document.original_file,
            metadata_id=pdf_metadata.id,
        )
        session.add(db_document)
        session.flush()

        # Insert chunking run
        chunking_run = ChunkingRun(
            document_id=db_document.id,
            strategy=strategy.value,
            parameters={},
            embedding_model=embedding_model,
        )
        session.add(chunking_run)
        session.flush()

        # Insert chunks
        for i, chunk in enumerate(chunks):
            db_chunk = ChunkModel(
                run_id=chunking_run.id,
                chunk_index=i,
                content=chunk.text,
                token_count=chunk.token_count,
            )
            session.add(db_chunk)

        session.commit()
        print("Insert erfolgreich!")

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def chunk_text(content: str, strategy: ChunkingStrategy) -> list[Chunk]:
    """Chunk text using the specified strategy.

    Args:
        content: Text content to chunk
        strategy: Chunking strategy to use

    Returns:
        List of Chunk objects

    Raises:
        ValueError: If content is empty or strategy is invalid
    """
    if not content.strip():
        raise ValueError("Inhalt darf nicht leer sein.")

    if not isinstance(strategy, ChunkingStrategy):
        raise ValueError("Strategie muss vorhanden sein.")

    chunks = []

    try:
        match strategy:
            case ChunkingStrategy.FIXED_SIZE:
                chunker = TokenChunker(
                    tokenizer="word", chunk_size=token_count, chunk_overlap=5
                )
                chunks = chunker.chunk(content)
                print("Fixed size strategy")

            case ChunkingStrategy.SENTENCE:
                chunker = SentenceChunker(
                    tokenizer="word", chunk_size=token_count
                )
                chunks = chunker.chunk(content)
                print("Sentence strategy")

            case ChunkingStrategy.RECURSIVE:
                chunker = RecursiveChunker(
                    tokenizer="word", chunk_size=token_count
                )
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
                chunker = LateChunker(
                    embedding_model=embedding_model, chunk_size=token_count
                )
                chunks = chunker.chunk(content)
                print("Late strategy")

            case _:
                raise Exception("Bitte geben Sie eine gültige Strategie an.")

    except Exception:
        raise

    return chunks


def test_connection() -> None:
    """Test database connection."""
    try:
        session = get_session()
        result = session.execute(text("SELECT current_database(), version()")).fetchone()

        if result is None:
            raise RuntimeError("Keine Datenbankinformationen zurückgegeben")

        print("Verbindung erfolgreich!")
        print("Datenbank:", result[0])
        print("PostgreSQL:", result[1])
        session.close()

    except Exception as error:
        print("Datenbankverbindung fehlgeschlagen:", error)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise ValueError(
            "Bitte einen PDF-Dateipfad angeben. Syntax: rag_project.database.database Dateipfad."
        )

    filepath = sys.argv[1]

    # Initialize database tables
    init_database()

    meta1 = Metadata(
        title=None,
        author=None,
        subject=None,
        keywords=None,
        pdf_created_at=None,
        page_count=None,
        file_size_bytes=None,
    )
    pdf_data = Path(filepath).read_bytes()
    doc1 = process_pdf(pdf_data)
    insert_document(filepath, doc1, ChunkingStrategy.FIXED_SIZE)
