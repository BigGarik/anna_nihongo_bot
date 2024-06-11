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
            "models": ['models.user', 'models.phrase', 'models.tts', "aerich.models"],
            "default_connection": "default",
        },
    },
}


async def init():
    # Инициализируем Tortoise ORM с использованием URL базы данных и указанием модулей моделей
    await Tortoise.init(config=TORTOISE_ORM)

    # Генерируем схемы базы данных на основе моделей
    await Tortoise.generate_schemas()


# async def init():
#     await Tortoise.init(
#         db_url=db_url,
#         modules={'models': ['models.user', 'models.phrase', 'models.tts']}
#     )
#     await Tortoise.generate_schemas()
