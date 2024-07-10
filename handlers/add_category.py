import logging

from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Group, Cancel

from models import Category
from services.i18n_format import I18NFormat, I18N_FORMAT_KEY
from states import AddCategorySG

logger = logging.getLogger('default')


async def category_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                         category_name: str) -> None:
    user_id = dialog_manager.event.from_user.id
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    category = await Category.get_or_none(name=category_name, user_id=user_id)
    if category:
        await message.answer(i18n_format('you-already-have-category'))
    else:
        try:
            await Category.create(name=category_name, user_id=user_id)
        except Exception as e:
            await message.answer(i18n_format('error-adding-category'))
            logger.error(f'Ошибка добавления категории: {e}')
        else:
            await message.answer(i18n_format('category-added-successfully'))

    await dialog_manager.done()


add_category_dialog = Dialog(
    Window(
        I18NFormat('enter-name-new-category'),
        TextInput(
            id='category_input',
            on_success=category_input,
        ),
        Group(
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            width=3
        ),
        state=AddCategorySG.start,
    ),
)
