import asyncio
import logging.config

import yaml
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, Redis, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs

from config_data.config import Config, load_config
from db import init as init_db
from handlers.user_handlers import router as user_router, start_dialog, text_to_speech_dialog
from handlers.admin_handlers import router as admin_router
from handlers.other_handlers import router as other_router
from keyboards.set_menu import set_main_menu
from aiohttp import web
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

''' TODO проверка комментария '''
# TODO база данных
# TODO отправлять файлы по ID
# TODO создать админку с добавлением категорий и загрузкой файлов в нее
# TODO добавить раздел собеседника
# TODO переписать код под aiogram_dialog

with open('config_data/logging_config.yaml', 'rt') as f:
    logging_config = yaml.safe_load(f.read())
# Загружаем настройки логирования из словаря `logging_config`
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# Загружаем конфиг в переменную config
config: Config = load_config()


async def on_startup(bot: Bot) -> None:
    # If you have a self-signed SSL certificate, then you will need to send a public
    # certificate to Telegram
    await bot.set_webhook(f"{config.webhook.base_webhook_url}{config.webhook.webhook_path}",
                          secret_token=config.webhook.webhook_secret)


# Функция конфигурирования и запуска бота
def main() -> None:
    redis = Redis(host=config.redis.redis_dsn)
    storage = RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True))
    database_url = f'postgres://{config.db.db_user}:{config.db.db_password}@{config.db.db_host}:{config.db.db_port}/{config.db.database}'
    init_db(database_url)

    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)

    # Настраиваем кнопку Menu
    set_main_menu(bot)

    # Регистрируем роутеры в диспетчере
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.include_router(start_dialog)
    dp.include_router(text_to_speech_dialog)
    dp.include_router(other_router)

    # dp.include_router(other_handlers.router)
    setup_dialogs(dp)

    # Пропускаем накопившиеся апдейты и запускаем polling
    bot.delete_webhook(drop_pending_updates=True)
    # await dp.start_polling(bot, allowed_updates=[])

    # Регистрируем хук на старт для инициализации webhook
    dp.startup.register(on_startup)

    # Создаем экземпляр aiohttp.web.Application
    app = web.Application()

    # Создаем экземпляр обработчика запросов,
    # aiogram предоставляет несколько реализаций для разных случаев использования
    # В этом примере мы используем SimpleRequestHandler, который предназначен для обработки простых случаев
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=config.webhook.webhook_secret,
    )
    # Регистрируем обработчик webhook в приложении
    webhook_requests_handler.register(app, path=config.webhook.webhook_path)

    # Подключаем хуки запуска и завершения работы диспетчера к приложению aiohttp
    setup_application(app, dp, bot=bot)

    # И, наконец, запускаем веб-сервер
    web.run_app(app, host=config.webhook.web_server_host, port=int(config.webhook.web_server_port))


if __name__ == "__main__":
    logger.info('Бот запущен и работает...')
    # asyncio.run(main())
    main()

