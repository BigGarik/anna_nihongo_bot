from aiogram.types import Message
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Row, Group
from aiogram_dialog.widgets.text import Const

from bot_init import bot
from external_services.openai_services import gpt_add_space
from models import User
from models.phrase import LexisPhrase
from services.services import replace_random_words
from .states import LexisTrainingSG
from .. import main_page_button_clicked


async def lexis_training_text(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):
    # Запикать звездочками часть слов
    spaced_phrase = gpt_add_space(text)
    if not await LexisPhrase.get(phrase=text):
        user = User.get(id=message.from_user.id)
        await LexisPhrase.create(phrase=text, spaced_phrase=spaced_phrase, user=user)
    with_gap_phrase = replace_random_words(spaced_phrase)
    # Удаление сообщения пользователя
    await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)

    await message.answer(with_gap_phrase)
    await dialog_manager.next()


async def check_answer_text(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str):

    pass


lexis_training_dialog = Dialog(
    Window(
        Const('Отправь мне сообщение и мы потренируемся в грамматике'),
        TextInput(
            id='grammar_training_text_input',
            on_success=lexis_training_text,
        ),
        Group(
            Cancel(Const('❌ Отмена'), id='button_cancel'),
            Button(
                text=Const('🏠 На главную'),
                id='main_page',
                on_click=main_page_button_clicked,
            ),
            width=3
        ),
        state=LexisTrainingSG.start
    ),
    Window(
        Const('Отправь ответ'),
        TextInput(
            id='answer_input',
            on_success=check_answer_text,
        ),
        Group(
            Cancel(Const('❌ Отмена'), id='button_cancel'),
            Button(
                text=Const('🏠 На главную'),
                id='main_page',
                on_click=main_page_button_clicked,
            ),
            width=3
        ),
        state=LexisTrainingSG.waiting_answer,
    ),
)
