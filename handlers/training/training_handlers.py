from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Group, Start

from services.i18n_format import I18NFormat
from states import UserTrainingSG, TranslationTrainingSG, PronunciationTrainingSG, LexisTrainingSG, TextToSpeechSG

user_training_dialog = Dialog(
    Window(
        I18NFormat("training-dialog"),
        Group(
            Start(I18NFormat('pronunciation'),
                  id='start_pronunciation_training_dialog',
                  state=PronunciationTrainingSG.select_category
                  ),
            Start(I18NFormat('vocabulary'),
                  id='start_lexis_training_dialog',
                  state=LexisTrainingSG.start
                  ),
            Start(I18NFormat('translation'),
                  id='start_translation_training_dialog',
                  state=TranslationTrainingSG.start
                  ),
            Start(I18NFormat('listening'),
                  id='start_text_to_speech_dialog',
                  state=TextToSpeechSG.start,
                  ),
            width=2
        ),
        state=UserTrainingSG.start
    ),
)
