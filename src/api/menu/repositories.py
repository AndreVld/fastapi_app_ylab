from typing import Annotated, Any

from fastapi import Depends, HTTPException
from pydantic import UUID4
from sqlalchemy import delete, distinct, exists, func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import get_session
from src.database.models import Dish, Menu, Submenu
from src.database.schemas import MenuUpdateCreate


class MenuRepository:

    def __init__(self, session: Annotated[AsyncSession, Depends(get_session)]) -> None:
        self.session = session
        self.model = Menu

    async def _check_exist(self, menu_id: UUID4) -> None:
        if not await self.session.scalar(select(exists().where(self.model.id == menu_id))):
            raise HTTPException(status_code=404, detail='menu not found')

    async def get_list_menu(self) -> list[dict[str, Any]]:

        query = await self.session.execute(
            select(
                Menu.id,
                Menu.title,
                Menu.description,
                func.count(distinct(Submenu.id)).label('submenus_count'),
                func.count(distinct(Dish.id)).label('dishes_count'))
            .outerjoin(Submenu, Menu.id == Submenu.menu_id)
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)
            .group_by(Menu)
        )
        data = [
            {
                'id': row[0],
                'title': row[1],
                'description': row[2],
                'submenus_count': row[3],
                'dishes_count': row[4]
            }
            for row in query.all()
        ]

        return data

    async def get_by_id(self, menu_id: UUID4) -> Menu:

        await self._check_exist(menu_id)

        query = await self.session.execute(
            select(
                Menu.id,
                Menu.title,
                Menu.description,
                func.count(distinct(Submenu.id)).label('submenus_count'),
                func.count(distinct(Dish.id)).label('dishes_count'))
            .outerjoin(Submenu, Menu.id == Submenu.menu_id)
            .outerjoin(Dish, Submenu.id == Dish.submenu_id)
            .where(Menu.id == menu_id)
            .group_by(Menu.id)
        )
        return query.first()

    async def create(self, data: MenuUpdateCreate) -> Menu:
        menu = Menu(
            title=data.title,
            description=data.description
        )
        try:
            self.session.add(menu)
            await self.session.commit()
            await self.session.refresh(menu)
            return menu
        except IntegrityError:
            await self.session.rollback()
            raise HTTPException(status_code=422, detail=f"The '{data.title}' is already stored!")

    async def update(self, menu_id: UUID4, data: MenuUpdateCreate) -> Menu:

        await self._check_exist(menu_id)

        menu = await self.session.scalar(update(self.model)
                                         .where(self.model.id == menu_id)
                                         .values(data.model_dump(exclude_unset=True))
                                         .returning(self.model))
        await self.session.commit()
        return menu

    async def delete(self, menu_id: UUID4) -> None:

        await self._check_exist(menu_id)

        await self.session.execute(
            delete(self.model)
            .where(self.model.id == menu_id)
        )
        await self.session.commit()
