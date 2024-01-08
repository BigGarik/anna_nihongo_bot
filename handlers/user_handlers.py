from aiogram import Router, F, Bot
from aiogram.types import Message, FSInputFile
from aiogram.filters import Command, CommandStart
from pathlib import Path

from voice_recognizer import SpeechRecognizer
from visualizer import PronunciationVisualizer
from original_files import original_files as files

import lexicon
import logging
import datetime
import librosa

# Инициализируем роутер уровня модуля
router = Router()


# Этот хэндлер срабатывает на команду /start
@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(text=lexicon.lexicon_ru.hello)


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=lexicon.lexicon_ru.help)


# Хэндлер на голосовое сообщение
@router.message(F.voice)
async def process_send_voice(message: Message, bot: Bot):
    logging.info(f'ID пользователя {message.from_user.id}')
    file_name = f"{message.from_user.id}_{datetime.datetime.now()}"
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"temp/{file_name}.oga")
    await bot.download_file(file_path, destination=file_on_disk)

    # Распознавание речи на японском языке
    original_recognizer = SpeechRecognizer(files[0]['path'])
    original_text = original_recognizer.recognize_speech()
    spoken_recognizer = SpeechRecognizer(file_on_disk)
    spoken_text = spoken_recognizer.recognize_speech()

    # Загрузка аудиофайлов
    original_audio, sample_rate = librosa.load(files[0]['path'])
    spoken_audio, _ = librosa.load(file_on_disk, sr=sample_rate)

    visual = PronunciationVisualizer(original_audio, spoken_audio, sample_rate, file_name)
    await visual.preprocess_audio()
    await visual.plot_waveform()  # Визуализация графика звуковой волны

    photo = FSInputFile(f'temp/{file_name}.png')
    await message.answer_photo(photo,
                               caption=f'Оригинал {original_text} ({files[0]["translation"]})\nВаш вариант {spoken_text}')

    # os.remove(file_on_disk)  # Удаление временного файла
    # os.remove(f'temp/{file_name}.png')
