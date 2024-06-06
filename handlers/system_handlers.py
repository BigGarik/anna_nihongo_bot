import os

from aiogram.types import User, CallbackQuery
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button

from .states import UserStartDialogSG


async def username_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    # Получение списка разрешенных ID пользователей из переменной окружения
    admin_ids = os.getenv('ADMIN_IDS')
    # Преобразование строки в список целых чисел
    admin_ids = [int(user_id) for user_id in admin_ids.split(',')]
    response = {'username': event_from_user.first_name or event_from_user.username}
    if event_from_user.id in admin_ids:
        response['is_admin'] = True
    else:
        response['is_admin'] = False
    return response


async def main_page_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=UserStartDialogSG.start)
