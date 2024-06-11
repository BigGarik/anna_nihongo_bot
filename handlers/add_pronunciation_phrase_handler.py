import base64
import os

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from pydub import AudioSegment
from tortoise import fields, models
from aiogram.utils.i18n import gettext as _
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Select, Group, Cancel, Next, Back
from aiogram_dialog.widgets.text import Const, Format, Multi

from bot_init import bot
from external_services.openai_services import text_to_speech
from handlers.states import AddOriginalPhraseSG
from models import PronunciationCategory, PronunciationPhrase, AudioFile


# Функция для динамического создания кнопок
async def get_categories(**kwargs):
    categories = await PronunciationCategory.all()
    items = [(category.name, str(category.id)) for category in categories]
    return {'categories': items}


def second_state_audio_getter(data, widget, dialog_manager: DialogManager):
    return 'audio' in dialog_manager.dialog_data


def first_state_audio_getter(data, widget, dialog_manager: DialogManager):
    return not second_state_audio_getter(data, widget, dialog_manager)


# Это хэндлер, срабатывающий на ввод категории пользователем
async def category_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    # Добавить категорию в dialog_data
    dialog_manager.dialog_data['category'] = text
    await PronunciationCategory.create(name=text)
    await dialog_manager.next()


# Это хэндлер, срабатывающий на нажатие кнопки с категорией фразы
async def category_selection(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    category = await PronunciationCategory.get_or_none(id=item_id)
    dialog_manager.dialog_data['category'] = category.name
    await dialog_manager.next()


async def text_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    dialog_manager.dialog_data['text'] = text
    await dialog_manager.next()


async def translation_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                            text: str) -> None:
    dialog_manager.dialog_data['translation'] = text
    await dialog_manager.next()


async def audio_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    file_id = message.audio.file_id if message.audio else message.voice.file_id
    if message.audio:
        file_name = message.audio.file_name
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, file_name)

        # Конвертирование аудио в формат .OGG с кодеком OPUS
        audio = AudioSegment.from_file(file_name)
        audio.export(f'{file_id}.ogg', format='ogg', codec='libopus')

        # Чтение сконвертированного аудио файла
        with open(f'{file_id}.ogg', 'rb') as f:
            audio_data = f.read()

        audio_data_base64 = base64.b64encode(audio_data).decode('utf-8')

        # Удаление временных файлов
        os.remove(file_name)
        os.remove(f'{file_id}.ogg')

        audio = {
            'tg_id': '',
            'audio': audio_data_base64
        }
        dialog_manager.dialog_data['audio'] = audio

    elif message.voice:
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, f'{file_id}.ogg')

        # Чтение голосового сообщения
        with open(f'{file_id}.ogg', 'rb') as f:
            audio_data = f.read()

        audio_data_base64 = base64.b64encode(audio_data).decode('utf-8')

        # Удаление временного файла
        os.remove(f'{file_id}.ogg')

        audio = {
            'tg_id': file_id,
            'audio': audio_data_base64
        }
        dialog_manager.dialog_data['audio'] = audio


