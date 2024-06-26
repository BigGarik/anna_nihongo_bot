import logging

from aiogram import Router
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Start, Button, Group, Back, Next
from aiogram_dialog.widgets.text import Const

from handlers import main_page_button_clicked
from models import Category
from states import AdminDialogSG, UserManagementSG

# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger(__name__)


async def category_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                         category: str) -> None:
    user_id = dialog_manager.event.from_user.id
    await Category.create(name=category, user_id=user_id, public=True)
    await dialog_manager.back()


admin_dialog = Dialog(
    Window(
        Const('Админка'),
        Start(Const('🧑‍🤝‍🧑 Управление пользователями'),
              id='user_management_dialog',
              state=UserManagementSG.start
              ),
        Next(text=Const('🆕 Добавить общую категорию')),
        # Cancel(Const('↩️ Отмена'), id='button_cancel'),
        Button(
            text=Const('🏠 На главную'),
            id='main_page',
            on_click=main_page_button_clicked,
        ),
        state=AdminDialogSG.start,
    ),
    Window(
        Const(text='Введи название общей категории:'),
        TextInput(
            id='category_input',
            on_success=category_input,
        ),
        Group(
            Back(Const('◀️ Назад'), id='back'),
            Button(
                text=Const('🏠 На главную'),
                id='main_page',
                on_click=main_page_button_clicked,
            ),
            width=3
        ),
        state=AdminDialogSG.add_category,
    ),
)
