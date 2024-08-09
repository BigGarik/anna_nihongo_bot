import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, Redis, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from dotenv import load_dotenv
from fluent.runtime import FluentResourceLoader, FluentLocalization

from middlewares.i18n_middleware import I18nMiddleware, update_middleware_manager

load_dotenv()
logger = logging.getLogger('default')


default_locale = os.getenv('DEFAULT_LOCALE')
locales = os.getenv('LOCALES').split(',')


def make_i18n_middleware():
    loader = FluentResourceLoader(os.path.join(
        os.path.dirname(__file__),
        "translations",
        "{locale}",
    ))
    l10ns = {
        locale: FluentLocalization(
            [locale, default_locale], ["main.ftl"], loader,
        )
        for locale in locales
    }
    return I18nMiddleware(l10ns, default_locale)


async def update_global_middleware(new_middleware):

    # Update message middleware
    update_middleware_manager(dp.message.middleware, new_middleware)

    # Update callback query middleware
    update_middleware_manager(dp.callback_query.middleware, new_middleware)


redis = Redis(host=os.getenv('REDIS_DSN'))
storage = RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True, with_bot_id=True))

# Инициализируем бот и диспетчер
bot = Bot(token=os.getenv('BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)

# Настройка диалогового менеджера
bg_factory = setup_dialogs(dp)


