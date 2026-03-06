"""
Database configuration module.

Uses SQLAlchemy to manage the connection to a SQLite database.
SQLite was chosen for portability — the examiner can clone and run
the project without installing a separate database server.
The ORM abstraction means switching to PostgreSQL would only
require changing the DATABASE_URL string.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Database file lives in the project root.
# Uses an environment variable so tests can override the path.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "hotel_bookings.db")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# SQLite-specific: check_same_thread=False allows FastAPI's async
# workers to share the connection safely
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


def get_db():
    """
    Dependency injection for FastAPI routes.
    Yields a database session and ensures it is closed after the request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
