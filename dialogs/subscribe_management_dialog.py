import base64
import json
import logging
import os
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Group, Cancel
from dotenv import load_dotenv

from models import Subscription, TypeSubscription
from services.i18n_format import I18NFormat
from services.yookassa import subscribe_command
from states import SubscribeSG, SubscribeManagementSG

logger = logging.getLogger('default')
load_dotenv()
bot_id = os.getenv('BOT_ID')


async def get_data(dialog_manager: DialogManager, **kwargs):
    subscription = await Subscription.get(user_id=dialog_manager.event.from_user.id).prefetch_related(
        'type_subscription')
    response = {'type_subscription': subscription.type_subscription.name,
                'date_end': subscription.date_end}
    if subscription.type_subscription.name != 'Подписка на 1 месяц':
        response['one_month'] = True
    if subscription.type_subscription.name != 'Подписка на 3 месяца':
        response['three_month'] = True
    if subscription.type_subscription.name != 'Подписка на 6 месяцев':
        response['six_month'] = True

    if subscription.type_subscription.name == 'Free' or subscription.type_subscription.name == 'Free trial':
        response['is_not_subscriber'] = True
    else:
        response['is_subscriber'] = True

    return response


async def one_month_subscription_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # TODO отправить оферту, подключить автоплатеж
    # i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    # await order(callback, bot)
    # await subscribe_command(callback)
    pass


async def three_month_subscription_button_clicked(callback: CallbackQuery, button: Button,
                                                  dialog_manager: DialogManager):
    # type_subscription = await TypeSubscription.get(payload=callback.data)
    # description = type_subscription.description
    # payload = callback.data
    # amount_value = type_subscription.price
    #
    # params = {
    #     'amount_value': amount_value,
    #     'description': description,
    #     'payload': payload,
    #     'bot_id': bot_id,
    #     'userId': callback.from_user.id,
    # }
    #
    # # Кодируем параметры в строку запроса
    # # import urllib.parse
    # # encoded_params = urllib.parse.urlencode(params)
    # encoded_params = base64.b64encode(json.dumps(params).encode()).decode()
    # # Создаем URL для WebApp с параметрами
    # # webapp_url = f"https://biggarik.ru/payment/test/?params={encoded_params}"
    # webapp_url = f"https://biggarik.ru/payment/create/?params={encoded_params}"
    # # web_app_button = InlineKeyboardButton(text="Оплатить", url=webapp_url)
    # web_app_button = InlineKeyboardButton(text="Оплатить", web_app=WebAppInfo(url=webapp_url))
    # keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app_button]])
    # await callback.message.answer("Нажмите кнопку ниже для оплаты.", reply_markup=keyboard)
    pass


async def six_month_subscription_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # TODO подключить автоплатеж
    pass


async def subscribe_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass
    # await dialog_manager.start(SubscribeSG.start)


async def change_subscribe_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass
    # await dialog_manager.start(SubscribeSG.start)


async def unsubscribe_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # TODO удалить автоплатеж
    pass


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
                on_click=one_month_subscription_button_clicked,
                when='one_month'
            ),
            Button(
                text=I18NFormat('three-month-subscription-button'),
                id='three_month_subscription',
                on_click=three_month_subscription_button_clicked,
                when='three_month'
            ),
            Button(
                text=I18NFormat('six-month-subscription-button'),
                id='six_month_subscription',
                on_click=six_month_subscription_button_clicked,
                when='six_month'
            ),
            width=3
        ),
        Cancel(I18NFormat("cancel"), id="button_cancel"),
        state=SubscribeSG.start,
        getter=get_data,
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
