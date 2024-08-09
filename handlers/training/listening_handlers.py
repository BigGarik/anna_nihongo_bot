import re

from aiogram.enums import ContentType
from aiogram.types import BufferedInputFile, Message
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Group

from bot_init import bot
from external_services.google_cloud_services import google_text_to_speech
from handlers.system_handlers import check_day_counter
from models import TextToSpeech, Subscription, User
from services.i18n_format import I18NFormat, I18N_FORMAT_KEY
from states import TextToSpeechSG


async def get_data(dialog_manager: DialogManager, **kwargs):
    first_time = dialog_manager.current_context().dialog_data.get("first_open", True)
    if first_time:
        dialog_manager.current_context().dialog_data["first_open"] = False
    return {
        "show_widget": first_time
    }


async def phrase_to_speech(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    if len(text) >= 150:
        await message.answer(i18n_format('sentence-too-long'))
    else:
        user_id = dialog_manager.event.from_user.id
        is_day_counter = await check_day_counter(dialog_manager)
        if is_day_counter:
            # Создать имя файла из строки
            filename = re.sub(r'[^\w\s-]', '', text).replace(' ', '_')
            # проверить есть ли в базе уже такая фраза
            voice = await TextToSpeech.filter(text=filename).first()

            if voice:
                await message.answer_voice(voice=voice.voice_id, caption=f'{text}')

            else:
                response = await google_text_to_speech(text)
                voice = BufferedInputFile(response.audio_content, filename="voice_tts.txt")
                msg = await message.answer_voice(voice=voice, caption=f'{text}')
                voice_id = msg.voice.file_id
                await TextToSpeech.create(
                    voice_id=voice_id,
                    user_id=user_id,
                    text=filename,
                    voice=response.audio_content,
                )


async def voice_message_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager) -> None:
    # Обработать аудио от пользователя
    pass
    # await message.answer(message.from_user.first_name)


text_to_speech_dialog = Dialog(
    Window(
        I18NFormat('listening-training-dialog', when="show_widget"),
        I18NFormat('listen-repeat'),
        TextInput(
            id='tts_input',
            on_success=phrase_to_speech,
        ),
        MessageInput(
            func=voice_message_handler,
            content_types=ContentType.VOICE,
        ),
        Group(
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            width=3
        ),
        state=TextToSpeechSG.start,
        getter=get_data,
    ),
)
