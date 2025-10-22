"""
Database Configuration and Session Management

Provides async database connection, session management, and base models
for PostgreSQL using SQLAlchemy 2.0+ async API.
"""

from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
    AsyncEngine
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

from api.config import settings
from api.logging_config import get_logger

logger = get_logger(__name__)

# Naming convention for constraints (helps with migrations)
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models"""
    metadata = metadata


# Global engine and session factory
_engine: Optional[AsyncEngine] = None
_async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_database_url() -> str:
    """Get database URL from settings or environment"""
    return settings.database_url


def create_engine() -> AsyncEngine:
    """
    Create async database engine

    Returns:
        AsyncEngine configured for PostgreSQL with asyncpg driver
    """
    database_url = get_database_url()

    logger.info("Creating database engine", extra={'extra_fields': {
        'database': database_url.split('@')[-1] if '@' in database_url else 'unknown'
    }})

    engine = create_async_engine(
        database_url,
        echo=False,  # Set to True for SQL logging
        pool_size=10,  # Number of connections to maintain
        max_overflow=20,  # Additional connections when pool is full
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,  # Recycle connections after 1 hour
    )

    return engine


def get_engine() -> AsyncEngine:
    """
    Get or create global async engine

    Returns:
        Singleton AsyncEngine instance
    """
    global _engine
    if _engine is None:
        _engine = create_engine()
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """
    Get or create global session factory

    Returns:
        Singleton async_sessionmaker instance
    """
    global _async_session_factory
    if _async_session_factory is None:
        engine = get_engine()
        _async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,  # Don't expire objects after commit
            autoflush=False,  # Don't auto-flush before queries
            autocommit=False  # Explicit commit required
        )
    return _async_session_factory


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session (context manager)

    Usage:
        async with get_session() as session:
            result = await session.execute(select(Character))
            characters = result.scalars().all()

    Yields:
        AsyncSession for database operations
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency for database sessions

    Usage in routes:
        @router.get("/items")
        async def list_items(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Item))
            return result.scalars().all()

    Yields:
        AsyncSession for database operations
    """
    async with get_session() as session:
        yield session


async def init_db():
    """
    Initialize database (create all tables)

    WARNING: Only use for development/testing. In production, use Alembic migrations.
    """
    engine = get_engine()

    logger.info("Initializing database (creating tables)")

    async with engine.begin() as conn:
        # Import all models here to ensure they're registered
        from api.models.db import (
            Character,
            ClothingItem,
            Outfit,
            Story,
            StoryScene
        )

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)

    logger.info("Database initialized successfully")


async def drop_db():
    """
    Drop all database tables

    WARNING: DESTRUCTIVE - Only use for testing!
    """
    engine = get_engine()

    logger.warning("Dropping all database tables (DESTRUCTIVE)")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    logger.warning("All database tables dropped")


async def close_db():
    """Close database connections"""
    global _engine, _async_session_factory

    if _engine:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None
        logger.info("Database connections closed")
