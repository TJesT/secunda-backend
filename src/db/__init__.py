from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from src.config import postgres_settings


async_engine = create_async_engine(postgres_settings.dsn, echo=True, echo_pool="debug")


async_session_factory = async_sessionmaker(async_engine, expire_on_commit=False)


async def get_db_session() -> AsyncGenerator:
    async with async_session_factory() as session:
        yield session


PostgresBase = declarative_base()
