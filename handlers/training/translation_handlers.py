from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput, TextInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Group, Cancel, Select
from aiogram_dialog.widgets.text import Const, Format, Multi

from models import Phrase, User, UserAnswer
from services.services import normalize_text
from states import TranslationTrainingSG
from ..system_handlers import get_random_phrase, get_user_categories, first_answer_getter, second_answer_getter, \
    get_context


async def category_selection(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    await get_random_phrase(dialog_manager, item_id)

    await dialog_manager.next()


async def check_answer_text(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                            answer_text: str):
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
        await message.answer('🏆 Ура!!! Ты лучший! 🥳')
        # voice_id = dialog_manager.dialog_data['audio_id']
        # if voice_id:
        #     await bot.send_voice(chat_id=message.from_user.id, voice=voice_id)
        dialog_manager.dialog_data.pop('answer', None)
        category_id = dialog_manager.dialog_data['category_id']
        await get_random_phrase(dialog_manager, category_id)

    else:
        dialog_manager.dialog_data['counter'] += 1
        user_answer.result = False
    await user_answer.save()


async def error_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    await message.answer('Моя твоя не понимать 🤔')


translation_training_dialog = Dialog(
    Window(
        Const('Раздел для тренировки перевода.'),
        Const(text='Выбирай категорию:'),
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
            Cancel(Const('↩️ Отмена'), id='button_cancel'),
            width=3
        ),
        getter=get_user_categories,
        state=TranslationTrainingSG.start
    ),
    Window(
        Multi(
            Format('Выбранная категория: <b>{category}</b>'),
            Format('Фраза:\n <b>{translation}</b>'),
            Const('Попробуй еще раз ))',
                  when=first_answer_getter),
            Const('Введи перевод фразы:',
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
            Cancel(Const('↩️ Отмена'), id='button_cancel'),
            width=3
        ),
        getter=get_context,
        state=TranslationTrainingSG.waiting_answer,
    ),
)
