from typing import Annotated

from fastapi import BackgroundTasks, Depends
from pydantic import UUID4

from src.database.schemas import AllMenu, MenuUpdateCreate

from .cache_menu import MenuCacheRepository
from .repositories import Menu, MenuRepository


class MenuService:

    def __init__(self, database_repo: Annotated[MenuRepository, Depends()],
                 cache_repo: Annotated[MenuCacheRepository, Depends()],
                 background_tasks: BackgroundTasks) -> None:
        self.database_repo = database_repo
        self.cache_repo = cache_repo
        self.background_tasks = background_tasks

    async def get_all_menu(self) -> list[AllMenu | None]:
        if cache := await self.cache_repo.get_all_menu_cache():
            return cache
        all_menu = await self.database_repo.get_all_menu()
        self.background_tasks.add_task(self.cache_repo.set_all_menu_cache, all_menu)
        return all_menu

    async def get_list_menu(self):
        cache = await self.cache_repo.get_menu_list_cache()
        if cache or cache == []:
            return cache
        menu_list = await self.database_repo.get_list_menu()
        self.background_tasks.add_task(self.cache_repo.set_menu_list_cache, menu_list)
        return menu_list

    async def get_by_id(self, id: UUID4) -> Menu:
        if cache := await self.cache_repo.get_menu_cache(id):
            return cache
        menu = await self.database_repo.get_by_id(id)
        self.background_tasks.add_task(self.cache_repo.set_menu_cache, id, menu)
        return menu

    async def delete(self, id: UUID4) -> None:
        self.background_tasks.add_task(self.database_repo.delete, id)
        self.background_tasks.add_task(self.cache_repo.delete_menu_cache, id)
        self.background_tasks.add_task(self.cache_repo.delete_menu_list_cache)
        self.background_tasks.add_task(self.cache_repo.delete_all_menu_cache)

    async def create(self, data: MenuUpdateCreate) -> Menu:
        menu = await self.database_repo.create(data)
        self.background_tasks.add_task(self.cache_repo.delete_menu_list_cache)
        self.background_tasks.add_task(self.cache_repo.delete_all_menu_cache)
        self.background_tasks.add_task(self.cache_repo.set_menu_cache, menu.id, menu)
        return menu

    async def update(self, id: UUID4, data: MenuUpdateCreate) -> Menu:
        menu = await self.database_repo.update(id, data)
        self.background_tasks.add_task(self.cache_repo.delete_menu_cache, id)
        self.background_tasks.add_task(self.cache_repo.delete_menu_list_cache)
        self.background_tasks.add_task(self.cache_repo.delete_all_menu_cache)
        self.background_tasks.add_task(self.cache_repo.set_menu_cache, id, menu)
        return menu
