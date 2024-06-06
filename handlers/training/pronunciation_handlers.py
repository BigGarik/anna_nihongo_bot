from aiogram.enums import ContentType

from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Const

from .states import PronunciationTrainingSG
from .. import main_page_button_clicked


async def voice_message_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager) -> None:
    await message.send_copy(message.chat.id)


pronunciation_training_dialog = Dialog(
    Window(
        Const('Отправь мне сообщение и мы потренируемся в произношении'),
        MessageInput(
            func=voice_message_handler,
            content_types=ContentType.VOICE,
        ),
        Cancel(Const('❌ Отмена'), id='button_cancel'),
        state=PronunciationTrainingSG.start
    ),
)
