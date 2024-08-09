from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from dotenv import load_dotenv

load_dotenv()


def get_keyboard(i18n_format, is_admin: bool):
    # Создаем кнопки с локализованным текстом
    start_training_button = KeyboardButton(text=i18n_format("start-training-button"))
    phrase_management_button = KeyboardButton(text=i18n_format("phrase-management-button"))
    my_progress_history_button = KeyboardButton(text=i18n_format("my-progress-history-button"))
    start_subscribe_management_button = KeyboardButton(text=i18n_format("subscribe-management-button"))
    start_admin_settings_button = KeyboardButton(text=i18n_format("admin-settings-button"))

    # Создаем объект клавиатуры
    keyboard = [
        [start_training_button, phrase_management_button],
        [my_progress_history_button],
        # [start_subscribe_management_button]
    ]

    if is_admin:
        keyboard.append([start_admin_settings_button])

    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=False)
