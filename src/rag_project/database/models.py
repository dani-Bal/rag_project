"""All ORM models for interaction with the database."""

from datetime import datetime

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import BigInteger, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.types import LargeBinary

from rag_project.config import get_settings


class Base(DeclarativeBase):
    pass


class Chunk(Base):
    """Model a chunk of document stored in the database."""

    VECTOR_DIMENSIONS = get_settings().vector_length
    __tablename__ = "chunks"

    __table_args__ = (
        UniqueConstraint("run_id", "chunk_index", name="unique_run_chunk_index"),
        Index("idx_chunks_run_id", "run_id"),
    )
    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)

    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("chunking_runs.id", ondelete="CASCADE"), nullable=False
    )
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int | None] = mapped_column(nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(VECTOR(VECTOR_DIMENSIONS))


class ChunkingRun(Base):
    """Model a chunking run stored in the database."""

    __tablename__ = "chunking_runs"

    __table_args__ = (Index("idx_chunking_runs_document_id", "document_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    strategy: Mapped[str] = mapped_column(String(50), nullable=False)

    embedding_model: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True,
    )
    parameters: Mapped[dict[str, object]] = mapped_column(
        JSONB,
        nullable=False,
        server_default="{}",
    )


class Document(Base):
    """Model a document stored in the database."""

    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    metadata_record: Mapped["MetaData"] = relationship(
        cascade="all, delete-orphan",
        single_parent=True,
        uselist=False,
    )

    filename: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    original_file: Mapped[bytes | None] = mapped_column(
        LargeBinary,
        nullable=True,
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=True,
    )


class MetaData(Base):
    """Model metadata for a document stored in the database."""

    __tablename__ = "pdf_metadata"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    document_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    author: Mapped[str | None] = mapped_column(Text, nullable=True)
    subject: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[str | None] = mapped_column(Text, nullable=True)
    pdf_created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    page_count: Mapped[int | None] = mapped_column(nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
