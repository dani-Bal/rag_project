"""PDFMetadata ORM model."""

from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, Integer, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from rag_project.database.models.base import Base


class PDFMetadata(Base):
    """ORM model for pdf_metadata table."""

    __tablename__ = "pdf_metadata"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    subject: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pdf_created_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # Relationship to Document
    document: Mapped[Optional["Document"]] = relationship(
        "Document", back_populates="metadata", uselist=False
    )

    def __repr__(self) -> str:
        return f"<PDFMetadata(id={self.id}, title={self.title})>"
