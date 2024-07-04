import base64
import logging
import os

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message, BufferedInputFile
from aiogram_dialog import DialogManager, Dialog, Window, ShowMode
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Group, Cancel, Next, Back
from aiogram_dialog.widgets.text import Multi
from pydub import AudioSegment

from bot_init import bot
from external_services.google_cloud_services import google_text_to_speech
from external_services.kandinsky import generate_image
from external_services.openai_services import openai_gpt_translate, openai_gpt_add_space
from handlers.system_handlers import repeat_ai_generate_image
from models import AudioFile, Category, Phrase, User
from services.i18n_format import I18NFormat, I18N_FORMAT_KEY, default_format_text
from services.services import remove_html_tags
from states import AddOriginalPhraseSG


logger = logging.getLogger(__name__)


def second_state_audio_getter(data, widget, dialog_manager: DialogManager):
    return "audio" in dialog_manager.dialog_data


def first_state_audio_getter(data, widget, dialog_manager: DialogManager):
    return not second_state_audio_getter(data, widget, dialog_manager)


async def get_data(dialog_manager: DialogManager, **kwargs):
    category_id = dialog_manager.start_data.get("category_id")
    category = await Category.get_or_none(id=category_id)
    # Инициализируем response с именем категории
    response = {"category": category.name}

    # Получаем текст фразы
    text_phrase = dialog_manager.dialog_data.get("text_phrase", "")
    if text_phrase:
        is_text_phrase = True
    else:
        is_text_phrase = False
    response["is_text_phrase"] = is_text_phrase

    response["text_phrase"] = text_phrase

    # Получаем перевод фразы
    translation = dialog_manager.dialog_data.get("translation", "")
    response["translation"] = translation

    # Получаем комментарий
    comment = dialog_manager.dialog_data.get("comment", "")
    response["comment"] = comment

    prompt = dialog_manager.dialog_data.get("prompt")
    if prompt:
        is_prompt = True
    else:
        is_prompt = False
    response["is_prompt"] = is_prompt

    audio = dialog_manager.dialog_data.get("audio")
    if audio:
        is_audio = True
    else:
        is_audio = False
    response["is_audio"] = is_audio

    return response


async def text_phrase_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                            text_phrase: str) -> None:
    phrase = await Phrase.get_or_none(text_phrase=text_phrase, user_id=message.from_user.id)
    if phrase:
        await bot.send_message(message.chat.id, "Ты уже добавлял эту фразу. Попробуй что-нибудь еще 😉")
    else:
        dialog_manager.dialog_data["text_phrase"] = text_phrase
        spaced_phrase = openai_gpt_add_space(text_phrase)
        dialog_manager.dialog_data["spaced_phrase"] = spaced_phrase
        await dialog_manager.next()


async def translation_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                            translation: str) -> None:
    dialog_manager.dialog_data["translation"] = remove_html_tags(translation)
    await dialog_manager.next()


async def translate_phrase(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    translation = openai_gpt_translate(dialog_manager.dialog_data["text_phrase"])
    dialog_manager.dialog_data["translation"] = translation


async def audio_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    file_id = message.audio.file_id if message.audio else message.voice.file_id
    if message.audio:
        file_name = message.audio.file_name
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, file_name)

        # Конвертирование аудио в формат .OGG с кодеком OPUS
        audio = AudioSegment.from_file(file_name)
        audio.export(f"{file_id}.ogg", format="ogg", codec="libopus")

        # Чтение сконвертированного аудио файла
        with open(f"{file_id}.ogg", "rb") as f:
            audio_data = f.read()

        audio_data_base64 = base64.b64encode(audio_data).decode("utf-8")

        # Удаление временных файлов
        os.remove(file_name)
        os.remove(f"{file_id}.ogg")

        audio = {
            "tg_id": "",
            "audio": audio_data_base64
        }
        dialog_manager.dialog_data["audio"] = audio

    elif message.voice:
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, f"{file_id}.ogg")

        # Чтение голосового сообщения
        with open(f"{file_id}.ogg", "rb") as f:
            audio_data = f.read()

        audio_data_base64 = base64.b64encode(audio_data).decode("utf-8")

        # Удаление временного файла
        os.remove(f"{file_id}.ogg")

        audio = {
            "tg_id": file_id,
            "audio": audio_data_base64
        }
        dialog_manager.dialog_data["audio"] = audio

    await dialog_manager.next()


