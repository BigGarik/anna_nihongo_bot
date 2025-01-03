import logging
from pathlib import Path

from aiogram import F
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode, StartMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Group, Button
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Multi
from dotenv import load_dotenv

from bot_init import bot
from external_services.voice_recognizer import SpeechRecognizer
from models import Phrase, User
from services.i18n_format import I18NFormat, I18N_FORMAT_KEY
from services.interval_training import check_user_answer, start_training
from services.services import replace_random_words
from states import IntervalSG, IntervalTrainingSG, UserTrainingSG, ManagementSG, ErrorIntervalSG

load_dotenv()
logger = logging.getLogger('default')


async def get_data(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    user = await User.get(id=user_id)
    dialog_manager.dialog_data['enabled_notifications'] = user.notifications
    return dialog_manager.dialog_data


async def get_lexis_data(dialog_manager: DialogManager, **kwargs):
    phrase = await Phrase.get(id=dialog_manager.start_data['phrase_id'])
    dialog_manager.dialog_data['phrase_id'] = dialog_manager.start_data['phrase_id']
    dialog_manager.dialog_data['question'] = phrase.text_phrase
    dialog_manager.dialog_data['translation'] = phrase.translation
    with_gap_phrase = replace_random_words(phrase.spaced_phrase)
    dialog_manager.dialog_data['with_gap_phrase'] = with_gap_phrase
    dialog_manager.dialog_data['training_selected'] = dialog_manager.start_data['training_selected']
    return dialog_manager.dialog_data


async def get_voice_data(dialog_manager: DialogManager, **kwargs):
    phrase = await Phrase.get(id=dialog_manager.start_data['phrase_id'])
    dialog_manager.dialog_data['phrase_id'] = dialog_manager.start_data['phrase_id']
    dialog_manager.dialog_data['training_selected'] = dialog_manager.start_data['training_selected']
    audio = MediaAttachment(ContentType.VOICE, file_id=MediaId(phrase.audio_id))
    return {'voice': audio}


async def get_translation_data(dialog_manager: DialogManager, **kwargs):
    phrase = await Phrase.get(id=dialog_manager.start_data['phrase_id'])
    dialog_manager.dialog_data['phrase_id'] = dialog_manager.start_data['phrase_id']
    dialog_manager.dialog_data['translation'] = phrase.translation
    dialog_manager.dialog_data['training_selected'] = dialog_manager.start_data['training_selected']
    return dialog_manager.dialog_data


async def cancel_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=IntervalSG.start, show_mode=ShowMode.SEND)


async def cancel_interval_dialog(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=UserTrainingSG.start, show_mode=ShowMode.SEND, mode=StartMode.RESET_STACK)


async def start_training_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await start_training(dialog_manager)


async def enable_notifications_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user = await User.get_or_none(id=dialog_manager.event.from_user.id)
    user.notifications = True
    await user.save()


async def disable_notifications_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    user = await User.get_or_none(id=dialog_manager.event.from_user.id)
    user.notifications = False
    await user.save()


async def pronunciation_training_input(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    phrase = await Phrase.get(id=dialog_manager.dialog_data['phrase_id'])
    user = await User.get_or_none(id=dialog_manager.event.from_user.id)
    training_selected = dialog_manager.dialog_data['training_selected']
    answer_voice_id = message.voice.file_id
    answer_voice = await bot.get_file(answer_voice_id)
    answer_voice_path = answer_voice.file_path
    answer_voice_on_disk = Path("", f"temp/{answer_voice_id}.ogg")
    await bot.download_file(answer_voice_path, destination=answer_voice_on_disk)
    spoken_recognizer = SpeechRecognizer(answer_voice_on_disk, answer_voice_id)
    answer_text = spoken_recognizer.recognize_speech()
    result = await check_user_answer(answer_text, phrase, user, training_selected)
    if result:
        await message.answer(i18n_format('right'))
    else:
        await message.answer(i18n_format('wrong'))

    await start_training(dialog_manager)


async def text_training_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                              answer_text: str):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    phrase = await Phrase.get(id=dialog_manager.dialog_data['phrase_id'])
    user = await User.get_or_none(id=dialog_manager.event.from_user.id)
    training_selected = dialog_manager.dialog_data['training_selected']
    result = await check_user_answer(answer_text, phrase, user, training_selected)
    if result:
        await message.answer(i18n_format('right'))
    else:
        await message.answer(i18n_format('wrong'))

    await start_training(dialog_manager)


