from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Group, Cancel, Button, Select, Column, Multiselect, ManagedMultiselect, Back
from aiogram_dialog.widgets.text import Const, Format, List, Multi

from handlers import main_page_button_clicked
from handlers.system_handlers import get_user_categories, get_phrases
from models import Category, Phrase
from states import ManagementSG, AddCategorySG, AddOriginalPhraseSG


async def get_category_for_delite(dialog_manager: DialogManager, **kwargs):
    category_ids = dialog_manager.dialog_data['category_filled']
    categories = await Category.filter(id__in=category_ids).all()
    items = [(category.name, str(category.id)) for category in categories]
    return {'categories_to_be_deleted': items}


async def get_phrases_for_delite(dialog_manager: DialogManager, **kwargs):
    phrases_ids = dialog_manager.dialog_data['phrases_filled']
    phrases = await Phrase.filter(id__in=phrases_ids).all()
    items = [(phrase.text_phrase, str(phrase.id)) for phrase in phrases]
    return {'phrases_to_be_deleted': items}


async def add_category_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=AddCategorySG.start)


async def add_phrase_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    category_id = dialog_manager.dialog_data['category_id']
    await dialog_manager.start(state=AddOriginalPhraseSG.text_phrase, data={"category_id": category_id})


async def category_filled(callback: CallbackQuery, checkbox: ManagedMultiselect, dialog_manager: DialogManager, *args,
                          **kwargs):
    dialog_manager.dialog_data['category_filled'] = checkbox.get_checked()


async def phrases_filled(callback: CallbackQuery, checkbox: ManagedMultiselect, dialog_manager: DialogManager, *args,
                         **kwargs):
    dialog_manager.dialog_data['phrases_filled'] = checkbox.get_checked()


async def category_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    if dialog_manager.find('multi_phrases'):
        multiselect_widget = dialog_manager.find('multi_phrases')
        await multiselect_widget.reset_checked()
    dialog_manager.dialog_data['category_id'] = item_id
    await dialog_manager.switch_to(state=ManagementSG.select_phrase)


async def cancel_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(state=ManagementSG.start)


async def delite_categories_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if dialog_manager.find('multi_categories'):
        multiselect_widget = dialog_manager.find('multi_categories')
        await multiselect_widget.reset_checked()
    await dialog_manager.next()


async def delite_selected_categories_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.next()


async def delite_phrases_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.next()


