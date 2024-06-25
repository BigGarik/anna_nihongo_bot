import logging
import os

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.kbd import Button, Row, Column, Start
from aiogram_dialog.widgets.text import Format, Const, Multi
from dotenv import load_dotenv

from keyboards.inline_kb import create_inline_kb
from lexicon.lexicon_ru import LEXICON_RU
from models import User
from services.services import get_folders
from states import StartDialogSG, UserStartDialogSG, AdminDialogSG, UserTrainingSG, TextToSpeechSG, ManagementSG, SubscribeSG
from . import start_getter

load_dotenv()
admin_id = os.getenv('ADMIN_ID')

# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger(__name__)


async def tts_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # await dialog_manager.done()
    await dialog_manager.start(state=TextToSpeechSG.start)

#
# async def category_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
#     keyboard = create_inline_kb(1, **get_folders('original_files'))
#     await callback.message.answer(
#         text=f"{LEXICON_RU['select_category']}",
#         reply_markup=keyboard
#     )
#     await dialog_manager.done()


async def training_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=UserTrainingSG.start)


async def phrase_management_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # user = await User.get_or_none(id=callback.from_user.id)
    # if user.subscription == 'Free':
    #     await callback.answer('Только по подписке', show_alert=True)
    # else:
    await dialog_manager.start(state=ManagementSG.start)


async def subscribe_management_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=SubscribeSG.start)


start_dialog = Dialog(
    Window(
        Multi(
            Const('初めまして', when='is_jp'),
            Format('<b>Привет, {username}!</b>'),
            Const('Я бот-помощник <b>Анны様</b> 😃\n'
                  'Я помогаю тренироваться в японском произношении и грамматике.\n\n'
                  'Хотите говорить по-японски как японцы?\n',
                  when='is_jp'
                  ),

            Const("Меня зовут мистер Хацу, я твой бот-помощник.\nЯ помогу тебе легко запоминать новые слова, "
                  "тренировать красивое произношение и научиться бегло говорить по-английски.\n\nLet's start!\n",
                  when='is_en'
                  ),
        ),
        Column(
            Row(
                Button(
                    text=Const('💪 Тренировки'),
                    id='training',
                    on_click=training_button_clicked),
                Button(
                    text=Const('🔊 Прослушивание (Озвучить текст)'),
                    id='tts',
                    on_click=tts_button_clicked),
                Button(
                    text=Const('📝 Управление моими фразами 💎ᴠɪᴘ'),
                    id='phrase_management',
                    on_click=phrase_management_button_clicked,
                ),
                Button(
                    text=Const('🔔 Подписаться 💎ᴠɪᴘ'),
                    id='subscribe_management',
                    on_click=subscribe_management_button_clicked,
                    when='is_not_subscribe'
                ),
                Button(
                    text=Const('🔔 Управление подпиской 💎ᴠɪᴘ'),
                    id='subscribe_management',
                    on_click=subscribe_management_button_clicked,
                    when='is_subscribe'
                ),
            ),
        ),
        getter=start_getter,
        state=StartDialogSG.start
    ),
)

user_start_dialog = Dialog(
    Window(
        Multi(
            Format('<b>{username}さん</b>、日本語を勉強しましょう！\nДавай выберем следующую тренировку!',
                   when='is_jp'
                   ),
            Format("<b>{username}</b>, let's go to the next level!\nДавай выберем следующую тренировку!",
                   when='is_en'
                   ),
            # Format('Подписка: <b>{subscription}</b>'),
        ),
        Column(
            Row(
                Button(
                    text=Const('💪 Тренировки'),
                    id='training',
                    on_click=training_button_clicked),
                Button(
                    text=Const('🔊 Прослушивание (Озвучить текст)'),
                    id='tts',
                    on_click=tts_button_clicked),
                Button(
                    text=Const('📝 Управление моими фразами 💎ᴠɪᴘ'),
                    id='phrase_management',
                    on_click=phrase_management_button_clicked,
                ),
                Button(
                    text=Const('🔔 Подписаться 💎ᴠɪᴘ'),
                    id='subscribe_management',
                    on_click=subscribe_management_button_clicked,
                    when='is_not_subscribe'
                ),
                Button(
                    text=Const('🔔 Управление подпиской 💎ᴠɪᴘ'),
                    id='subscribe_management',
                    on_click=subscribe_management_button_clicked,
                    when='is_subscribe'
                ),
            ),
        ),
        Row(
            Start(Const('⚙️ Настройки(для админов)'),
                  id='settings',
                  state=AdminDialogSG.start
                  ),
            when='is_admin',
        ),
        getter=start_getter,
        # Состояние этого окна для переключения на него
        state=UserStartDialogSG.start
    ),
)


# Этот хэндлер будет срабатывать на /start
@router.message(CommandStart())
async def process_start_command(message: Message, dialog_manager: DialogManager):
    user_id = message.from_user.id
    user = await User.filter(id=user_id).first()
    if user:
        await dialog_manager.start(state=UserStartDialogSG.start, mode=StartMode.RESET_STACK)
    else:
        username = message.from_user.username or ""
        first_name = message.from_user.first_name or ""
        last_name = message.from_user.last_name or ""
        await User.create(id=user_id, username=username,
                          first_name=first_name, last_name=last_name)
        await dialog_manager.start(state=StartDialogSG.start, mode=StartMode.RESET_STACK)


@router.message(Command(commands='cancel'))
async def process_help_command(message: Message, state: FSMContext, dialog_manager: DialogManager):
    await message.answer(text=LEXICON_RU['/cancel'])
    await dialog_manager.done()
    dialog_manager.dialog_data.clear()
    await state.clear()