async def ai_voice_message(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    text = dialog_manager.dialog_data['text']
    audio_data = await text_to_speech(text)
    audio = {
        'tg_id': '',
        'audio': audio_data
    }
    dialog_manager.dialog_data['audio'] = audio


async def save_audio(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if 'audio' in dialog_manager.dialog_data:
        await dialog_manager.next()
    else:
        await callback.answer("Пока нет аудио для сохранения")


async def image_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    # Обработчик для загрузки изображения
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    await bot.download_file(file_path, f'{file_id}.jpg')
    with open(f'{file_id}.jpg', 'rb') as f:
        image_data = f.read()
    image_data_base64 = base64.b64encode(image_data).decode('utf-8')
    os.remove(f'{file_id}.jpg')
    image = {'tg_id': file_id, 'image': image_data_base64}
    dialog_manager.dialog_data['image'] = image


async def ai_image(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # Функция для генерации изображения автоматически
    # Пример: image_data = await generate_image(dialog_manager.dialog_data['text'])
    image_data = 'base64_encoded_image_data'
    image = {'tg_id': '', 'image': image_data}
    dialog_manager.dialog_data['image'] = image


async def comment_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, text: str) -> None:
    dialog_manager.dialog_data['comment'] = text
    await dialog_manager.next()


async def save_phrase_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    category = await PronunciationCategory.get_or_none(name=dialog_manager.dialog_data['category'])
    audio = await AudioFile.create(tg_id=dialog_manager.dialog_data['audio']['tg_id'],
                                   audio=dialog_manager.dialog_data['audio']['audio'])
    await PronunciationPhrase.create(
        category=category,
        text=dialog_manager.dialog_data['text'],
        translation=dialog_manager.dialog_data['translation'],
        audio=audio,
    )


add_original_phrase_dialog = Dialog(
    Window(
        Const(text='Выберите категорию или напишите новую:'),
        Group(
            Select(
                Format('{item[0]}'),
                id='categ',
                item_id_getter=lambda x: x[1],
                items='categories',
                on_click=category_selection,
            ),
            width=2
        ),
        TextInput(
            id='category_input',
            on_success=category_input,
        ),
        Group(
            Cancel(Const('❌ Отмена'), id='button_cancel'),
            Next(Const('▶️ Пропустить'), id='next'),
            width=3
        ),
        state=AddOriginalPhraseSG.category,
        getter=get_categories
    ),

    # ввести текст text = State()
    Window(
        Const(text='Введите текст новой фразы:'),
        TextInput(
            id='text_input',
            on_success=text_input,
        ),
        Group(
            Back(Const('◀️ Назад'), id='back'),
            Cancel(Const('❌ Отмена'), id='button_cancel'),
            Next(Const('▶️ Пропустить'), id='next'),
            width=3
        ),
        state=AddOriginalPhraseSG.text
    ),

    # translation = State()
    Window(
        Const(text='Введите перевод новой фразы или жмите "Пропустить" и я переведу автоматически:'),
        TextInput(
            id='translation_input',
            on_success=translation_input,
        ),
        Group(
            Back(Const('◀️ Назад'), id='back'),
            Cancel(Const('❌ Отмена'), id='button_cancel'),
            Next(Const('▶️ Пропустить'), id='next'),
            width=3
        ),
        state=AddOriginalPhraseSG.translation
    ),

    # audio = State()
    Window(
        Multi(
            Const('<b>Добавление аудио</b>'),
            Const('Сейчас отправьте мне аудио новой фразы, '
                  'голосовое сообщение или нажмите <code>Озвучить с помощью ИИ</code>.',
                  when=first_state_audio_getter),
            Const('Если все ОК, жми <code>Сохранить</code> или отправь еще раз',
                  when=second_state_audio_getter),
            sep='\n\n'
        ),
        MessageInput(
            func=audio_handler,
            content_types=[ContentType.AUDIO, ContentType.VOICE],
        ),
        Button(Const('🤖 Озвучить с помощью ИИ'), id='voice_message', on_click=ai_voice_message),
        Group(
            Back(Const('◀️ Назад'), id='back'),
            Cancel(Const('❌ Отмена'), id='button_cancel'),
            Button(Const('✅ Сохранить'), id='save', on_click=save_audio),
            # Next(Const('▶️ Пропустить'), id='next'),
            width=3
        ),
        state=AddOriginalPhraseSG.audio
    ),

    # image = State()
    Window(
        Const(text='Отправьте иллюстрацию для фразы, сгенерируйте или просто пропустите этот шаг:'),
        MessageInput(func=image_handler, content_types=[ContentType.PHOTO]),
        Button(Const('🖼 Сгенерировать'), id='ai_image', on_click=ai_image),
        Group(
            Back(Const('◀️ Назад'), id='back'),
            Cancel(Const('❌ Отмена'), id='button_cancel'),
            Next(Const('▶️ Пропустить'), id='next'),
            width=3
        ),
        state=AddOriginalPhraseSG.image
    ),

    # comment = State()
    Window(
        Const(text='Здесь можно добавить комментарий к фразе:'),
        TextInput(id='comment_input', on_success=comment_input),
        Group(
            Back(Const('◀️ Назад'), id='back'),
            Cancel(Const('❌ Отмена'), id='button_cancel'),
            Next(Const('▶️ Пропустить'), id='next'),
            width=3
        ),
        state=AddOriginalPhraseSG.comment
    ),
    # save = State()
    Window(
        Multi(
            Format('Суммарная информация'),
            Const(text='Сохранить фразу?'),
        ),
        Group(
            Back(Const('◀️ Назад'), id='back'),
            Cancel(Const('❌ Отмена'), id='button_cancel'),
            Button(
                text=Const('✅ Сохранить'),
                id='save_phrase',
                on_click=save_phrase_button_clicked,
            ),
            width=3
        ),
        state=AddOriginalPhraseSG.save
    ),
)
