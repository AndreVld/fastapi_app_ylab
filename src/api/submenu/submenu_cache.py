from fastapi import Depends
from typing import Annotated, Any
from pydantic import UUID4
from aioredis import Redis
from src.database.base import get_redis_pool
from .repositories import Submenu
from src.config import EXPIRATION
import pickle


class SubmenuCacheRepositiry:
    def __init__(self, redis: Annotated[Redis, Depends(get_redis_pool)]) -> None:
        self.redis = redis
        self.ex = EXPIRATION
        self.key_submenu_list_prefix = 'submenu_for_menu:'
        self.key_prefix = 'submenu:'
        self.key_prefix_menu = 'menu:'
        self.key_menu_list = 'all_menu'

    async def get_submenu_list_cache(self, menu_id: UUID4) -> list[Submenu | None] | None:
        if cache := await self.redis.get(f'{self.key_submenu_list_prefix}{str(menu_id)}'):
            return pickle.loads(cache)
        return None

    async def set_submenu_list_cache(self, menu_id: UUID4, submenu: list[Submenu])-> None:
        await self.redis.set(f'{self.key_submenu_list_prefix}{str(menu_id)}',
                             pickle.dumps(submenu),
                             ex=self.ex)
        return None
    
    async def get_submenu_cache(self, submenu_id: UUID4) -> Submenu | None:
        if cache := await self.redis.get(f'{self.key_prefix}{str(submenu_id)}'):
            return pickle.loads(cache)
        return None
    
    async def set_submenu_cache(self, submenu_id: UUID4, submenu : Submenu) -> None:
        await self.redis.set(f'{self.key_prefix}{str(submenu_id)}', 
                             pickle.dumps(submenu),
                             ex=self.ex)

    async def delete_submenu_cache(self, submenu_id: UUID4) -> None:
        await self.redis.delete(f'{self.key_prefix}{str(submenu_id)}')
        if keys_menu:= await self.redis.keys(f'{self.key_prefix_menu}*'):
            await self.redis.delete(*keys_menu)
        await self.redis.delete(f'{self.key_menu_list}')
        

    async def delete_submenu_list_cache(self) -> None:
        if keys_menu:= await self.redis.keys(f'{self.key_submenu_list_prefix}*'):
            await self.redis.delete(*keys_menu)

    async def delete_menu_list_cache(self):
        await self.redis.delete(f'{self.key_menu_list}')

    async def delete_menu_cache(self, menu_id):
        await self.redis.delete(f'{self.key_prefix_menu}{str(menu_id)}')