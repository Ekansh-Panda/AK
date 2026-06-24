"""Database engine, session factory and dependency wiring."""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.logging import get_logger
from app.db.base import Base

logger = get_logger(__name__)

# SQLite needs `check_same_thread=False` to be shared across FastAPI threads.
_connect_args = (
    {"check_same_thread": False}
    if settings.DATABASE_URL.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=_connect_args,
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(
    bind=engine, autocommit=False, autoflush=False, expire_on_commit=False
)


def init_db() -> None:
    """Create all tables. Imports models so they register with the metadata."""
    # Import models for side effects (table registration).
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized at %s", settings.DATABASE_URL)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a scoped DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
