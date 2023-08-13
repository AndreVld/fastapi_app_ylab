from database.base import async_session
from openpyxl import open
import re
import asyncio
from sqlalchemy import exists, select, update, delete
from src.database.models import Dish, Menu, Submenu
from sqlalchemy.exc import IntegrityError


class ExcelDBLoader:

    def __init__(self) -> None:
        self.exel_file = '/fastapi_app/admin/Menu.xlsx'
        self.async_session = async_session
        self.uuid_pattern = re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$')
        self.model_menu = Menu
        self.model_submenu = Submenu
        self.model_dish = Dish

    def _parse_data(self) -> dict:
        '''Parses data from the Excel file into structured dictionaries'''
        sheet = open(self.exel_file, read_only=True).active

        data = {
            'list_menu': [],
            'list_subm': [],
            'list_dish': [],
        }

        for row in range(1, sheet.max_row):
            if menu_id:= sheet[row][0].value:
                # Extracts menu data from the Excel sheet
                menu = sheet[row][1].value
                menu_descrtiprion = sheet[row][2].value
                data['list_menu'].append({'id': menu_id,
                                          'title': menu,
                                          'description': menu_descrtiprion,})
                menu_id_for_submenu = menu_id
                continue
            submenu_id = sheet[row][1].value
            if submenu_id and self.uuid_pattern.match(submenu_id):
                # Extracts submenu data from the Excel sheet
                submenu = sheet[row][2].value
                submenu_description = sheet[row][3].value
                data['list_subm'].append({'id': submenu_id,
                                          'title': submenu,
                                          'description': submenu_description,
                                          'menu_id': menu_id_for_submenu})
                submenu_id_for_dish = submenu_id
                continue
            dish_id = sheet[row][2].value
            if dish_id and self.uuid_pattern.match(dish_id):
                # Extracts dishes data from the Excel sheet
                dish = sheet[row][3].value
                description_dish = sheet[row][4].value
                price = sheet[row][5].value
                data['list_dish'].append({'id': dish_id,
                                          'title': dish,
                                          'description': description_dish,
                                          'price': price,
                                          'submenu_id': submenu_id_for_dish})
            
            if not menu_id and not submenu_id and not dish_id:
                break

        return data

    async def _check_exist(self, model: Menu | Submenu | Dish, id: str) -> bool:
        ''' Checks if a record with the given ID exists in the database'''
        async with self.async_session() as session: 
            return await session.scalar(select(exists().where(model.id == id)))
    
    async def get_deleted_ids_from_excel(self, model: Menu | Submenu | Dish, list_items: list) -> set:
        '''Retrieves IDs of records that are in the database but not in the Excel file'''
        async with self.async_session() as session:
            set_id_from_db = set(await session.scalars(select(model.id)))

        set_id_from_excel = set([item['id'] for item in list_items])
        return set_id_from_db - set_id_from_excel

    async def delete_record(self, model: Menu | Submenu | Dish, list_id: list) -> None:
        '''Deletes records from the database based on a list of IDs'''
        async with self.async_session() as session:
            for deleted_record_id in list_id:
                await session.execute(delete(model).where(model.id == deleted_record_id))
                await session.commit()

    async def update_record(self, model: Menu | Submenu | Dish, data: dict) -> None:
        '''Updates a record in the database with new data'''
        async with self.async_session() as session:
            await session.scalar(update(model).where(model.id == data['id']).values(**data))


    async def create_record(self, model: Menu | Submenu | Dish, data: dict) -> None:
        '''Creates a new record in the database with the provided data'''
        async with self.async_session() as session:
            try:
                new_record = model(**data)
                session.add(new_record)
                await session.commit()
            except IntegrityError:
                await session.rollback()


    async def add_data_to_database(self)-> None:
        '''Parses Excel data and updates/creates records in the database'''
        data = await asyncio.to_thread(self._parse_data)
        list_menu = data['list_menu']
        list_subm = data['list_subm']
        list_dish = data['list_dish']


        if deleted_menu_from_excel:=await self.get_deleted_ids_from_excel(self.model_menu, list_menu):
            await self.delete_record(self.model_menu, deleted_menu_from_excel)
            
        for menu in list_menu:
            if await self._check_exist(self.model_menu, menu['id']):
                await self.update_record(self.model_menu, menu)
                
            await self.create_record(self.model_menu, menu)


        if deleted_submenu_from_excel:= await self.get_deleted_ids_from_excel(self.model_submenu, list_subm):
            await self.delete_record(self.model_submenu, deleted_submenu_from_excel)

        for submenu in list_subm:
            if await self._check_exist(self.model_submenu, submenu['id']):
                await self.update_record(self.model_submenu, submenu)

            await self.create_record(self.model_submenu, submenu)

        if deleted_dish_from_excel:= await self.get_deleted_ids_from_excel(self.model_dish, list_dish):
            await self.delete_record(self.model_dish, deleted_dish_from_excel)

        for dish in list_dish:
            if await self._check_exist(self.model_dish, dish['id']):
                await self.update_record(self.model_dish, dish)

            await self.create_record(self.model_dish, dish)
