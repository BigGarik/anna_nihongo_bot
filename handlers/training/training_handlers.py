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
                  id='start_pronunciation_training_dialog',
                  state=PronunciationTrainingSG.select_category
                  ),
            Start(Const('🎯 Лексика'),
                  id='start_lexis_training_dialog',
                  state=LexisTrainingSG.start
                  ),
            Start(Const('🔊 Прослушивание'),
                  id='start_text_to_speech_dialog',
                  state=TextToSpeechSG.start
                  ),
            Start(Const('🌍 Перевод'),
                  id='start_translation_training_dialog',
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
