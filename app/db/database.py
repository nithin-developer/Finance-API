from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    pass


engine = None
SessionLocal = None


def configure_engine(database_url: str | None = None) -> None:
    global engine, SessionLocal

    target_url = database_url or settings.database_url
    engine = create_async_engine(
        target_url,
        pool_pre_ping=True,
    )
    SessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


configure_engine(settings.database_url)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if SessionLocal is None:
        raise RuntimeError("Database session factory has not been configured")

    async with SessionLocal() as session:
        yield session


async def init_models() -> None:
    # Import models to register metadata before create_all.
    from app import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_engine() -> None:
    if engine is not None:
        await engine.dispose()
