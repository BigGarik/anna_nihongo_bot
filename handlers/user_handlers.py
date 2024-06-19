import datetime
import logging
import uuid
from pathlib import Path

import librosa
from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, FSInputFile, CallbackQuery, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Row, Column, Start
from aiogram_dialog.widgets.text import Format, Const, Multi
from dotenv import load_dotenv

from bot_init import bot, redis
from db.requests import get_user_ids
from external_services.visualizer import PronunciationVisualizer
from external_services.voice_recognizer import SpeechRecognizer
from keyboards.inline_kb import create_inline_kb
from lexicon.lexicon_ru import LEXICON_RU, LEXICON_KB_FAST_BUTTONS_RU
from services.services import create_kb_file, get_folders, get_all_ogg_files, get_tag
from states.states import FSMInLearn, user_dict
from . import username_getter
from states import StartDialogSG, UserStartDialogSG, AdminDialogSG, UserTrainingSG, TextToSpeechSG

load_dotenv()

# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger(__name__)


async def tts_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # await dialog_manager.done()
    await dialog_manager.start(state=TextToSpeechSG.start)


async def category_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    keyboard = create_inline_kb(1, **get_folders('original_files'))
    await callback.message.answer(
        text=f"{LEXICON_RU['select_category']}",
        reply_markup=keyboard
    )
    await dialog_manager.done()


async def access_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # Генерируем уникальный идентификатор для запроса
    request_id = str(uuid.uuid4())

    # Сохраняем данные пользователя в Redis с использованием хеша
    await redis.hmset(f"access_request:{request_id}", {
        "user_id": callback.from_user.id,
        "username": callback.from_user.username or "",
        "first_name": callback.from_user.first_name or "",
        "last_name": callback.from_user.last_name or "",
    })

    # Создаем кнопки
    button1 = InlineKeyboardButton(text="Подтвердить", callback_data=f"confirm_access:{request_id}")
    button2 = InlineKeyboardButton(text="Отменить", callback_data=f"cancel_access:{request_id}")

    # Создаем разметку клавиатуры
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [button1],  # Кнопки располагаются в ряд
        [button2],
    ])

    await bot.send_message(
        693131974,
        f"Пользователь @{callback.from_user.username} запрашивает доступ.",
        reply_markup=keyboard
    )
    await dialog_manager.done()
    await callback.message.answer('Заявка отправлена администратору.')


async def training_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=UserTrainingSG.start)


start_dialog = Dialog(
    Window(
        Multi(
            Format('日本語を勉強しよう\n'
                   '<b>Привет, {username}!</b>\nЯ бот-помощник Анны-сэнсэй 😃\n'
                   'Я помогаю тренироваться в японском произношении и грамматике.\n\n'
                   'Хотите говорить по-японски как японцы?\n'
                   ),
        ),
        Row(
            Button(
                text=Const('Запросить доступ'),
                id='access',
                on_click=access_button_clicked),
        ),
        getter=username_getter,
        state=StartDialogSG.start
    ),
)

user_start_dialog = Dialog(
    Window(
        Multi(
            Format('日本語を勉強しよう\n'
                   '<b>Привет, {username}!</b>\nЯ бот-помощник Анны-сэнсэй 😃\n'
                   'Я помогаю тренироваться в японском произношении и грамматике.\n\n'
                   'Хотите говорить по-японски как японцы?\n'
                   ),
        ),
        Column(
            Row(
                Button(
                    text=Const('Категории фраз'),
                    id='category',
                    on_click=category_button_clicked),

            ),
            Row(
                Button(
                    text=Const('💪 Тренировки'),
                    id='training',
                    on_click=training_button_clicked),
                Button(
                    text=Const('🔊 Прослушивание (Озвучить текст)'),
                    id='tts',
                    on_click=tts_button_clicked),
            ),
        ),
        Row(
            Start(Const('⚙️ Настройки(для админов)'),
                  id='settings',
                  state=AdminDialogSG.start
                  ),
            when='is_admin',
        ),
        getter=username_getter,
        # Состояние этого окна для переключения на него
        state=UserStartDialogSG.start
    ),
)


# Этот хэндлер будет срабатывать на /start
@router.message(CommandStart())
async def process_start_command(message: Message, dialog_manager: DialogManager):
    # получить пользователей из БД
    # Если ИД в базе, то user_start_dialog
    user_ids = await get_user_ids()
    if message.from_user.id in user_ids:
        await dialog_manager.start(state=UserStartDialogSG.start, mode=StartMode.RESET_STACK)
    # иначе start_dialog
    else:
        await dialog_manager.start(state=StartDialogSG.start, mode=StartMode.RESET_STACK)


@router.message(Command(commands='cancel'))
async def process_help_command(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await message.answer(text=LEXICON_RU['/cancel'])
    await dialog_manager.done()
    await state.clear()


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
async def process_choose_phrase(callback: CallbackQuery, state: FSMContext):
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
