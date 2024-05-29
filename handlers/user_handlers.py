import datetime
import io
import logging
import os
import re
from pathlib import Path

import librosa
from aiogram import Router, F, Bot, types
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state, StatesGroup, State
from aiogram.types import Message, FSInputFile, CallbackQuery, User, InputFile, BufferedInputFile
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Format, Const, Multi

from external_services.openai_services import text_to_speech
from external_services.visualizer import PronunciationVisualizer
from external_services.voice_recognizer import SpeechRecognizer
from keyboards.inline_kb import create_inline_kb
from lexicon.lexicon_ru import LEXICON_RU, LEXICON_KB_FAST_BUTTONS_RU
from models import TextToSpeech
from services.services import create_kb_file, get_folders, get_all_ogg_files, get_tag
from states.states import FSMInLearn, user_dict
from dotenv import load_dotenv


load_dotenv()

# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger(__name__)


class StartDialogSG(StatesGroup):
    start = State()


class TextToSpeechSG(StatesGroup):
    start = State()


# Этот хэндлер будет срабатывать на /start
@router.message(CommandStart())
async def process_start_command(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartDialogSG.start, mode=StartMode.RESET_STACK)


@router.message(Command(commands='cancel'))
async def process_help_command(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU['/cancel'])
    await state.clear()


async def username_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    # Получение списка разрешенных ID пользователей из переменной окружения
    admin_ids = os.getenv('ADMIN_IDS')
    # Преобразование строки в список целых чисел
    admin_ids = [int(user_id) for user_id in admin_ids.split(',')]
    response = {'username': event_from_user.first_name or event_from_user.username}
    if event_from_user.id in admin_ids:
        response['is_admin'] = True
    else:
        response['is_admin'] = False
    return response


async def category_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    keyboard = create_inline_kb(1, **get_folders('original_files'))
    await callback.message.answer(
        text=f"{LEXICON_RU['select_category']}",
        reply_markup=keyboard
    )
    await dialog_manager.done()


async def tts_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # await dialog_manager.done()
    await dialog_manager.start(state=TextToSpeechSG.start)


async def main_page_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartDialogSG.start, mode=StartMode.RESET_STACK)


