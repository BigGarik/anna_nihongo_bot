
from aiogram.types import Message
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from .states import GrammarTrainingSG
from .. import main_page_button_clicked


async def grammar_training_text(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    # Запикать звездочками часть слов

    pass


grammar_training_dialog = Dialog(
    Window(
        Const('Отправь мне сообщение и мы потренируемся в грамматике'),
        Button(
            text=Const('На главную'),
            id='main_page',
            on_click=main_page_button_clicked,
        ),
        TextInput(
            id='grammar_training_text_input',
            on_success=grammar_training_text,
        ),
        state=GrammarTrainingSG.start
    ),
    Window(

    ),
)

