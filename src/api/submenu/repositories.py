from typing import Annotated
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from src.database.base import get_session
from src.database.models import Menu, Submenu, Dish
from sqlalchemy import select, exists, update, delete, func, distinct
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError
from src.database.schemas import SubmenuUpdateCreate


class SubmenuRepository:

    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.session = session
        self.model = Submenu

    async def _check_exist(self, id: UUID4, model=Menu) -> None:
        if not await self.session.scalar(select(exists().where(model.id == id))):
            raise HTTPException(status_code=404, detail="submenu not found")
            
    async def get_list_submenu(self, menu_id: UUID4) -> list[Submenu]:
        await self._check_exist(menu_id)
        query = await self.session.execute(
            select(
                self.model.id,
                self.model.title,
                self.model.description,
                self.model.menu_id,
                func.count(distinct(Dish.id)).label('dishes_count'))
                .outerjoin(Dish, self.model.id==Dish.submenu_id)
                .filter(self.model.menu_id==menu_id)
                .group_by(self.model.id)
        )        
        return query.all()           

    async def get_by_id(self, submenu_id : UUID4) -> Submenu:
        await self._check_exist(submenu_id, self.model)
        query = await self.session.execute(
            select(
                self.model,
                func.count(Dish.id).label('dishes_count'))
                .outerjoin(Dish, self.model.id==Dish.submenu_id)
                .where(self.model.id==submenu_id)
                .group_by(self.model.id)
        )
        data = query.first()
        submenu = jsonable_encoder(data[0])
        submenu['dishes_count'] = data[1]
        return  submenu
        
    async def create(self, menu_id: UUID4, data: SubmenuUpdateCreate) -> Submenu:
        await self._check_exist(menu_id)
        submenu = self.model(
            title=data.title,
            description=data.description,
            menu_id=menu_id,
        )
        try:
            self.session.add(submenu)
            await self.session.commit()
            await self.session.refresh(submenu)
            return submenu
        except IntegrityError as ex:
            await self.session.rollback()
            raise HTTPException(status_code=422, detail=f"The '{data.title}' is already stored!")

    async def update(self, submenu_id : UUID4, data: SubmenuUpdateCreate) -> Submenu:

        await self._check_exist(submenu_id, model=self.model)
        
        submenu = await self.session.scalar(update(self.model)
            .where(self.model.id==submenu_id)
            .values(data.model_dump(exclude_unset=True))
            .returning(self.model))
        await self.session.commit()
        return submenu

    async def delete(self, submenu_id : UUID4) -> None:

        await self._check_exist(submenu_id, self.model)

        await self.session.execute(
            delete(self.model)
            .where(self.model.id==submenu_id)
        )
        await self.session.commit()
