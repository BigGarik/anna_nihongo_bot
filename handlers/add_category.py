from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Group, Cancel
from aiogram_dialog.widgets.text import Const

from models import Category
from states import AddCategorySG


async def category_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                         category: str) -> None:
    # Добавить категорию в dialog_data
    user_id = dialog_manager.event.from_user.id
    await Category.create(name=category, user_id=user_id)
    await dialog_manager.done()


add_category_dialog = Dialog(
    Window(
        Const(text='Введи название новой категории:'),
        TextInput(
            id='category_input',
            on_success=category_input,
        ),
        Group(
            Cancel(Const('↩️ Отмена'), id='button_cancel'),
            width=3
        ),
        state=AddCategorySG.start,
    ),
)
