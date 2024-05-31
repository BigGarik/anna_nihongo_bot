from aiogram.fsm.state import StatesGroup, State


class UserTrainingSG(StatesGroup):
    start = State()


class GrammarTrainingSG(StatesGroup):
    start = State()


class PronunciationTrainingSG(StatesGroup):
    start = State()


class TextToSpeechSG(StatesGroup):
    start = State()
