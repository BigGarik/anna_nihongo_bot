import asyncio
import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message, Update
from aiohttp import web

from services.i18n_format import I18N_FORMAT_KEY, default_format_text

logger = logging.getLogger('default')


# Собственный фильтр, проверяющий юзера на админа
class IsAdmin(BaseFilter):
    def __init__(self, admin_ids: list[int]) -> None:
        # В качестве параметра фильтр принимает список с целыми числами
        self.admin_ids = admin_ids

    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids


# Фильтр для отсеивания запросов с X-Telegram-Bot-Api-Secret-Token
def yookassa_webhook_filter(request):
    return 'X-Telegram-Bot-Api-Secret-Token' not in request.headers


# Кастомный фильтр для YooKassa
class YooKassaFilter(asyncio.Protocol):
    async def __call__(self, update: Update, event_from_user):
        if not isinstance(update, web.Request):
            return False
        return 'DFer1234' not in update.headers
