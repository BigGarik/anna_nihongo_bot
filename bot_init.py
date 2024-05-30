import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage, Redis, DefaultKeyBuilder
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


redis = Redis(host=os.getenv('REDIS_DSN'))
storage = RedisStorage(redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True))

# Инициализируем бот и диспетчер
bot = Bot(token=os.getenv('BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=storage)
