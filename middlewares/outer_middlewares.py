import logging
import os
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Update
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


# Middleware для логирования всех апдейтов
class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
        print(f"Received update type: {event.event_type}")
        print(f"Update content: {event.model_dump_json(indent=2)}")
        return await handler(event, data)


if __name__ == '__main__':
    pass
