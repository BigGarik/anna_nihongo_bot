import re

from aiogram.enums import ContentType
from aiogram.types import BufferedInputFile, Message
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Group
from aiogram_dialog.widgets.text import Const

from external_services.google_cloud_services import google_text_to_speech
from models import TextToSpeech
from states import TextToSpeechSG


async def phrase_to_speech(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    user_id = message.from_user.id
    # Создать имя файла из строки
    filename = re.sub(r'[^\w\s-]', '', text).replace(' ', '_')
    # проверить есть ли в базе уже такая фраза
    voice = await TextToSpeech.filter(text=filename).first()

    if voice:
        await message.answer_voice(voice=voice.voice_id, caption=f'{text}\nСлушайте и повторяйте')

    else:
        response = await google_text_to_speech(text)
        voice = BufferedInputFile(response.audio_content, filename="voice_tts.txt")
        msg = await message.answer_voice(voice=voice, caption=f'{text}\nСлушайте и повторяйте')
        voice_id = msg.voice.file_id
        await TextToSpeech.create(
            voice_id=voice_id,
            user_id=user_id,
            text=filename,
            voice=response.audio_content,
        )


async def voice_message_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager) -> None:
    # Обработать аудио от пользователя

    await message.answer(message.from_user.first_name)


text_to_speech_dialog = Dialog(
    Window(
        Const('Раздел для тренировки слушания.'),
        Const('Отправь мне фразу и я ее озвучу'),
        TextInput(
            id='tts_input',
            on_success=phrase_to_speech,
        ),
        MessageInput(
            func=voice_message_handler,
            content_types=ContentType.VOICE,
        ),
        Group(
            Cancel(Const('↩️ Отмена'), id='button_cancel'),
            width=3
        ),
        state=TextToSpeechSG.start
    ),
)
