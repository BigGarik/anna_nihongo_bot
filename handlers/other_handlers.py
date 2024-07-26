import logging
import re

from aiogram import Router
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, Update, ErrorEvent

from bot_init import redis
from lexicon.lexicon_ru import LEXICON_RU

# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger('default')


@router.callback_query()
async def process_phrase(callback: CallbackQuery):
    await callback.message.answer(text=callback.data)


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
            for key in redis.scan_iter("*"):
                value = redis.get(key)
                if value and intent_id.encode() in value:
                    redis.delete(key)
                    logger.info(f"Удален ключ из Redis: {key}")
                    break
            else:
                logger.warning(f"Ключ для intent id {intent_id} не найден в Redis")

