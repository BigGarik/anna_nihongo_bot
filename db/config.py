from tortoise import Tortoise


async def init(db_url):
    await Tortoise.init(
        db_url=db_url,
        modules={'models': ['models.user', 'models.phrase', 'models.tts']}
    )
    await Tortoise.generate_schemas()

