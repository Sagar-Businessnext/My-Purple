"""Async database engine + session factory, and one-time schema setup."""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from purple.config import settings
from purple.memory.models import Base
from purple.utils.logging import get_logger

log = get_logger("db")

engine = create_async_engine(settings.pg_dsn, echo=False, pool_pre_ping=True)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def init_db() -> None:
    """Enable pgvector and create tables. Safe to call on every startup."""
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    log.info("db_ready", dsn=settings.pg_dsn.split("@")[-1])
