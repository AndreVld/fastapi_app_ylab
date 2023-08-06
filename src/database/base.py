from typing import AsyncGenerator

from aioredis import Redis, from_url
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.config import (
    DB_HOST,
    DB_NAME,
    DB_PASS,
    DB_PORT,
    DB_USER,
    REDIS_HOST,
    REDIS_PORT,
)

DATABASE_URI = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
async_engine = create_async_engine(DATABASE_URI)
async_session = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_redis_pool() -> AsyncGenerator[Redis, None]:
    async with from_url(url=f'redis://{REDIS_HOST}:{REDIS_PORT}') as redis:
        yield redis
