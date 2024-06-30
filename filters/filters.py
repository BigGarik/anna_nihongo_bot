import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

from services.i18n_format import I18N_FORMAT_KEY, default_format_text

logger = logging.getLogger(__name__)


# Собственный фильтр, проверяющий юзера на админа
class IsAdmin(BaseFilter):
    def __init__(self, admin_ids: list[int]) -> None:
        # В качестве параметра фильтр принимает список с целыми числами
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids


# class I18nTextFilter(BaseFilter):
#     def __init__(self, text_key: str):
#         self.text_key = text_key
#
#     async def __call__(self, message: Message) -> bool:
#         dialog_manager = get_dialog_manager()  # Получаем DialogManager из контекста
#         i18n_format = dialog_manager.middleware_data.get(I18N_FORMAT_KEY, default_format_text)
#         localized_text = i18n_format(self.text_key, {})
#         print(f"I18nTextFilter: key='{self.text_key}', localized='{localized_text}', message='{message.text}'")
#         return message.text == localized_text