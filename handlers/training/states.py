from aiogram.fsm.state import StatesGroup, State


class UserTrainingSG(StatesGroup):
    start = State()


class LexisTrainingSG(StatesGroup):
    start = State()
    waiting_answer = State()


class PronunciationTrainingSG(StatesGroup):
    start = State()


class TextToSpeechSG(StatesGroup):
    start = State()
