import base64
import json
import logging
import os

from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button, Group, Cancel, WebApp, Next
from aiogram_dialog.widgets.text import Text, Format
from dotenv import load_dotenv

from models import Subscription, TypeSubscription, User
from services.i18n_format import I18NFormat, I18N_FORMAT_KEY
from states import SubscribeSG, SubscribeManagementSG

logger = logging.getLogger('default')
load_dotenv()
bot_id = os.getenv('BOT_ID')
base_webhook_url = os.getenv('BASE_WEBHOOK_URL')


async def get_data(dialog_manager: DialogManager, **kwargs):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    subscription = await Subscription.get_or_none(user_id=dialog_manager.event.from_user.id).prefetch_related(
        'type_subscription')
    response = {'type_subscription': i18n_format(subscription.type_subscription.name),
                'date_end': subscription.date_end}
    if subscription.payment_token:
        if subscription.type_subscription.name != 'one-month-subscription-name':
            response['one_month'] = True
        if subscription.type_subscription.name != 'three-month-subscription-name':
            response['three_month'] = True
        if subscription.type_subscription.name != 'six-month-subscription-name':
            response['six_month'] = True
    else:
        response['one_month'] = True
        response['three_month'] = True
        response['six_month'] = True

    if subscription.payment_token:
        response['is_subscriber'] = True
    else:
        response['is_not_subscriber'] = True

    type_subscriptions = await TypeSubscription.all()
    for type_sub in type_subscriptions:
        prise = type_sub.price
        name_prise = type_sub.name
        response[str(name_prise)] = prise
    return response


async def get_webapp_url(dialog_manager: DialogManager, **kwargs):
    return dialog_manager.dialog_data


async def subscription_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    type_subscription = await TypeSubscription.get(payload=callback.data)
    description = i18n_format(type_subscription.description)
    payload = callback.data
    amount_value = type_subscription.price

    params = {
        'amount_value': amount_value,
        'description': description,
        'payload': payload,
        'bot_id': bot_id,
        'userId': callback.from_user.id,
    }

    # Кодируем параметры в строку запроса
    encoded_params = base64.b64encode(json.dumps(params).encode()).decode()
    # Создаем URL для WebApp с параметрами
    webapp_url = f"{base_webhook_url}/payment/create/?params={encoded_params}"
    dialog_manager.dialog_data['webapp_url'] = webapp_url
    # web_app_button = InlineKeyboardButton(text=i18n_format("pay"), web_app=WebAppInfo(url=webapp_url))
    # keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app_button]])
    # pay_msg = await callback.message.answer(i18n_format("click-to-pay"), reply_markup=keyboard)
    # user = await User.get(id=callback.from_user.id)
    # user.pay_msg_id = pay_msg.message_id
    # await user.save()
    await dialog_manager.next()


# async def three_month_subscription_button_clicked(callback: CallbackQuery, button: Button,
#                                                   dialog_manager: DialogManager):
#     i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
#     type_subscription = await TypeSubscription.get(payload=callback.data)
#     description = i18n_format(type_subscription.description)
#     payload = callback.data
#     amount_value = type_subscription.price
#
#     params = {
#         'amount_value': amount_value,
#         'description': description,
#         'payload': payload,
#         'bot_id': bot_id,
#         'userId': callback.from_user.id,
#     }
#
#     # Кодируем параметры в строку запроса
#     encoded_params = base64.b64encode(json.dumps(params).encode()).decode()
#     # Создаем URL для WebApp с параметрами
#     webapp_url = f"{base_webhook_url}/payment/create/?params={encoded_params}"
#     web_app_button = InlineKeyboardButton(text=i18n_format("pay"), web_app=WebAppInfo(url=webapp_url))
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app_button]])
#     pay_msg = await callback.message.answer(i18n_format("click-to-pay"), reply_markup=keyboard)
#     user = await User.get(id=callback.from_user.id)
#     user.pay_msg_id = pay_msg.message_id
#     await user.save()
#
#
# async def six_month_subscription_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
#     # TODO подключить автоплатеж
#     pass


async def subscribe_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(SubscribeSG.start)


async def change_subscribe_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(SubscribeSG.start)


async def unsubscribe_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    subscription = await Subscription.get_or_none(user_id=callback.from_user.id)
    subscription.payment_token = None
    await subscription.save()
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    await callback.message.answer(i18n_format('subscription-canceled'))
    dialog_manager.show_mode = ShowMode.SEND


# async def cancel_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
#
#     await dialog_manager.done()


subscribe_dialog = Dialog(
    Window(
        I18NFormat('user-subscribe-info-dialog'),
        I18NFormat('subscription-information'),
        Group(
            Button(
                text=I18NFormat('one-month-subscription-button'),
                id='one_month_subscription',
                on_click=subscription_button_clicked,
                when='one_month'
            ),
            Button(
                text=I18NFormat('three-month-subscription-button'),
                id='three_month_subscription',
                on_click=subscription_button_clicked,
                when='three_month'
            ),
            Button(
                text=I18NFormat('six-month-subscription-button'),
                id='six_month_subscription',
                on_click=subscription_button_clicked,
                when='six_month'
            ),
            width=3
        ),
        Cancel(I18NFormat("cancel"), id="button_cancel"),
        state=SubscribeSG.start,
        getter=get_data,
    ),
    Window(
        I18NFormat('click-to-pay'),
        WebApp(url=Format('{webapp_url}'), text=I18NFormat('pay')),
        state=SubscribeSG.payment,
        getter=get_webapp_url,
    ),
    Window(
        I18NFormat('subscription'),
        state=SubscribeSG.payment_result,
    ),
)

subscribe_management_dialog = Dialog(
    Window(
        I18NFormat('user-subscribe-info-dialog'),
        Group(
            Button(
                text=I18NFormat('change-subscribe-button'),
                id='change_subscribe',
                on_click=change_subscribe_button_clicked,
            ),
            Button(
                text=I18NFormat('unsubscribe-button'),
                id='unsubscribe',
                on_click=unsubscribe_button_clicked,
            ),
            when='is_subscriber',
            width=2
        ),
        Button(
            text=I18NFormat('subscribe-button'),
            id='subscribe',
            on_click=subscribe_button_clicked,
            when='is_not_subscriber',
        ),
        state=SubscribeManagementSG.start,
        getter=get_data,
    ),
)
