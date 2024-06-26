import contextlib
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from os import getenv
DATABASE_URL = f'postgresql+asyncpg://{getenv("POSTGRES_USER")}:{getenv("POSTGRES_PASSWORD")}@{getenv("POSTGRES_HOST")}:5432/{getenv("POSTGRES_DB")}'


class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

get_async_session_context = contextlib.asynccontextmanager(get_async_session)
