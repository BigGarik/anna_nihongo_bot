import logging
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv

from bot_init import bot
from models import User, TypeSubscription, Subscription

logger = logging.getLogger('default')

load_dotenv()
location = os.getenv('LOCATION')
admin_ids = os.getenv('ADMIN_IDS')


# async def create_user(message) -> None:
    # try:
    #     user = User(
    #         id=message.from_user.id,
    #         username=message.from_user.username,
    #         first_name=message.from_user.first_name,
    #         last_name=message.from_user.last_name,
    #     )
    #     if location == 'ja-JP':
    #         user.language = 'ru'
    #     await user.save()
    #     type_subscription = await TypeSubscription.get(name='Free trial')
    #     await Subscription.create(user=user,
    #                               type_subscription=type_subscription,
    #                               date_start=datetime.now(),
    #                               date_end=datetime.now() + timedelta(days=30),
    #                               )
    #     logger.debug(f"Пользователь {message.from_user.username} {message.from_user.first_name} "
    #                  f"{message.from_user.last_name} создан.")
    # except Exception as e:
    #     logger.error("Ошибка при создании пользователя: %s", e)


async def update_user_info(message) -> None:
    try:
        user = await User.get(id=message.from_user.id)
        user.username = message.from_user.username
        user.first_name = message.from_user.first_name
        user.last_name = message.from_user.last_name
        await user.save()
        logger.debug(f"Пользователь {message.from_user.username} {message.from_user.first_name} "
                     f"{message.from_user.last_name} обновлен.")
    except Exception as e:
        logger.error("Ошибка при обновлении информации о пользователе: %s", e)
