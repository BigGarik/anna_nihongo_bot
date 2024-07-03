from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import MessageInput, TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Group, Cancel, Select, Back, Button
from aiogram_dialog.widgets.text import Format, Multi

from models import Phrase, User, UserAnswer
from services.i18n_format import I18NFormat, I18N_FORMAT_KEY, default_format_text
from services.services import normalize_text
from states import TranslationTrainingSG
from ..system_handlers import get_random_phrase, get_user_categories, first_answer_getter, second_answer_getter, \
    get_context


async def category_selection(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    await get_random_phrase(dialog_manager, item_id)
    await dialog_manager.next()


async def next_phrase_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    category_id = dialog_manager.dialog_data['category_id']
    await get_random_phrase(dialog_manager, category_id)


async def check_answer_text(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                            answer_text: str):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY, default_format_text)
    dialog_manager.dialog_data['answer'] = answer_text
    text_phrase = dialog_manager.dialog_data['question']
    phrase = await Phrase.get_or_none(text_phrase=text_phrase)
    user_id = dialog_manager.event.from_user.id
    user = await User.get_or_none(id=user_id)
    user_answer = UserAnswer(
        user=user,
        phrase=phrase,
        answer_text=answer_text,
        exercise='translation'
    )
    normalized_question = normalize_text(text_phrase)
    normalized_answer = normalize_text(answer_text)
    if normalized_question == normalized_answer:
        dialog_manager.dialog_data['counter'] = 0
        user_answer.result = True
        await message.answer(i18n_format('congratulations'))
        dialog_manager.dialog_data.pop('answer', None)
        category_id = dialog_manager.dialog_data['category_id']
        await get_random_phrase(dialog_manager, category_id)

    else:
        dialog_manager.dialog_data['counter'] += 1
        user_answer.result = False
    await user_answer.save()


async def error_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY, default_format_text)
    await message.answer(i18n_format('error-handler'))


translation_training_dialog = Dialog(
    Window(
        I18NFormat('translate-training-dialog'),
        Group(
            Select(
                Format('{item[0]}'),
                id='category',
                item_id_getter=lambda x: x[1],
                items='categories',
                on_click=category_selection,
            ),
            width=2
        ),
        Group(
            Select(
                Format('{item[0]}'),
                id='cat_for_all',
                item_id_getter=lambda x: x[1],
                items='categories_for_all',
                on_click=category_selection,
            ),
            width=2
        ),
        Group(
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            width=3
        ),
        getter=get_user_categories,
        state=TranslationTrainingSG.start
    ),
    Window(
        Multi(
            I18NFormat('training-category'),
            I18NFormat('translate-training-phrase'),
            I18NFormat('translate-training'),
            I18NFormat('training-try-again',
                       when=first_answer_getter),
            I18NFormat('enter-answer-text',
                       when=second_answer_getter),
            sep='\n\n'
        ),
        TextInput(
            id='answer_input',
            on_success=check_answer_text,
        ),
        MessageInput(
            func=error_handler,
            content_types=ContentType.ANY,
        ),
        Group(
            Back(I18NFormat('back'), id='back'),
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            Button(
                text=I18NFormat('next'),
                id='next_phrase',
                on_click=next_phrase_button_clicked,
            ),
            width=3
        ),
        getter=get_context,
        state=TranslationTrainingSG.waiting_answer,
    ),
)
