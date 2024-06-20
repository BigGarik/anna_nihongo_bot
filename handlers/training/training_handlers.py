from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Const

from states import UserTrainingSG, TranslationTrainingSG, PronunciationTrainingSG, LexisTrainingSG


async def pronunciation_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=PronunciationTrainingSG.select_category)


async def lexis_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=LexisTrainingSG.start)


async def translation_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=TranslationTrainingSG.start)


user_training_dialog = Dialog(
    Window(
        Const(text='Ты в разделе тренировок. Выбирай тренировку и погнали...'),
        Button(
            text=Const('🗣 Произношение'),
            id='pronunciation',
            on_click=pronunciation_button_clicked),
        Button(
            text=Const('🎯 Лексика'),
            id='lexis',
            on_click=lexis_button_clicked),
        Button(
            text=Const('🌍 Перевод'),
            id='translation',
            on_click=translation_button_clicked),
        Cancel(Const('❌ Отмена'), id='button_cancel'),
        state=UserTrainingSG.start
    ),
)
