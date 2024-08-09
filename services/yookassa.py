import json
import logging
import os
from datetime import datetime
from typing import Optional

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram_dialog import DialogManager
from aiohttp import web
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
from yookassa import Configuration, Payment
from yookassa.domain.common import SecurityHelper
from yookassa.domain.notification import WebhookNotificationFactory, WebhookNotificationEventType

from bot_init import bot, bg_factory
from models import Payment as PaymentModel, Subscription
from models import TypeSubscription, User
from states import SubscribeSG

load_dotenv()
router = Router()
logger = logging.getLogger('default')

account_id = os.getenv('YOOKASSA_ACCOUNT_ID')
secret_key = os.getenv('YOOKASSA_SECRET_KEY')
redirect_uri = os.getenv('RETURN_URL')

Configuration.account_id = account_id
Configuration.secret_key = secret_key


def get_client_ip(request: web.Request) -> Optional[str]:
    """
    Извлекает IP-адрес клиента из объекта запроса.

    Args:
        request (web.Request): Объект запроса aiohttp.

    Returns:
        Optional[str]: IP-адрес клиента или None, если не удалось определить.
    """
    # Проверяем заголовок X-Forwarded-For
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        # X-Forwarded-For может содержать список IP-адресов, берем первый
        ip = x_forwarded_for.split(',')[0].strip()
    elif request.remote:
        # Если X-Forwarded-For отсутствует, используем remote
        ip = request.remote
    else:
        # Если и remote отсутствует, используем peer_name
        peername = request.transport.get_extra_info('peername')
        if peername is not None:
            ip, _ = peername
        else:
            ip = None

    return ip


async def subscribe_command(callback: CallbackQuery, description: str):
    try:
        type_subscription = await TypeSubscription.get(payload=callback.data)
        # description = type_subscription.description
        description = description
        payload = callback.data
        amount_value = type_subscription.price

        order = Payment.create({
            "amount": {
                "value": amount_value,
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": redirect_uri
            },
            "capture": True,
            "description": description,
            "save_payment_method": True,
            "metadata": {
                'userId': callback.from_user.id,
                'payload': payload,
            },
        })
        order_data = json.loads(order.json())

        await PaymentModel.create(
            user_id=callback.from_user.id,
            type_subscription=type_subscription,
            description=description,
            payload=payload,
            amount_value=amount_value,
            amount_currency="RUB",
            income_amount_currency="RUB",
            payment_method_id=order_data.get('id'),
        )

        user = await User.get(id=callback.from_user.id)
        user.payment_method = order_data.get('id')
        await user.save()

        button = InlineKeyboardButton(text="Оплатить подписку", url=order.confirmation.confirmation_url)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])

        await callback.message.answer('<a href="https://www.google.com">договор оферты</a>\nДля оплаты подписки перейдите по ссылке:', reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Ошибка при сохранении платежа: {e}")


async def auto_renewal_subscription_command(subscription_id):
    try:
        subscription = await Subscription.get(id=subscription_id).prefetch_related('type_subscription')
        amount_value = subscription.type_subscription.price
        description = subscription.type_subscription.description
        payload = subscription.type_subscription.payload
        payment_method_id = subscription.payment_token
        user_id = subscription.user_id

        order = Payment.create({
            "amount": {
                "value": amount_value,
                "currency": "RUB"
            },
            "capture": True,
            "payment_method_id": payment_method_id,
            "description": description,
            "metadata": {
                'userId': user_id,
                'payload': payload,
            },
        })
        order_data = json.loads(order.json())

        await PaymentModel.create(
            user_id=user_id,
            type_subscription_id=subscription.type_subscription.id,
            description=description,
            payload=payload,
            amount_value=amount_value,
            amount_currency="RUB",
            income_amount_currency="RUB",
            payment_method_id=order_data.get('id'),
        )
        logger.info(f"Автоматический для пользователя {user_id} успешно создан")
    except Exception as e:
        logger.error(f"Ошибка при сохранении платежа: {e}")


async def process_yookassa_webhook(request: web.Request):
    try:
        print(f"Получен запрос {request.method} {request.url}")
        event_json = await request.json()
        print(event_json)

        payment_id = event_json.get('paymentId')
        user_id = event_json.get('userId')
        payload = event_json.get('payload')
        is_auto = event_json.get('is_auto')
        amount = event_json.get('amount')
        currency = event_json.get('currency')

        type_subscription = await TypeSubscription.get(payload=payload)

        subscription = await Subscription.get(user_id=user_id)
        subscription.payment_token = payment_id
        subscription.type_subscription = type_subscription
        subscription.date_end = subscription.date_end + relativedelta(months=type_subscription.months)
        await subscription.save()

        user = await User.get(id=user_id)
        # Получаем менеджер диалога для конкретного пользователя и чата
        dialog_manager = bg_factory.bg(
            bot=bot,
            user_id=user_id,
            chat_id=user_id
        )
        await dialog_manager.switch_to(state=SubscribeSG.payment_result)

        if is_auto:
            msg_to_admin = (
                f"Пользователь {user_id} {user.username} {user.first_name} успешно подписался на бота. "
                f"Платеж на сумму {amount} {currency} прошел успешно.")
            await bot.send_message(chat_id=693131974, text=msg_to_admin)
        else:
            msg = f"Поздравляем! Вы оформили подписку. Приятного обучения!"
            msg_to_admin = (
                f"Пользователь {user_id} {user.username} {user.first_name} успешно подписался на бота. "
                f"Платеж на сумму {amount} {currency} прошел успешно.")
            await bot.send_message(chat_id=693131974, text=msg_to_admin)
            await bot.send_message(chat_id=user_id, text=msg)
    except Exception as e:
        logger.error(f"Ошибка при обработке платежа: {e}")
        return web.Response(status=400)  # Сообщаем, что что-то пошло не так

    return web.Response(status=200)  # Сообщаем, что все хорошо
