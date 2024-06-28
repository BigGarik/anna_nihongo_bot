import os
from dotenv import load_dotenv

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, User

load_dotenv()

# Получение списка ID администраторов из переменной окружения
ADMIN_IDS = list(map(int, os.getenv('ADMIN_IDS', '').split(',')))


def is_admin(user: User) -> bool:
    """
    Проверяет, является ли пользователь администратором.

    :param user: Объект пользователя Telegram
    :return: True, если пользователь админ, иначе False
    """
    return user.id in ADMIN_IDS


# Создаем кнопки
start_training_button = KeyboardButton(text='💪 Тренировки')
phrase_management_button = KeyboardButton(text='📝 Управление моими фразами 💎')
start_subscribe_management_button = KeyboardButton(text='🔔 Управление подпиской 💎')
start_admin_settings_button = KeyboardButton(text='⚙️ Настройки(для админов)')

# Создаем объект клавиатуры
user_reply_kb = ReplyKeyboardMarkup(
    keyboard=[[start_training_button, phrase_management_button],
              [start_subscribe_management_button]],
    resize_keyboard=True,
    one_time_keyboard=False,  # Клавиатура прячется
)

admin_reply_kb = ReplyKeyboardMarkup(
    keyboard=[[start_training_button, phrase_management_button],
              [start_subscribe_management_button],
              [start_admin_settings_button]],
    resize_keyboard=True,
    one_time_keyboard=False,  # Клавиатура прячется
)
