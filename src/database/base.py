# import aioredis
from typing import AsyncGenerator
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from src.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER


DATABASE_URI = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
async_engine = create_async_engine(DATABASE_URI)
async_session = sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False)

# Dependency
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

# # Dependency
# async def get_redis():
#     yield aioredis.from_url(url=f"redis://{REDIS_HOST}:{REDIS_PORT}")