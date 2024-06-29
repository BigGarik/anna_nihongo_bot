import logging.config
import os

import yaml
from aiogram.types import Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram_dialog import setup_dialogs
from aiohttp import web
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot_init import bot, dp
from config_data.config import Config, load_config
from db import init_db
from handlers.add_lexis_phrase import add_lexis_phrase_dialog
from handlers.add_original_phrase_handler import add_original_phrase_dialog
from handlers.admin_handlers import router as admin_router, admin_dialog
from handlers.other_handlers import router as other_router
from handlers.phrase_management_handlers import management_dialog
from handlers.add_category import add_category_dialog
from handlers.subscribe_management_handlers import subscribe_dialog, subscribe_management_dialog
from handlers.training.lexis_handlers import lexis_training_dialog
from handlers.training.listening_handlers import text_to_speech_dialog
from handlers.training.pronunciation_handlers import pronunciation_training_dialog
from handlers.training.training_handlers import user_training_dialog
from handlers.training.translation_handlers import translation_training_dialog
from handlers.user_handlers import router as user_router, start_dialog
from handlers.user_management import user_management_dialog
from middlewares.i18n_middleware import I18nMiddleware
from fluent.runtime import FluentLocalization, FluentResourceLoader
# from keyboards.set_menu import set_main_menu
from services.services import check_subscriptions


load_dotenv()

web_server_host = os.getenv('WEB_SERVER_HOST')
web_server_port = int(os.getenv('WEB_SERVER_PORT'))
base_webhook_url = os.getenv('BASE_WEBHOOK_URL')
webhook_path = os.getenv('WEBHOOK_PATH')
webhook_url = f"{base_webhook_url}{webhook_path}"
webhook_secret = os.getenv('WEBHOOK_SECRET')

# location = os.getenv('LOCATION')
# language_code = location.split('-')[0]
DEFAULT_LOCALE = "en"
LOCALES = ["en", 'ru']


with open('config_data/logging_config.yaml', 'rt') as f:
    logging_config = yaml.safe_load(f.read())
# Загружаем настройки логирования из словаря `logging_config`
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# Загружаем конфиг в переменную config
config: Config = load_config()


def make_i18n_middleware():
    loader = FluentResourceLoader(os.path.join(
        os.path.dirname(__file__),
        "translations",
        "{locale}",
    ))
    l10ns = {
        locale: FluentLocalization(
            [locale, DEFAULT_LOCALE], ["main.ftl"], loader,
        )
        for locale in LOCALES
    }
    return I18nMiddleware(l10ns, DEFAULT_LOCALE)


async def on_startup(app):
    await init_db()
    # await set_main_menu(bot)
    await bot.set_webhook(webhook_url, secret_token=webhook_secret)


async def on_shutdown(app):
    await bot.delete_webhook()


async def handle(request):
    update = Update(**await request.json())
    await dp.feed_update(bot, update)
    return web.Response()


def main() -> None:
    # # Создаем объект типа TranslatorHub
    # translator_hub: TranslatorHub = create_translator_hub()

    # Список всех роутеров
    routers = [
        admin_router,
        user_router,
        start_dialog,
        subscribe_dialog,
        subscribe_management_dialog,
        add_original_phrase_dialog,
        admin_dialog,
        user_management_dialog,
        add_lexis_phrase_dialog,
        text_to_speech_dialog,
        add_category_dialog,
        lexis_training_dialog,
        pronunciation_training_dialog,
        translation_training_dialog,
        management_dialog,
        user_training_dialog,
        other_router
    ]

    # Включение всех роутеров в диспетчер
    for router in routers:
        dp.include_router(router)

    # dp.include_router(other_handlers.router)
    setup_dialogs(dp)

    # Инициализация планировщика
    scheduler = AsyncIOScheduler()
    # Добавление задачи на выполнение каждый день в полночь
    scheduler.add_job(check_subscriptions, 'cron', hour=11, minute=0)
    # Добавление задачи для выполнения каждую минуту
    # scheduler.add_job(check_subscriptions, 'cron', minute='*')
    # Запуск планировщика
    scheduler.start()
    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)

    # Регистрируем миддлварь для i18n
    # dp.update.middleware(TranslatorRunnerMiddleware())
    i18n_middleware = make_i18n_middleware()
    dp.message.middleware(i18n_middleware)
    dp.callback_query.middleware(i18n_middleware)

    # Create aiohttp.web.Application instance
    app = web.Application()

    # Create an instance of request handler,
    # aiogram has few implementations for different cases of usage
    # In this example we use SimpleRequestHandler which is designed to handle simple cases
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=webhook_secret,
    )
    # Register webhook handler on application
    webhook_requests_handler.register(app, path=webhook_path)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # And finally start webserver
    web.run_app(app, host=web_server_host, port=web_server_port)


if __name__ == "__main__":
    logger.info('Бот запущен и работает...')
    main()
