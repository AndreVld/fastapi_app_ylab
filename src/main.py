
from fastapi import FastAPI
from src.api.menu.router import router as menu_router
from src.api.submenu.router import router as submenu_router
from src.api.dish.router import router as dish_router


app = FastAPI()
app.include_router(menu_router)
app.include_router(submenu_router)
app.include_router(dish_router)
