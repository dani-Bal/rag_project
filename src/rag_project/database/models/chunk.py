"""Chunk ORM model."""

from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from rag_project.database.models.base import Base


class Chunk(Base):
    """ORM model for chunks table."""

    __tablename__ = "chunks"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    # Foreign key to chunking_runs
    run_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("chunking_runs.id", ondelete="CASCADE"), nullable=False
    )

    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        Vector(384), nullable=True
    )

    # Relationship
    chunking_run: Mapped["ChunkingRun"] = relationship(
        "ChunkingRun", back_populates="chunks"
    )

    # Unique constraint
    __table_args__ = (UniqueConstraint("run_id", "chunk_index"),)

    def __repr__(self) -> str:
        return f"<Chunk(id={self.id}, run_id={self.run_id}, index={self.chunk_index})>"
