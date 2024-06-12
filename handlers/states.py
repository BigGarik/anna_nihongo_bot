from aiogram.fsm.state import StatesGroup, State


class StartDialogSG(StatesGroup):
    start = State()


class UserStartDialogSG(StatesGroup):
    start = State()


class AdminDialogSG(StatesGroup):
    start = State()


class AddOriginalPhraseSG(StatesGroup):
    category = State()
    text_phrase = State()
    translation = State()
    audio = State()
    image = State()
    comment = State()
    save = State()


class AddPhraseSG(StatesGroup):
    category = State()
    phrase = State()

