from typing import Annotated

from fastapi import Depends, HTTPException
from pydantic import UUID4
from sqlalchemy import delete, exists, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import get_session
from src.database.models import Dish, Submenu
from src.database.schemas import DishUpdateCreate


class DishRepository:

    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.session = session
        self.model = Dish

    async def _check_exist(self, id: UUID4, model=Submenu) -> None:
        if not await self.session.scalar(select(exists().where(model.id == id))):
            raise HTTPException(status_code=404, detail='dish not found')

    async def get_list_dish(self, submenu_id: UUID4) -> list[Dish]:
        query = await self.session.scalars(
            select(self.model)
            .where(self.model.submenu_id == submenu_id)
        )
        return query

    async def get_by_id(self, dish_id: UUID4) -> Dish:
        await self._check_exist(dish_id, self.model)
        query = await self.session.scalar(
            select(self.model,)
            .where(self.model.id == dish_id)
        )
        return query

    async def create(self, submenu_id: UUID4, data: DishUpdateCreate) -> Dish:
        await self._check_exist(submenu_id)
        dish = self.model(
            title=data.title,
            description=data.description,
            submenu_id=submenu_id,
            price=data.price,
        )
        try:
            self.session.add(dish)
            await self.session.commit()
            await self.session.refresh(dish)
            return dish
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=422, detail=f"The '{data.title}' is already stored!")

    async def update(self, dish_id: UUID4, data: DishUpdateCreate) -> Dish:

        await self._check_exist(dish_id, model=self.model)

        dish = await self.session.scalar(update(self.model)
                                         .where(self.model.id == dish_id)
                                         .values(data.model_dump(exclude_unset=True))
                                         .returning(self.model))
        await self.session.commit()
        return dish

    async def delete(self, dish_id: UUID4) -> None:

        await self._check_exist(dish_id, self.model)

        await self.session.execute(
            delete(self.model)
            .where(self.model.id == dish_id)
        )
        await self.session.commit()
