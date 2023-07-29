from fastapi.encoders import jsonable_encoder
from typing import  Annotated
from fastapi import FastAPI, Depends, Path, Body
from fastapi.responses import JSONResponse
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from databese import get_session
from models import models
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, exists
import service
import schemas


app = FastAPI()


# Удалить блюдо 
@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
async def delete_dish(dish_id: Annotated[UUID4, Path()],
                      session: Annotated[AsyncSession, Depends(get_session)]):
    
    if not await session.scalar(select(exists().where(models.Dish.id == dish_id))):
        raise HTTPException(status_code=404, detail="dish not found")
    
    result = await service.delete_record(session, service.Tables.dish, dish_id)

    return JSONResponse(content={'deleted': jsonable_encoder(result)})


# Обновить запись блюда
@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=schemas.DishSchema)
async def update_dish(dish_id: Annotated[UUID4, Path()],
                      dish_in: Annotated[schemas.DishUpdateCreate, Body()],
                      session: Annotated[AsyncSession, Depends(get_session)]):
    
    return await service.update_record(session, service.Tables.dish, dish_in, dish_id)


# Определенное блюдо
@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=schemas.DishSchema)
async def get_dish(dish_id: Annotated[UUID4, Path()], 
                   session: Annotated[AsyncSession, Depends(get_session)]):
    
    if result := await service.get_specific_record(session, service.Tables.dish, dish_id):
        return result 
    raise HTTPException(status_code=404, detail="dish not found")


# Добавить блюдо
@app.post('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=schemas.DishSchema, status_code=201)
async def create_dish(submenu_id: Annotated[UUID4, Path()],
                      dish_in: Annotated[schemas.DishUpdateCreate, Body],
                      session: Annotated[AsyncSession, Depends(get_session)]):
    
    if not await session.scalar(select(exists().where(models.Submenu.id == submenu_id))):
        raise HTTPException(status_code=404, detail='submenu not found')
    try:
        new_dish = service.add_record(session, service.Tables.dish, dish_in, submenu_id)
        session.add(new_dish)
        await session.commit()
        await session.refresh(new_dish)
        return new_dish
    except IntegrityError as ex:
        await session.rollback()
        raise HTTPException(status_code=422,detail=f"The '{dish_in.title}' is already stored!")


# Cписок блюд 
@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', response_model=list[schemas.DishSchema])
async def get_list_dish(submenu_id: Annotated[UUID4, Path()],
                        session: Annotated[AsyncSession, Depends(get_session)]):
    
    # if not await session.scalar(select(exists().where(models.Submenu.id == submenu_id))):
    #     raise HTTPException(status_code=404, detail='submenu not found')
    return await service.get_list(session, service.Tables.dish, submenu_id)


# Удалить подменю
@app.delete('/api/v1/menus/{menu_id}/submenus/{submenu_id}')
async def delete_submenu(submenu_id: Annotated[UUID4, Path()], 
                         session: Annotated[AsyncSession, Depends(get_session)]):
    if not await session.scalar(select(exists().where(models.Submenu.id == submenu_id))):
        raise HTTPException(status_code=404, detail="submenu not found")
    
    result = await service.delete_record(session, service.Tables.submenu, submenu_id)

    return JSONResponse(content={'deleted': jsonable_encoder(result)})


# Обновить запись подменю
@app.patch('/api/v1/menus/{menu_id}/submenus/{submenu_id}', response_model=schemas.SubmenuSchema)
async def update_submenu(submenu_id: Annotated[UUID4, Path()],
                         submenu_in: Annotated[schemas.SubmenuUpdateCreate, Body()],
                         session: Annotated[AsyncSession, Depends(get_session)]):
    
    if await session.scalar(select(exists().where(models.Submenu.id == submenu_id))):
         return await service.update_record(session, service.Tables.submenu, submenu_in, submenu_id)

    raise HTTPException(status_code=404, detail="submenu not found")
            
     
# Определенное подменю
@app.get('/api/v1/menus/{menu_id}/submenus/{submenu_id}', response_model=schemas.SubmenuSchema)
async def get_submenu(submenu_id: Annotated[UUID4, Path()],
                      session: Annotated[AsyncSession, Depends(get_session)]):
    
    if await session.scalar(select(exists().where(models.Submenu.id == submenu_id))):
        return await service.get_specific_record(session, service.Tables.submenu, submenu_id)
       
    raise HTTPException(status_code=404, detail="submenu not found")
    

# Список подменю
@app.get('/api/v1/menus/{menu_id}/submenus', response_model=list[schemas.SubmenuSchema])
async def get_list_submenu(menu_id: Annotated[UUID4, Path()], 
                           session: Annotated[AsyncSession, Depends(get_session)]):
    return await service.get_list(session, service.Tables.submenu, menu_id)


# Добавить подменю 
@app.post('/api/v1/menus/{menu_id}/submenus', response_model=schemas.SubmenuSchema, status_code=201)
async def create_submenu(menu_id: Annotated[UUID4, Path()], 
                         submenu_in: Annotated[schemas.SubmenuUpdateCreate, Body()],
                         session: AsyncSession = Depends(get_session)):
    if await session.scalar(select(exists().where(models.Menu.id == menu_id))):
        try:
            new_submenu = service.add_record(session, service.Tables.submenu, submenu_in, menu_id)
            session.add(new_submenu)
            await session.commit()
            return new_submenu
        except IntegrityError as ex:
            await session.rollback()
            raise HTTPException(status_code=422,detail=f"The '{new_submenu.title}' is already stored!")
    
    raise HTTPException(status_code=404, detail="menu not found")



# Удалить меню
@app.delete('/api/v1/menus/{menu_id}')
async def delete_menu(menu_id: Annotated[UUID4, Path()], 
                      session: AsyncSession = Depends(get_session)):

    if not await session.scalar(select(exists().where(models.Menu.id == menu_id))):
        raise HTTPException(status_code=404 ,detail='menu not found')

    result = await service.delete_record(session, service.Tables.menu, menu_id)
    return JSONResponse(content={'deleted': jsonable_encoder(result)})


# Определенное меню
@app.get('/api/v1/menus/{menu_id}', response_model=schemas.MenuSchema)
async def get_menu(menu_id: Annotated[UUID4, Path()],
                   session: AsyncSession = Depends(get_session)):
    
    if await session.scalar(select(exists().where(models.Menu.id == menu_id))):
        return await service.get_specific_record(session, service.Tables.menu, menu_id)
    
    raise HTTPException(status_code=404, detail="menu not found")


# Список меню
@app.get('/api/v1/menus/', response_model=list[schemas.MenuSchema])
async def get_list_menu(session: AsyncSession = Depends(get_session)):
    result = await service.get_list(session)
    return result


# Добавить меню 
@app.post('/api/v1/menus/', response_model=schemas.MenuSchema, status_code=201)
async def create_menu(menu_in: schemas.MenuUpdateCreate, 
                      session: Annotated[AsyncSession, Depends(get_session)]):
    try:
        new_menu = service.add_record(session, service.Tables.menu, menu_in)
        await session.commit()
        return new_menu
    except IntegrityError as ex:
        await session.rollback()
        raise HTTPException(status_code=422, detail=f"The '{new_menu.title}' is already stored!")


# Обновить запись Меню
@app.patch('/api/v1/menus/{menu_id}', response_model=schemas.MenuSchema)
async def update_menu(menu_id: Annotated[UUID4, Path()],
                      menu_in: Annotated[schemas.MenuUpdateCreate, Body()],
                      session: AsyncSession = Depends(get_session)):

    return await service.update_record(session, service.Tables.menu, menu_in, menu_id)
