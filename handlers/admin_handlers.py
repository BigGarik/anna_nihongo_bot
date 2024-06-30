import logging

from aiogram import Router
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Start, Button, Group, Back, Next
from aiogram_dialog.widgets.text import Const

from models import Category
from models.main import MainPhoto
from states import AdminDialogSG, UserManagementSG

# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger(__name__)


async def category_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                         category: str) -> None:
    user_id = dialog_manager.event.from_user.id
    await Category.create(name=category, user_id=user_id, public=True)
    await dialog_manager.back()


async def add_main_image(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(state=AdminDialogSG.add_main_image)


async def main_image_input(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    image_id = message.photo[-1].file_id
    photo = await MainPhoto.get_or_none(id=1)
    if photo:
        photo.tg_id = image_id
        await photo.save()
    else:
        await MainPhoto.create(tg_id=image_id)
    await dialog_manager.done()


admin_dialog = Dialog(
    Window(
        Const('Админка'),
        Start(Const('🧑‍🤝‍🧑 Управление пользователями'),
              id='start_user_management_dialog',
              state=UserManagementSG.start
              ),
        Next(text=Const('🆕 Добавить общую категорию')),
        Button(
            text=Const(text='Добавить главное изображение'),
            id='button_add_main_image',
            on_click=add_main_image
        ),
        # Cancel(Const('↩️ Отмена'), id='button_cancel'),
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
            width=3
        ),
        state=AdminDialogSG.add_category,
    ),
    Window(
        Const(text='Добавить главное изображение'),
        MessageInput(
            func=main_image_input,
            content_types=ContentType.PHOTO,
        ),
        Group(
            Back(Const('◀️ Назад'), id='back'),
            width=3
        ),
        state=AdminDialogSG.add_main_image,
    ),
)


@router.message(lambda message: message.text in ["⚙️ Настройки(для админов)", "⚙️ Settings (for admins)"])
async def process_admin_settings(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=AdminDialogSG.start)
