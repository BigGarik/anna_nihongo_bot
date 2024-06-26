from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format, Const

from handlers import main_page_button_clicked
from states import SubscribeSG, SubscribeManagementSG


async def subscribe_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def change_subscribe_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


async def unsubscribe_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    pass


subscribe_dialog = Dialog(
    Window(
        Format(
            'Описание всех вариантов подписки'
        ),
        Button(
            text=Const('Оформить подписку'),
            id='subscribe',
            on_click=subscribe_button_clicked,
        ),
        Button(
            text=Const('🏠 На главную'),
            id='main_page',
            on_click=main_page_button_clicked,
        ),
        state=SubscribeSG.start
    ),
)


subscribe_management_dialog = Dialog(
    Window(
        Format(
            'Описание текущей подписки'
        ),
        Button(
            text=Const('Изменить подписку'),
            id='change_subscribe',
            on_click=change_subscribe_button_clicked,
        ),
        Button(
            text=Const('Отменить подписку'),
            id='unsubscribe',
            on_click=unsubscribe_button_clicked,
        ),
        Button(
            text=Const('🏠 На главную'),
            id='main_page',
            on_click=main_page_button_clicked,
        ),
        state=SubscribeManagementSG.start
    ),
)
