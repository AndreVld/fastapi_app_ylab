from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path
from fastapi.responses import JSONResponse
from pydantic import UUID4

from src.database.schemas import DishSchema, DishUpdateCreate

from .dish_service import DishService

router = APIRouter(
    prefix='/api/v1/menus',
    tags=['Dish']
)


@router.get('/{menu_id}/submenus/{submenu_id}/dishes', response_model=list[DishSchema | None])
async def get_list_dish(submenu_id: Annotated[UUID4, Path()],
                        dish: Annotated[DishService, Depends()]):
    return await dish.get_list_dish(submenu_id)


@router.post('/{menu_id}/submenus/{submenu_id}/dishes', response_model=DishSchema, status_code=201)
async def create_dish(submenu_id: Annotated[UUID4, Path()],
                      dish_in: Annotated[DishUpdateCreate, Body()],
                      dish: Annotated[DishService, Depends()]):
    return await dish.create(submenu_id, dish_in)


@router.get('/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=DishSchema)
async def get_dish(dish_id: Annotated[UUID4, Path()],
                   dish: Annotated[DishService, Depends()]):
    return await dish.get_by_id(dish_id)


@router.patch('/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', response_model=DishSchema)
async def update_dish(dish_id: Annotated[UUID4, Path()],
                      dish_in: Annotated[DishUpdateCreate, Body()],
                      dish: Annotated[DishService, Depends()]):
    return await dish.update(dish_id, dish_in)


@router.delete('/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
async def delete_dish(dish_id: Annotated[UUID4, Path()],
                      dish: Annotated[DishService, Depends()]):

    await dish.delete(dish_id)
    return JSONResponse(content='dish has been removed')
