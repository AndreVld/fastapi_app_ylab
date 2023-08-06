from typing import Annotated

from fastapi import Depends
from pydantic import UUID4

from src.database.schemas import MenuUpdateCreate

from .cache_menu import MenuCacheRepository
from .repositories import Menu, MenuRepository


class MenuService:

    def __init__(self, database_repo: Annotated[MenuRepository, Depends()],
                 cache_repo: Annotated[MenuCacheRepository, Depends()]) -> None:
        self.database_repo = database_repo
        self.cache_repo = cache_repo

    async def get_list_menu(self):
        cache = await self.cache_repo.get_menu_list_cache()
        if cache or cache == []:
            return cache
        menu_list = await self.database_repo.get_list_menu()
        await self.cache_repo.set_menu_list_cache(menu_list)
        return menu_list

    async def get_by_id(self, id: UUID4) -> Menu:
        if cache := await self.cache_repo.get_menu_cache(id):
            return cache
        menu = await self.database_repo.get_by_id(id)
        await self.cache_repo.set_menu_cache(id, menu)
        return menu

    async def delete(self, id: UUID4) -> None:
        await self.database_repo.delete(id)
        await self.cache_repo.delete_menu_cache(id)
        await self.cache_repo.delete_menu_list_cache()

    async def create(self, data: MenuUpdateCreate) -> Menu:
        menu = await self.database_repo.create(data)
        await self.cache_repo.delete_menu_list_cache()
        await self.cache_repo.set_menu_cache(menu.id, menu)
        return menu

    async def update(self, id: UUID4, data: MenuUpdateCreate) -> Menu:
        await self.cache_repo.delete_menu_cache(id)
        await self.cache_repo.delete_menu_list_cache()
        menu = await self.database_repo.update(id, data)
        await self.cache_repo.set_menu_cache(id, menu)
        return menu