async def phrase_to_speech(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    user_id = message.from_user.id
    # Создать имя файла из строки
    filename = re.sub(r'[^\w\s-]', '', text).replace(' ', '_')
    # проверить есть ли в базе уже такая фраза
    voice = await TextToSpeech.filter(text=filename).first()

    if voice:
        await message.answer_voice(voice=voice.voice_id, caption=f'{text}\nСлушайте и повторяйте')

    else:
        response = await text_to_speech(text)
        voice = BufferedInputFile(response.content, filename="voice_tts.txt")
        msg = await message.answer_voice(voice=voice, caption=f'{text}\nСлушайте и повторяйте')
        voice_id = msg.voice.file_id
        await TextToSpeech.create(
            voice_id=voice_id,
            user_id=user_id,
            text=filename,
            voice=response.content,
        )


async def settings_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.answer(text='Настройки для админов (в разработке)')



start_dialog = Dialog(
    # Стартовое окно админки
    Window(
        Multi(
            Format('日本語を勉強しよう\n'
                   '<b>Привет, {username}!</b>\nЯ бот-помощник Анны-сэнсэй 😃\n'
                   'Я помогаю тренироваться в японском произношении и грамматике.\n\n'
                   'Хотите говорить по-японски как японцы?\n'
                   ),
        ),
        # кнопки Настройки и т.д.
        Button(
            text=Const('Категории'),
            id='category',
            on_click=category_button_clicked),
        Button(
            text=Const('Озвучить текст'),
            id='tts',
            on_click=tts_button_clicked),
        Row(
            Button(
                text=Const('Настройки(для админов)'),
                id='settings',
                on_click=settings_button_clicked),
            when='is_admin',
        ),
        getter=username_getter,
        # Состояние этого окна для переключения на него
        state=StartDialogSG.start
    ),
)

text_to_speech_dialog = Dialog(
    Window(
        Const('Отправь мне фразу и я ее озвучу'),
        Button(
            text=Const('На главную'),
            id='main_page',
            on_click=main_page_button_clicked,
        ),
        TextInput(
            id='tts_input',
            on_success=phrase_to_speech,
        ),
        getter=username_getter,
        state=TextToSpeechSG.start
    ),
)


# Этот хэндлер срабатывает на команду /start в состоянии original_phrase
# Предлагаем выбрать новую фразу
#
# @router.message(CommandStart(), StateFilter(FSMInLearn.original_phrase))
# async def process_start_command(message: Message):
#     keyboard = create_inline_kb(1, **kb_names)
#     await message.answer(
#         text=LEXICON_RU['choose_phrase'],
#         reply_markup=keyboard
#     )


@router.message(Command(commands='contact'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/contact'])


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])


# Хендлер обрабатывающий нажатие инлайн кнопки выбора фразы
# установит состояние в original_phrase
# отправить пользователю оригинальное произношение и предложит повторить
# @router.callback_query(F.date.in_(BUTTONS_LIST))

@router.callback_query(F.data == 'new_them')
async def process_select_category(callback: CallbackQuery, state: FSMContext):
    keyboard = create_inline_kb(1, **get_folders('original_files'))
    await callback.message.answer(
        text=LEXICON_RU['select_category'],
        reply_markup=keyboard
    )


@router.callback_query(F.data == 'new_phrase')
async def process_select_category(callback: CallbackQuery, state: FSMContext):
    # Сохраняем выбранную категорию в хранилище состояний
    # await state.update_data(select_category=callback.data)
    dir_to_files = f'{user_dict[callback.from_user.id]["select_category"]}'
    # Создаем клавиатуру с файлами
    keyboard = create_inline_kb(1, **create_kb_file(dir_to_files))
    await callback.message.answer(
        text=LEXICON_RU['choose_phrase'],
        reply_markup=keyboard
    )


# Колбек на нажатие кнопки с выбором категории
@router.callback_query(F.data.in_(list(get_folders('original_files').values())))
async def process_select_category(callback: CallbackQuery, state: FSMContext):
    print(callback.data)
    # Сохраняем выбранную категорию в хранилище состояний
    await state.update_data(select_category=callback.data)
    # Создаем клавиатуру с файлами
    keyboard = create_inline_kb(1, **create_kb_file(callback.data))
    await callback.message.edit_text(
        text=LEXICON_RU['choose_phrase'],
        reply_markup=keyboard
    )


# Колбек на нажатие кнопки с выбором фразы
@router.callback_query(F.data.in_(get_all_ogg_files('original_files')))
async def process_choose_phrase(callback: CallbackQuery, state: FSMContext):
    # Устанавливаем состояние ожидания голосового сообщения повторения оригинала
    await state.set_state(FSMInLearn.original_phrase)
    # Сохраняем выбранную фразу в хранилище состояний
    await state.update_data(current_phrase=callback.data)
    # Добавляем в "базу данных" данные пользователя
    # по ключу id пользователя
    user_dict[callback.from_user.id] = await state.get_data()
    # Удаляем сообщение с кнопками, потому что следующий этап - загрузка голосового сообщения
    # чтобы у пользователя не было желания тыкать кнопки
    await callback.message.delete()
    await callback.message.answer_photo(FSInputFile(f'{user_dict[callback.from_user.id]["select_category"]}/'
                                                    f'{callback.data.replace(".ogg", ".png")}'))
    # Тут нужно отправить оригинальный файл аудио
    await callback.message.answer_voice(
        FSInputFile(f'{user_dict[callback.from_user.id]["select_category"]}/{callback.data}'),
        caption='Послушайте оригинал и попробуйте повторить'
    )
    # TODO добавить кнопку грамматический комментарий


# Хэндлер на голосовое сообщение
@router.message(F.voice, ~StateFilter(default_state))
async def process_send_voice(message: Message, bot: Bot, state: FSMContext):
    # Получаем голосовое сообщение и сохраняем на диск
    user_id = message.from_user.id
    current_phrase = user_dict[user_id]["current_phrase"]
    current_phrase = current_phrase.rsplit('.', 1)[0]
    file_name = f"{user_id}_{datetime.datetime.now()}_{current_phrase}"
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"temp/{file_name}.ogg")
    await bot.download_file(file_path, destination=file_on_disk)
    logger.info(f'ID пользователя {user_id} имя {message.from_user.first_name} '
                f'фраза {user_dict[user_id]["current_phrase"]} '
                f'файл - {file_on_disk}')
    logging.debug(await state.get_state())

    original_file = f'{user_dict[user_id]["select_category"]}/{user_dict[user_id]["current_phrase"]}'
    original_script = get_tag(original_file, 'script')
    original_translation = get_tag(original_file, 'translation')

    # # Распознавание речи на японском языке
    # original_recognizer = SpeechRecognizer(original_file)
    # original_text = original_recognizer.recognize_speech()
    spoken_recognizer = SpeechRecognizer(file_on_disk, user_id)
    spoken_text = spoken_recognizer.recognize_speech()
    # Загрузка аудиофайлов
    original_audio, sample_rate = librosa.load(original_file)
    spoken_audio, _ = librosa.load(file_on_disk, sr=sample_rate)
    visual = PronunciationVisualizer(original_audio, spoken_audio, sample_rate, file_name)
    await visual.preprocess_audio()
    await visual.plot_waveform()  # Визуализация графика звуковой волны
    photo = FSInputFile(f'temp/{file_name}.png')
    keyboard = create_inline_kb(2, **LEXICON_KB_FAST_BUTTONS_RU)
    await message.answer_photo(photo, caption=f'Оригинал\n{original_script}\n{original_translation}\n\n'
                                              f'Ваш вариант {spoken_text}', reply_markup=keyboard)

    # os.remove(file_on_disk)  # Удаление временного файла
    # os.remove(f'temp/{file_name}.png')
