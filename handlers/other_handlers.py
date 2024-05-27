import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from lexicon.lexicon_ru import LEXICON_RU

# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger(__name__)


@router.callback_query()
async def process_phrase(callback: CallbackQuery):
    await callback.message.answer(text=callback.data)


# Этот хэндлер будет срабатывать на любые сообщения
@router.message()
async def send_echo(message: Message, state: FSMContext):
    await message.reply(text=LEXICON_RU['error'])
    await state.clear()
