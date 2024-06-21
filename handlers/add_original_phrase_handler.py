import base64
import os

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Group, Cancel, Next, Back
from aiogram_dialog.widgets.text import Const, Format, Multi
from pydub import AudioSegment

from bot_init import bot
from external_services.google_cloud_services import google_text_to_speech
from external_services.openai_services import openai_gpt_translate, openai_gpt_add_space
from models import AudioFile, Category, Phrase, User
from states import AddOriginalPhraseSG


def second_state_audio_getter(data, widget, dialog_manager: DialogManager):
    return 'audio' in dialog_manager.dialog_data


def first_state_audio_getter(data, widget, dialog_manager: DialogManager):
    return not second_state_audio_getter(data, widget, dialog_manager)


async def get_data(dialog_manager: DialogManager, **kwargs):
    text_phrase = dialog_manager.dialog_data['text_phrase']
    translation = dialog_manager.dialog_data['translation']
    comment = dialog_manager.dialog_data['comment']
    audio_data = dialog_manager.dialog_data['audio_data']

    return {'text_phrase': text_phrase,
            'translation': translation,
            'comment': comment}


async def text_phrase_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                            text_phrase: str) -> None:
    dialog_manager.dialog_data['text_phrase'] = text_phrase
    spaced_phrase = openai_gpt_add_space(text_phrase)
    dialog_manager.dialog_data['spaced_phrase'] = spaced_phrase
    await dialog_manager.next()


async def translation_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                            translation: str) -> None:
    dialog_manager.dialog_data['translation'] = translation
    await dialog_manager.next()


async def translate_phrase(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    translation = openai_gpt_translate(dialog_manager.dialog_data['text_phrase'])
    dialog_manager.dialog_data['translation'] = translation


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

    await dialog_manager.next()


async def ai_voice_message(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    text_phrase = dialog_manager.dialog_data['text_phrase']

    text_to_speech = await google_text_to_speech(text_phrase)
    voice = BufferedInputFile(text_to_speech.audio_content, filename="voice_tts.ogg")
    msg = await callback.message.answer_voice(voice=voice, caption=f'Озвучка')
    voice_id = msg.voice.file_id

    audio = await AudioFile.create(
        tg_id=voice_id,
        audio=voice.data
    )

    audio_data = {
        'tg_id': voice_id,
        'audio_id': audio.id
    }
    dialog_manager.dialog_data['audio_data'] = audio_data

    await dialog_manager.next()


#
# async def save_audio(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
#     if 'audio' in dialog_manager.dialog_data:
#         await dialog_manager.next()
#     else:
#         await callback.answer("Пока нет аудио для сохранения")


async def image_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    image_id = message.photo[-1].file_id
    dialog_manager.dialog_data['image_id'] = image_id
    await dialog_manager.next()


async def ai_image(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # Функция для генерации изображения автоматически
    # Пример: image_data = await generate_image(dialog_manager.dialog_data['text'])
    image_data = 'base64_encoded_image_data'
    image = {'tg_id': '', 'image': image_data}
    dialog_manager.dialog_data['image'] = image


async def comment_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                        comment: str) -> None:
    dialog_manager.dialog_data['comment'] = comment
    await dialog_manager.next()


async def comment_next_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['comment'] = ''


async def save_phrase_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    category = await Category.get_or_none(id=dialog_manager.start_data['category_id'])
    user_id = dialog_manager.event.from_user.id
    user = await User.get_or_none(id=user_id)
    text_phrase = dialog_manager.dialog_data['text_phrase']
    voice_id = dialog_manager.dialog_data['audio_data']['tg_id']
    phrase = Phrase(
        category=category,
        user=user,
        text_phrase=text_phrase,
        audio_id=voice_id,
    )
    if dialog_manager.dialog_data.get('translation'):
        phrase.translation = dialog_manager.dialog_data['translation']
    if dialog_manager.dialog_data.get('image_id'):
        phrase.image_id = dialog_manager.dialog_data.get('image_id')
    if dialog_manager.dialog_data.get('comment'):
        phrase.comment = dialog_manager.dialog_data.get('comment')
    if dialog_manager.dialog_data.get('spaced_phrase'):
        phrase.spaced_phrase = dialog_manager.dialog_data.get('spaced_phrase')

    await phrase.save()
    await dialog_manager.done()


add_original_phrase_dialog = Dialog(
    Window(
        Const(text='Введите текст новой фразы:'),
        TextInput(
            id='text_phrase_input',
            on_success=text_phrase_input,
        ),
        Group(
            Cancel(Const('↩️ Отмена'), id='button_cancel'),
            width=3
        ),
        state=AddOriginalPhraseSG.text_phrase
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
            Cancel(Const('↩️ Отмена'), id='button_cancel'),
            Next(Const('▶️ Пропустить'), id='next', on_click=translate_phrase),
            width=3
        ),
        state=AddOriginalPhraseSG.translation
    ),

    # audio = State()
    Window(
        Multi(
            Const('<b>Добавление аудио</b>'),
            Const('Отправь мне аудио новой фразы, '
                  'голосовое сообщение или нажми <code>Озвучить с помощью ИИ</code>.',
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
            Cancel(Const('↩️ Отмена'), id='button_cancel'),
            # Button(Const('✅ Сохранить'), id='save', on_click=save_audio),
            # Next(Const('▶️ Пропустить'), id='next'),
            width=3
        ),
        state=AddOriginalPhraseSG.audio
    ),

    # image = State()
    Window(
        Const(text='Отправьте иллюстрацию для фразы, сгенерируйте или просто пропустите этот шаг:'),
        MessageInput(func=image_handler, content_types=[ContentType.PHOTO]),
        Button(Const('🖼 Сгенерировать (в разработке)'), id='ai_image', on_click=ai_image),
        Group(
            Back(Const('◀️ Назад'), id='back'),
            Cancel(Const('↩️ Отмена'), id='button_cancel'),
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
            Cancel(Const('↩️ Отмена'), id='button_cancel'),
            Next(Const('▶️ Пропустить'), id='next', on_click=comment_next_button_clicked),
            width=3
        ),
        state=AddOriginalPhraseSG.comment
    ),
    # save = State()
    Window(
        Multi(
            Format('Суммарная информация'),
            Format('{text_phrase}'),
            Format('{translation}'),
            Format('{comment}'),
            Const(text='Сохранить фразу?'),
        ),
        Group(
            Back(Const('◀️ Назад'), id='back'),
            Cancel(Const('↩️ Отмена'), id='button_cancel'),
            Button(
                text=Const('✅ Сохранить'),
                id='save_phrase',
                on_click=save_phrase_button_clicked,
            ),
            width=3
        ),
        getter=get_data,
        state=AddOriginalPhraseSG.save
    ),
)
