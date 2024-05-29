import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message


# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger(__name__)


# Этот хэндлер срабатывает на команду /settings
@router.message(Command(commands='settings'), F.from_user.id.in_({815174734, 693131974}))
async def process_settings_command(message: Message):
    await message.answer(text='/settings')
