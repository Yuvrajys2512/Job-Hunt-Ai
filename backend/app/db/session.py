"""
Database session management.

SQLAlchemy is an ORM (Object Relational Mapper). Instead of writing raw SQL,
you define Python classes (models) and SQLAlchemy translates them to SQL queries.

Why async?
FastAPI is async by nature. If your DB queries were synchronous (blocking),
every query would freeze the entire server while waiting for the DB.
asyncpg + SQLAlchemy async means the server stays responsive during DB waits.

Connection pooling:
We don't open a new DB connection for every request — that's slow and exhausts
the DB. Instead, we maintain a pool of reusable connections (like a taxi rank).
pool_size=20 means 20 taxis always ready. max_overflow=10 means up to 10 extra
can be created in a rush, then destroyed when traffic drops.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


# ── Engine ────────────────────────────────────────────────────────────────────
# The engine manages the actual connection to PostgreSQL.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,      # if True, prints every SQL query (useful in dev)
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,       # test connection health before using from pool
)


# ── Session factory ───────────────────────────────────────────────────────────
# AsyncSession is like a "unit of work" — one session per request.
# All DB operations within a request share the same session.
# expire_on_commit=False means objects remain accessible after commit.
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── Base class for all ORM models ─────────────────────────────────────────────
# Every model (User, Job, Application) inherits from this.
# SQLAlchemy uses it to know which classes represent DB tables.
class Base(DeclarativeBase):
    pass


# ── Database initialization ───────────────────────────────────────────────────
async def init_db():
    """Create all tables that don't exist yet. Called on app startup."""
    # Import all models here so SQLAlchemy knows about them before creating tables
    from app.models import user, job, resume, application  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ── Dependency: get a session per request ─────────────────────────────────────
# FastAPI's dependency injection system calls this for every request that needs
# a DB session. The `yield` makes it a context manager — session is automatically
# closed after the request finishes (even if an error occurs).
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()    # commit if no exceptions
        except Exception:
            await session.rollback()  # rollback if something went wrong
            raise
