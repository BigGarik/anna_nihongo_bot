from aiogram.fsm.state import State, StatesGroup

# Создаем базу данных пользователей
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


class AdminDialogSG(StatesGroup):
    start = State()
    add_category = State()
    add_main_image = State()
    generate_image = State()


class AddCategorySG(StatesGroup):
    start = State()


class AddOriginalPhraseSG(StatesGroup):
    text_phrase = State()
    translation = State()
    audio = State()
    image = State()
    comment = State()
    save = State()


class EditPhraseSG(StatesGroup):
    start = State()
    text_phrase = State()
    translation = State()
    audio = State()
    image = State()
    comment = State()


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


class IntervalSG(StatesGroup):
    start = State()
    # pronunciation = State()
    # pronunciation_text = State()
    # lexis = State()
    # listening = State()
    # translation = State()


class IntervalTrainingSG(StatesGroup):
    pronunciation = State()
    pronunciation_text = State()
    lexis = State()
    listening = State()
    translation = State()


class ErrorIntervalSG(StatesGroup):
    start = State()


class TranslationTrainingSG(StatesGroup):
    start = State()
    waiting_answer = State()


class ManagementSG(StatesGroup):
    start = State()
    select_category = State()
    confirm_deletion_category = State()
    select_phrase = State()
    select_phrase_for_delete = State()
    confirm_deletion_phrase = State()


class SubscribeSG(StatesGroup):
    start = State()
    payment = State()
    payment_result = State()


class SubscribeManagementSG(StatesGroup):
    start = State()


class UserManagementSG(StatesGroup):
    start = State()
    user_delite = State()
    user_manage = State()


class SelectLanguageSG(StatesGroup):
    start = State()


class SmartPhraseAdditionSG(StatesGroup):
    start = State()
    save = State()
