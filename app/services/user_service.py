from typing import Optional

from app.database.connection import get_async_session
from app.database.repositories.user_repository import UserRepository
from app.models.user import User


class UserService:
    """Сервис для работы с пользователями."""
    
    async def register_or_update_user(
        self,
        telegram_id: int,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """Регистрирует нового пользователя или обновляет существующего."""
        async with get_async_session() as session:
            user_repo = UserRepository(session)
            
            # Ищем существующего пользователя
            user = await user_repo.get_by_telegram_id(telegram_id)
            
            if user:
                # Обновляем данные
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
            else:
                # Создаем нового
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name
                )
            
            await user_repo.save(user)
            return user
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получает пользователя по Telegram ID."""
        async with get_async_session() as session:
            user_repo = UserRepository(session)
            return await user_repo.get_by_telegram_id(telegram_id)

    # Алиас для обратной совместимости
    get_by_telegram_id = get_user_by_telegram_id
