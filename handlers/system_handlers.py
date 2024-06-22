import os
import random

from aiogram.types import User, CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button, Select
from tortoise.expressions import RawSQL

from models import Category, Phrase
from services.services import replace_random_words
from states import UserStartDialogSG


location = os.getenv('LOCATION')


async def start_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    # Получение списка разрешенных ID пользователей из переменной окружения
    admin_ids = os.getenv('ADMIN_IDS')
    # Преобразование строки в список целых чисел
    admin_ids = [int(user_id) for user_id in admin_ids.split(',')]
    response = {'username': event_from_user.first_name or event_from_user.username}
    if event_from_user.id in admin_ids:
        response['is_admin'] = True
    else:
        response['is_admin'] = False

    if location == 'ja-JP':
        response['is_jp'] = True
    else:
        response['is_jp'] = False

    if location == 'en-US':
        response['is_en'] = True
    else:
        response['is_en'] = False

    return response



async def get_user_categories(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    categories = await Category.filter(user_id=user_id).all()
    items = [(category.name, str(category.id)) for category in categories]
    return {'categories': items}


async def get_phrases(dialog_manager: DialogManager, **kwargs):
    items = dialog_manager.dialog_data['phrases']
    return {'phrases': items}


async def category_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    category = await Category.get(id=item_id)
    dialog_manager.dialog_data['category_id'] = category.id
    user_id = dialog_manager.event.from_user.id
    phrases = await Phrase.filter(category_id=item_id, user_id=user_id).all()
    items = [(phrase.text_phrase, str(phrase.id)) for phrase in phrases]
    dialog_manager.dialog_data['phrases'] = items
    await dialog_manager.next()


async def get_random_phrase(dialog_manager: DialogManager, item_id: str, **kwargs):
    phrases = await Phrase.filter(category_id=item_id).all()

    if dialog_manager.dialog_data.get('question'):
        text_phrase = dialog_manager.dialog_data['question']
        if len(phrases) > 1:
            filtered_phrases = [phrase for phrase in phrases if phrase.text_phrase != text_phrase]
        else:
            filtered_phrases = phrases
    else:
        filtered_phrases = phrases
    random_phrase = random.choice(filtered_phrases)

    with_gap_phrase = replace_random_words(random_phrase.spaced_phrase)
    dialog_manager.dialog_data['with_gap_phrase'] = with_gap_phrase
    dialog_manager.dialog_data['question'] = random_phrase.text_phrase
    dialog_manager.dialog_data['audio_id'] = random_phrase.audio_id
    dialog_manager.dialog_data['translation'] = random_phrase.translation
    dialog_manager.dialog_data['counter'] = 0
    category = await Category.get_or_none(id=item_id)
    dialog_manager.dialog_data['category'] = category.name
    dialog_manager.dialog_data['category_id'] = item_id


async def get_context(dialog_manager: DialogManager, **kwargs):
    with_gap_phrase = dialog_manager.dialog_data['with_gap_phrase']
    question = dialog_manager.dialog_data['question']
    translation = dialog_manager.dialog_data['translation']
    counter = dialog_manager.dialog_data['counter']
    category = dialog_manager.dialog_data['category']
    category_id = dialog_manager.dialog_data['category_id']

    return {'with_gap_phrase': with_gap_phrase,
            'question': question,
            'translation': translation,
            'counter': counter,
            'category': category,
            'category_id': category_id}


def first_answer_getter(data, widget, dialog_manager: DialogManager):
    # до первого ответа вернет False
    return 'answer' in dialog_manager.dialog_data


def second_answer_getter(data, widget, dialog_manager: DialogManager):
    return not first_answer_getter(data, widget, dialog_manager)


async def main_page_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.done()
    await dialog_manager.start(state=UserStartDialogSG.start)
