import random

from aiogram.enums import ContentType

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, Select, Back
from aiogram_dialog.widgets.text import Const, Format, Multi

from models import Phrase, Category
from .states import PronunciationTrainingSG
from .. import main_page_button_clicked


# Функция для динамического создания кнопок
async def get_categories(**kwargs):
    categories = await Category.all()
    items = [(category.name, str(category.id)) for category in categories]
    return {'categories': items}


async def get_phrases(dialog_manager: DialogManager, **kwargs):
    category_id = dialog_manager.dialog_data['category_id']
    phrases = await Phrase.filter(category_id=category_id).all()
    items = [(phrase.text_phrase, str(phrase.id)) for phrase in phrases]
    return {'phrases': items}


async def voice_message_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager) -> None:
    await message.send_copy(message.chat.id)


# Это хэндлер, срабатывающий на нажатие кнопки с категорией фразы
async def category_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    # нужно создать словарь и положить его в dialog_data с именами и ИД фраз из выбранной категории

    category = await Category.get(id=item_id)
    dialog_manager.dialog_data['category_id'] = category.id

    await dialog_manager.next()


async def phrase_selected(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item_id: str):
    phrase = await Phrase.get_or_none(id=item_id)
    if phrase:
        await callback.message.answer(f"Selected phrase: {phrase.text_phrase}")
    else:
        await callback.message.answer("Phrase not found.")


async def random_phrase_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    phrases = await Phrase.all()
    if phrases:
        random_phrase = random.choice(phrases)
        await phrase_selected(callback, button, dialog_manager, item_id=str(random_phrase.id))
    else:
        await callback.message.answer("No phrases available.")





pronunciation_training_dialog = Dialog(
    Window(
        # Получить список категорий и вывести их кнопки
        Const('Выбирай категорию для тренировки'),
        Group(
            Select(
                Format('{item[0]}'),
                id='category',
                item_id_getter=lambda x: x[1],
                items='categories',
                on_click=category_selected,
            ),
            width=2
        ),

        Group(
            Cancel(Const('❌ Отмена'), id='button_cancel'),
            Button(
                text=Const('🏠 На главную'),
                id='main_page',
                on_click=main_page_button_clicked,
            ),
            width=3
        ),
        getter=get_categories,
        state=PronunciationTrainingSG.select_category
    ),
    Window(
        # Пользователь выбирает фразу или
        # отправляем рандомную фразу из выбранной категории
        Multi(
            Const('Выбирай фразу или тренируй случайную'),
            Format(''),

              ),
        Group(
            Select(
                Format('{item[0]}'),
                id='phrase',
                item_id_getter=lambda x: x[1],
                items='phrases',
                on_click=phrase_selected,
            ),
            width=2
        ),
        Button(
            text=Const('🎲 Случайная фраза'),
            id='random_phrase',
            on_click=random_phrase_button_clicked,
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
        getter=get_phrases,
        state=PronunciationTrainingSG.select_phrase
    ),
)
