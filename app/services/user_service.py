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
        last_name: Optional[str] = None,
        organization_name: Optional[str] = None
    ) -> User:
        """Регистрирует нового пользователя или обновляет существующего."""
        async with get_async_session() as session:
            user_repo = UserRepository(session)
            print(f"[register_or_update_user] called for telegram_id={telegram_id}")
            # Ищем существующего пользователя
            user = await user_repo.get_by_telegram_id(telegram_id)
            print(f"[register_or_update_user] user found: {user is not None}")
            if user:
                # Обновляем данные
                user.username = username
                user.first_name = first_name
                user.last_name = last_name
                # Обновляем все поля
                if username is not None:
                    user.username = username
                if first_name is not None:
                    user.first_name = first_name
                if last_name is not None:
                    user.last_name = last_name
                if organization_name is not None:
                    print(f"[register_or_update_user] updating organization for {telegram_id} from '{user.organization_name}' to '{organization_name}'")
                    user.organization_name = organization_name
                
                print(f"[register_or_update_user] updating user {telegram_id}")
                await session.commit()
                await session.refresh(user)
            else:
                # Создаем нового
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    organization_name=organization_name
                )
                print(f"[register_or_update_user] creating new user {telegram_id} with organization: '{organization_name}'")
            if user.id:  # Если пользователь существует
                await user_repo.update(user)
                print(f"[register_or_update_user] user updated {telegram_id}")
            else:  # Новый пользователь
                await user_repo.add(user)
                print(f"[register_or_update_user] user added {telegram_id}")
            return user
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получает пользователя по Telegram ID."""
        async with get_async_session() as session:
            user_repo = UserRepository(session)
            return await user_repo.get_by_telegram_id(telegram_id)

    # Алиас для обратной совместимости
    get_by_telegram_id = get_user_by_telegram_id

    async def get_all_users(self) -> list[User]:
        """Возвращает всех пользователей."""
        async with get_async_session() as session:
            user_repo = UserRepository(session)
            return await user_repo.get_all_users()