async def ai_voice_message(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    text_phrase = dialog_manager.dialog_data["text_phrase"]

    text_to_speech = await google_text_to_speech(text_phrase)
    voice = BufferedInputFile(text_to_speech.audio_content, filename="voice_tts.ogg")
    msg = await callback.message.answer_voice(voice=voice, caption=f"Озвучка")
    voice_id = msg.voice.file_id

    audio = await AudioFile.create(
        tg_id=voice_id,
        audio=voice.data
    )

    audio = {
        "tg_id": voice_id,
        "audio_id": audio.id
    }
    dialog_manager.dialog_data["audio"] = audio

    await dialog_manager.next(show_mode=ShowMode.SEND)


async def image_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    image_id = message.photo[-1].file_id
    dialog_manager.dialog_data["image_id"] = image_id
    await dialog_manager.next()


async def ai_image(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data["prompt"] = dialog_manager.dialog_data["translation"]
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY, default_format_text)
    await callback.message.answer(i18n_format("starting-generate-image"))
    # Функция для генерации изображения автоматически
    try:
        images = generate_image(prompt=dialog_manager.dialog_data["prompt"], style='ANIME', width=512, height=512)
        if images and len(images) > 0:
            # Декодируем изображение из Base64
            image_data = base64.b64decode(images[0])
            image = BufferedInputFile(image_data, filename="image.png")
            # Отправляем изображение
            msg = await callback.message.answer_photo(photo=image, caption=i18n_format("generated-image"))
            image_id = msg.photo[-1].file_id
            dialog_manager.dialog_data["image_id"] = image_id
            await dialog_manager.next(show_mode=ShowMode.SEND)
        else:
            await callback.message.answer(i18n_format("failed-generate-image"))
            await dialog_manager.show()
    except Exception as e:
        await callback.message.answer(text=i18n_format("failed-generate-image"))
        logger.error('Ошибка при генерации изображения: %s', e)


async def comment_input(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager,
                        comment: str) -> None:
    dialog_manager.dialog_data["comment"] = remove_html_tags(comment)
    await dialog_manager.next()


async def comment_next_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data["comment"] = ""


async def save_phrase_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    category = await Category.get_or_none(id=dialog_manager.start_data["category_id"])
    user_id = dialog_manager.event.from_user.id
    user = await User.get_or_none(id=user_id)
    text_phrase = dialog_manager.dialog_data["text_phrase"]
    voice_id = dialog_manager.dialog_data["audio"]["tg_id"]
    phrase = Phrase(
        category=category,
        user=user,
        text_phrase=text_phrase,
        audio_id=voice_id,
    )
    if dialog_manager.dialog_data.get("translation"):
        phrase.translation = dialog_manager.dialog_data["translation"]
    if dialog_manager.dialog_data.get("image_id"):
        phrase.image_id = dialog_manager.dialog_data.get("image_id")
    if dialog_manager.dialog_data.get("comment"):
        phrase.comment = dialog_manager.dialog_data.get("comment")
    if dialog_manager.dialog_data.get("spaced_phrase"):
        phrase.spaced_phrase = dialog_manager.dialog_data.get("spaced_phrase")

    await phrase.save()

    new_phrase = [phrase.text_phrase, phrase.id]

    await dialog_manager.done(result={"new_phrase": new_phrase})


add_original_phrase_dialog = Dialog(
    Window(
        Multi(
            I18NFormat("selected-category"),
            I18NFormat("input-text-phrase"),
        ),

        TextInput(
            id="text_phrase_input",
            on_success=text_phrase_input,
        ),
        Group(
            Cancel(I18NFormat("cancel"), id="button_cancel"),
            width=3
        ),
        getter=get_data,
        state=AddOriginalPhraseSG.text_phrase
    ),
    # translation = State()
    Window(
        Multi(
            I18NFormat("selected-category"),
            I18NFormat("text-phrase"),
            I18NFormat("input-translate"),
        ),

        TextInput(
            id="translation_input",
            on_success=translation_input,
        ),
        Group(
            Back(I18NFormat("back"), id="back"),
            Cancel(I18NFormat("cancel"), id="button_cancel"),
            Next(I18NFormat("next"), id="next", on_click=translate_phrase),
            width=3
        ),
        getter=get_data,
        state=AddOriginalPhraseSG.translation
    ),

    # audio = State()
    Window(
        Multi(
            I18NFormat("selected-category"),
            I18NFormat("text-phrase"),
            I18NFormat("translation-phrase"),
        ),
        Multi(
            I18NFormat("add-audio"),
            I18NFormat("add-audio-info-first",
                  when=first_state_audio_getter),
            I18NFormat("add-audio-info-second",
                  when=second_state_audio_getter),
            sep="\n\n"
        ),
        MessageInput(
            func=audio_handler,
            content_types=[ContentType.AUDIO, ContentType.VOICE],
        ),
        Button(I18NFormat("voice-with-ai-button"), id="voice_message", on_click=ai_voice_message),
        Group(
            Back(I18NFormat("back"), id="back"),
            Cancel(I18NFormat("cancel"), id="button_cancel"),
            Next(I18NFormat("next"), id="next", when='is_audio'),
            width=3
        ),
        getter=get_data,
        state=AddOriginalPhraseSG.audio
    ),

    # image = State()
    Window(
        Multi(
            I18NFormat("selected-category"),
            I18NFormat("text-phrase"),
            I18NFormat("translation-phrase"),
        ),
        I18NFormat(text="add-image-info"),
        MessageInput(func=image_handler, content_types=[ContentType.PHOTO]),
        Button(
            I18NFormat("generate-image-button"),
            id="ai_image",
            on_click=ai_image),
        Button(
            I18NFormat("repeat"),
            id="repeat_generate_image_button",
            on_click=repeat_ai_generate_image,
            when="is_prompt",
        ),
        Group(
            Back(I18NFormat("back"), id="back"),
            Cancel(I18NFormat("cancel"), id="button_cancel"),
            Next(I18NFormat("next"), id="next"),
            width=3
        ),
        getter=get_data,
        state=AddOriginalPhraseSG.image
    ),

    # comment = State()
    Window(
        Multi(
            I18NFormat("selected-category"),
            I18NFormat("text-phrase"),
            I18NFormat("translation-phrase"),
        ),
        I18NFormat(text="add-comment"),
        TextInput(id="comment_input", on_success=comment_input),
        Group(
            Back(I18NFormat("back"), id="back"),
            Cancel(I18NFormat("cancel"), id="button_cancel"),
            Next(I18NFormat("next"), id="next", on_click=comment_next_button_clicked),
            width=3
        ),
        getter=get_data,
        state=AddOriginalPhraseSG.comment
    ),
    # save = State()
    Window(
        Multi(
            I18NFormat("summary-information"),
        ),
        Group(
            Back(I18NFormat("back"), id="back"),
            Cancel(I18NFormat("cancel"), id="button_cancel"),
            Button(
                text=I18NFormat("save"),
                id="save_phrase",
                on_click=save_phrase_button_clicked,
            ),
            width=3
        ),
        getter=get_data,
        state=AddOriginalPhraseSG.save
    ),
)
