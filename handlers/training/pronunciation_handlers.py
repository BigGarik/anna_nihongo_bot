import io
import os
import random
from pathlib import Path

import librosa
from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery, InputFile, FSInputFile
from aiogram_dialog import DialogManager, Dialog, Window, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, Select, Back
from aiogram_dialog.widgets.text import Const, Format, Multi

from bot_init import bot
from external_services.visualizer import PronunciationVisualizer
from external_services.voice_recognizer import SpeechRecognizer
from models import Phrase, Category, AudioFile
from services.services import get_user_categories
from .. import main_page_button_clicked
from states import PronunciationTrainingSG, PronunciationSG, AddOriginalPhraseSG


async def get_phrases(dialog_manager: DialogManager, **kwargs):
    user_id = dialog_manager.event.from_user.id
    category_id = dialog_manager.dialog_data['category_id']
    phrases = await Phrase.filter(category_id=category_id, user_id=user_id).all()
    items = [(phrase.text_phrase, str(phrase.id)) for phrase in phrases]
    return {'phrases': items}


async def exercises_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=PronunciationTrainingSG.select_category)


async def add_phrase_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=AddOriginalPhraseSG.category)


async def voice_message_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager) -> None:
    await message.send_copy(message.chat.id)


# Это хэндлер, срабатывающий на нажатие кнопки с категорией фразы
async def category_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    # нужно создать словарь и положить его в dialog_data с именами и ИД фраз из выбранной категории

    category = await Category.get(id=item_id)
    dialog_manager.dialog_data['category_id'] = category.id

    await dialog_manager.next()


async def phrase_selected(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, item_id: str):
    print(item_id)
    phrase = await Phrase.get_or_none(id=item_id)
    dialog_manager.dialog_data['phrase_id'] = phrase.id
    # отправить изображение и голосовое с подписью
    await callback.message.delete()
    if phrase.image_id:
        await callback.message.answer_photo(phrase.image_id)
    await callback.message.answer_voice(phrase.audio_id,
                                        caption='Послушайте оригинал и попробуйте повторить')
    await dialog_manager.next()


async def random_phrase_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    phrases = await Phrase.filter(category_id=dialog_manager.dialog_data['category_id']).all()
    if phrases:
        random_phrase = random.choice(phrases)
        print(random_phrase)
        print(random_phrase.id)
        await phrase_selected(callback, button, dialog_manager, item_id=str(random_phrase.id))
    else:
        await callback.message.answer("No phrases available.")


async def answer_audio_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    '''
    скачать голосовое
    построить график
    распознать голосовое
    если нет оригинального аудио,
        скачать оригинал, построить график и сохранить в базу
    склеить графики
    отправить пользователю результат
    '''
    phrase_id = dialog_manager.dialog_data['phrase_id']
    phrase = await Phrase.get_or_none(id=phrase_id)
    phrase_text = phrase.text_phrase
    phrase_translation = phrase.translation
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

    original_voice, sample_rate = librosa.load(original_voice_on_disk)
    spoken_audio, _ = librosa.load(answer_voice_on_disk, sr=sample_rate)
    visual = PronunciationVisualizer(original_voice, spoken_audio, sample_rate, answer_voice_id)
    await visual.preprocess_audio()
    await visual.plot_waveform()  # Визуализация графика звуковой волны
    photo = FSInputFile(f'temp/{answer_voice_id}.png')
    await message.answer_photo(photo, caption=f'Оригинал\n<b>{phrase_text}</b>\n{phrase_translation}\n\n'
                                              f'Ваш вариант <b>{answer_text}</b>')

    os.remove(answer_voice_on_disk)
    os.remove(f'temp/{answer_voice_id}.png')


async def error_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    await message.answer('Моя твоя не понимать 🤔')


pronunciation_dialog = Dialog(
    Window(
        Const('Раздел тренировки произношения'),
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
        state=PronunciationSG.start
    ),
)


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
        getter=get_user_categories,
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
    Window(
        Const('Продолжай тренировку пока произношение не станет идеальным 🤯'),
        MessageInput(
            func=answer_audio_handler,
            content_types=ContentType.VOICE,
        ),
        MessageInput(
            func=error_handler,
            content_types=ContentType.ANY,
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
        state=PronunciationTrainingSG.waiting_answer
    ),
)
