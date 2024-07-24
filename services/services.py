import logging
import os
import random
import re
import string
from datetime import date, timedelta, datetime

import pytz
from aiogram import Router
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Chat
from aiogram.types import User as AiogramUser
from aiogram_dialog.manager.bg_manager import BgManager
from aiogram_dialog import DialogManager, StartMode, ShowMode
from dotenv import load_dotenv
from tortoise.expressions import Q

from bot_init import bot, dp
from models import Subscription, TypeSubscription, User, ReviewStatus
from services.i18n import create_translator_hub
from services.yookassa import auto_renewal_subscription_command
from states import IntervalSG

load_dotenv()
location = os.getenv('LOCATION')

logger = logging.getLogger('default')


def remove_html_tags(text):
    # Используем регулярное выражение для поиска и удаления всех HTML-тегов
    clean_text = re.sub(r'<.*?>', '', text)
    return clean_text


def is_admin(user_id) -> bool:
    admin_ids = os.getenv('ADMIN_IDS', '')
    admin_ids_list = [int(admin_id) for admin_id in admin_ids.split(',') if admin_id.isdigit()]
    return user_id in admin_ids_list


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
    try:
        logger.debug('Checking subscriptions...')
        free_subscription_type = await TypeSubscription.get_or_none(name="Free")
        current_date = date.today()

        # Получение всех подписок, у которых истек срок действия и тип не Free
        expired_subscriptions = await Subscription.filter(
            Q(date_end__lt=current_date) | Q(date_end__isnull=True),
            ~Q(type_subscription=free_subscription_type)
        )

        for subscription in expired_subscriptions:
            # Установка типа подписки на "Free"
            subscription.type_subscription = free_subscription_type
            await subscription.save()

            user = await User.get(id=subscription.user_id)
            user_locale = user.language
            translator_hub = create_translator_hub()
            translator = translator_hub.get_translator_by_locale(user_locale)
            subscribe = translator.get('subscribe-button')
            use_free = translator.get('use-free')

            # Создание кнопки "Подписаться"
            subscribe_button = InlineKeyboardButton(text=subscribe, callback_data="open_subscribe_dialog")
            free_subscribe_button = InlineKeyboardButton(text=use_free, callback_data="use_free_subscribe")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[subscribe_button], [free_subscribe_button]])

            # Отправка сообщения с кнопкой
            subscription_expired = translator.get('subscription-expired')
            # await bot.send_message(chat_id=subscription.user_id, text=subscription_expired, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in check_subscriptions: {e}")


async def auto_renewal_subscriptions():
    try:
        logger.debug('Auto renewal subscriptions')
        free_subscription_type = await TypeSubscription.get_or_none(name="Free")
        free_trial_subscription_type = await TypeSubscription.get_or_none(name="Free trial")
        current_date = date.today()

        # Получение всех подписок, которые заканчиваются в ближайшие 2 дня
        ending_subscriptions = await Subscription.filter(Q(date_end__lte=current_date + timedelta(days=2)),
                                                         (~Q(type_subscription=free_subscription_type) |
                                                          ~Q(type_subscription=free_trial_subscription_type)))

        for subscription in ending_subscriptions:
            await auto_renewal_subscription_command(subscription.id)
    except Exception as e:
        logger.error(f"Error in auto_renewal_subscriptions: {e}")


async def interval_notifications():
    users = await User.filter(notifications=True).all()
    logger.debug('Interval notifications start')
    logger.debug(f'Interval notifications users: {users}')
    translator_hub = create_translator_hub()

    for user in users:
        user_locale = user.language
        now = datetime.now(pytz.UTC)
        review_statuses = await ReviewStatus.filter(
            Q(user_id=user.id) &
            Q(note=False) &
            Q(next_review__lt=now)
        ).all()

        if review_statuses:
            # Отправляем сообщение пользователю
            translator = translator_hub.get_translator_by_locale(user_locale)
            practice_time = translator.get('practice-time')
            next_practice = translator.get('next')

            try:
                button = InlineKeyboardButton(text=next_practice, callback_data="open_interval_dialog")
                keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
                # Отправка сообщения с кнопкой
                await bot.send_message(chat_id=user.id, text=practice_time, reply_markup=keyboard)
                # Обновляем статусы
                await ReviewStatus.filter(id__in=[status.id for status in review_statuses]).update(note=True)

            except Exception as e:
                logger.error(f"Не удалось отправить сообщение пользователю {user.id}: {e}")
