import logging.config
import os

import yaml
from aiogram.types import Update
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram_dialog import setup_dialogs
from aiohttp import web
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot_init import bot, dp, make_i18n_middleware
from config_data.config import Config, load_config
from db import init_db
from dialogs.edit_phrase_dialog import edit_phrase_dialog
from dialogs.select_language_dialog import select_language_dialog
from dialogs.smart_phrase_addition_dialog import smart_phrase_addition_dialog
from dialogs.training.interval_training import interval_training_dialog, interval_dialog
from handlers.add_original_phrase_handler import add_original_phrase_dialog
from handlers.admin_handlers import router as admin_router, admin_dialog
from handlers.other_handlers import router as other_router
from handlers.phrase_management_handlers import management_dialog
from handlers.add_category import add_category_dialog
from dialogs.subscribe_management_dialog import subscribe_dialog, subscribe_management_dialog
from handlers.training.lexis_handlers import lexis_training_dialog
from handlers.training.listening_handlers import text_to_speech_dialog
from handlers.training.pronunciation_handlers import pronunciation_training_dialog
from handlers.training.training_handlers import user_training_dialog
from handlers.training.translation_handlers import translation_training_dialog
from handlers.user_handlers import router as user_router, start_dialog
from handlers.user_management import user_management_dialog
from keyboards.set_menu import set_default_commands
from middlewares.outer_middlewares import LoggingMiddleware
from services.services import check_subscriptions, auto_renewal_subscriptions, interval_notifications, \
    auto_reset_daily_counter
from services.yookassa import process_yookassa_webhook

load_dotenv()

web_server_host = os.getenv('WEB_SERVER_HOST')
web_server_port = int(os.getenv('WEB_SERVER_PORT'))
base_webhook_url = os.getenv('BASE_WEBHOOK_URL')
webhook_path = os.getenv('WEBHOOK_PATH')
webhook_url = f"{base_webhook_url}{webhook_path}"
webhook_secret = os.getenv('WEBHOOK_SECRET')
bot_webhook = os.getenv('BOT_WEBHOOK')

# location = os.getenv('LOCATION')
# language_code = location.split('-')[0]


with open('config_data/logging_config.yaml', 'rt') as f:
    logging_config = yaml.safe_load(f.read())
# Загружаем настройки логирования из словаря `logging_config`
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# Загружаем конфиг в переменную config
config: Config = load_config()


async def on_startup(app):
    await init_db()
    await set_default_commands(bot)
    await bot.set_webhook(webhook_url, secret_token=webhook_secret)

    # Инициализация планировщика
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_subscriptions, 'cron', hour=11, minute=0, misfire_grace_time=3600)
    scheduler.add_job(auto_renewal_subscriptions, 'cron', hour=12, minute=0, misfire_grace_time=3600)
    scheduler.add_job(interval_notifications, "interval", minutes=5, misfire_grace_time=3600)
    scheduler.add_job(auto_reset_daily_counter, 'cron', hour=23, minute=0, misfire_grace_time=3600)
    # scheduler.add_job(check_subscriptions, "interval", minutes=1, misfire_grace_time=3600)
    scheduler.start()

    # Сохраните планировщик в app для последующего доступа
    app['scheduler'] = scheduler


async def on_shutdown(app):
    await bot.delete_webhook()
    # Остановка планировщика при завершении работы приложения
    app['scheduler'].shutdown()


async def handle(request):
    update = Update(**await request.json())
    await dp.feed_update(bot, update)
    return web.Response()


def main() -> None:

    # Список всех роутеров
    routers = [
        admin_router,
        user_router,
        start_dialog,
        select_language_dialog,
        subscribe_dialog,
        subscribe_management_dialog,
        smart_phrase_addition_dialog,
        add_original_phrase_dialog,
        edit_phrase_dialog,
        admin_dialog,
        user_management_dialog,
        interval_dialog,
        interval_training_dialog,
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
    #setup_dialogs(dp)
    # Register startup hook to initialize webhook
    dp.startup.register(on_startup)

    # Регистрируем миддлварь для i18n
    i18n_middleware = make_i18n_middleware()
    dp.message.middleware(i18n_middleware)
    dp.callback_query.middleware(i18n_middleware)
    # для логирования
    # dp.update.outer_middleware(LoggingMiddleware())

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
    # Добавляем обработчик для вебхуков ЮKassa
    app.router.add_post(bot_webhook, process_yookassa_webhook)

    # Mount dispatcher startup and shutdown hooks to aiohttp application
    setup_application(app, dp, bot=bot)

    # And finally start webserver
    web.run_app(app, host=web_server_host, port=web_server_port)


if __name__ == "__main__":
    logger.info('Бот запущен и работает...')
    main()
