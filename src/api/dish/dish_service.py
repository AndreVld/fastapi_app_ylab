from fastapi import Depends
from typing import Annotated

from pydantic import UUID4

from src.database.schemas import DishUpdateCreate
from .repositories import DishRepository, Dish
from .dish_cache import DishCacheRepository


class DishService:

    def __init__(self, database_repo: Annotated[DishRepository, Depends()],
                       cache_repo: Annotated[DishCacheRepository, Depends()]) -> None:
        self.database_repo = database_repo
        self.cache_repo = cache_repo
    
    async def get_list_dish(self, submenu_id: UUID4):
        cache = await self.cache_repo.get_dish_list_cache(submenu_id)
        if cache or cache == []:
            return cache
        dish_list  = await self.database_repo.get_list_dish(submenu_id)
        await self.cache_repo.set_dish_list_cache(submenu_id, dish_list)
        return dish_list
    
    async def get_by_id(self, id: UUID4) -> Dish:
        if cache := await self.cache_repo.get_dish_cache(id):
            return cache
        dish = await self.database_repo.get_by_id(id)
        await self.cache_repo.set_dish_cache(id, dish)
        return dish
    
    async def delete(self, id: UUID4) -> None:
        await self.database_repo.delete(id)
        await self.cache_repo.delete_dish_cache(id)
        await self.cache_repo.delete_dish_list_cache()

    async def create(self, submenu_id: UUID4, data: DishUpdateCreate) -> Dish:
        dish = await self.database_repo.create(submenu_id, data)
        await self.cache_repo.delete_cache(submenu_id)
        await self.cache_repo.set_dish_cache(dish.id, dish)
        await self.cache_repo.delete_dish_list_cache()
        return dish
    
    async def update(self, id: UUID4, data: DishUpdateCreate) -> Dish:
        dish =  await self.database_repo.update(id, data)
        await self.cache_repo.delete_dish_list_cache()
        await self.cache_repo.delete_dish_cache(id)
        await self.cache_repo.set_dish_cache(dish.id, dish)
        return dish