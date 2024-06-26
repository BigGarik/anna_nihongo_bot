from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group, Start
from aiogram_dialog.widgets.text import Const

from handlers import main_page_button_clicked
from states import UserTrainingSG, TranslationTrainingSG, PronunciationTrainingSG, LexisTrainingSG, TextToSpeechSG


user_training_dialog = Dialog(
    Window(
        Const(text='Ты в разделе тренировок. Выбирай тренировку и погнали...'),
        Group(
            Start(Const('🗣 Произношение'),
                  id='user_management_dialog',
                  state=PronunciationTrainingSG.select_category
                  ),
            Start(Const('🎯 Лексика'),
                  id='user_management_dialog',
                  state=LexisTrainingSG.start
                  ),
            Start(Const('🔊 Прослушивание'),
                  id='user_management_dialog',
                  state=TextToSpeechSG.start
                  ),
            Start(Const('🌍 Перевод'),
                  id='user_management_dialog',
                  state=TranslationTrainingSG.start
                  ),
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
