import logging
import os

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button

from bot_init import bot
from handlers.pay import order
from models import Subscription
from services.i18n_format import I18NFormat, I18N_FORMAT_KEY
from states import SubscribeSG, SubscribeManagementSG

logger = logging.getLogger('default')


async def get_data(dialog_manager: DialogManager, **kwargs):
    subscription = await Subscription.get_or_none(user_id=dialog_manager.event.from_user.id).prefetch_related(
        'type_subscription')
    if subscription:
        type_subscription = subscription.type_subscription.name
        date_end = subscription.date_end
        return {
            'type_subscription': type_subscription,
            'date_end': date_end,
        }


async def one_month_subscription_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # TODO отправить оферту, подключить автоплатеж
    # i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY)
    await order(callback, bot)


async def three_month_subscription_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # TODO подключить автоплатеж
    pass


async def six_month_subscription_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # TODO подключить автоплатеж
    pass


async def change_subscribe_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # TODO удалить автоплатеж
    # await dialog_manager.start(SubscribeSG.start)
    pass


async def unsubscribe_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # TODO удалить автоплатеж
    pass


subscribe_dialog = Dialog(
    Window(
        I18NFormat('user-subscribe-info-dialog'),
        I18NFormat('subscription-information'),
        Button(
            text=I18NFormat('one-month-subscription-button'),
            id='one_month_subscription',
            on_click=one_month_subscription_button_clicked,
        ),
        Button(
            text=I18NFormat('three-month-subscription-button'),
            id='three_month_subscription',
            on_click=three_month_subscription_button_clicked,
        ),
        Button(
            text=I18NFormat('six-month-subscription-button'),
            id='six_month_subscription',
            on_click=six_month_subscription_button_clicked,
        ),
        state=SubscribeSG.start
    ),
)

subscribe_management_dialog = Dialog(
    Window(
        I18NFormat('user-subscribe-info-dialog'),
        Button(
            text=I18NFormat('change-subscribe-button'),
            id='change_subscribe',
            on_click=change_subscribe_button_clicked,
        ),
        Button(
            text=I18NFormat('unsubscribe'),
            id='unsubscribe',
            on_click=unsubscribe_button_clicked,
        ),
        state=SubscribeManagementSG.start,
        getter=get_data,
    ),
)
