from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, Select, ScrollingGroup
from aiogram_dialog.widgets.text import Const, Format, Multi

from handlers.system_handlers import get_non_admin_users, get_user_data
from models import User, Subscription
from services.i18n_format import I18NFormat
from states import UserManagementSG


async def select_user_button_clicked(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager,
                                     user_id: str):
    user = await User.get_or_none(id=user_id)
    subscription = await Subscription.get_or_none(user_id=user_id)
    if subscription:
        sub_date_start = subscription.date_start.strftime('%Y-%m-%d')
        sub_date_end = subscription.date_end.strftime('%Y-%m-%d') if subscription.date_end else None
        type_subscription = await subscription.type_subscription.first()
    else:
        sub_date_start = ''
        sub_date_end = ''
        type_subscription = ''

    user_management_user = {
        'user_id': user_id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'sub_date_start': sub_date_start,
        'sub_date_end': sub_date_end,
        'type_subscription': type_subscription.name,
    }
    await dialog_manager.update(user_management_user)
    await dialog_manager.next()


user_management_dialog = Dialog(
    Window(
        I18NFormat('Админка'),
        I18NFormat('Управление пользователями'),
        ScrollingGroup(
            Select(
                Format('{item[0]} {item[1]}'),
                id='user',
                item_id_getter=lambda x: x[2],
                items="users",
                on_click=select_user_button_clicked
            ),
            id="users",
            width=1,
            height=6,
        ),
        Group(
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            width=3
        ),
        state=UserManagementSG.start,
        getter=get_non_admin_users,
    ),
    Window(
        Multi(
            I18NFormat('Информация о пользователе:'),
            I18NFormat('Пользователь: <b>{username} {first_name} {last_name}</b>'),
            I18NFormat('Текущая подписка:  <b>{type_subscription}</b>'),
            I18NFormat('С <b>{sub_date_start}</b> до <b>{sub_date_end}</b>'),
        ),
        Group(
            Cancel(I18NFormat('cancel'), id='button_cancel'),
            width=3
        ),
        getter=get_user_data,
        state=UserManagementSG.user_manage
    )
)
