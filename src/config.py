import os
from enum import Enum

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')

DB_HOST_TEST = os.environ.get('DB_HOST_TEST')
DB_PORT_TEST = os.environ.get('DB_PORT_TEST')
DB_NAME_TEST = os.environ.get('DB_NAME_TEST')
DB_USER_TEST = os.environ.get('DB_USER_TEST')
DB_PASS_TEST = os.environ.get('DB_PASS_TEST')

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')
EXPIRATION = 355


class Keys(Enum):
    key_submenu_list_prefix = 'submenu_for_menu:'
    key_prefix_submenu = 'submenu:'
    key_prefix_menu = 'menu:'
    key_menu_list = 'list_menu'
    key_dish_list_prefix = 'dishes_for_submenu:'
    key_dish_prefix = 'dish:'
    key_all_menu = 'all_menu'
