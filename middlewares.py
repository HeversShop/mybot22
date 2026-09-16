'''Simple per-user throttling middleware.'''
import time
from typing import Any, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from config import THROTTLE_RATE_SECONDS


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate=THROTTLE_RATE_SECONDS):
        self.rate = rate
        self._last = {}

    async def __call__(self, handler, event: TelegramObject, data: Dict[str, Any]):
        # Never throttle payments, WebApp orders or shared contacts
        if isinstance(event, Message) and (event.successful_payment or event.web_app_data or event.contact):
            return await handler(event, data)
        user = data.get('event_from_user')
        if user is not None:
            now = time.monotonic()
            last = self._last.get(user.id, 0.0)
            if now - last < self.rate:
                if isinstance(event, CallbackQuery):
                    await event.answer('Slishkom bystro, podozhdite')
                return None
            self._last[user.id] = now
        return await handler(event, data)
