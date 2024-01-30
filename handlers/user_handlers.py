from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Command, CommandStart, StateFilter
from pathlib import Path
from keyboards.inline_kb import create_inline_kb
from external_services.voice_recognizer import SpeechRecognizer
from external_services.visualizer import PronunciationVisualizer
from services.services import get_ogg_files, create_kb_file, get_folders, get_all_ogg_files, get_all_tags, get_tag
from states.states import FSMInLearn, user_dict

from lexicon.lexicon_ru import LEXICON_RU, LEXICON_KB_FAST_BUTTONS_RU
import logging
import datetime
import librosa

# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger(__name__)


# Этот хэндлер срабатывает на команду /start вне состояний
# рисуем клавиатуру с категориями
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    keyboard = create_inline_kb(1, **get_folders('original_files'))
    await message.answer(
        text=f"{LEXICON_RU['/start']}{LEXICON_RU['select_category']}",
        reply_markup=keyboard
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


@router.message(Command(commands='cancel'))
async def process_help_command(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU['/cancel'])
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
    # logging.warning(await state.get_data())
    # Добавляем в "базу данных" данные пользователя
    # по ключу id пользователя
    user_dict[callback.from_user.id] = await state.get_data()
    # logger.warning(f'current_phrase пользователя - {user_dict[callback.from_user.id]["current_phrase"]}')
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


@router.callback_query()
async def process_phrase(callback: CallbackQuery):
    await callback.message.answer(text=callback.data)


# Хэндлер на голосовое сообщение
@router.message(F.voice, ~StateFilter(default_state))
async def process_send_voice(message: Message, bot: Bot, state: FSMContext):
    # Получаем голосовое сообщение и сохраняем на диск
    user_id = message.from_user.id
    current_phrase = user_dict[user_id]["current_phrase"]
    current_phrase = current_phrase.rsplit('.', 1)[0]
    file_name = f"{user_id}_{current_phrase}_{datetime.datetime.now()}"
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"temp/{file_name}.ogg")
    await bot.download_file(file_path, destination=file_on_disk)
    # print(message.from_user.id)
    # print(message.from_user.first_name)
    # print(user_dict[message.from_user.id]["current_phrase"])
    # print(file_on_disk)
    #logger.warning('проверка логера')
    logger.warning(f'ID пользователя {user_id} имя {message.from_user.first_name} '
                   f'фраза {user_dict[user_id]["current_phrase"]} '
                   f'файл - {file_on_disk}')
    # logging.debug(await state.get_state())
    # logger.warning(
        # f'{user_dict[message.from_user.id]["select_category"]}/{user_dict[message.from_user.id]["current_phrase"]}')
    # print(555555)

    original_file = f'{user_dict[user_id]["select_category"]}/{user_dict[user_id]["current_phrase"]}'
    # print(original_file)
    original_script = get_tag(original_file, 'script')
    # print(original_script)
    original_translation = get_tag(original_file, 'translation')
    # print(original_translation)

    # logger.warning(original_file)
    # # Распознавание речи на японском языке
    # original_recognizer = SpeechRecognizer(original_file)
    # original_text = original_recognizer.recognize_speech()
    spoken_recognizer = SpeechRecognizer(file_on_disk, user_id)
    spoken_text = spoken_recognizer.recognize_speech()
    # Загрузка аудиофайлов
    original_audio, sample_rate = librosa.load(original_file)
    # print(111111111)
    spoken_audio, _ = librosa.load(file_on_disk, sr=sample_rate)

    visual = PronunciationVisualizer(original_audio, spoken_audio, sample_rate, file_name)
    # print(2222222222)
    await visual.preprocess_audio()
    await visual.plot_waveform()  # Визуализация графика звуковой волны
    photo = FSInputFile(f'temp/{file_name}.png')
    keyboard = create_inline_kb(2, **LEXICON_KB_FAST_BUTTONS_RU)
    await message.answer_photo(photo, caption=f'Оригинал\n{original_script}\n{original_translation}\n\n'
                                              f'Ваш вариант {spoken_text}', reply_markup=keyboard)

    # print(await state.get_state())
    # os.remove(file_on_disk)  # Удаление временного файла
    # os.remove(f'temp/{file_name}.png')


# Этот хэндлер будет срабатывать на любые сообщения
@router.message()
async def send_echo(message: Message, state: FSMContext):
    await message.reply(text=LEXICON_RU['error'])
    await state.clear()
