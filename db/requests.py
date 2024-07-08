import logging

from tortoise.exceptions import IntegrityError

from models import User

logger = logging.getLogger(__name__)


async def add_user(user_id: int, username: str, first_name: str, last_name: str):
    try:
        await User.create(id=user_id, username=username, first_name=first_name, last_name=last_name)
    except IntegrityError as e:
        logger.error("Пользователь с таким username уже существует. ", e)


async def get_user_ids() -> list:
    user_ids = await User.all().values_list('id', flat=True)
    return user_ids
