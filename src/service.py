from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from models.models import Menu, Submenu, Dish
from pydantic import UUID4
from enum import Enum


class Tables(Enum):
      menu = 'Menu'
      submenu = 'Submenu'
      dish = 'Dish'


# delete record from menu, submenu or dish
async def delete_record(session: AsyncSession, table : Tables, id : UUID4):
    if table is Tables.menu:
        model = Menu
        pk = Menu.id
    elif table is Tables.submenu:
        model = Submenu
        pk = Submenu.id
    else:
        model = Dish
        pk = Dish.id

    stmt = delete(model).where(pk==id).returning(model)
    deleted_record =  await session.scalar(stmt)
    await session.commit()
    return deleted_record

# get a specific record from menu, submenu or dish
async def get_specific_record(session: AsyncSession, table : Tables, id : UUID4):
    if table is Tables.menu:
        menu_q = select(Menu).where(Menu.id == id)
        count_submenu_q = select(func.count(Submenu.id)).where(Submenu.menu_id == id)
        count_dish_q = select(func.count(Dish.id)).join(Submenu).where(Submenu.menu_id == id)
        
        menu_data = await session.scalar(menu_q)
        subm_dish = {
            'submenus_count' :await session.scalar(count_submenu_q),
            'dishes_count' :await session.scalar(count_dish_q)
            }
        menu = jsonable_encoder(menu_data)
        menu.update(subm_dish)
        
        return menu
    
    elif table is Tables.submenu:
        query = select(Submenu, func.count(Dish.id)).\
                outerjoin(Dish, Dish.submenu_id==Submenu.id).\
                where(Submenu.id == id).\
                group_by(Submenu.id)
        data = await session.execute(query)
        data = data.first()
        submenu = jsonable_encoder(data[0])
        submenu['dishes_count'] = data[1]

        return submenu
    
    else:
        dish = await session.scalar(select(Dish).where(Dish.id==id))
        return dish


# update record menu or submenu or dish
async def update_record(session: AsyncSession, table : Tables, new_data, id : UUID4):
    if table is Tables.menu:
        model = Menu
        pk = Menu.id
    elif table is Tables.submenu:
        model = Submenu
        pk = Submenu.id
    else:
        model = Dish
        pk = Dish.id
    stmt = update(model).\
            where(pk==id).\
            values(new_data.model_dump(exclude_unset=True)).\
            returning(model)

    result = await session.scalar(stmt)
    await session.commit()
    return result


# add record in menu, submenu or dish
def add_record(session: AsyncSession, table: Tables, data, id: UUID4=None):
    if table is Tables.menu:

        new_record = Menu(title=data.title, 
                          description=data.description
                          )
    elif table is Tables.submenu:

        new_record = Submenu(title=data.title,
                             description=data.description,
                             menu_id=id
                             )
        
    else:
        new_record = Dish(title=data.title,
                          description=data.description,
                          submenu_id=id,
                          price=data.price
                          )
        
    session.add(new_record)
    return new_record

# get menu list or submenu or dish
async def get_list(session: AsyncSession, table: Tables=None, id: UUID4=None):
    if id is None or table is None:
          return await session.scalars(select(Menu))
    elif table is Tables.submenu:
          return await session.scalars(select(Submenu).where(Submenu.menu_id==id))
    return await session.scalars(select(Dish).where(Dish.submenu_id==id))