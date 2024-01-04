import asyncio
import logging
import os
import visualizer
import soundfile as sf

import numpy as np
from visualizer import PronunciationVisualizer
from aiogram import Bot, Dispatcher, types
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from pathlib import Path

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)
# Объект бота
bot = Bot(token="6983818183:AAEaUcHTbxoDIR9dc1Or3FR2r5WfEGUGQL0")
# Диспетчер
dp = Dispatcher()


# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")


# Хэндлер на голосовое сообщение
@dp.message(F.voice)
async def process_send_voice(message: Message):
    file_id = message.voice.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    file_on_disk = Path("", f"{file_id}.ogg")
    await bot.download_file(file_path, destination=file_on_disk)

    original_audio, original_sample_rate = sf.read('sumimasen.ogg')
    spoken_audio, spoken_sample_rate = sf.read(file_on_disk)

    # Приведение аудиофайлов к одной длине
    min_length = min(len(original_audio), len(spoken_audio))
    original_audio = original_audio[:min_length]
    spoken_audio = spoken_audio[:min_length]

    # Нормализация громкости аудиофайлов
    max_amplitude = max(np.max(np.abs(original_audio)), np.max(np.abs(spoken_audio)))
    original_audio /= max_amplitude
    spoken_audio /= max_amplitude

    visual = PronunciationVisualizer(original_audio, spoken_audio, original_sample_rate)
    visual.plot_waveform()  # Визуализация графика звуковой волны

    photo = FSInputFile('voice.png')
    await message.answer_photo(photo, caption='ваш вариант')

    os.remove(file_on_disk)  # Удаление временного файла


# Запуск процесса поллинга новых апдейтов
async def main():
    # Где-то в другом месте, например, в функции main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