async def back_categories_to_be_deleted(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if dialog_manager.find('multi_categories'):
        multiselect_widget = dialog_manager.find('multi_categories')
        await multiselect_widget.reset_checked()
    await dialog_manager.switch_to(state=ManagementSG.select_category)


async def back_phrases_to_be_deleted(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if dialog_manager.find('multi_phrases'):
        multiselect_widget = dialog_manager.find('multi_phrases')
        await multiselect_widget.reset_checked()
    await dialog_manager.switch_to(state=ManagementSG.select_phrase)


async def confirm_deletion_category_button_clicked(callback: CallbackQuery, button: Button,
                                                   dialog_manager: DialogManager):
    category_ids = dialog_manager.dialog_data['category_filled']
    for cat_id in category_ids:
        await Category.filter(id=cat_id).delete()
        await Phrase.filter(category_id=cat_id).delete()
    await dialog_manager.back()
    await dialog_manager.switch_to(state=ManagementSG.start)


async def confirm_deletion_phrase_button_clicked(callback: CallbackQuery, button: Button,
                                                 dialog_manager: DialogManager):
    phrase_ids = dialog_manager.dialog_data['phrases_filled']
    for phrase_id in phrase_ids:
        await Phrase.filter(id=phrase_id).delete()
    await dialog_manager.switch_to(state=ManagementSG.start)


management_dialog = Dialog(
    Window(
        Multi(
            Const(text='Управление фразами.'),
            # Const(text='Управление фразами.'),
        ),
        Group(
            Select(
                Format('{item[0]}'),
                id='category',
                item_id_getter=lambda x: x[1],
                items='categories',
                on_click=category_selected,
            ),
            width=2
        ),
        Button(
            text=Const('➕ Добавить категорию'),
            id='add_category',
            on_click=add_category_button_clicked,
        ),
        Button(
            text=Const('❌ Удаление категорий'),
            id='deletion_category',
            on_click=delite_categories_button_clicked,
        ),
        Group(
            Cancel(Const('↩️ Отмена'), id='button_cancel'),
            Button(
                text=Const('🏠 На главную'),
                id='main_page',
                on_click=main_page_button_clicked,
            ),
            width=3
        ),
        getter=get_user_categories,
        state=ManagementSG.start
    ),
    Window(
        Const(text='Выбери категории для удаления:'),
        Const('❗❗❗ Все фразы в выбранных категориях будут удалены'),
        Column(
            Multiselect(
                checked_text=Format('[✔️] {item[0]}'),
                unchecked_text=Format('[     ] {item[0]}'),
                id='multi_categories',
                item_id_getter=lambda x: x[1],
                items="categories",
                # on_click=category_filled
                on_state_changed=category_filled
            ),
        ),
        Button(
            text=Const('❌ Удалить выбранные'),
            id='delite_categories',
            on_click=delite_selected_categories_button_clicked,
        ),
        Group(
            Button(
                text=Const('↩️ Отмена'),
                id='button_cancel',
                on_click=cancel_button_clicked,
            ),
            Button(
                text=Const('🏠 На главную'),
                id='main_page',
                on_click=main_page_button_clicked,
            ),
            width=3
        ),
        getter=get_user_categories,
        state=ManagementSG.select_category
    ),
    Window(
        List(
            field=Format('<b>{item[0]}</b>'),
            items='categories_to_be_deleted'),
        Const('\nУдалить выбранные категории со всеми фразами❓'),
        Group(
            Button(
                text=Const('◀️ Назад'),
                id='back',
                on_click=back_categories_to_be_deleted,
            ),
            Button(
                text=Const('↩️ Отмена'),
                id='button_cancel',
                on_click=cancel_button_clicked,
            ),
            Button(
                text=Const('✅ Удалить'),
                id='confirm_deletion_category',
                on_click=confirm_deletion_category_button_clicked,
            ),
            width=3
        ),
        getter=get_category_for_delite,
        state=ManagementSG.confirm_deletion_category
    ),
    Window(
        Const(text='Выбери фразы для удаления:'),
        Column(
            Multiselect(
                checked_text=Format('[✔️] {item[0]}'),
                unchecked_text=Format('[     ] {item[0]}'),
                id='multi_phrases',
                item_id_getter=lambda x: x[1],
                items="phrases",
                # on_click=category_filled
                on_state_changed=phrases_filled
            ),
        ),
        Button(
            text=Const('➕ Добавить фразу'),
            id='add_phrase',
            on_click=add_phrase_button_clicked,
        ),
        Button(
            text=Const('❌ Удалить выбранные'),
            id='delite_phrases',
            on_click=delite_phrases_button_clicked,
        ),
        Group(
            Button(
                text=Const('↩️ Отмена'),
                id='button_cancel',
                on_click=cancel_button_clicked,
            ),
            Button(
                text=Const('🏠 На главную'),
                id='main_page',
                on_click=main_page_button_clicked,
            ),
            width=3
        ),
        getter=get_phrases,
        state=ManagementSG.select_phrase
    ),
    Window(
        List(
            field=Format('<b>{item[0]}</b>'),
            items='phrases_to_be_deleted'),
        Const('\nУдалить выбранные?'),
        Group(
            Button(
                text=Const('◀️ Назад'),
                id='back',
                on_click=back_phrases_to_be_deleted,
            ),
            Button(
                text=Const('↩️ Отмена'),
                id='button_cancel',
                on_click=cancel_button_clicked,
            ),
            Button(
                text=Const('✅ Удалить'),
                id='confirm_deletion_phrase',
                on_click=confirm_deletion_phrase_button_clicked,
            ),
            width=3
        ),
        getter=get_phrases_for_delite,
        state=ManagementSG.confirm_deletion_phrase
    ),
)
