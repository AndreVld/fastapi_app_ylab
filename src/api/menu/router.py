from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse
from pydantic import UUID4

from src.database.schemas import MenuSchema, MenuUpdateCreate

from .menu_service import MenuService

router = APIRouter(
    prefix='/api/v1/menus',
    tags=['Menu']
)


@router.delete('/{menu_id}')
async def delete_menu(menu_id: Annotated[UUID4, Path()],
                      menu: Annotated[MenuService, Depends()]):
    await menu.delete(menu_id)
    return JSONResponse(content='menu has been removed',)


@router.get('/', )
async def get_list_menu(menu: Annotated[MenuService, Depends()]):
    '''Get menu list with the number of submenus and dishes'''
    return await menu.get_list_menu()


@router.get('/{menu_id}', response_model=MenuSchema)
async def get_menu(menu_id: Annotated[UUID4, Path()],
                   menu: Annotated[MenuService, Depends()]):
    """Get menu with the number of submenus and dishes"""
    return await menu.get_by_id(menu_id)


@router.post('/', response_model=MenuSchema, status_code=201)
async def create_menu(menu: Annotated[MenuService, Depends()],
                      menu_in: Annotated[MenuUpdateCreate, Body()]):
    return await menu.create(menu_in)


@router.patch('/{menu_id}', response_model=MenuSchema)
async def update_menu(menu_id: Annotated[UUID4, Path()],
                      menu: Annotated[MenuService, Depends()],
                      menu_in: Annotated[MenuUpdateCreate, Body()]):
    return await menu.update(menu_id, menu_in)
