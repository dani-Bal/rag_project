"""Document ORM model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, ForeignKey, LargeBinary, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rag_project.database.models.base import Base


class Document(Base):
    """ORM model for documents table."""

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    original_file: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Foreign key to pdf_metadata
    metadata_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("pdf_metadata.id", ondelete="SET NULL"), unique=True
    )

    # Relationships
    metadata: Mapped[Optional["PDFMetadata"]] = relationship(
        "PDFMetadata", back_populates="document"
    )
    chunking_runs: Mapped[list["ChunkingRun"]] = relationship(
        "ChunkingRun", back_populates="document", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, filename={self.filename})>"
