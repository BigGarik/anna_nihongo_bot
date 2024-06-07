import os
from pathlib import Path

from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import DialogManager, Dialog, Window, ShowMode
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Group
from aiogram_dialog.widgets.text import Const
from tortoise.exceptions import DoesNotExist

from bot_init import bot
from external_services.openai_services import gpt_add_space
from external_services.voice_recognizer import SpeechRecognizer
from models import User, LexisPhrase

from services.services import replace_random_words
from .states import LexisTrainingSG
from .. import main_page_button_clicked


def first_answer_getter(data, widget, dialog_manager: DialogManager):
    # до первого ответа вернет False
    return 'answer' in dialog_manager.dialog_data


def second_answer_getter(data, widget, dialog_manager: DialogManager):
    return not first_answer_getter(data, widget, dialog_manager)


async def answer_audio_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    user_id = message.from_user.id
    # Скачиваем файл
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"temp/{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk)

    spoken_recognizer = SpeechRecognizer(file_on_disk, user_id)
    spoken_answer = spoken_recognizer.recognize_speech()

    # Удаление временного файла
    os.remove(file_on_disk)

    dialog_manager.dialog_data['answer'] = spoken_answer
    if dialog_manager.dialog_data['question'] == spoken_answer:
        await message.answer(f'Ты произнес:\n{spoken_answer}\n\nУра!!! Ты лучший! 🥳')
        dialog_manager.dialog_data.pop('answer', None)
        await dialog_manager.back()
    else:
        await message.answer(f'Кажется ты произнес:\n{spoken_answer}')




async def lexis_training_text(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['question'] = text
    phrase = await LexisPhrase.get_or_none(phrase=text)
    # Запикать звездочками часть слов
    if not phrase:
        user = await User.get_or_none(id=message.from_user.id)
        spaced_phrase = gpt_add_space(text)
        phrase = await LexisPhrase.create(phrase=text, spaced_phrase=spaced_phrase, user=user)

    spaced_phrase = phrase.spaced_phrase
    with_gap_phrase = replace_random_words(spaced_phrase)
    # Удаление сообщения пользователя
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    await message.answer(with_gap_phrase)
    await dialog_manager.next()


async def check_answer_text(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    dialog_manager.dialog_data['answer'] = text
    if dialog_manager.dialog_data['question'] == text:
        await message.answer('Ура!!! Ты лучший! 🥳')
        dialog_manager.dialog_data.pop('answer', None)
        await dialog_manager.back()


async def error_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    await message.answer('Моя твоя не понимать 🤔')


lexis_training_dialog = Dialog(
    Window(
        Const('Отправь мне фразу в голосовом сообщении и мы потренируемся в грамматике'),
        # MessageInput(
        #     func=question_audio_handler,
        #     content_types=ContentType.VOICE,
        # ),
        TextInput(
            id='grammar_training_text_input',
            on_success=lexis_training_text,
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
        state=LexisTrainingSG.start
    ),
    Window(
        Const('Попробуй еще раз ))',
              when=first_answer_getter),
        Const('Отправь ответ',
              when=second_answer_getter),
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
        Group(
            Cancel(Const('❌ Отмена'), id='button_cancel'),
            Button(
                text=Const('🏠 На главную'),
                id='main_page',
                on_click=main_page_button_clicked,
            ),
            width=3
        ),
        state=LexisTrainingSG.waiting_answer,
    ),
)
