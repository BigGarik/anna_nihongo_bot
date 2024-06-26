from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.text import Const

from handlers import main_page_button_clicked
from states import UserTrainingSG, TranslationTrainingSG, PronunciationTrainingSG, LexisTrainingSG, TextToSpeechSG


async def pronunciation_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=PronunciationTrainingSG.select_category)


async def lexis_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=LexisTrainingSG.start)


async def tts_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # await dialog_manager.done()
    await dialog_manager.start(state=TextToSpeechSG.start)


async def translation_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=TranslationTrainingSG.start)


user_training_dialog = Dialog(
    Window(
        Const(text='Ты в разделе тренировок. Выбирай тренировку и погнали...'),
        Group(
            Button(
                text=Const('🗣 Произношение'),
                id='pronunciation',
                on_click=pronunciation_button_clicked),
            Button(
                text=Const('🎯 Лексика'),
                id='lexis',
                on_click=lexis_button_clicked),
            Button(
                text=Const('🔊 Прослушивание'),
                id='tts',
                on_click=tts_button_clicked),
            Button(
                text=Const('🌍 Перевод'),
                id='translation',
                on_click=translation_button_clicked),
            width=2
        ),
        Button(
            text=Const('🏠 На главную'),
            id='main_page',
            on_click=main_page_button_clicked,
        ),
        state=UserTrainingSG.start
    ),
)
