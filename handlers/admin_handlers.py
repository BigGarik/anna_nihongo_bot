import logging

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Cancel, Start
from aiogram_dialog.widgets.text import Const

from bot_init import redis, bot
from models import User
from states import AddOriginalPhraseSG, AdminDialogSG

# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger(__name__)

admin_dialog = Dialog(
    Window(
        Const('Админка'),

        Start(Const('🆕 Добавить оригинальную фразу'),
              id='go_add_original_phrase_dialog',
              state=AddOriginalPhraseSG.text_phrase
              ),
        Cancel(Const('↩️ Отмена'), id='button_cancel'),
        state=AdminDialogSG.start,
    ),
)


@router.callback_query(F.data.startswith('confirm_access:'))
async def process_confirm_access(callback: CallbackQuery):
    # Извлекаем уникальный идентификатор запроса из callback_data
    _, request_id = callback.data.split(':')
    # Извлекаем данные пользователя из Redis
    user_data = await redis.hgetall(f"access_request:{request_id}")

    if user_data:
        user_data_decoded = {key.decode(): value.decode() for key, value in user_data.items()}
        user_id_str = user_data_decoded.get("user_id")
        if user_id_str:
            user_id = int(user_id_str)  # Преобразуем user_id в int
            username = user_data_decoded.get("username")
            first_name = user_data_decoded.get("first_name")
            last_name = user_data_decoded.get("last_name")

            # Создать пользователя в базе данных если еще нет
            user = await User.filter(id=user_id).first()
            if not user:
                await User.create(id=user_id, username=username,
                                  first_name=first_name, last_name=last_name)

            await bot.send_message(user_id, "Ваш запрос на доступ подтвержден.\nНажмите /start для начала обучения")
        else:
            # Обработка случая, когда user_id не найден в user_data
            await callback.answer("Ошибка: ID пользователя не найден.", show_alert=True)
    else:
        # Обработка случая, когда данные пользователя не найдены в Redis
        await callback.answer("Ошибка: данные запроса на доступ не найдены.", show_alert=True)

    # удалить запись из Redis
    await redis.delete(f"access_request:{request_id}")
    await callback.message.delete()
    # await bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)


@router.callback_query(F.data.startswith('cancel_access:'))
async def process_cancel_access(callback: CallbackQuery):
    # Извлекаем уникальный идентификатор запроса из callback_data
    _, request_id = callback.data.split(':')
    await redis.delete(f"access_request:{request_id}")
    await callback.message.delete()
    await callback.answer("Запрос отменён.", show_alert=True)
