from typing import Annotated

from fastapi import Depends
from pydantic import UUID4

from src.database.schemas import SubmenuUpdateCreate

from .repositories import Submenu, SubmenuRepository
from .submenu_cache import SubmenuCacheRepository


class SubmenuService:

    def __init__(self, database_repo: Annotated[SubmenuRepository, Depends()],
                 cache_repo: Annotated[SubmenuCacheRepository, Depends()]) -> None:
        self.database_repo = database_repo
        self.cache_repo = cache_repo

    async def get_list_submenu(self, menu_id: UUID4):
        cache = await self.cache_repo.get_submenu_list_cache(menu_id)
        if cache or cache == []:
            return cache
        submenu_list = await self.database_repo.get_list_submenu(menu_id)
        await self.cache_repo.set_submenu_list_cache(menu_id, submenu_list)
        return submenu_list

    async def get_by_id(self, id: UUID4) -> Submenu:
        if cache := await self.cache_repo.get_submenu_cache(id):
            return cache
        submenu = await self.database_repo.get_by_id(id)
        await self.cache_repo.set_submenu_cache(id, submenu)
        return submenu

    async def delete(self, id: UUID4) -> None:
        await self.database_repo.delete(id)
        await self.cache_repo.delete_submenu_cache(id)
        await self.cache_repo.delete_menu_list_cache()
        await self.cache_repo.delete_submenu_list_cache()

    async def create(self, menu_id: UUID4, data: SubmenuUpdateCreate) -> Submenu:
        submenu = await self.database_repo.create(menu_id, data)
        await self.cache_repo.delete_submenu_list_cache()
        await self.cache_repo.delete_menu_list_cache()
        await self.cache_repo.delete_menu_cache(menu_id)
        await self.cache_repo.set_submenu_cache(submenu.id, submenu)
        return submenu

    async def update(self, id: UUID4, data: SubmenuUpdateCreate) -> Submenu:
        submenu = await self.database_repo.update(id, data)
        await self.cache_repo.delete_submenu_list_cache()
        await self.cache_repo.delete_submenu_cache(id)
        await self.cache_repo.set_submenu_cache(submenu.id, submenu)
        return submenu
