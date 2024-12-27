import logging
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv

from models import User, TypeSubscription, Subscription
from services.services import notify_admins

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


# async def update_or_create_user(message) -> None:
#     user = await User.get_or_none(id=message.from_user.id)
#     if user is None:
#         # Новый пользователь
#         try:
#             user = User(
#                 id=message.from_user.id,
#                 username=message.from_user.username,
#                 first_name=message.from_user.first_name,
#                 last_name=message.from_user.last_name,
#             )
#             if location == 'ja-JP':
#                 user.language = 'ru'
#             await user.save()
#             type_subscription = await TypeSubscription.get(name='Free trial')
#             await Subscription.create(user=user,
#                                       type_subscription=type_subscription,
#                                       date_start=datetime.now(),
#                                       date_end=datetime.now() + timedelta(days=30),
#                                       )
#             # Отправляем админам информацию о новом пользователе
#             message_for_admin = (
#                 f'🤖 <b>У нас новый пользователь</b>\n'
#                 f'[id: {message.from_user.id}]\n'
#                 f'[first name: {message.from_user.first_name}]\n'
#                 f'[last name: {message.from_user.last_name}]\n'
#                 f'[username: {message.from_user.username}]\n'
#             )
#             for admin_id in admin_ids.split(','):
#                 await bot.send_message(chat_id=admin_id, text=message_for_admin)
#             logger.debug(f"Пользователь {message.from_user.username} {message.from_user.first_name} "
#                          f"{message.from_user.last_name} создан.")
#         except Exception as e:
#             logger.error("Ошибка при создании пользователя: %s", e)
#     else:
#         # Пользователь вернулся
#         try:
#             # user = await User.get(id=message.from_user.id)
#             user.username = message.from_user.username
#             user.first_name = message.from_user.first_name
#             user.last_name = message.from_user.last_name
#             await user.save()
#             logger.debug(f"Пользователь {message.from_user.username} {message.from_user.first_name} "
#                          f"{message.from_user.last_name} обновлен.")
#         except Exception as e:
#             logger.error("Ошибка при обновлении информации о пользователе: %s", e)


async def update_or_create_user(message):
    """
    Обновляет информацию о пользователе или создаёт нового, если он отсутствует в базе.

    :param message: Объект сообщения или события изменения статуса участника чата.
    """
    user_id = message.from_user.id
    user = await User.get_or_none(id=user_id)

    if user is None:
        # Новый пользователь
        try:
            user = User(
                id=user_id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language='ru' if location == 'ja-JP' else 'en'
            )
            await user.save()

            # Создание пробной подписки
            type_subscription = await TypeSubscription.get(name='Free trial')
            await Subscription.create(
                user=user,
                type_subscription=type_subscription,
                date_start=datetime.now(),
                date_end=datetime.now() + timedelta(days=30)
            )

            # Уведомление администраторов о новом пользователе
            await notify_admins(user, 'У нас новый пользователь')
            logger.debug(f"Пользователь {user.username} создан.")
        except Exception as e:
            logger.error(f"Ошибка при создании пользователя [id: {user_id}]: {e}")
    else:
        # Обновляем данные пользователя
        try:
            user.username = message.from_user.username
            user.first_name = message.from_user.first_name
            user.last_name = message.from_user.last_name
            user.user_status = 'active'
            await user.save()

            logger.debug(f"Пользователь {user.username} обновлён.")
        except Exception as e:
            logger.error(f"Ошибка при обновлении информации о пользователе [id: {user_id}]: {e}")
