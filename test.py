import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Устанавливаем уровень логирования
logging.basicConfig(level=logging.INFO)

# Создаем экземпляры бота и диспетчера
bot = Bot(token="6777279637:AAFbsUE8GUYIfolIJEV_DmBozuu0GSiYMoQ")
dp = Dispatcher()


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.reply("Привет! Я эхо-бот. Отправь мне сообщение, и я повторю его.")


# Обработчик всех остальных сообщений
@dp.message()
async def echo_message(message: types.Message):
    await message.answer(message.text)


# Создаем функцию, которая будет принимать апдейты от Telegram через webhook
async def on_startup(app):
    await bot.set_webhook("https://a36b-212-3-131-87.ngrok-free.app")


# Создаем объект приложения aiohttp и добавляем роут для хандлера апдейтов
app = web.Application()
app.on_startup.append(on_startup)
app.router.add_post('/https://a36b-212-3-131-87.ngrok-free.app', dp.update)

# Запускаем приложение на вашем IP и порту
web.run_app(app, host='https://a36b-212-3-131-87.ngrok-free.app', port=80)
