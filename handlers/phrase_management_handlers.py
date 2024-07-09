from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, Data, ShowMode
from aiogram_dialog.widgets.kbd import Group, Button, Select, Column, Multiselect, ManagedMultiselect, Next, \
    Start, Back
from aiogram_dialog.widgets.text import Format, List, Multi

from handlers.system_handlers import get_user_categories, get_phrases
from models import Category, Phrase
from services.i18n_format import I18NFormat, I18N_FORMAT_KEY, default_format_text
from states import ManagementSG, AddCategorySG, AddOriginalPhraseSG, EditPhraseSG


async def management_dialog_process_result(statr_data: Data, result: dict, dialog_manager: DialogManager, **kwargs):
    if result:
        if 'new_phrase' in result:
            new_phrase = result["new_phrase"]
            phrases = dialog_manager.dialog_data['phrases']
            phrases.append(new_phrase)
            phrases_count = dialog_manager.dialog_data.get('phrases_count')
            phrases_count += 1
            dialog_manager.dialog_data['phrases_count'] = phrases_count


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


async def add_phrase_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY, default_format_text)
    if dialog_manager.dialog_data.get('phrases_count') > 15:
        await callback.answer(i18n_format('phrase-limit'), show_alert=True)
    else:
        category_id = dialog_manager.dialog_data['category_id']
        await dialog_manager.start(state=AddOriginalPhraseSG.text_phrase, data={"category_id": category_id})


async def category_filled(callback: CallbackQuery, checkbox: ManagedMultiselect, dialog_manager: DialogManager, *args,
                          **kwargs):
    dialog_manager.dialog_data['category_filled'] = checkbox.get_checked()


async def phrases_filled(callback: CallbackQuery, checkbox: ManagedMultiselect, dialog_manager: DialogManager, *args,
                         **kwargs):
    dialog_manager.dialog_data['phrases_filled'] = checkbox.get_checked()


async def category_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data['category_id'] = item_id
    user_id = dialog_manager.event.from_user.id
    phrases = await Phrase.filter(category_id=item_id, user_id=user_id).all()
    items = [(phrase.text_phrase, str(phrase.id)) for phrase in phrases]
    dialog_manager.dialog_data['phrases'] = items
    count = len(items)
    dialog_manager.dialog_data['phrases_count'] = count
    await dialog_manager.switch_to(state=ManagementSG.select_phrase)


async def phrase_selected(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    phrase = await Phrase.get(id=item_id)
    if phrase.image_id:
        await callback.message.answer_photo(photo=phrase.image_id)
    if phrase.audio_id:
        await callback.message.answer_audio(audio=phrase.audio_id)
    await dialog_manager.start(state=EditPhraseSG.start, show_mode=ShowMode.DELETE_AND_SEND, data={"phrase_id": item_id})


async def select_phrase_for_delete_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if dialog_manager.find('multi_phrases'):
        multiselect_widget = dialog_manager.find('multi_phrases')
        await multiselect_widget.reset_checked()

    await dialog_manager.switch_to(state=ManagementSG.select_phrase_for_delete)


async def cancel_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.switch_to(state=ManagementSG.start)


async def delite_categories_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    if dialog_manager.find('multi_categories'):
        multiselect_widget = dialog_manager.find('multi_categories')
        await multiselect_widget.reset_checked()
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
    await dialog_manager.switch_to(state=ManagementSG.select_phrase_for_delete)


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
            I18NFormat('phrase-management-dialog'),
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
        Start(I18NFormat('add-category-button'),
              id='start_add_category_dialog',
              state=AddCategorySG.start
              ),
        Button(
            text=I18NFormat('delite-category-button'),
            id='deletion_category',
            on_click=delite_categories_button_clicked,
        ),
        Group(
            # Cancel(I18NFormat('cancel'), id='button_cancel'),
            width=3
        ),
        getter=get_user_categories,
        state=ManagementSG.start
    ),
    Window(
        I18NFormat('delite-category'),
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
        Next(text=I18NFormat('delete-selected-button')),
        Group(
            Button(
                text=I18NFormat('cancel'),
                id='button_cancel',
                on_click=cancel_button_clicked,
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
        I18NFormat('delete-selected-category'),
        Group(
            Button(
                text=I18NFormat('back'),
                id='back',
                on_click=back_categories_to_be_deleted,
            ),
            Button(
                text=I18NFormat('cancel'),
                id='button_cancel',
                on_click=cancel_button_clicked,
            ),
            Button(
                text=I18NFormat('delite'),
                id='confirm_deletion_category',
                on_click=confirm_deletion_category_button_clicked,
            ),
            width=3
        ),
        getter=get_category_for_delite,
        state=ManagementSG.confirm_deletion_category
    ),
    Window(
        I18NFormat('editing-category'),
        Column(
            Select(
                Format('{item[0]}'),
                id='phrase',
                item_id_getter=lambda x: x[1],
                items="phrases",
                on_click=phrase_selected,
            ),
        ),
        Button(
            text=I18NFormat('add-phrase-button'),
            id='add_phrase',
            on_click=add_phrase_button_clicked,
        ),
        Button(
            text=I18NFormat('select-phrase-to-delete'),
            id='select_phrase_for_delete',
            on_click=select_phrase_for_delete_button_clicked,
        ),
        # Next(text=I18NFormat('delete-selected-button')),
        Group(
            Button(
                text=I18NFormat('back'),
                id='button_cancel',
                on_click=cancel_button_clicked,
            ),
            width=3
        ),
        getter=get_phrases,
        state=ManagementSG.select_phrase,
    ),
    Window(
        I18NFormat('editing-category'),
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
        Next(text=I18NFormat('delete-selected-button')),
        Group(
            Back(text=I18NFormat('back')),
            Button(
                text=I18NFormat('cancel'),
                id='button_cancel',
                on_click=cancel_button_clicked,
            ),
            width=3
        ),
        getter=get_phrases,
        state=ManagementSG.select_phrase_for_delete,
    ),
    Window(
        List(
            field=Format('<b>{item[0]}</b>'),
            items='phrases_to_be_deleted'),
        I18NFormat('delete-selected-ones'),
        Group(
            Button(
                text=I18NFormat('back'),
                id='back',
                on_click=back_phrases_to_be_deleted,
            ),
            Button(
                text=I18NFormat('cancel'),
                id='button_cancel',
                on_click=cancel_button_clicked,
            ),
            Button(
                text=I18NFormat('delite'),
                id='confirm_deletion_phrase',
                on_click=confirm_deletion_phrase_button_clicked,
            ),
            width=3
        ),
        getter=get_phrases_for_delite,
        state=ManagementSG.confirm_deletion_phrase
    ),
    on_process_result=management_dialog_process_result
)
