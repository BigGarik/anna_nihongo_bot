import logging
import os

from aiogram import Bot, types
from aiogram.types import BotCommand
from dotenv import load_dotenv

from bot_init import make_i18n_middleware
from lexicon.lexicon_ru import LEXICON_COMMANDS_RU


load_dotenv()
logger = logging.getLogger('default')


default_locale = os.getenv('DEFAULT_LOCALE')


# Функция для получения локализованного меню
async def get_localized_menu(i18n_format):
    return [
        types.BotCommand(command="start", description=i18n_format("command-start")),
        types.BotCommand(command="language", description=i18n_format("command-language")),
        types.BotCommand(command="contacts", description=i18n_format("command-contacts")),
        types.BotCommand(command="help", description=i18n_format("command-help"))
    ]


# Функция для установки меню бота с локалью по умолчанию
async def set_default_commands(bot: Bot):
    default_l10n = make_i18n_middleware().l10ns[default_locale]
    default_menu = await get_localized_menu(default_l10n.format_value)
    await bot.set_my_commands(default_menu)


# Функция для настройки кнопки Menu бота
async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(
            command=command,
            description=description
        ) for command, description in LEXICON_COMMANDS_RU.items()
    ]
    await bot.set_my_commands(main_menu_commands)
