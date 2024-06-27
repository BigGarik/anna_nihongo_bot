import os
import random
import string
from datetime import date

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from tortoise.expressions import Q

from bot_init import bot
from models import Subscription, TypeSubscription

load_dotenv()
location = os.getenv('LOCATION')


def normalize_text(text):
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = text.strip()
    return text


def replace_random_words(phrase):
    words = phrase.split()
    # Убедимся, что в фразе есть более двух слов для замены
    if len(words) > 3:
        # Выбираем два разных случайных индекса слов, которые не находятся рядом
        first_index = random.randint(0, len(words) - 3)
        second_index = random.randint(first_index + 2, len(words) - 1)

        # Заменяем выбранные слова на три подчеркивания
        words[first_index] = '___'
        words[second_index] = '___'
    else:
        index = random.randint(0, len(words) - 1)
        words[index] = '___'
    # Возвращаем измененную фразу
    if location == 'ja-JP':
        return ''.join(words)
    else:
        return ' '.join(words)


async def check_subscriptions():
    free_subscription_type = await TypeSubscription.get_or_none(name="Free")
    current_date = date.today()

    # Получение всех подписок, у которых истек срок действия
    expired_subscriptions = await Subscription.filter(
        Q(date_end__lt=current_date) | Q(date_end__isnull=True),
        ~Q(type_subscription=free_subscription_type)
    )

    for subscription in expired_subscriptions:
        # Установка типа подписки на "Free"
        subscription.type_subscription = free_subscription_type
        await subscription.save()

        # Создание кнопки "Подписаться"
        subscribe_button = InlineKeyboardButton(text="Подписаться", callback_data="open_subscribe_dialog")
        free_subscribe_button = InlineKeyboardButton(text="Продолжить бесплатно", callback_data="use_free_subscribe")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[subscribe_button], [free_subscribe_button]])

        # Отправка сообщения с кнопкой
        # await bot.send_message(subscription.user_id, "Ваша подписка истекла.", reply_markup=keyboard)

