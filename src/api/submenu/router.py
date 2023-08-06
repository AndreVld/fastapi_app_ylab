from fastapi import APIRouter, Depends, Path, Body
from typing import Annotated
from fastapi.responses import JSONResponse
from .repositories import SubmenuRepository 
from src.database.schemas import SubmenuSchema, SubmenuUpdateCreate
from pydantic import UUID4


router = APIRouter(
    prefix='/api/v1/menus',
    tags=['Submenu']
)


@router.get('/{menu_id}/submenus', response_model=list[SubmenuSchema | None])
async def get_list_submenu(menu_id: Annotated[UUID4, Path()], 
                           submenu : Annotated[SubmenuRepository, Depends()]):
    return await submenu.get_list_submenu(menu_id)


@router.post('/{menu_id}/submenus', response_model=SubmenuSchema, status_code=201)
async def create_submenu(menu_id: Annotated[UUID4, Path()], 
                         submenu_in: Annotated[SubmenuUpdateCreate, Body()],
                         submenu : Annotated[SubmenuRepository, Depends()]):
    return await submenu.create(menu_id, submenu_in)


@router.get('/{menu_id}/submenus/{submenu_id}', response_model=SubmenuSchema)
async def get_submenu(submenu_id: Annotated[UUID4, Path()],
                      submenu : Annotated[SubmenuRepository, Depends()]):
    return await submenu.get_by_id(submenu_id)


@router.patch('/{menu_id}/submenus/{submenu_id}', response_model=SubmenuSchema)
async def update_submenu(submenu_id: Annotated[UUID4, Path()],
                         submenu_in: Annotated[SubmenuUpdateCreate, Body()],
                         submenu : Annotated[SubmenuRepository, Depends()]):
    return await submenu.update(submenu_id, submenu_in)


@router.delete('/{menu_id}/submenus/{submenu_id}')
async def delete_submenu(submenu_id: Annotated[UUID4, Path()], 
                         submenu : Annotated[SubmenuRepository, Depends()]):

    await submenu.delete(submenu_id)
    return JSONResponse(content='submenu has been removed')
