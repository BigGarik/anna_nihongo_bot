import base64
import os

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram_dialog import DialogManager, Dialog, Window, ShowMode
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Group, Cancel, Next, Back
from aiogram_dialog.widgets.text import Format, Multi
from pydub import AudioSegment

from bot_init import bot
from external_services.google_cloud_services import google_text_to_speech
from external_services.kandinsky import generate_image
from external_services.openai_services import openai_gpt_translate, openai_gpt_add_space
from models import AudioFile, Category, Phrase, User
from services.i18n_format import I18NFormat
from services.services import remove_html_tags
from states import AddOriginalPhraseSG


def second_state_audio_getter(data, widget, dialog_manager: DialogManager):
    return 'audio' in dialog_manager.dialog_data


def first_state_audio_getter(data, widget, dialog_manager: DialogManager):
    return not second_state_audio_getter(data, widget, dialog_manager)


async def get_data(dialog_manager: DialogManager, **kwargs):
    category_id = dialog_manager.start_data.get('category_id')
    category = await Category.get_or_none(id=category_id)
    # Инициализируем response с именем категории
    response = {'category_name': category.name}

    # Получаем текст фразы
    text_phrase = dialog_manager.dialog_data.get('text_phrase', '')
    response['text_phrase'] = text_phrase

    # Получаем перевод фразы
    translation = dialog_manager.dialog_data.get('translation', '')
    response['translation'] = translation

    # Получаем комментарий
    comment = dialog_manager.dialog_data.get('comment', '')
    response['comment'] = comment

    return response


async def text_phrase_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                            text_phrase: str) -> None:
    phrase = await Phrase.get_or_none(text_phrase=text_phrase, user_id=message.from_user.id)
    if phrase:
        await bot.send_message(message.chat.id, 'Ты уже добавлял эту фразу. Попробуй что-нибудь еще 😉')
    else:
        dialog_manager.dialog_data['text_phrase'] = text_phrase
        spaced_phrase = openai_gpt_add_space(text_phrase)
        dialog_manager.dialog_data['spaced_phrase'] = spaced_phrase
        await dialog_manager.next()


async def translation_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                            translation: str) -> None:
    dialog_manager.dialog_data['translation'] = remove_html_tags(translation)
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

    await dialog_manager.next(show_mode=ShowMode.SEND)


async def image_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    image_id = message.photo[-1].file_id
    dialog_manager.dialog_data['image_id'] = image_id
    await dialog_manager.next()


async def ai_image(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await callback.message.answer('Начинаю генерацию изображения. Это может занять некоторое время...')
    # Функция для генерации изображения автоматически
    # Получаем API ключи
    api_key = os.getenv('KANDINSKY_API_KEY')
    secret_key = os.getenv('KANDINSKY_SECRET_KEY')
    # Генерируем изображение
    images = await generate_image(api_key, secret_key, dialog_manager.dialog_data['text_phrase'])

    if images and len(images) > 0:
        # Декодируем изображение из Base64
        image_data = base64.b64decode(images[0])
        image = BufferedInputFile(image_data, filename="image.png")
        # Отправляем изображение
        msg = await callback.message.answer_photo(photo=image, caption="Вот сгенерированное изображение!")
        image_id = msg.photo[-1].file_id
        dialog_manager.dialog_data['image_id'] = image_id
        await dialog_manager.next(show_mode=ShowMode.SEND)
    else:
        await callback.message.answer("Извините, не удалось сгенерировать изображение.")



async def comment_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                        comment: str) -> None:
    dialog_manager.dialog_data['comment'] = remove_html_tags(comment)
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

    new_phrase = [phrase.text_phrase, phrase.id]

    await dialog_manager.done(result={"new_phrase": new_phrase})


