import os
import subprocess
from typing import Dict, List, Any

import azure.cognitiveservices.speech as speechsdk
import pykakasi

# from bot import config

# speech_key = config.azure.speech_key
# service_region = config.azure.service_region
# language = os.getenv('LOCATION')
speech_key = "EEQySvBXetcyZ2qrLkPEcZSH6JR1uVi05ikalyrcGraeFc6PDeXVJQQJ99ALACYeBjFXJ3w3AAAYACOGTzb2"
service_region = "eastus"

# reference_text = "I love going hiking when I camp"  # Ссылочный текст
# audio_file_path = "../AwACAgIAAxkBAAIS12bxBvIrUrnpbnw-_JVmLDbmYnalAAL9WwAC-e6JS5BbAzw8LT1aNgQtemp.wav"
# language = "en-US"

reference_text = "はじめまして、あんなです、どうぞよろしく。"  # Ссылочный текст
audio_file_path = "../media/bad.wav"
language = "ja-JP"


def convert_ogg_to_wav(ogg_file_path: str):
    """
    Конвертирует аудиофайл из формата OGG в WAV с частотой дискретизации 16 кГц.

    :param ogg_file_path: Путь к входному OGG файлу.
    :return: Путь к выходному WAV файлу.
    """
    wav_file_path = os.path.splitext(ogg_file_path)[0] + ".wav"
    try:
        subprocess.run([
            "ffmpeg", "-i", ogg_file_path, "-ar", "16000", "-ac", "1", wav_file_path
        ], check=True)
        print(f"Файл успешно сконвертирован: {wav_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при конвертации файла: {e}")
        wav_file_path = None
    return wav_file_path


def speech_recognize_once_from_file():
    """performs one-shot speech recognition with input from an audio file"""

    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
    speech_config.set_property_by_name("OPENSSL_DISABLE_CRL_CHECK", "true")
    audio_config = speechsdk.audio.AudioConfig(filename=audio_file_path)
    # Creates a speech recognizer using a file as audio input, also specify the speech language
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, language=language, audio_config=audio_config)

    result = speech_recognizer.recognize_once()

    # Check the result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))


# Функция для анализа произношения с помощью Azure Cognitive Services Speech SDK
def analyze_pronunciation_azure(subscription_key, region, audio_file_path: str, reference_text: str):
    """
    Анализирует произношение записанного аудио файла с ссылочным текстом (если предоставлен) и выводит обратную связь.

    :param audio_file_path: Путь к записи аудио файла (.wav)
    :param reference_text: Оригинальный текст для сравнения
    :param subscription_key: Подписочный ключ аккаунта Azure Cognitive Services
    :param region: Регион Azure
    """

    # Инициализация Speech SDK
    speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
    audio_config = speechsdk.AudioConfig(filename=audio_file_path)

    pronunciation_assessment_config = speechsdk.PronunciationAssessmentConfig(
        reference_text=reference_text,
        grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
        granularity=speechsdk.PronunciationAssessmentGranularity.Phoneme,
        enable_miscue=True
    )
    # pronunciation_assessment_config.phoneme_alphabet = 'IPA'

    # Создание распознавателя
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config,
        language=language,
        audio_config=audio_config)
    pronunciation_assessment_config.apply_to(speech_recognizer)

    result = speech_recognizer.recognize_once()

    # Обработка результатов
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        pronunciation_assessment_result_json = result.properties.get(
            speechsdk.PropertyId.SpeechServiceResponse_JsonResult)
        return pronunciation_assessment_result_json
    else:
        print(f"Recognition failed: {result.reason}")
        if result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print(f"Cancellation reason: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print(f"Error details: {cancellation_details.error_details}")


def process_japanese_text(json_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Обрабатывает JSON данные, добавляя слоги и фонемы (ромадзи) для японского текста.

    Args:
        json_data: Словарь с данными для обработки

    Returns:
        Dict с дополненными данными о слогах и фонемах
    """
    kks = pykakasi.kakasi()

    def get_phonemes_and_syllables(text: str) -> tuple[List[str], List[str]]:
        """
        Извлекает фонемы (ромадзи) и слоги из японского текста.

        Args:
            text: Японский текст для обработки

        Returns:
            Tuple из списков фонем (ромадзи) и слогов
        """
        result = kks.convert(text)

        # Получаем хирагану для слогов
        syllables = list(''.join(item['hira'] for item in result))

        # Получаем ромадзи для фонем
        # Разбиваем каждый элемент ромадзи на отдельные символы
        phonemes = []
        for item in result:
            phonemes.extend(list(item['hepburn']))

        return phonemes, syllables

    # Обрабатываем каждое слово в JSON
    for nbest in json_data.get('NBest', []):
        for word_data in nbest.get('Words', []):
            word = word_data.get('Word', '')
            if not word:
                continue

            phonemes, syllables = get_phonemes_and_syllables(word)

            # Обновляем слоги
            for i, syllable in enumerate(syllables):
                if i < len(word_data.get('Syllables', [])):
                    word_data['Syllables'][i]['Syllable'] = syllable

            # Обновляем фонемы
            for i, phoneme in enumerate(phonemes):
                if i < len(word_data.get('Phonemes', [])):
                    word_data['Phonemes'][i]['Phoneme'] = phoneme

    return json_data


# Пример вызова функции
if __name__ == "__main__":
    # analyze_pronunciation_azure(speech_key, service_region, audio_file_path, reference_text)
    print(analyze_pronunciation_azure(speech_key, service_region, audio_file_path, reference_text))
