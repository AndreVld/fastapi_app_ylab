import asyncio
from typing import AsyncGenerator

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.database.base import async_engine, async_session
from src.database.models import Base, Dish, Menu, Submenu
from src.main import app

Base.metadata.bind = async_engine


@pytest.fixture(scope='session', autouse=True)
async def prepare_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        menu = Menu(title='menu', description='menu description')
        session.add(menu)
        await session.commit()

        submenu = Submenu(title='submenu',
                          description='submenu description',
                          menu_id=menu.id)
        session.add(submenu)
        await session.commit()
        dish = Dish(title='Dish',
                    description='dish description',
                    price='123.12',
                    submenu_id=submenu.id)
        session.add(dish)
        await session.commit()
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope='function')
async def menu_id():
    async with async_session() as session:
        return await session.scalar(select(Menu.id))


@pytest.fixture(scope='function')
async def submenu_id():
    async with async_session() as session:
        return await session.scalar(select(Submenu.id))


@pytest.fixture(scope='function')
async def dish_id():
    async with async_session() as session:
        return await session.scalar(select(Dish.id))


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://tests', follow_redirects=True) as ac:
        yield ac
