import pickle
from typing import Annotated, Any

from aioredis import Redis
from fastapi import Depends
from pydantic import UUID4

from src.config import EXPIRATION, Keys
from src.database.base import get_redis_pool

from .repositories import Menu


class MenuCacheRepository:
    def __init__(self, redis: Annotated[Redis, Depends(get_redis_pool)]) -> None:
        self.redis = redis
        self.ex = EXPIRATION
        self.key_submenu_list_prefix = Keys.key_submenu_list_prefix.value
        self.key_prefix_submenu = Keys.key_prefix_submenu.value
        self.key_prefix_menu = Keys.key_prefix_menu.value
        self.key_menu_list = Keys.key_menu_list.value
        self.key_dish_list_prefix = Keys.key_dish_list_prefix.value
        self.key_dish_prefix = Keys.key_dish_prefix.value

    async def get_menu_list_cache(self) -> list[Menu | None] | None:
        if cache := await self.redis.get(self.key_menu_list):
            return pickle.loads(cache)
        return None

    async def set_menu_list_cache(self, menu: list[dict[str, Any]]) -> None:
        await self.redis.set(self.key_menu_list,
                             pickle.dumps(menu),
                             ex=self.ex)
        return None

    async def get_menu_cache(self, menu_id: UUID4) -> Menu | None:
        if cache := await self.redis.get(f'{self.key_prefix_menu}{str(menu_id)}'):
            return pickle.loads(cache)
        return None

    async def set_menu_cache(self, menu_id: UUID4, menu: Menu) -> None:
        await self.redis.set(f'{self.key_prefix_menu}{str(menu_id)}',
                             pickle.dumps(menu),
                             ex=self.ex)

    async def delete_menu_cache(self, menu_id: UUID4) -> None:
        await self.redis.delete(f'{self.key_prefix_menu}{str(menu_id)}')
        await self.delete_cache(menu_id)

    async def delete_menu_list_cache(self) -> None:
        await self.redis.delete(self.key_menu_list)

    async def delete_cache(self, menu_id: UUID4):
        await self.redis.delete(f'{self.key_submenu_list_prefix}{str(menu_id)}')
        keys_dish: list = await self.redis.keys(f'{self.key_dish_prefix}*')
        keys_submenu: list = await self.redis.keys(f'{self.key_prefix_submenu}*')
        keys_dish_list: list = await self.redis.keys(f'{self.key_dish_list_prefix}*')
        keys_dish.extend(keys_submenu)
        keys_dish.extend(keys_dish_list)
        if keys_dish:
            await self.redis.delete(*keys_dish)
