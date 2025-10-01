from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from src.api.config import get_settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models."""


def _create_engine():
    # For SQLite file DB, check for proper URI and pragmas
    settings = get_settings()
    url = settings.sqlalchemy_database_url
    # For SQLite, need check_same_thread=False if using standard sqlite:///
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(url, connect_args=connect_args, future=True, echo=False)


engine = _create_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session, expire_on_commit=False)


# PUBLIC_INTERFACE
def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency to provide a database session and ensure cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    """Context manager for non-HTTP usage to ensure transaction handling."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
