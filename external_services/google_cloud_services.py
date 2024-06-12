import os
from typing import Sequence
import google.cloud.texttospeech as tts
from dotenv import load_dotenv

load_dotenv()
voice_name = os.getenv('VOICE_NAME')

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "anna-nihongo-bot-96c6f518f0cd.json"


def unique_languages_from_voices(voices: Sequence[tts.Voice]):
    language_set = set()
    for voice in voices:
        for language_code in voice.language_codes:
            language_set.add(language_code)
    return language_set


def list_languages():
    client = tts.TextToSpeechClient()
    response = client.list_voices()
    languages = unique_languages_from_voices(response.voices)

    print(f" Languages: {len(languages)} ".center(60, "-"))
    for i, language in enumerate(sorted(languages)):
        print(f"{language:>10}", end="\n" if i % 5 == 4 else "")


def list_voices(language_code=None):
    client = tts.TextToSpeechClient()
    response = client.list_voices(language_code=language_code)
    voices = sorted(response.voices, key=lambda voice: voice.name)

    print(f" Voices: {len(voices)} ".center(60, "-"))
    for voice in voices:
        languages = ", ".join(voice.language_codes)
        name = voice.name
        gender = tts.SsmlVoiceGender(voice.ssml_gender).name
        rate = voice.natural_sample_rate_hertz
        print(f"{languages:<8} | {name:<24} | {gender:<8} | {rate:,} Hz")


def google_text_to_speech(text: str):
    language_code = "-".join(voice_name.split("-")[:2])
    text_input = tts.SynthesisInput(text=text)
    voice_params = tts.VoiceSelectionParams( language_code=language_code, name=voice_name)
    audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.OGG_OPUS)

    client = tts.TextToSpeechClient()
    response = client.synthesize_speech(
        input=text_input,
        voice=voice_params,
        audio_config=audio_config,
    )
    #
    # filename = f"{voice_name}.ogg"
    # with open(filename, "wb") as out:
    #     out.write(response.audio_content)
    #     print(f'Generated speech saved to "{filename}"')
    return response
