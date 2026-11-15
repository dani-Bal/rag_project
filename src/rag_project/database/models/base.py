"""Base configuration for SQLAlchemy ORM."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from rag_project.config import get_settings


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    pass


_engine = None
_SessionLocal = None


def get_engine() -> any:
    """Get or create the database engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        database_url = (
            f"postgresql://{settings.db_user}:{settings.db_password}"
            f"@{settings.db_host}:{settings.db_port}/{settings.db_name}"
        )
        _engine = create_engine(database_url, echo=settings.debug)
    return _engine


def get_session() -> any:
    """Get a database session."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal()
