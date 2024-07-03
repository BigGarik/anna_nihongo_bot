from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button

from models import Subscription
from services.i18n_format import I18NFormat
from states import SubscribeSG, SubscribeManagementSG


async def get_data(dialog_manager: DialogManager, **kwargs):
    subscription = await Subscription.get_or_none(user_id=dialog_manager.event.from_user.id).prefetch_related('type_subscription')
    if subscription:
        type_subscription = subscription.type_subscription.name
        date_end = subscription.date_end
        return {
            'type_subscription': type_subscription,
            'date_end': date_end,
        }


async def subscribe_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def change_subscribe_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def unsubscribe_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


subscribe_dialog = Dialog(
    Window(
        I18NFormat(
            'Описание всех вариантов подписки'
        ),
        Button(
            text=I18NFormat('subscribe-button'),
            id='subscribe',
            on_click=subscribe_button_clicked,
        ),
        state=SubscribeSG.start
    ),
)


subscribe_management_dialog = Dialog(
    Window(
        I18NFormat('subscribe-info-dialog'),
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
