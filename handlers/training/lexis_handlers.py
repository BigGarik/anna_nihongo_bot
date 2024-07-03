import os
from pathlib import Path

from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, Select, Back
from aiogram_dialog.widgets.text import Format, Multi

from bot_init import bot
from external_services.voice_recognizer import SpeechRecognizer
from models import User, Phrase, UserAnswer
from services.i18n_format import I18NFormat, I18N_FORMAT_KEY, default_format_text
from services.services import normalize_text
from states import LexisTrainingSG
from ..system_handlers import get_random_phrase, get_user_categories, first_answer_getter, second_answer_getter, \
    get_context


def get_counter(data, widget, dialog_manager: DialogManager):
    ''' проверить столько неправильных ответоа
     если 3 и больше, то count_answer = True '''
    if dialog_manager.dialog_data.get('counter', 0) >= 3:
        return True
    return False


async def answer_audio_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY, default_format_text)
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
        exercise='lexis'
    )
    if dialog_manager.dialog_data['question'] == spoken_answer:
        dialog_manager.dialog_data['counter'] = 0
        user_answer.result = True
        await message.answer(i18n_format('congratulations-spoken-answer', dialog_manager.dialog_data))
        dialog_manager.dialog_data.pop('answer', None)
        await dialog_manager.back()
    else:
        await message.answer(i18n_format('spoken-answer', dialog_manager.dialog_data))
        user_answer.result = False
    await user_answer.save()


async def check_answer_text(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                            answer_text: str):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY, default_format_text)
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
    question = dialog_manager.dialog_data.get('question', '')
    normalized_question = normalize_text(question)
    normalized_answer = normalize_text(answer_text)

    if normalized_question == normalized_answer:
        dialog_manager.dialog_data['counter'] = 0
        user_answer.result = True
        await message.answer(i18n_format('congratulations'))
        # voice_id = dialog_manager.dialog_data['audio_id']
        # if voice_id:
        #     await bot.send_voice(chat_id=message.from_user.id, voice=voice_id)
        dialog_manager.dialog_data.pop('answer', None)
        category_id = dialog_manager.dialog_data['category_id']
        await get_random_phrase(dialog_manager, category_id)

    else:
        dialog_manager.dialog_data['counter'] += 1
        user_answer.result = False
    await user_answer.save()


# Хэндлер для выбора категории
async def category_selection(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    await get_random_phrase(dialog_manager, item_id)
    await dialog_manager.next()


async def next_phrase_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    category_id = dialog_manager.dialog_data['category_id']
    await get_random_phrase(dialog_manager, category_id)


async def listen_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    voice_id = dialog_manager.dialog_data['audio_id']
    await bot.send_voice(chat_id=callback.from_user.id, voice=voice_id)


async def error_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY, default_format_text)
    await message.answer(i18n_format('error-handler'))


lexis_training_dialog = Dialog(
    Window(
        I18NFormat('lexis-training-dialog'),
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
            Select(
                Format('{item[0]}'),
                id='cat_for_all',
                item_id_getter=lambda x: x[1],
                items='categories_for_all',
                on_click=category_selection,
            ),
            width=2
        ),
        Group(
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            width=3
        ),
        getter=get_user_categories,
        state=LexisTrainingSG.start
    ),
    Window(
        Multi(
            I18NFormat('training-category'),
            I18NFormat('lexis-training-phrase'),
            I18NFormat('training-translation'),
            I18NFormat('lexis-training'),
            I18NFormat('training-try-again',
                  when=first_answer_getter),
            I18NFormat('enter-answer-text',
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
            text=I18NFormat('listen'),
            id='listen',
            on_click=listen_button_clicked,
            when=get_counter
        ),
        Group(
            Back(I18NFormat('back'), id='back'),
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            Button(
                text=I18NFormat('next'),
                id='next_phrase',
                on_click=next_phrase_button_clicked,
            ),
            width=3
        ),
        getter=get_context,
        state=LexisTrainingSG.waiting_answer,
    ),
)
