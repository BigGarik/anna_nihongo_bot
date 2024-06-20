from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Const

from states import UserTrainingSG, LexisSG, PronunciationSG


async def pronunciation_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=PronunciationSG.start)


async def lexis_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # await dialog_manager.done()
    await dialog_manager.start(state=LexisSG.start)


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
        Cancel(Const('❌ Отмена'), id='button_cancel'),
        state=UserTrainingSG.start
    ),
)
