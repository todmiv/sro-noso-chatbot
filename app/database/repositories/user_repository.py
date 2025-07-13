from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """CRUD-операции для модели User."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_telegram_id(self, tg_id: int) -> Optional[User]:
        stmt = select(User).where(User.telegram_id == tg_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, user: User) -> None:
        self._session.add(user)
        await self._session.commit()
