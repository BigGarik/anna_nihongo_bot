from aiogram.fsm.state import State, StatesGroup

# Создаем "базу данных" пользователей
user_dict: dict[int, dict[str, str | int | bool]] = {}


# Создаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMInLearn(StatesGroup):
    # Создаем экземпляры класса State, последовательно
    # перечисляя возможные состояния, в которых будет находиться
    # бот в разные моменты взаимодействия с пользователем
    select_category = State()  # Состояние выбора категории
    original_phrase = State()  # Состояние ожидания голосового сообщения с повтором оригинальной фразы
    self_phrase = State()  # Состояние ожидания голосового сообщения любой своей фразы


class StartDialogSG(StatesGroup):
    start = State()


class UserStartDialogSG(StatesGroup):
    start = State()


class AdminDialogSG(StatesGroup):
    start = State()


class AddCategorySG(StatesGroup):
    start = State()


class AddOriginalPhraseSG(StatesGroup):
    text_phrase = State()
    translation = State()
    audio = State()
    image = State()
    comment = State()
    save = State()


class AddPhraseSG(StatesGroup):
    category = State()
    phrase = State()


class UserTrainingSG(StatesGroup):
    start = State()


class LexisTrainingSG(StatesGroup):
    start = State()
    waiting_answer = State()


class PronunciationTrainingSG(StatesGroup):
    select_category = State()
    select_phrase = State()
    waiting_answer = State()


class TextToSpeechSG(StatesGroup):
    start = State()


class TranslationTrainingSG(StatesGroup):
    start = State()
    waiting_answer = State()


class ManagementSG(StatesGroup):
    start = State()
    select_category = State()
    confirm_deletion_category = State()
    select_phrase = State()
    confirm_deletion_phrase = State()