async def phrase_management_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=ManagementSG.start, mode=StartMode.RESET_STACK)


interval_dialog = Dialog(
    Window(
        I18NFormat('interval-training-dialog'),
        Button(
            text=I18NFormat('start-training'),
            id='start_training',
            on_click=start_training_button_clicked,
        ),
        Button(
            text=I18NFormat('enable-notifications'),
            id='enable_notifications',
            on_click=enable_notifications_button_clicked,
            when=F['enabled_notifications'] != True,
        ),
        Button(
            text=I18NFormat('disable-notifications'),
            id='disable_notifications',
            on_click=disable_notifications_button_clicked,
            when='enabled_notifications',
        ),
        Group(
            Button(text=I18NFormat('cancel'), id='button_cancel', on_click=cancel_interval_dialog),
            # Next(I18NFormat('next'), id='button_next'),
            width=3
        ),
        getter=get_data,
        state=IntervalSG.start
    ),
    # Window(
    #     I18NFormat('interval-training-dialog'),
    #     Back(I18NFormat('back'), id='button_back'),
    #     state=IntervalSG.pronunciation
    # ),
)

interval_training_dialog = Dialog(
    Window(
        I18NFormat('interval-training-pronunciation-dialog'),
        DynamicMedia("voice"),
        MessageInput(
            func=pronunciation_training_input,
            content_types=ContentType.VOICE,
        ),
        Group(
            Button(text=I18NFormat('cancel'), id='button_cancel', on_click=cancel_button_clicked),
            # Cancel(I18NFormat('cancel'), id='button_cancel', on_click=cancel_button_clicked),
            width=3
        ),
        getter=get_voice_data,
        state=IntervalTrainingSG.pronunciation
    ),
    Window(
        I18NFormat('interval-training-pronunciation-text-dialog'),
        MessageInput(
            func=pronunciation_training_input,
            content_types=ContentType.VOICE,
        ),
        Group(
            Button(text=I18NFormat('cancel'), id='button_cancel', on_click=cancel_button_clicked),
            width=3
        ),
        getter=get_lexis_data,
        state=IntervalTrainingSG.pronunciation_text
    ),
    Window(
        Multi(
            # I18NFormat('interval-training-lexis-dialog'),
            I18NFormat('lexis-training-phrase'),
            I18NFormat('training-translation'),
            I18NFormat('lexis-training'),
            sep='\n\n'
        ),
        TextInput(
            id='lexis_training_input',
            on_success=text_training_input,
        ),
        Group(
            Button(text=I18NFormat('cancel'), id='button_cancel', on_click=cancel_button_clicked),
            width=3
        ),
        getter=get_lexis_data,
        state=IntervalTrainingSG.lexis
    ),
    Window(
        I18NFormat('interval-training-listening-dialog'),
        DynamicMedia("voice"),
        TextInput(
            id='listening_training_input',
            on_success=text_training_input,
        ),
        Group(
            Button(text=I18NFormat('cancel'), id='button_cancel', on_click=cancel_button_clicked),
            width=3
        ),
        getter=get_voice_data,
        state=IntervalTrainingSG.listening
    ),
    Window(
        I18NFormat('interval-training-translation-dialog'),
        TextInput(
            id='translation_training_input',
            on_success=text_training_input,
        ),
        Group(
            Button(text=I18NFormat('cancel'), id='button_cancel', on_click=cancel_button_clicked),
            width=3
        ),
        getter=get_translation_data,
        state=IntervalTrainingSG.translation
    ),
)


error_interval_dialog = Dialog(
    Window(
        I18NFormat('error-interval-training-dialog'),  # нет добавленных фраз
        Button(  # кнопка управление фразами
            text=I18NFormat('phrase-management-button'),
            id='phrase_management_button',
            on_click=phrase_management_button_clicked,
        ),
        Group(
            Button(text=I18NFormat('cancel'), id='button_cancel', on_click=cancel_interval_dialog),
            # Next(I18NFormat('next'), id='button_next'),
            width=3
        ),
        state=ErrorIntervalSG.start
    ),
)
