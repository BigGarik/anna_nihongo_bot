import os
from pathlib import Path

from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, Select
from aiogram_dialog.widgets.text import Const, Format, Multi
from tortoise.expressions import RawSQL

from bot_init import bot
from external_services.voice_recognizer import SpeechRecognizer
from models import User, Phrase, Category, UserAnswer, AudioFile
from services.services import replace_random_words
from .. import main_page_button_clicked
from states import LexisTrainingSG, LexisSG, AddPhraseSG


# Функция для динамического создания кнопок с категориями
async def get_user_categories(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    categories = await Category.filter(phrases__user_id=user_id).distinct().all()

    items = [(category.name, str(category.id)) for category in categories]
    return {'categories': items}


async def get_category(dialog_manager: DialogManager, **kwargs):
    category_name = dialog_manager.dialog_data['category']
    return {'category': category_name}


async def get_context(dialog_manager: DialogManager, **kwargs):
    with_gap_phrase = dialog_manager.dialog_data['with_gap_phrase']
    question = dialog_manager.dialog_data['question']
    translation = dialog_manager.dialog_data['translation']
    counter = dialog_manager.dialog_data['counter']
    category = dialog_manager.dialog_data['category']

    return {'with_gap_phrase': with_gap_phrase,
            'question': question,
            'translation': translation,
            'counter': counter,
            'category': category}


def get_counter(data, widget, dialog_manager: DialogManager):
    ''' проверить столько неправильных ответоа
     если 3 и больше, то count_answer = True '''
    if dialog_manager.dialog_data.get('counter', 0) >= 3:
        return True
    return False


def first_answer_getter(data, widget, dialog_manager: DialogManager):
    # до первого ответа вернет False
    return 'answer' in dialog_manager.dialog_data


def second_answer_getter(data, widget, dialog_manager: DialogManager):
    return not first_answer_getter(data, widget, dialog_manager)


async def answer_audio_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    user_id = message.from_user.id
    # Скачиваем файл
    voice_id = message.voice.file_id
    file = await bot.get_file(voice_id)
    file_path = file.file_path
    file_on_disk = Path("", f"temp/{voice_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk)

    spoken_recognizer = SpeechRecognizer(file_on_disk, user_id)
    spoken_answer = spoken_recognizer.recognize_speech()

    # Удаление временного файла
    os.remove(file_on_disk)

    dialog_manager.dialog_data['answer'] = spoken_answer
    text_phrase = dialog_manager.dialog_data['question']
    phrase = await Phrase.get_or_none(text_phrase=text_phrase)
    user_id = dialog_manager.event.from_user.id
    user = await User.get_or_none(id=user_id)
    user_answer = UserAnswer(
        user=user,
        phrase=phrase,
        answer_text=spoken_answer,
        audio_id=voice_id,
    )
    if dialog_manager.dialog_data['question'] == spoken_answer:
        dialog_manager.dialog_data['counter'] = 0
        user_answer.result = True
        await message.answer(f'Ты произнес:\n{spoken_answer}\n\nУра!!! Ты лучший! 🥳')
        dialog_manager.dialog_data.pop('answer', None)
        await dialog_manager.back()
    else:
        await message.answer(f'Кажется ты произнес:\n{spoken_answer}')
        user_answer.result = False
    await user_answer.save()


async def check_answer_text(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                            answer_text: str):
    dialog_manager.dialog_data['answer'] = answer_text
    text_phrase = dialog_manager.dialog_data['question']
    phrase = await Phrase.get_or_none(text_phrase=text_phrase)
    user_id = dialog_manager.event.from_user.id
    user = await User.get_or_none(id=user_id)
    user_answer = UserAnswer(
        user=user,
        phrase=phrase,
        answer_text=answer_text,
    )
    if dialog_manager.dialog_data['question'] == answer_text:
        dialog_manager.dialog_data['counter'] = 0
        user_answer.result = True
        await message.answer('Ура!!! Ты лучший! 🥳')
        dialog_manager.dialog_data.pop('answer', None)
        await dialog_manager.back()

    else:
        dialog_manager.dialog_data['counter'] += 1
        user_answer.result = False
    await user_answer.save()


async def exercises_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=LexisTrainingSG.start)


async def add_phrase_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=AddPhraseSG.category)


# Хэндлер для выбора категории
async def category_selection(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    random_phrase = await Phrase.filter(category_id=item_id).annotate(
        random_order=RawSQL("RANDOM()")).order_by("random_order").first()
    with_gap_phrase = replace_random_words(random_phrase.spaced_phrase)
    dialog_manager.dialog_data['with_gap_phrase'] = with_gap_phrase
    dialog_manager.dialog_data['question'] = random_phrase.text_phrase
    dialog_manager.dialog_data['audio_id'] = random_phrase.audio_id
    dialog_manager.dialog_data['translation'] = random_phrase.translation
    dialog_manager.dialog_data['counter'] = 0
    category = await Category.get_or_none(id=item_id)
    dialog_manager.dialog_data['category'] = category.name

    # await callback.message.answer(with_gap_phrase)
    await dialog_manager.next()


async def listen_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    voice_id = dialog_manager.dialog_data['audio_id']
    await bot.send_voice(chat_id=callback.from_user.id, voice=voice_id)


async def error_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    await message.answer('Моя твоя не понимать 🤔')


lexis_dialog = Dialog(
    Window(
        Const('Раздел тренировки лексики'),
        Button(
            text=Const('Упражнения'),
            id='exercises',
            on_click=exercises_button_clicked,
        ),
        Button(
            text=Const('Добавить фразы'),
            id='add_phrase',
            on_click=add_phrase_button_clicked,
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
        state=LexisSG.start
    ),
)

lexis_training_dialog = Dialog(
    Window(
        Const(text='Выберите категорию:'),
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
        Group(
            Cancel(Const('❌ Отмена'), id='button_cancel'),
            Button(
                text=Const('🏠 На главную'),
                id='main_page',
                on_click=main_page_button_clicked,
            ),
            width=3
        ),
        getter=get_user_categories,
        state=LexisTrainingSG.start
    ),
    Window(
        Multi(
            Format('Выбранная категория: <b>{category}</b>'),
            Format('Фраза:\n <strong>{with_gap_phrase}</strong>'),
            Format('Перевод:\n <tg-spoiler>{translation}</tg-spoiler>'),
            Const('Попробуй еще раз ))',
                  when=first_answer_getter),
            Const('Введи текст ответа:',
                  when=second_answer_getter),
            sep='\n\n'
        ),
        MessageInput(
            func=answer_audio_handler,
            content_types=ContentType.VOICE,
        ),
        TextInput(
            id='answer_input',
            on_success=check_answer_text,
        ),
        MessageInput(
            func=error_handler,
            content_types=ContentType.ANY,
        ),
        Button(
            text=Const('Послушать'),
            id='listen',
            on_click=listen_button_clicked,
            when=get_counter
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
        getter=get_context,
        state=LexisTrainingSG.waiting_answer,
    ),
)
