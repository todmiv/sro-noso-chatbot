from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from typing import Any, Awaitable, Callable, Dict

from app.services.auth_service import AuthService


class AuthMiddleware(BaseMiddleware):
    """Проверяет право пользователя на доступ к приватным функциям."""

    def __init__(self, auth_service: AuthService) -> None:
        self._auth_service = auth_service

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id if hasattr(event, "from_user") else None
        data["is_member"] = await self._auth_service.is_member(user_id) if user_id else False
        return await handler(event, data)
