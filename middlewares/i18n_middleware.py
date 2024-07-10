import logging
from typing import Any, Awaitable, Callable, Dict, Union

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.dispatcher.middlewares.manager import MiddlewareManager
from aiogram.types import CallbackQuery, Message
from fluent.runtime import FluentLocalization

from models import User
from services.i18n_format import I18N_FORMAT_KEY

logger = logging.getLogger('default')


def update_middleware_manager(manager: MiddlewareManager, new_middleware):
    # Find and remove the old i18n middleware
    old_middleware = next((m for m in manager._middlewares if isinstance(m, I18nMiddleware)), None)
    if old_middleware:
        manager.unregister(old_middleware)

    # Register the new middleware
    manager.register(new_middleware)


class I18nMiddleware(BaseMiddleware):
    def __init__(
            self,
            l10ns: Dict[str, FluentLocalization],
            default_lang: str,
    ):
        super().__init__()
        self.l10ns = l10ns
        self.default_lang = default_lang

    async def __call__(
            self,
            handler: Callable[
                [Union[Message, CallbackQuery], Dict[str, Any]],
                Awaitable[Any],
            ],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        user = await User.get_or_none(id=user_id)
        lang = user.language if user else self.default_lang
        l10n = self.l10ns[lang]
        data[I18N_FORMAT_KEY] = l10n.format_value

        return await handler(event, data)