@router.message(Command(commands='contact'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/contact'])


# Этот хэндлер срабатывает на команду /help
@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])

# Хендлер обрабатывающий нажатие инлайн кнопки выбора фразы
# установит состояние в original_phrase
# отправить пользователю оригинальное произношение и предложит повторить
# @router.callback_query(F.date.in_(BUTTONS_LIST))

# @router.callback_query(F.data == 'new_them')
# async def process_select_category(callback: CallbackQuery, state: FSMContext):
#     keyboard = create_inline_kb(1, **get_folders('original_files'))
#     await callback.message.answer(
#         text=LEXICON_RU['select_category'],
#         reply_markup=keyboard
#     )
#
#
# @router.callback_query(F.data == 'new_phrase')
# async def process_choose_phrase(callback: CallbackQuery, state: FSMContext):
#     # Сохраняем выбранную категорию в хранилище состояний
#     # await state.update_data(select_category=callback.data)
#     dir_to_files = f'{user_dict[callback.from_user.id]["select_category"]}'
#     # Создаем клавиатуру с файлами
#     keyboard = create_inline_kb(1, **create_kb_file(dir_to_files))
#     await callback.message.answer(
#         text=LEXICON_RU['choose_phrase'],
#         reply_markup=keyboard
#     )
#
#
# # Колбек на нажатие кнопки с выбором категории
# @router.callback_query(F.data.in_(list(get_folders('original_files').values())))
# async def process_select_category(callback: CallbackQuery, state: FSMContext):
#     # Сохраняем выбранную категорию в хранилище состояний
#     await state.update_data(select_category=callback.data)
#     # Создаем клавиатуру с файлами
#     keyboard = create_inline_kb(1, **create_kb_file(callback.data))
#     await callback.message.edit_text(
#         text=LEXICON_RU['choose_phrase'],
#         reply_markup=keyboard
#     )
#
#
# # Колбек на нажатие кнопки с выбором фразы
# @router.callback_query(F.data.in_(get_all_ogg_files('original_files')))
# async def process_choose_phrase(callback: CallbackQuery, state: FSMContext):
#     # Устанавливаем состояние ожидания голосового сообщения повторения оригинала
#     await state.set_state(FSMInLearn.original_phrase)
#     # Сохраняем выбранную фразу в хранилище состояний
#     await state.update_data(current_phrase=callback.data)
#     # Добавляем в "базу данных" данные пользователя
#     # по ключу id пользователя
#     user_dict[callback.from_user.id] = await state.get_data()
#     # Удаляем сообщение с кнопками, потому что следующий этап - загрузка голосового сообщения
#     # чтобы у пользователя не было желания тыкать кнопки
#     await callback.message.delete()
#     await callback.message.answer_photo(FSInputFile(f'{user_dict[callback.from_user.id]["select_category"]}/'
#                                                     f'{callback.data.replace(".ogg", ".png")}'))
#     # Тут нужно отправить оригинальный файл аудио
#     await callback.message.answer_voice(
#         FSInputFile(f'{user_dict[callback.from_user.id]["select_category"]}/{callback.data}'),
#         caption='Послушайте оригинал и попробуйте повторить'
#     )
#
#
# # Хэндлер на голосовое сообщение
# @router.message(F.voice, ~StateFilter(default_state))
# async def process_send_voice(message: Message, bot: Bot, state: FSMContext):
#     # Получаем голосовое сообщение и сохраняем на диск
#     user_id = message.from_user.id
#     current_phrase = user_dict[user_id]["current_phrase"]
#     current_phrase = current_phrase.rsplit('.', 1)[0]
#     file_name = f"{user_id}_{datetime.datetime.now()}_{current_phrase}"
#     file_id = message.voice.file_id
#     file = await bot.get_file(file_id)
#     file_path = file.file_path
#     file_on_disk = Path("", f"temp/{file_name}.ogg")
#     await bot.download_file(file_path, destination=file_on_disk)
#     logger.info(f'ID пользователя {user_id} имя {message.from_user.first_name} '
#                 f'фраза {user_dict[user_id]["current_phrase"]} '
#                 f'файл - {file_on_disk}')
#     logging.debug(await state.get_state())
#
#     original_file = f'{user_dict[user_id]["select_category"]}/{user_dict[user_id]["current_phrase"]}'
#     original_script = get_tag(original_file, 'script')
#     original_translation = get_tag(original_file, 'translation')
#
#     # # Распознавание речи на японском языке
#     # original_recognizer = SpeechRecognizer(original_file)
#     # original_text = original_recognizer.recognize_speech()
#     spoken_recognizer = SpeechRecognizer(file_on_disk, user_id)
#     spoken_text = spoken_recognizer.recognize_speech()
#     # Загрузка аудиофайлов
#     original_audio, sample_rate = librosa.load(original_file)
#     spoken_audio, _ = librosa.load(file_on_disk, sr=sample_rate)
#     visual = PronunciationVisualizer(original_audio, spoken_audio, sample_rate, file_name)
#     await visual.preprocess_audio()
#     await visual.plot_waveform()  # Визуализация графика звуковой волны
#     photo = FSInputFile(f'temp/{file_name}.png')
#     keyboard = create_inline_kb(2, **LEXICON_KB_FAST_BUTTONS_RU)
#     await message.answer_photo(photo, caption=f'Оригинал\n{original_script}\n{original_translation}\n\n'
#                                               f'Ваш вариант {spoken_text}', reply_markup=keyboard)

# os.remove(file_on_disk)  # Удаление временного файла
# os.remove(f'temp/{file_name}.png')
