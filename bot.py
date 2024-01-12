import asyncio
import logging.config
from handlers.user_handlers import router
# import handlers.other_handlers

from aiogram import Bot, Dispatcher
from config_data.config import Config, load_config
from config_data.logging_settings import logging_config
# from handlers import other_handlers, user_handlers
from keyboards.set_menu import set_main_menu
from aiogram.fsm.storage.redis import RedisStorage, Redis
# from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

# Загружаем настройки логирования из словаря `logging_config`
logging.config.dictConfig(logging_config)
logger = logging.getLogger(__name__)

# Инициализируем Redis
redis = Redis(host='localhost')

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = RedisStorage(redis=redis)

# async def on_startup(bot: Bot) -> None:
#     # If you have a self-signed SSL certificate, then you will need to send a public
#     # certificate to Telegram
#     await bot.set_webhook(f"{config.webhook.base_webhook_url}{config.webhook.webhook_path}",
#                           secret_token=config.webhook.webhook_secret)


# Функция конфигурирования и запуска бота
async def main() -> None:
    # Загружаем конфиг в переменную config
    config: Config = load_config()
    # Инициализируем бот и диспетчер
    bot = Bot(token=config.tg_bot.token,
              parse_mode='HTML')
    dp = Dispatcher(storage=storage)

    # Настраиваем кнопку Menu
    await set_main_menu(bot)

    # Регистрируем роутеры в диспетчере
    dp.include_router(router)
    # dp.include_router(other_handlers.router)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=[])

    # # Register startup hook to initialize webhook
    # dp.startup.register(on_startup)
    # # Create aiohttp.web.Application instance
    # app = web.Application()
    #
    # # Create an instance of request handler,
    # # aiogram has few implementations for different cases of usage
    # # In this example we use SimpleRequestHandler which is designed to handle simple cases
    # webhook_requests_handler = SimpleRequestHandler(
    #     dispatcher=dp,
    #     bot=bot,
    #     secret_token=config.webhook.webhook_secret,
    # )
    # # Register webhook handler on application
    # webhook_requests_handler.register(app, path=config.webhook.webhook_path)
    #
    # # Mount dispatcher startup and shutdown hooks to aiohttp application
    # setup_application(app, dp, bot=bot)
    #
    # # And finally start webserver
    # web.run_app(app, host=config.webhook.web_server_host, port=int(config.webhook.web_server_port))


if __name__ == "__main__":
    asyncio.run(main())
