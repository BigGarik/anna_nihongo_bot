import asyncio
import logging
import os
import sys
import lexicon
import librosa

import visualizer
import soundfile as sf

import numpy as np
from recognizer import SpeechRecognizer
from visualizer import PronunciationVisualizer
from aiogram import Bot, Dispatcher, types
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from pathlib import Path
from original_files import original_files as files
from config import load_config

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO,
                    format='[{asctime}] #{levelname:8} {filename}:'
                           '{lineno} - {name} - {message}',
                    style='{'
                    )
logger = logging.getLogger(__name__)
# Инициализируем хэндлер, который будет перенаправлять логи в stdout
stdout_handler = logging.StreamHandler(sys.stdout)
# Добавляем хэндлеры логгеру
logger.addHandler(stdout_handler)

config = load_config('.env')
# Объект бота
bot = Bot(token=config.tg_bot.token)
# Диспетчер
dp = Dispatcher()


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(lexicon.lexicon_ru.hello)


# Хэндлер на голосовое сообщение
@dp.message(F.voice)
async def process_send_voice(message: Message):
    logging.info(f'ID пользователя {message.from_user.id}')
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"temp/{file_id}.oga")
    await bot.download_file(file_path, destination=file_on_disk)

    # Распознавание речи на японском языке
    original_recognizer = SpeechRecognizer(files[0]['path'])
    original_text = original_recognizer.recognize_speech()
    spoken_recognizer = SpeechRecognizer(file_on_disk)
    spoken_text = spoken_recognizer.recognize_speech()

    # Загрузка аудиофайлов
    original_audio, sample_rate = librosa.load(files[0]['path'])
    spoken_audio, _ = librosa.load(file_on_disk, sr=sample_rate)

    visual = PronunciationVisualizer(original_audio, spoken_audio, sample_rate, file_id)
    await visual.preprocess_audio()
    await visual.plot_waveform()  # Визуализация графика звуковой волны

    photo = FSInputFile(f'temp/{file_id}.png')
    await message.answer_photo(photo, caption=f'Оригинал {original_text} ({files[0]["translation"]})\nВаш вариант {spoken_text}')

    os.remove(file_on_disk)  # Удаление временного файла
    os.remove(f'temp/{file_id}.png')


# Запуск процесса поллинга новых апдейтов
async def main():
    # Где-то в другом месте, например, в функции main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
