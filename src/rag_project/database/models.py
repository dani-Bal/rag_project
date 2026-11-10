"""All ORM models for interaction with the database."""

from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Column, Integer
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

from rag_project.config import get_settings

Base = declarative_base()

settings = get_settings()


class DocumentChunk(Base):
    """Model a chunk of document stored in the database."""

    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)
    embedding: Mapped[list[float]] = mapped_column(VECTOR(settings.vector_length), nullable=False)
