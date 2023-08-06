import pickle
from typing import Annotated

from aioredis import Redis
from fastapi import Depends
from pydantic import UUID4

from src.config import EXPIRATION, Keys
from src.database.base import get_redis_pool

from .repositories import Dish


class DishCacheRepository:
    def __init__(self, redis: Annotated[Redis, Depends(get_redis_pool)]) -> None:
        self.redis = redis
        self.ex = EXPIRATION
        self.key_submenu_list_prefix = Keys.key_submenu_list_prefix.value
        self.key_prefix_submenu = Keys.key_prefix_submenu.value
        self.key_prefix_menu = Keys.key_prefix_menu.value
        self.key_menu_list = Keys.key_menu_list.value
        self.key_dish_list_prefix = Keys.key_dish_list_prefix.value
        self.key_dish_prefix = Keys.key_dish_prefix.value

    async def get_dish_list_cache(self, submenu_id: UUID4) -> list[Dish | None] | None:
        if cache := await self.redis.get(f'{self.key_dish_list_prefix}{str(submenu_id)}'):
            return pickle.loads(cache)
        return None

    async def set_dish_list_cache(self, submenu_id: UUID4, data: list[Dish]) -> None:
        await self.redis.set(f'{self.key_dish_list_prefix}{str(submenu_id)}',
                             pickle.dumps(data),
                             ex=self.ex)
        return None

    async def get_dish_cache(self, dish_id: UUID4) -> Dish | None:
        if cache := await self.redis.get(f'{self.key_dish_prefix}{str(dish_id)}'):
            return pickle.loads(cache)
        return None

    async def set_dish_cache(self, dish_id: UUID4, data: Dish) -> None:
        await self.redis.set(f'{self.key_dish_prefix}{str(dish_id)}',
                             pickle.dumps(data),
                             ex=self.ex)
        return None

    async def delete_dish_cache(self, dish_id: UUID4) -> None:
        await self.redis.delete(f'{self.key_dish_prefix}{str(dish_id)}')
        await self.redis.delete(f'{self.key_menu_list}')
        keys_submenu: list = await self.redis.keys(f'{self.key_prefix_submenu}*')
        keys_menu: list = await self.redis.keys(f'{self.key_prefix_menu}*')
        keys_menu.extend(keys_submenu)
        if keys_menu:
            await self.redis.delete(*keys_menu)

    async def delete_dish_list_cache(self) -> None:
        if keys := await self.redis.keys(f'{self.key_dish_list_prefix}*'):
            await self.redis.delete(*keys)

    async def delete_cache(self, submenu_id) -> None:
        keys: list = await self.redis.keys(f'{self.key_prefix_menu}*')
        await self.redis.delete(f'{self.key_prefix_submenu}{str(submenu_id)}')
        keys.append(self.key_menu_list)
        await self.redis.delete(*keys)
