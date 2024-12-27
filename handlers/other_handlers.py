import logging
import os
import re

from aiogram import Router
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ErrorEvent, ChatMemberUpdated
from dotenv import load_dotenv

from bot_init import redis
from lexicon.lexicon_ru import LEXICON_RU
from models import User
from services.create_update_user import update_or_create_user
from services.services import notify_admins

load_dotenv()
admin_ids = os.getenv('ADMIN_IDS')
location = os.getenv('LOCATION')

# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger('default')


@router.callback_query()
async def process_phrase(callback: CallbackQuery):
    await callback.message.answer(text=callback.data)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def new_member_bot(event: ChatMemberUpdated):
    """
    Обработчик события изменения статуса участника чата.

    Создает нового пользователя в базе данных или обновляет существующего.
    Также уведомляет администраторов о новых и возвращающихся пользователях.

    :param event: Событие изменения статуса участника чата.
    """
    try:
        if event.chat.type != "private":
            return  # Игнорируем если это не личный чат

        user = await User.get_or_none(id=event.from_user.id)
        if user:
            user.user_status = 'active'
            await user.save()
            # Отправляем админам информацию о новом пользователе
            await notify_admins(user, 'Пользователь снова с нами')

    except Exception as e:
        logger.error("Ошибка при обновлении информации о пользователе: %s", e)

    # user_id = event.from_user.id
    # user = await User.get_or_none(id=user_id)
    # if user is None:
    #     # Новый пользователь
    #     try:
    #         user = User(
    #             id=event.from_user.id,
    #             username=event.from_user.username,
    #             first_name=event.from_user.first_name,
    #             last_name=event.from_user.last_name,
    #         )
    #         if location == 'ja-JP':
    #             user.language = 'ru'
    #         await user.save()
    #         type_subscription = await TypeSubscription.get(name='Free trial')
    #         await Subscription.create(user=user,
    #                                   type_subscription=type_subscription,
    #                                   date_start=datetime.now(),
    #                                   date_end=datetime.now() + timedelta(days=30),
    #                                   )
    #         # Отправляем админам информацию о новом пользователе
    #         message_for_admin = (
    #             f'🤖 <b>У нас новый пользователь</b>\n'
    #             f'[id: {event.from_user.id}]\n'
    #             f'[first name: {event.from_user.first_name}]\n'
    #             f'[last name: {event.from_user.last_name}]\n'
    #             f'[username: {event.from_user.username}]\n'
    #         )
    #         for admin_id in admin_ids.split(','):
    #             await bot.send_message(chat_id=admin_id, text=message_for_admin)
    #         logger.debug(f"Пользователь {event.from_user.username} {event.from_user.first_name} "
    #                      f"{event.from_user.last_name} создан.")
    #     except Exception as e:
    #         logger.error("Ошибка при создании пользователя: %s", e)
    # else:
    #     # Пользователь вернулся
    #     try:
    #         user = await User.get(id=event.from_user.id)
    #         user.username = event.from_user.username
    #         user.first_name = event.from_user.first_name
    #         user.last_name = event.from_user.last_name
    #         user.user_status = 'active'
    #         await user.save()
    #         # Отправляем админам информацию о вернувшемся пользователе
    #         message_for_admin = (
    #             f'🤖 <b>Пользователь снова с нами</b>\n'
    #             f'[id: {event.from_user.id}]\n'
    #             f'[first name: {event.from_user.first_name}]\n'
    #             f'[last name: {event.from_user.last_name}]\n'
    #             f'[username: {event.from_user.username}]\n'
    #         )
    #         for admin_id in admin_ids.split(','):
    #             await bot.send_message(chat_id=admin_id, text=message_for_admin)
    #         logger.debug(f"Пользователь {event.from_user.username} {event.from_user.first_name} "
    #                      f"{event.from_user.last_name} обновлен.")
    #     except Exception as e:
    #         logger.error("Ошибка при обновлении информации о пользователе: %s", e)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def kick_member_bot(event: ChatMemberUpdated):
    """
    Обработчик события удаления участника чата (бота).

    Обновляет статус пользователя в базе данных как "заблокированный" и уведомляет администраторов.

    :param event: Событие изменения статуса участника чата.
    """
    try:
        user = await User.get_or_none(id=event.from_user.id)
        if user:
            user.user_status = 'blocked'
            await user.save()
            # Отправляем админам информацию о заблокированном пользователе
            await notify_admins(user, 'Пользователь заблокировал бота')
    except Exception as e:
        logger.error("Ошибка при обновлении информации о удалившемся пользователе: %s", e)


# Этот хэндлер будет срабатывать на любые сообщения
@router.message()
async def send_echo(message: Message, state: FSMContext):
    await message.reply(text=LEXICON_RU['error'])
    await state.clear()


@router.error()
async def error_handler(event: ErrorEvent):
    logger.critical("Critical error caused by %s", event.exception, exc_info=True)
    if "Context not found for intent id" in str(event.exception):
        # Извлекаем ID интента из сообщения об ошибке
        intent_id_match = re.search(r'intent id: (\w+)', str(event.exception))
        if intent_id_match:
            intent_id = intent_id_match.group(1)

            # Поиск и удаление ключа в Redis
            async for key in redis.scan_iter("*"):
                value = await redis.get(key)
                if value and intent_id.encode() in value:
                    await redis.delete(key)
                    logger.info(f"Удален ключ из Redis: {key}")
                    break
            else:
                logger.warning(f"Ключ для intent id {intent_id} не найден в Redis")

