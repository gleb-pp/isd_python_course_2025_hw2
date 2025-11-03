from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.app.repo.base import Base

DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/events_db"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables() -> None:
    """Create database tables based on the defined models."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Session generator for database operations."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
