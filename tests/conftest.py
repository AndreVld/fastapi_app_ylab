from fastapi.encoders import jsonable_encoder
import asyncio
import pytest
from typing import AsyncGenerator
from httpx import AsyncClient 
from sqlalchemy.orm import sessionmaker
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
import sys
import os


sys.path.insert(0 ,os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import app
from src import get_session
from src.models.models import Base, Menu
from src.config import DB_HOST_TEST, DB_NAME_TEST, DB_PASS_TEST, DB_PORT_TEST, DB_USER_TEST


DATABASE_URL_TEST = f"postgresql+asyncpg://{DB_USER_TEST}:{DB_PASS_TEST}@{DB_HOST_TEST}:{DB_PORT_TEST}/{DB_NAME_TEST}"


async_engine_test = create_async_engine(DATABASE_URL_TEST, echo=False)
async_session_maker = sessionmaker(async_engine_test, class_=AsyncSession, expire_on_commit=False)
Base.metadata.bind = async_engine_test


async def override_get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


app.dependency_overrides[get_session] = override_get_session


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with async_engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        

@pytest.fixture(scope='session')
async def menu_id():
    async with async_session_maker() as session:
        result = await session.scalar(select(Menu))
        result = jsonable_encoder(result)
        return result['id']


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://127.0.0.1:8000', follow_redirects=True) as ac:
        yield ac
        