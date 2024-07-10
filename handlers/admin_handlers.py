import base64
import logging
import os

from aiogram import Router
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Start, Button, Group, Back, Next

from external_services.kandinsky import generate_image
from handlers.system_handlers import getter_prompt, repeat_ai_generate_image
from models import Category
from models.main import MainPhoto
from services.i18n_format import I18NFormat, I18N_FORMAT_KEY, default_format_text
from states import AdminDialogSG, UserManagementSG

# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger(__name__)


async def category_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                         category: str) -> None:
    user_id = dialog_manager.event.from_user.id
    await Category.create(name=category, user_id=user_id, public=True)
    await dialog_manager.back()


async def go_start_window(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(state=AdminDialogSG.start)


async def go_generate_image(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(state=AdminDialogSG.generate_image)


async def ai_generate_image(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, prompt: str):
    dialog_manager.dialog_data['prompt'] = prompt
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    await message.answer(text=i18n_format("starting-generate-image"))
    # Генерируем изображение
    try:
        images = generate_image(prompt)
        if images and len(images) > 0:
            image_data = base64.b64decode(images[0])
            image = BufferedInputFile(image_data, filename="image.png")
            await message.answer_photo(photo=image, caption=i18n_format("generated-image"))
        else:
            await message.answer(i18n_format("failed-generate-image"))
        # await dialog_manager.show(show_mode=ShowMode.SEND)
    except Exception as e:
        logger.error('Ошибка при генерации изображения: %s', e)
        await message.answer(text=i18n_format("failed-generate-image"))
        # await dialog_manager.show(show_mode=ShowMode.SEND)


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
        I18NFormat('admin-panel'),
        Start(I18NFormat('user-management'),
              id='start_user_management_dialog',
              state=UserManagementSG.start
              ),
        Next(text=I18NFormat('add-general-category')),
        Button(
            text=I18NFormat('generate-image-button'),
            id='generate_image_button',
            on_click=go_generate_image
        ),
        Button(
            text=I18NFormat('add-main-image'),
            id='button_add_main_image',
            on_click=add_main_image
        ),
        state=AdminDialogSG.start,
    ),
    Window(
        I18NFormat(text='Введи название общей категории:'),
        TextInput(
            id='category_input',
            on_success=category_input,
        ),
        Group(
            Button(
                I18NFormat('back'),
                id='go_start_window',
                on_click=go_start_window
            ),
            # Back(I18NFormat('back'), id='back'),
            width=3
        ),
        state=AdminDialogSG.add_category,
    ),
    Window(
        I18NFormat('generate-image-dialog'),
        TextInput(
            id='prompt_for_image',
            on_success=ai_generate_image,
        ),
        Group(
            Button(
                I18NFormat('back'),
                id='go_start_window',
                on_click=go_start_window
            ),
            Button(
                I18NFormat('repeat'),
                id='repeat_generate_image_button',
                on_click=repeat_ai_generate_image,
                when='is_prompt',
            ),
            width=3
        ),
        state=AdminDialogSG.generate_image,
        getter=getter_prompt
    ),
    Window(
        I18NFormat('add-main-image'),
        MessageInput(
            func=main_image_input,
            content_types=ContentType.PHOTO,
        ),
        Group(
            Button(
                I18NFormat('back'),
                id='go_start_window',
                on_click=go_start_window
            ),
            # Back(I18NFormat('back'), id='back'),
            width=3
        ),
        state=AdminDialogSG.add_main_image,
    ),
)


@router.message(lambda message: message.text in ["⚙️ Настройки(для админов)", "⚙️ Settings (for admins)"])
async def process_admin_settings(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=AdminDialogSG.start)
