from fastapi import APIRouter, Depends, Path, Body
from typing import Annotated
from fastapi.responses import JSONResponse
from .repositories import MenuRepository
from src.database.schemas import MenuSchema, MenuUpdateCreate
from pydantic import UUID4


router = APIRouter(
    prefix='/api/v1/menus',
    tags=['Menu']
)


@router.delete('/{menu_id}')
async def delete_menu(menu_id: Annotated[UUID4, Path()],
                      menu : Annotated[MenuRepository, Depends()]): 
    await menu.delete(menu_id)
    return JSONResponse(content='menu has been removed',)


@router.get('/', response_model=list[MenuSchema | None])
async def get_list_menu(menu : Annotated[MenuRepository, Depends()]):
    '''Get menu list with the number of submenus and dishes'''
    return await menu.get_list_menu()


@router.get('/{menu_id}', response_model=MenuSchema)
async def get_menu(menu_id: Annotated[UUID4, Path()],
                   menu : Annotated[MenuRepository, Depends()]):
    """Get menu with the number of submenus and dishes"""
    return await menu.get_by_id(menu_id)
    

@router.post('/', response_model=MenuSchema, status_code=201)
async def create_menu(menu : Annotated[MenuRepository, Depends()],
                      menu_in: Annotated[MenuUpdateCreate, Body()]):
    return await menu.create(menu_in)


@router.patch('/{menu_id}', response_model=MenuSchema)
async def update_menu(menu_id: Annotated[UUID4, Path()],
                      menu : Annotated[MenuRepository, Depends()],
                      menu_in: Annotated[MenuUpdateCreate, Body()]):
    return await menu.update(menu_id=menu_id, data=menu_in)
