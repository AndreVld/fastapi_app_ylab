from typing import Annotated

from fastapi import BackgroundTasks, Depends
from pydantic import UUID4

from src.database.schemas import SubmenuUpdateCreate

from .repositories import Submenu, SubmenuRepository
from .submenu_cache import SubmenuCacheRepository


class SubmenuService:

    def __init__(self, database_repo: Annotated[SubmenuRepository, Depends()],
                 cache_repo: Annotated[SubmenuCacheRepository, Depends()],
                 background_tasks: BackgroundTasks) -> None:
        self.database_repo = database_repo
        self.cache_repo = cache_repo
        self.background_tasks = background_tasks

    async def get_list_submenu(self, menu_id: UUID4):
        cache = await self.cache_repo.get_submenu_list_cache(menu_id)
        if cache or cache == []:
            return cache
        submenu_list = await self.database_repo.get_list_submenu(menu_id)
        self.background_tasks.add_task(self.cache_repo.set_submenu_list_cache, menu_id, submenu_list)
        return submenu_list

    async def get_by_id(self, id: UUID4) -> Submenu:
        if cache := await self.cache_repo.get_submenu_cache(id):
            return cache
        submenu = await self.database_repo.get_by_id(id)
        self.background_tasks.add_task(self.cache_repo.set_submenu_cache, id, submenu)
        return submenu

    async def delete(self, id: UUID4) -> None:
        self.background_tasks.add_task(self.database_repo.delete, id)
        self.background_tasks.add_task(self.cache_repo.delete_submenu_cache, id)
        self.background_tasks.add_task(self.cache_repo.delete_menu_list_cache)
        self.background_tasks.add_task(self.cache_repo.delete_all_menu_cache)
        self.background_tasks.add_task(self.cache_repo.delete_submenu_list_cache)

    async def create(self, menu_id: UUID4, data: SubmenuUpdateCreate) -> Submenu:
        submenu = await self.database_repo.create(menu_id, data)
        self.background_tasks.add_task(self.cache_repo.delete_submenu_list_cache)
        self.background_tasks.add_task(self.cache_repo.delete_menu_list_cache)
        self.background_tasks.add_task(self.cache_repo.delete_all_menu_cache)
        self.background_tasks.add_task(self.cache_repo.delete_menu_cache, menu_id)
        self.background_tasks.add_task(self.cache_repo.set_submenu_cache, submenu.id, submenu)
        return submenu

    async def update(self, id: UUID4, data: SubmenuUpdateCreate) -> Submenu:
        submenu = await self.database_repo.update(id, data)
        self.background_tasks.add_task(self.cache_repo.delete_submenu_list_cache)
        self.background_tasks.add_task(self.cache_repo.delete_submenu_cache, id)
        self.background_tasks.add_task(self.cache_repo.delete_all_menu_cache)
        self.background_tasks.add_task(self.cache_repo.set_submenu_cache, submenu.id, submenu)
        return submenu
