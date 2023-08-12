from typing import Annotated

from fastapi import BackgroundTasks, Depends
from pydantic import UUID4

from src.database.schemas import DishUpdateCreate

from .dish_cache import DishCacheRepository
from .repositories import Dish, DishRepository


class DishService:

    def __init__(self, database_repo: Annotated[DishRepository, Depends()],
                 cache_repo: Annotated[DishCacheRepository, Depends()],
                 background_tasks: BackgroundTasks) -> None:
        self.database_repo = database_repo
        self.cache_repo = cache_repo
        self.background_tasks = background_tasks

    async def get_list_dish(self, submenu_id: UUID4):
        cache = await self.cache_repo.get_dish_list_cache(submenu_id)
        if cache or cache == []:
            return cache
        dish_list = await self.database_repo.get_list_dish(submenu_id)
        self.background_tasks.add_task(self.cache_repo.set_dish_list_cache, submenu_id, dish_list)
        return dish_list

    async def get_by_id(self, id: UUID4) -> Dish:
        if cache := await self.cache_repo.get_dish_cache(id):
            return cache
        dish = await self.database_repo.get_by_id(id)
        self.background_tasks.add_task(self.cache_repo.set_dish_cache, id, dish)
        return dish

    async def delete(self, id: UUID4) -> None:
        self.background_tasks.add_task(self.database_repo.delete, id)
        self.background_tasks.add_task(self.cache_repo.delete_dish_cache, id)
        self.background_tasks.add_task(self.cache_repo.delete_dish_list_cache)
        self.background_tasks.add_task(self.cache_repo.delete_all_menu_cache)

    async def create(self, submenu_id: UUID4, data: DishUpdateCreate) -> Dish:
        dish = await self.database_repo.create(submenu_id, data)
        self.background_tasks.add_task(self.cache_repo.delete_cache, submenu_id)
        self.background_tasks.add_task(self.cache_repo.set_dish_cache, dish.id, dish)
        self.background_tasks.add_task(self.cache_repo.delete_dish_list_cache)
        self.background_tasks.add_task(self.cache_repo.delete_all_menu_cache)
        return dish

    async def update(self, id: UUID4, data: DishUpdateCreate) -> Dish:
        dish = await self.database_repo.update(id, data)
        self.background_tasks.add_task(self.cache_repo.delete_dish_list_cache)
        self.background_tasks.add_task(self.cache_repo.delete_dish_cache, id)
        self.background_tasks.add_task(self.cache_repo.set_dish_cache, dish.id, dish)
        self.background_tasks.add_task(self.cache_repo.delete_all_menu_cache)
        return dish
