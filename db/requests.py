from tortoise import Tortoise, run_async
from tortoise.exceptions import IntegrityError

from models import User


async def add_user(user_id: int, username: str, first_name: str, last_name: str):
    try:
        await User.create(id=user_id, username=username, first_name=first_name, last_name=last_name)
    except IntegrityError:
        print("Пользователь с таким username уже существует.")


async def get_user_ids() -> list:
    user_ids = await User.all().values_list('id', flat=True)
    return user_ids

