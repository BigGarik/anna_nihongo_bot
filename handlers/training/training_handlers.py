from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from .states import PronunciationTrainingSG, GrammarTrainingSG, TextToSpeechSG, UserTrainingSG


async def pronunciation_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(state=PronunciationTrainingSG.start)


async def grammar_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # await dialog_manager.done()
    await dialog_manager.start(state=GrammarTrainingSG.start)


async def tts_button_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    # await dialog_manager.done()
    await dialog_manager.start(state=TextToSpeechSG.start)


user_training_dialog = Dialog(
    Window(
        Const(text='Ты в разделе тренировок. Выбирай тренировку и погнали...'),
        Button(
            text=Const('Произношение'),
            id='pronunciation',
            on_click=pronunciation_button_clicked),
        Button(
            text=Const('Грамматика'),
            id='grammar',
            on_click=grammar_button_clicked),
        Button(
            text=Const('Прослушивание (Озвучить текст)'),
            id='tts',
            on_click=tts_button_clicked),
        state=UserTrainingSG.start
    ),
)
