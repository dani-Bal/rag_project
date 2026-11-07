from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Column, Integer
from sqlalchemy.orm import Mapped, mapped_column

from rag_project.config import get_settings
from rag_project.database.base import Base

settings = get_settings()


class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    id = Column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    text: Mapped[str] = mapped_column(nullable=False)
    embedding: Mapped[list[float]] = mapped_column(VECTOR(settings.vector_length), nullable=False)
