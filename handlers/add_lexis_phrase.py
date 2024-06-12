import base64
import os

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select, Group, Cancel, Next, Back
from aiogram_dialog.widgets.text import Const, Format, Multi
from tortoise import fields, models
from bot_init import bot
from external_services.google_cloud_services import google_text_to_speech
from external_services.openai_services import openai_gpt_add_space, openai_gpt_translate
from handlers import main_page_button_clicked
from handlers.states import AddPhraseSG
from models import Category, Phrase, User, AudioFile


# Функция для динамического создания кнопок с категориями
async def get_user_categories(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    categories = await Category.filter(user__id=user_id).distinct().all()

    items = [(category.name, str(category.id)) for category in categories]
    return {'categories': items}


async def get_current_category(dialog_manager: DialogManager, **kwargs):
    category_name = dialog_manager.dialog_data['category']
    return {'category': category_name}


# Хэндлер для выбора категории
async def category_selection(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    category = await Category.get_or_none(id=item_id)
    dialog_manager.dialog_data['category'] = category.name
    await dialog_manager.next()


# Хэндлер для ввода новой категории
async def category_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    user_id = dialog_manager.event.from_user.id
    category = await Category.create(name=text, user_id=user_id)
    dialog_manager.dialog_data['category'] = category.name
    await dialog_manager.next()


# Хэндлер для ввода текста фразы
async def phrase_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text_phrase: str):
    category_name = dialog_manager.dialog_data['category']
    category = await Category.get(name=category_name)
    spaced_phrase = openai_gpt_add_space(text_phrase)

    translation = openai_gpt_translate(text_phrase)

    text_to_speech = google_text_to_speech(text_phrase)
    audio = await AudioFile.create(audio=text_to_speech.audio_content)

    user_id = dialog_manager.event.from_user.id
    user = await User.get_or_none(id=user_id)

    await Phrase.create(
        category=category,
        text_phrase=text_phrase,
        spaced_phrase=spaced_phrase,
        translation=translation,
        audio=audio,
        user=user
    )
    await message.answer('Фраза добавлена! ✅')
    # await dialog_manager.done()


# Описание диалога
add_lexis_phrase_dialog = Dialog(
    Window(
        Const(text='Выберите категорию или добавьте новую:'),
        Group(
            Select(
                Format('{item[0]}'),
                id='category',
                item_id_getter=lambda x: x[1],
                items='categories',
                on_click=category_selection,
            ),
            width=2
        ),
        TextInput(
            id='category_input',
            on_success=category_input,
        ),
        Group(
            Cancel(Const('❌ Отмена'), id='button_cancel'),
            Button(
                text=Const('🏠 На главную'),
                id='main_page',
                on_click=main_page_button_clicked,
            ),
            Next(Const('▶️ Пропустить'), id='next'),
            width=3
        ),
        state=AddPhraseSG.category,
        getter=get_user_categories
    ),
    Window(
        Multi(
            Format('Выбранная категория: <b>{category}</b>'),
            Const(text='Введите текст новой фразы:'),
        ),
        TextInput(
            id='phrase_input',
            on_success=phrase_input,
        ),
        Group(
            Back(Const('◀️ Назад'), id='back'),
            Cancel(Const('❌ Отмена'), id='button_cancel'),
            Button(
                text=Const('🏠 На главную'),
                id='main_page',
                on_click=main_page_button_clicked,
            ),
            width=3
        ),
        state=AddPhraseSG.phrase,
        getter=get_current_category,
    ),
)
