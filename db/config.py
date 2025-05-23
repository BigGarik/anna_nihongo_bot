import os

from dotenv import load_dotenv
from tortoise import Tortoise

load_dotenv()
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
database = os.getenv('DATABASE')
db_url = f'postgres://{db_user}:{db_password}@{db_host}:{db_port}/{database}'

TORTOISE_ORM = {
    "connections": {
        "default": db_url,
    },
    "apps": {
        "models": {
            "models": ['models.user', 'models.phrase', 'models.tts', 'aerich.models', 'models.payments',
                       'models.subscription', 'models.main'],
            "default_connection": "default",
        },
    },
}


async def init_db():
    # Инициализируем Tortoise ORM с использованием URL базы данных и указанием модулей моделей
    await Tortoise.init(config=TORTOISE_ORM)

    # Генерируем схемы базы данных на основе моделей
    await Tortoise.generate_schemas()
