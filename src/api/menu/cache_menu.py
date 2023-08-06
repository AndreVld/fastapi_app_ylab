import pickle
from typing import Annotated, Any

from aioredis import Redis
from fastapi import Depends
from pydantic import UUID4

from src.config import EXPIRATION
from src.database.base import get_redis_pool

from .repositories import Menu


class MenuCacheRepositiry:
    def __init__(self, redis: Annotated[Redis, Depends(get_redis_pool)]) -> None:
        self.redis = redis
        self.ex = EXPIRATION
        self.key_menu_list = 'all_menu'
        self.key_prefix = 'menu:'

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
        if cache := await self.redis.get(f'{self.key_prefix}{str(menu_id)}'):
            return pickle.loads(cache)
        return None

    async def set_menu_cache(self, menu_id: UUID4, menu: Menu) -> None:
        await self.redis.set(f'{self.key_prefix}{str(menu_id)}',
                             pickle.dumps(menu),
                             ex=self.ex)

    async def delete_menu_cache(self, menu_id: UUID4) -> None:
        await self.redis.delete(f'{self.key_prefix}{str(menu_id)}')

    async def delete_menu_list_cache(self) -> None:
        await self.redis.delete(self.key_menu_list)
