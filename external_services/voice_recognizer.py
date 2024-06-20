import logging
import os

import speech_recognition as sr
from dotenv import load_dotenv
from pydub import AudioSegment
from speech_recognition import UnknownValueError

from lexicon.lexicon_ru import LEXICON_RU

logger = logging.getLogger(__name__)

load_dotenv()
location = os.getenv('LOCATION')


class SpeechRecognizer:
    def __init__(self, spoken_file, voice_id):
        self.spoken_file = spoken_file
        self.voice_id = voice_id

    def recognize_speech(self):
        recognizer = sr.Recognizer()

        # Загрузка аудиофайла и конвертация во временный WAV-файл
        audio = AudioSegment.from_ogg(self.spoken_file)
        audio.export(f"{self.voice_id}temp.wav", format="wav")

        # Распознавание речи на японском языке из временного WAV-файла
        with sr.AudioFile(f"{self.voice_id}temp.wav") as source:
            audio_data = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio_data, language=location)
            # text = recognizer.recognize_google(audio_data, language="en-US")
            except UnknownValueError:
                text = LEXICON_RU['value_error']

        # Удаление временного WAV-файла
        os.remove(f"{self.voice_id}temp.wav")

        return text

    def check_pronunciation(self, text):
        # Здесь можно добавить логику для проверки произношения и предоставления рекомендаций
        # Например, использовать библиотеку для обработки текста и анализа речи на японском языке

        # Вернуть заглушку для примера
        return "Нет рекомендаций на данный момент."
