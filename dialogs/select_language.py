from aiogram import types
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select

from bot_init import bot, make_i18n_middleware, update_global_middleware
from dialogs.getters import get_languages
from keyboards.reply_kb import get_keyboard
from keyboards.set_menu import get_localized_menu
from models import User
from services.i18n_format import I18NFormat, I18N_FORMAT_KEY
from services.services import is_admin
from states import SelectLanguageSG


async def select_language_button_clicked(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item: str):
    user = await User.get(id=callback.from_user.id)
    user.language = item
    await user.save()

    # Recreate the i18n middleware with the new language
    i18n_middleware = make_i18n_middleware()

    # Update the middleware in the dialog manager
    dialog_manager.middleware_data[I18N_FORMAT_KEY] = i18n_middleware.l10ns[item].format_value

    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)

    user_menu = await get_localized_menu(i18n_format)
    chat_id = callback.message.chat.id
    await bot.set_my_commands(user_menu, scope=types.BotCommandScopeChat(chat_id=chat_id))
    is_user_admin = is_admin(callback.from_user.id)
    keyboard = get_keyboard(i18n_format, is_user_admin)
    msg = i18n_format('language-changed') + ' ' + i18n_format(item)
    await callback.message.answer(text=msg, reply_markup=keyboard)

    await update_global_middleware(i18n_middleware)

    await dialog_manager.done(show_mode=ShowMode.EDIT)


select_language_dialog = Dialog(
    Window(
        I18NFormat(text='select-language'),
        Select(
            I18NFormat(text='{item[0]}'),
            id='language',
            item_id_getter=lambda x: x[1],
            items="languages",
            on_click=select_language_button_clicked
        ),
        getter=get_languages,
        state=SelectLanguageSG.start,
    ),
)
