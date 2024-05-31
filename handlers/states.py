from aiogram.fsm.state import StatesGroup, State


class StartDialogSG(StatesGroup):
    start = State()


class UserStartDialogSG(StatesGroup):
    start = State()
