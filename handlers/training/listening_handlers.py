import re

from aiogram.types import BufferedInputFile, Message, CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from external_services.google_cloud_services import google_text_to_speech
from .states import TextToSpeechSG
from .. import main_page_button_clicked
from models import TextToSpeech


async def phrase_to_speech(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    user_id = message.from_user.id
    # Создать имя файла из строки
    filename = re.sub(r'[^\w\s-]', '', text).replace(' ', '_')
    # проверить есть ли в базе уже такая фраза
    voice = await TextToSpeech.filter(text=filename).first()

    if voice:
        await message.answer_voice(voice=voice.voice_id, caption=f'{text}\nСлушайте и повторяйте')

    else:
        response = google_text_to_speech('ja-JP-Wavenet-A', text)
        voice = BufferedInputFile(response.audio_content, filename="voice_tts.txt")
        msg = await message.answer_voice(voice=voice, caption=f'{text}\nСлушайте и повторяйте')
        voice_id = msg.voice.file_id
        await TextToSpeech.create(
            voice_id=voice_id,
            user_id=user_id,
            text=filename,
            voice=response.audio_content,
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
        state=TextToSpeechSG.start
    ),
)
