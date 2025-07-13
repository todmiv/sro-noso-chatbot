from typing import Optional

from app.database.repositories.user_repository import UserRepository


class AuthService:
    """Сервис аутентификации и проверки членства СРО."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._user_repo = user_repo

    async def is_member(self, telegram_id: Optional[int]) -> bool:
        if telegram_id is None:
            return False
        user = await self._user_repo.get_by_telegram_id(telegram_id)
        return bool(user and user.is_member)
