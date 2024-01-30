from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, User
from aiogram_dialog import Dialog, DialogManager, StartMode, Window, setup_dialogs
from aiogram_dialog.widgets.text import Format
from environs import Env
from aiogram.fsm.storage.redis import RedisStorage, Redis
import logging.config
import yaml


with open('config_data/logging_config.yaml', 'rt') as f:
    config = yaml.safe_load(f.read())

logging.config.dictConfig(config)
logger = logging.getLogger(__name__)

env = Env()
env.read_env()

BOT_TOKEN = env('BOT_TOKEN')

redis = Redis(host='localhost')
storage = RedisStorage(redis=redis)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)


class StartSG(StatesGroup):
    start = State()


async def username_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    return {'username': event_from_user.username}


start_dialog = Dialog(
    Window(
        Format('Привет, {username}!'),
        getter=username_getter,
        state=StartSG.start
    ),
)


@dp.message(CommandStart())
async def command_start_process(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=StartSG.start, mode=StartMode.RESET_STACK)


if __name__ == '__main__':
    dp.include_router(start_dialog)
    setup_dialogs(dp)
    dp.run_polling(bot)
