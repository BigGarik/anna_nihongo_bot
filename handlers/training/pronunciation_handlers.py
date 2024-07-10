import os
import random
from pathlib import Path

import librosa
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram_dialog import DialogManager, Dialog, Window, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, Select, Back
from aiogram_dialog.widgets.text import Format, Multi

from bot_init import bot
from external_services.visualizer import PronunciationVisualizer
from external_services.voice_recognizer import SpeechRecognizer
from models import Phrase, UserAnswer
from services.i18n_format import I18NFormat, I18N_FORMAT_KEY
from states import PronunciationTrainingSG
from ..system_handlers import category_selected, get_user_categories, get_phrases


async def phrase_selected(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item_id: str):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    phrase = await Phrase.get_or_none(id=item_id)
    dialog_manager.dialog_data['phrase_id'] = phrase.id
    # отправить изображение и голосовое с подписью
    if phrase.image_id:
        await callback.message.answer_photo(phrase.image_id)
    await callback.message.answer_voice(phrase.audio_id,
                                        caption=i18n_format('listen-original'))
    await dialog_manager.next(show_mode=ShowMode.DELETE_AND_SEND)


async def random_phrase_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    phrases = await Phrase.filter(category_id=dialog_manager.dialog_data['category_id']).all()
    if dialog_manager.dialog_data.get('phrase_id'):
        phrase_id = dialog_manager.dialog_data['phrase_id']
        if len(phrases) > 1:
            filtered_phrases = [phrase for phrase in phrases if phrase.id != phrase_id]
        else:
            filtered_phrases = phrases
    else:
        filtered_phrases = phrases
    if phrases:
        random_phrase = random.choice(filtered_phrases)
        await phrase_selected(callback, button, dialog_manager, item_id=str(random_phrase.id))
    else:
        await callback.message.answer(i18n_format('no-phrases-available'))


async def answer_audio_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    await message.answer(i18n_format('processing-message'))
    phrase_id = dialog_manager.dialog_data['phrase_id']
    phrase = await Phrase.get_or_none(id=phrase_id)
    dialog_manager.dialog_data['text_phrase'] = phrase.text_phrase
    dialog_manager.dialog_data['translation'] = phrase.translation
    dialog_manager.dialog_data['comment'] = phrase.comment if phrase.comment else ' '
    answer_voice_id = message.voice.file_id
    original_voice_id = phrase.audio_id
    # download files
    answer_voice = await bot.get_file(answer_voice_id)
    original_voice = await bot.get_file(original_voice_id)
    answer_voice_path = answer_voice.file_path
    original_voice_path = original_voice.file_path
    answer_voice_on_disk = Path("", f"temp/{answer_voice_id}.ogg")
    original_voice_on_disk = Path("", f"temp/{original_voice_id}.ogg")
    await bot.download_file(answer_voice_path, destination=answer_voice_on_disk)
    if not original_voice_on_disk.exists():
        await bot.download_file(original_voice_path, destination=original_voice_on_disk)
    # recognize file
    spoken_recognizer = SpeechRecognizer(answer_voice_on_disk, answer_voice_id)
    answer_text = spoken_recognizer.recognize_speech()
    dialog_manager.dialog_data['answer_text'] = answer_text
    original_voice, sample_rate = librosa.load(original_voice_on_disk)
    spoken_audio, _ = librosa.load(answer_voice_on_disk, sr=sample_rate)
    visual = PronunciationVisualizer(original_voice, spoken_audio, sample_rate, answer_voice_id)
    await visual.preprocess_audio()
    await visual.plot_waveform()  # Визуализация графика звуковой волны
    photo = FSInputFile(f'temp/{answer_voice_id}.png')
    await message.answer_photo(photo, caption=i18n_format('image-caption', dialog_manager.dialog_data))
    await UserAnswer.create(
        user_id=message.from_user.id,
        phrase_id=phrase_id,
        answer_text=answer_text,
        audio_id=answer_voice_id,
        exercise='pronunciation'
    )
    os.remove(answer_voice_on_disk)
    os.remove(f'temp/{answer_voice_id}.png')


async def error_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    await message.answer(i18n_format('error-handler'))


pronunciation_training_dialog = Dialog(
    Window(
        I18NFormat('pronunciation_training_dialog'),
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
            Select(
                Format('{item[0]}'),
                id='cat_for_all',
                item_id_getter=lambda x: x[1],
                items='categories_for_all',
                on_click=category_selected,
            ),
            width=2
        ),

        Group(
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            width=3
        ),
        getter=get_user_categories,
        state=PronunciationTrainingSG.select_category
    ),
    Window(
        # Пользователь выбирает фразу или
        # отправляем рандомную фразу из выбранной категории
        Multi(
            I18NFormat('choose-phrase'),
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
            text=I18NFormat('random-phrase'),
            id='random_phrase',
            on_click=random_phrase_button_clicked,
            when='show_random_button'
        ),
        Group(
            Back(I18NFormat('back'), id='back'),
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            width=3
        ),
        getter=get_phrases,
        state=PronunciationTrainingSG.select_phrase
    ),
    Window(
        I18NFormat('try-again'),
        MessageInput(
            func=answer_audio_handler,
            content_types=ContentType.VOICE,
        ),
        MessageInput(
            func=error_handler,
            content_types=ContentType.ANY,
        ),
        Group(
            Back(I18NFormat('back'), id='back'),
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            width=3
        ),
        state=PronunciationTrainingSG.waiting_answer
    ),
)
