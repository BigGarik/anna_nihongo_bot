import logging
import os
import re

from aiogram import Router, Bot
from aiogram.filters import ChatMemberUpdatedFilter, KICKED
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ErrorEvent, ChatMemberUpdated
from dotenv import load_dotenv

from bot_init import redis
from lexicon.lexicon_ru import LEXICON_RU

load_dotenv()
admin_ids = os.getenv('ADMIN_IDS')

# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger('default')


@router.callback_query()
async def process_phrase(callback: CallbackQuery):
    await callback.message.answer(text=callback.data)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def kick_member_bot(event: ChatMemberUpdated, bot: Bot):
    message_for_admin = (
        f'🤖 <b>Пользователь заблокировал бота</b>\n'
        f'[id: {event.from_user.id}]\n'
        f'[first name: {event.from_user.first_name}]\n'
        f'[last name: {event.from_user.last_name}]\n'
        f'[username: {event.from_user.username}]\n'
    )
    for admin_id in admin_ids.split(','):
        await bot.send_message(chat_id=admin_id, text=message_for_admin)


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

