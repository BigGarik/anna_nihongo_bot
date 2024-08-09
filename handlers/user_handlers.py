import logging
import os

from aiogram import Router, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InputFile, BufferedInputFile
from aiogram_dialog import Dialog, Window, DialogManager, StartMode
from aiogram_dialog.widgets.text import Multi
from dotenv import load_dotenv

from bot_init import bot
from handlers.system_handlers import start_getter
from keyboards.reply_kb import get_keyboard
from keyboards.set_menu import get_localized_menu
from models import User, Subscription
from models.main import MainPhoto
from services.create_update_user import update_or_create_user
from services.i18n_format import I18NFormat, I18N_FORMAT_KEY, default_format_text
from services.interval_training import start_training
from services.services import is_admin, build_user_progress_histogram
from states import StartDialogSG, UserTrainingSG, ManagementSG, SubscribeManagementSG, SelectLanguageSG, IntervalSG

load_dotenv()
admin_id = os.getenv('ADMIN_ID')

# Инициализируем роутер уровня модуля
router = Router()

logger = logging.getLogger('default')


start_dialog = Dialog(
    Window(

        Multi(
            I18NFormat("First-hello-user-jp", when='is_jp'),
            I18NFormat("First-hello-user-en", when='is_en'),
            when='new_user'
        ),
        Multi(
            I18NFormat("hello-user-jp", when='is_jp'),
            I18NFormat("hello-user-en", when='is_en'),
            when='not_new_user'
        ),
        getter=start_getter,
        state=StartDialogSG.start
    ),
)


@router.message(CommandStart())
async def process_start_command(message: Message, dialog_manager: DialogManager):
    user_id = message.from_user.id
    user = await User.get_or_none(id=user_id)
    main_photo = await MainPhoto.get_or_none(id=1)
    main_photo_tg_id = main_photo.tg_id
    not_new_user = False
    new_user = False
    if user:
        not_new_user = True
        await update_or_create_user(message)
    else:
        new_user = True
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY, default_format_text)
    user_menu = await get_localized_menu(i18n_format)
    chat_id = message.chat.id
    await bot.set_my_commands(user_menu, scope=types.BotCommandScopeChat(chat_id=chat_id))
    is_user_admin = is_admin(message.from_user.id)
    keyboard = get_keyboard(i18n_format, is_user_admin)
    await message.answer_photo(main_photo_tg_id, reply_markup=keyboard)
    await dialog_manager.start(state=StartDialogSG.start,
                               mode=StartMode.RESET_STACK,
                               data={"new_user": new_user, 'not_new_user': not_new_user})


@router.message(Command(commands='language'))
async def process_language_command(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=SelectLanguageSG.start)


@router.message(Command(commands='contacts'))
async def process_cancel_command(message: Message, dialog_manager: DialogManager):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    await message.answer(text=i18n_format('contacts-teacher'))
    await message.answer(text=i18n_format('contacts-developer'))


@router.message(Command(commands='cancel'))
async def process_cancel_command(message: Message, state: FSMContext, dialog_manager: DialogManager):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    await message.answer(text=i18n_format("command-cancel"))
    await dialog_manager.reset_stack()
    await state.clear()


@router.message(lambda message: message.text in ["💪 Тренировки",
                                                 "💪 Exercises"])
async def process_start_training(message: Message, dialog_manager: DialogManager):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    user_menu = await get_localized_menu(i18n_format)
    chat_id = message.chat.id
    await bot.set_my_commands(user_menu, scope=types.BotCommandScopeChat(chat_id=chat_id))
    await update_or_create_user(message)
    await dialog_manager.start(state=UserTrainingSG.start, mode=StartMode.RESET_STACK)


@router.message(lambda message: message.text in ["📝 Управление фразами для тренировок 💎",
                                                 "📝 Manage phrases for my exercises 💎"])
async def process_phrase_management(message: Message, dialog_manager: DialogManager):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    user_menu = await get_localized_menu(i18n_format)
    chat_id = message.chat.id
    await bot.set_my_commands(user_menu, scope=types.BotCommandScopeChat(chat_id=chat_id))
    await update_or_create_user(message)
    await dialog_manager.start(state=ManagementSG.start, mode=StartMode.RESET_STACK)
    # subscription = await Subscription.get_or_none(user_id=message.from_user.id).prefetch_related('type_subscription')
    # if subscription:
    #     if subscription.type_subscription.name == 'Free':
    #         await message.answer(text=i18n_format("managing-your-own-phrases-only-available-subscription"), show_alert=True)
    #     else:
    #         await dialog_manager.start(state=ManagementSG.start, mode=StartMode.RESET_STACK)


@router.message(lambda message: message.text in ["📈 Мой прогресс",
                                                 "📈 My progress"])
async def process_phrase_management(message: Message, dialog_manager: DialogManager):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    user_menu = await get_localized_menu(i18n_format)
    chat_id = message.chat.id
    user_id = message.from_user.id
    await bot.set_my_commands(user_menu, scope=types.BotCommandScopeChat(chat_id=chat_id))
    await update_or_create_user(message)
    days = 7
    img_buf = await build_user_progress_histogram(user_id, days=days)
    photo = BufferedInputFile(img_buf.read(), filename='image.jpg')
    await message.answer_photo(photo=photo)


@router.message(lambda message: message.text in ["🔔 Управление подпиской 💎",
                                                 "🔔 Manage my subscription 💎"])
async def process_subscribe_management(message: Message, dialog_manager: DialogManager):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    user_menu = await get_localized_menu(i18n_format)
    chat_id = message.chat.id
    await bot.set_my_commands(user_menu, scope=types.BotCommandScopeChat(chat_id=chat_id))
    await update_or_create_user(message)
    await dialog_manager.start(state=SubscribeManagementSG.start, mode=StartMode.RESET_STACK)


@router.callback_query(F.data == 'open_interval_dialog')
async def open_interval_dialog(callback_query: types.CallbackQuery, dialog_manager: DialogManager):
    # await dialog_manager.start(state=IntervalSG.start)
    # await dialog_manager.reset_stack()
    await start_training(dialog_manager)