add_original_phrase_dialog = Dialog(
    Window(
        Multi(
            I18NFormat('<b>Категория:</b> {category_name}\n'),
            I18NFormat(text='💬 Введи текст новой фразы:'),
        ),

        TextInput(
            id='text_phrase_input',
            on_success=text_phrase_input,
        ),
        Group(
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            width=3
        ),
        getter=get_data,
        state=AddOriginalPhraseSG.text_phrase
    ),
    # translation = State()
    Window(
        Multi(
            I18NFormat('<b>Категория:</b> {category_name}'),
            I18NFormat('<b>Текст:</b> {text_phrase}\n'),
            I18NFormat(text='🌐 Введи перевод новой фразы или жми "Пропустить" и я переведу автоматически:'),
        ),

        TextInput(
            id='translation_input',
            on_success=translation_input,
        ),
        Group(
            Back(I18NFormat('back'), id='back'),
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            Next(I18NFormat('next'), id='next', on_click=translate_phrase),
            width=3
        ),
        getter=get_data,
        state=AddOriginalPhraseSG.translation
    ),

    # audio = State()
    Window(
        Multi(
            Format('<b>Категория:</b> {category_name}'),
            Format('<b>Текст:</b> {text_phrase}'),
            Format('<b>Перевод:</b> {translation}\n'),
        ),
        Multi(
            I18NFormat('<b>Добавление аудио</b>'),
            I18NFormat('🔊 Отправь мне аудио новой фразы, '
                  'голосовое сообщение или нажми <b>Озвучить с помощью ИИ</b>.',
                  when=first_state_audio_getter),
            I18NFormat('Если все ОК, жми <b>Сохранить</b> или отправь еще раз',
                  when=second_state_audio_getter),
            sep='\n\n'
        ),
        MessageInput(
            func=audio_handler,
            content_types=[ContentType.AUDIO, ContentType.VOICE],
        ),
        Button(I18NFormat('🤖 Озвучить с помощью ИИ'), id='voice_message', on_click=ai_voice_message),
        Group(
            Back(I18NFormat('back'), id='back'),
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            # Button(I18NFormat('✅ Сохранить'), id='save', on_click=save_audio),
            # Next(I18NFormat('next'), id='next'),
            width=3
        ),
        getter=get_data,
        state=AddOriginalPhraseSG.audio
    ),

    # image = State()
    Window(
        Multi(
            Format('<b>Категория:</b> {category_name}'),
            Format('<b>Текст:</b> {text_phrase}'),
            Format('<b>Перевод:</b> {translation}\n'),
        ),
        I18NFormat(text='<b>🎨 Отправь иллюстрацию для фразы, или просто пропусти этот шаг:</b>'),
        MessageInput(func=image_handler, content_types=[ContentType.PHOTO]),
        Button(I18NFormat('generate-image-button'), id='ai_image', on_click=ai_image),
        Group(
            Back(I18NFormat('back'), id='back'),
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            Next(I18NFormat('next'), id='next'),
            width=3
        ),
        getter=get_data,
        state=AddOriginalPhraseSG.image
    ),

    # comment = State()
    Window(
        Multi(
            Format('<b>Категория:</b> {category_name}'),
            Format('<b>Текст:</b> {text_phrase}'),
            Format('<b>Перевод:</b> {translation}\n'),
        ),
        I18NFormat(text='<b>Здесь можно добавить комментарий к фразе:</b>'),
        TextInput(id='comment_input', on_success=comment_input),
        Group(
            Back(I18NFormat('back'), id='back'),
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            Next(I18NFormat('next'), id='next', on_click=comment_next_button_clicked),
            width=3
        ),
        getter=get_data,
        state=AddOriginalPhraseSG.comment
    ),
    # save = State()
    Window(
        Multi(
            I18NFormat('Суммарная информация\n'),
            I18NFormat('<b>Категория:</b> {category_name}'),
            I18NFormat('<b>Текст:</b> {text_phrase}'),
            I18NFormat('<b>Перевод:</b> {translation}'),
            I18NFormat('<b>Комментарий:</b> {comment}\n'),
            I18NFormat(text='<b>Сохранить фразу?</b>'),
        ),
        Group(
            Back(I18NFormat('back'), id='back'),
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            Button(
                text=I18NFormat('✅ Сохранить'),
                id='save_phrase',
                on_click=save_phrase_button_clicked,
            ),
            width=3
        ),
        getter=get_data,
        state=AddOriginalPhraseSG.save
    ),
)
