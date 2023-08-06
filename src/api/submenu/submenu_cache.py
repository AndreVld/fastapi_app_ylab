import pickle
from typing import Annotated

from aioredis import Redis
from fastapi import Depends
from pydantic import UUID4

from src.config import EXPIRATION, Keys
from src.database.base import get_redis_pool

from .repositories import Submenu


class SubmenuCacheRepository:
    def __init__(self, redis: Annotated[Redis, Depends(get_redis_pool)]) -> None:
        self.redis = redis
        self.ex = EXPIRATION
        self.key_submenu_list_prefix = Keys.key_submenu_list_prefix.value
        self.key_prefix_submenu = Keys.key_prefix_submenu.value
        self.key_prefix_menu = Keys.key_prefix_menu.value
        self.key_menu_list = Keys.key_menu_list.value
        self.key_dish_list_prefix = Keys.key_dish_list_prefix.value
        self.key_dish_prefix = Keys.key_dish_prefix.value

    async def get_submenu_list_cache(self, menu_id: UUID4) -> list[Submenu | None] | None:
        if cache := await self.redis.get(f'{self.key_submenu_list_prefix}{str(menu_id)}'):
            return pickle.loads(cache)
        return None

    async def set_submenu_list_cache(self, menu_id: UUID4, data: list[Submenu]) -> None:
        await self.redis.set(f'{self.key_submenu_list_prefix}{str(menu_id)}',
                             pickle.dumps(data),
                             ex=self.ex)
        return None

    async def get_submenu_cache(self, submenu_id: UUID4) -> Submenu | None:
        if cache := await self.redis.get(f'{self.key_prefix_submenu}{str(submenu_id)}'):
            return pickle.loads(cache)
        return None

    async def set_submenu_cache(self, submenu_id: UUID4, data: Submenu) -> None:
        await self.redis.set(f'{self.key_prefix_submenu}{str(submenu_id)}',
                             pickle.dumps(data),
                             ex=self.ex)

    async def delete_submenu_cache(self, submenu_id: UUID4) -> None:
        await self.redis.delete(f'{self.key_prefix_submenu}{str(submenu_id)}')
        if keys_menu := await self.redis.keys(f'{self.key_prefix_menu}*'):
            await self.redis.delete(*keys_menu)
        await self.redis.delete(f'{self.key_menu_list}')

    async def delete_submenu_list_cache(self) -> None:
        if keys_submenu := await self.redis.keys(f'{self.key_submenu_list_prefix}*'):
            await self.redis.delete(*keys_submenu)

    async def delete_menu_list_cache(self):
        await self.redis.delete(f'{self.key_menu_list}')

    async def delete_menu_cache(self, menu_id):
        await self.redis.delete(f'{self.key_prefix_menu}{str(menu_id)}')

    async def delete_cache(self, submenu_id):
        if keys := await self.redis.keys(f'{self.key_dish_prefix}*'):
            await self.redis.delete(*keys)
        await self.redis.delete(f'{self.key_dish_list_prefix}{str(submenu_id)}')
