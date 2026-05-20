"""
Air Quality Platform - Database Connection Manager
Handles SQLAlchemy engine, session factory, and database initialization.
"""

import os
import sys
import logging
from pathlib import Path
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from config import config
from backend.database.models import Base

logger = logging.getLogger(__name__)

# ===================== ENGINE SETUP =====================

def get_engine(database_url: str = None):
    """Create SQLAlchemy engine with connection pooling."""
    url = database_url or config.DATABASE_URL

    engine_kwargs = {
        "echo": config.APP_DEBUG and config.APP_ENV == "development",
    }

    if "sqlite" in url:
        engine_kwargs.update({
            "connect_args": {"check_same_thread": False},
            "pool_pre_ping": True,
        })
        engine = create_engine(url, **engine_kwargs)

        # Enable WAL mode and foreign keys for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=5000")
            cursor.close()
    else:
        # PostgreSQL / MySQL connection pooling
        engine_kwargs.update({
            "pool_size": 10,
            "max_overflow": 20,
            "pool_recycle": 3600,
            "pool_pre_ping": True,
        })
        engine = create_engine(url, **engine_kwargs)

    return engine


# Create global engine and session factory
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# ===================== SESSION MANAGEMENT =====================

def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_session():
    """Context manager for database sessions."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


# ===================== DATABASE INITIALIZATION =====================

def init_db():
    """Create all database tables."""
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully.")


def drop_db():
    """Drop all database tables (use with caution)."""
    logger.warning("Dropping all database tables!")
    Base.metadata.drop_all(bind=engine)
    logger.info("All tables dropped.")


def check_connection() -> bool:
    """Check if database connection is healthy."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


# ===================== INIT ON IMPORT =====================

# Auto-create tables in development
if config.APP_ENV == "development":
    init_db()
