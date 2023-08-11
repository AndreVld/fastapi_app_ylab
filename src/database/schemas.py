from decimal import Decimal

from pydantic import UUID4, BaseModel


class MenuUpdateCreate(BaseModel):
    title: str
    description: str = ''


class MenuSchema(MenuUpdateCreate):
    id: UUID4 = None
    submenus_count: int = 0
    dishes_count: int = 0


class SubmenuUpdateCreate(BaseModel):
    title: str
    description: str = ''


class SubmenuSchema(SubmenuUpdateCreate):
    id: UUID4 = None
    menu_id: UUID4
    dishes_count: int = 0


class DishUpdateCreate(BaseModel):
    title: str
    description: str = ''
    price: Decimal


class DishSchema(DishUpdateCreate):
    id: UUID4
    submenu_id: UUID4


class SubmenuDish(SubmenuUpdateCreate):
    id: UUID4
    menu_id: UUID4
    dishes: list[DishSchema | None]


class AllMenu(MenuUpdateCreate):
    id: UUID4
    submenus: list[SubmenuDish | None]
