from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, FSInputFile, CallbackQuery
from aiogram.filters import Command, CommandStart, StateFilter
from pathlib import Path
from keyboards.inline_kb import create_inline_kb
from external_services.voice_recognizer import SpeechRecognizer
from external_services.visualizer import PronunciationVisualizer
from services.services import get_ogg_files, create_kb_name
from states.states import FSMInLearn, user_dict

from lexicon.lexicon_ru import LEXICON_RU
import logging.config
import datetime
import librosa

# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger(__name__)

kb_names = create_kb_name('original_files')



# Этот хэндлер срабатывает на команду /start вне состояний
@router.message(CommandStart(), StateFilter(default_state))
async def process_start_command(message: Message):
    keyboard = create_inline_kb(1, **kb_names)
    await message.answer(
        text=f"{LEXICON_RU['/start']}{LEXICON_RU['choose_phrase']}",
        reply_markup=keyboard
    )


# Этот хэндлер срабатывает на команду /start в состоянии original_phrase
# Предлагаем выбрать новую фразу и очищаем состояние
@router.message(CommandStart(), StateFilter(FSMInLearn.original_phrase))
async def process_start_command(message: Message):
    keyboard = create_inline_kb(1, **kb_names)
    await message.answer(
        text=LEXICON_RU['choose_phrase'],
        reply_markup=keyboard
    )


@router.message(Command(commands='cancel'))
async def process_help_command(message: Message, state: FSMContext):
    await message.answer(text=LEXICON_RU['/cancel'])
    await state.clear()


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])


# Хендлер обрабатывающий нажатие инлайн кнопки выбора фразы
# установит состояние в original_phrase
# отправить пользователю оригинальное произношение и предложит повторить
# @router.callback_query(F.date.in_(BUTTONS_LIST))

@router.callback_query(F.data.in_(list(kb_names.keys())))
async def process_choose_phrase(callback: CallbackQuery, state: FSMContext):
    # Устанавливаем состояние ожидания голосового сообщения повторения оригинала
    await state.set_state(FSMInLearn.original_phrase)
    # Сохряняем выбранную фразу в хранилище состояний
    await state.update_data(current_phrase=callback.data)
    # logging.warning(await state.get_data())
    # Добавляем в "базу данных" данные пользователя
    # по ключу id пользователя
    user_dict[callback.from_user.id] = await state.get_data()
    logger.warning(f'current_phrase - {user_dict[callback.from_user.id]["current_phrase"]}')
    # Удаляем сообщение с кнопками, потому что следующий этап - загрузка голосового сообщения
    # чтобы у пользователя не было желания тыкать кнопки
    await callback.message.delete()
    # Тут нужно отправить оригинальный файл аудио
    await callback.message.answer_voice(
        FSInputFile(f'original_files/{callback.data}'),
        caption='Послушайте оригинал и попробуйте повторить'
    )


@router.callback_query()
async def process_phrase(callback: CallbackQuery):
    await callback.message.answer(text=callback.data)


# Хэндлер на голосовое сообщение
@router.message(F.voice, ~StateFilter(default_state))
async def process_send_voice(message: Message, bot: Bot, state: FSMContext):
    # Получаем голосовое сообщение и сохраняем на диск
    file_name = f"{message.from_user.id}_{datetime.datetime.now()}"
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"temp/{file_name}.ogg")
    await bot.download_file(file_path, destination=file_on_disk)

    logger.warning(f'ID пользователя {message.from_user.id} имя {message.from_user.first_name} '
                   f'фраза {user_dict[message.from_user.id]["current_phrase"]} '
                   f'файл - {file_on_disk}')
    # logging.debug(await state.get_state())
    # logger.warning(user_dict[message.from_user.id]["current_phrase"])

    original_file = f'original_files/{user_dict[message.from_user.id]["current_phrase"]}'
    # Распознавание речи на японском языке
    original_recognizer = SpeechRecognizer(original_file)
    original_text = original_recognizer.recognize_speech()
    spoken_recognizer = SpeechRecognizer(file_on_disk)
    spoken_text = spoken_recognizer.recognize_speech()

    # Загрузка аудиофайлов
    original_audio, sample_rate = librosa.load(original_file)
    spoken_audio, _ = librosa.load(file_on_disk, sr=sample_rate)

    visual = PronunciationVisualizer(original_audio, spoken_audio, sample_rate, file_name)
    await visual.preprocess_audio()
    await visual.plot_waveform()  # Визуализация графика звуковой волны

    photo = FSInputFile(f'temp/{file_name}.png')
    await message.answer_photo(photo,
                               caption=f'Оригинал {original_text}\nВаш вариант {spoken_text}')

    # os.remove(file_on_disk)  # Удаление временного файла
    # os.remove(f'temp/{file_name}.png')


# Этот хэндлер будет срабатывать на любые сообщения
@router.message()
async def send_echo(message: Message):
    await message.reply(text=LEXICON_RU['error'])
