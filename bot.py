import asyncio
import logging.config

import yaml
from aiogram_dialog import setup_dialogs

from bot_init import bot, dp
from config_data.config import Config, load_config
from db import init as init_db
from handlers.add_lexis_phrase import add_lexis_phrase_dialog
from handlers.add_original_phrase_handler import add_original_phrase_dialog
from handlers.admin_handlers import router as admin_router, admin_dialog
from handlers.other_handlers import router as other_router
from handlers.training.lexis_handlers import lexis_training_dialog
from handlers.training.listening_handlers import text_to_speech_dialog
from handlers.training.pronunciation_handlers import pronunciation_training_dialog
from handlers.training.training_handlers import user_training_dialog
from handlers.training.translation_handlers import translation_training_dialog
from handlers.user_handlers import router as user_router, start_dialog, user_start_dialog
from keyboards.set_menu import set_main_menu

# from aiohttp import web
# from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application


with open('config_data/logging_config.yaml', 'rt') as f:
    logging_config = yaml.safe_load(f.read())
# Загружаем настройки логирования из словаря `logging_config`
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# Загружаем конфиг в переменную config
config: Config = load_config()


# async def on_startup(bot: Bot) -> None:
#     # If you have a self-signed SSL certificate, then you will need to send a public
#     # certificate to Telegram
#     await bot.set_webhook(f"{config.webhook.base_webhook_url}{config.webhook.webhook_path}",
#                           secret_token=config.webhook.webhook_secret)


async def main() -> None:
    await init_db()

    # Настраиваем кнопку Menu
    await set_main_menu(bot)

    # Регистрируем роутеры в диспетчере
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.include_router(start_dialog)
    dp.include_router(user_start_dialog)
    dp.include_router(add_original_phrase_dialog)
    dp.include_router(admin_dialog)
    dp.include_router(add_lexis_phrase_dialog)
    dp.include_router(text_to_speech_dialog)
    dp.include_router(lexis_training_dialog)
    dp.include_router(pronunciation_training_dialog)
    dp.include_router(translation_training_dialog)

    dp.include_router(user_training_dialog)
    dp.include_router(other_router)

    # dp.include_router(other_handlers.router)
    setup_dialogs(dp)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=[])

    # # Регистрируем хук на старт для инициализации webhook
    # dp.startup.register(on_startup)
    #
    # # Создаем экземпляр aiohttp.web.Application
    # app = web.Application()
    #
    # # Создаем экземпляр обработчика запросов,
    # # aiogram предоставляет несколько реализаций для разных случаев использования
    # # В этом примере мы используем SimpleRequestHandler, который предназначен для обработки простых случаев
    # webhook_requests_handler = SimpleRequestHandler(
    #     dispatcher=dp,
    #     bot=bot,
    #     secret_token=config.webhook.webhook_secret,
    # )
    # # Регистрируем обработчик webhook в приложении
    # webhook_requests_handler.register(app, path=config.webhook.webhook_path)
    #
    # # Подключаем хуки запуска и завершения работы диспетчера к приложению aiohttp
    # setup_application(app, dp, bot=bot)
    #
    # runner = web.AppRunner(app)
    # await runner.setup()
    # site = web.TCPSite(runner, host=config.webhook.web_server_host, port=config.webhook.web_server_port)
    # await site.start()
    #
    # try:
    #     await asyncio.Event().wait()
    # finally:
    #     await runner.cleanup()

    # И, наконец, запускаем веб-сервер
    # web.run_app(app, host=config.webhook.web_server_host, port=int(config.webhook.web_server_port))


if __name__ == "__main__":
    try:
        logger.info('Бот запущен и работает...')
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
