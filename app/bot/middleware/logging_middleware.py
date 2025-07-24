from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        # Логируем все входящие сообщения
        if isinstance(event, Message):
            print(f"[INCOMING MESSAGE] User: {event.from_user.id} Chat: {event.chat.id}")
            print(f"Raw text: '{event.text}'")
            print(f"Entities: {event.entities}")
            print(f"State: {data.get('state')}")
            
        return await handler(event, data)
