import io
import logging
import os
import random
import re
import string
from datetime import date, timedelta, datetime, timezone

import pytz
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from tortoise.exceptions import IntegrityError
from tortoise.expressions import Q
from tortoise.functions import Avg

from bot_init import bot
from models import Subscription, TypeSubscription, User, ReviewStatus, UserProgress
from services.i18n import create_translator_hub
from services.yookassa import auto_renewal_subscription_command

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
            if subscription.payment_token:
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
        logger.debug(f'Interval notifications review statuses: {review_statuses}')

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

                three_days_ago = now - timedelta(days=3)
                await ReviewStatus.filter(id__in=[status.id for status in review_statuses],
                                          next_review__lt=three_days_ago).delete()

            except Exception as e:
                logger.error(f"Не удалось отправить сообщение пользователю {user.id}: {e}")


async def auto_reset_daily_counter():
    users = await User.all()
    today = datetime.now().date()
    for user in users:
        try:
            # Попытка создать новую запись
            progress = await UserProgress.create(
                user_id=user.id,
                date=today,
                score=user.day_counter
            )
            logger.debug(f"Created new progress for user {user.id}: {progress.score}")
        except IntegrityError:
            # Если запись уже существует, получаем и обновляем ее
            progress = await UserProgress.get(
                user_id=user.id,
                date=today
            )
            progress.score = user.day_counter
            await progress.save()
            logger.debug(f"Updated progress for user {user.id}: {progress.score}")

        # Опционально: сбрасываем day_counter пользователя
        user.day_counter = 0
        await user.save()

    logger.debug('=============================================')


async def build_user_progress_histogram(user_id: int, days: int = 30):
    """
    Строит гистограмму прогресса пользователя за указанный период.
    :param user_id: ID пользователя
    :param days: количество дней для анализа (7 или 30)
    :return: объект BytesIO с изображением гистограммы
    """
    if days not in [7, 30]:
        raise ValueError("Период должен быть 7 или 30 дней")

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days - 1)

    user = await User.get(id=user_id)
    today_counter = user.day_counter

    # Получаем данные о прогрессе пользователя
    progress_data = await UserProgress.filter(
        user_id=user_id,
        date__range=[start_date, end_date]
    ).values('date', 'score')

    # Создаем словарь для хранения данных за каждый день
    daily_scores = {start_date + timedelta(days=i): 0 for i in range(days)}

    # Заполняем словарь данными из базы
    for item in progress_data:
        daily_scores[item['date']] = item['score']

    # Добавляем данные текущего дня
    daily_scores[end_date] = max(daily_scores[end_date], today_counter)

    # Подготавливаем данные для построения графика
    dates = list(daily_scores.keys())
    scores = list(daily_scores.values())

    # Создаем график
    plt.figure(figsize=(12, 6))
    bars = plt.bar(dates, scores, align='center', alpha=0.8)
    plt.title(f"Прогресс за последние {days} дней")
    plt.xlabel("Дата")
    plt.ylabel("Количество выполненных заданий")
    plt.xticks(rotation=45)

    # Добавляем текстовые метки с точными значениями над каждым столбцом
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2., height,
                 f'{height:.0f}', ha='center', va='bottom')

    plt.tight_layout()

    # Сохраняем график в BytesIO объект
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    plt.close()

    return img_buf
