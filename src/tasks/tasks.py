from celery import Celery
from database.service import ExcelDBLoader
import asyncio
from config import SCHEDULE

celery_app = Celery('tasks', broker='pyamqp://guest@rabbitmq//')


celery_app.conf.beat_schedule = {
    'execute_task_every_15_seconds': {
        'task': 'tasks.tasks.exeldb', 
        'schedule': SCHEDULE,
    },
}

@celery_app.task
def exeldb():
    loop = asyncio.get_event_loop()
    exel_db = ExcelDBLoader()

    async def add_data():
        await exel_db.add_data_to_database()

    loop.run_until_complete(add_data())
