from pydantic import BaseModel, UUID4
from decimal import Decimal


class MenuUpdateCreate(BaseModel):
    title: str
    description: str = None

class MenuSchema(MenuUpdateCreate):
    id: UUID4 = None
    submenus_count : int = 0
    dishes_count : int = 0

class SubmenuUpdateCreate(BaseModel):
    title: str
    description: str = None

class SubmenuSchema(SubmenuUpdateCreate):
    id: UUID4 = None
    menu_id: UUID4
    dishes_count : int = 0

class DishUpdateCreate(BaseModel):
    title: str
    description: str = None
    price: Decimal
    
class DishSchema(DishUpdateCreate):
    id: UUID4
    submenu_id: UUID4
