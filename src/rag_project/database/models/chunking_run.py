"""ChunkingRun ORM model."""

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from rag_project.database.models.base import Base


class ChunkingRun(Base):
    """ORM model for chunking_runs table."""

    __tablename__ = "chunking_runs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)

    # Foreign key to documents
    document_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )

    strategy: Mapped[str] = mapped_column(String(50), nullable=False)
    parameters: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default={}
    )
    embedding_model: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    document: Mapped["Document"] = relationship(
        "Document", back_populates="chunking_runs"
    )
    chunks: Mapped[list["Chunk"]] = relationship(
        "Chunk", back_populates="chunking_run", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ChunkingRun(id={self.id}, strategy={self.strategy})>"
