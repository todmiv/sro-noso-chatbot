from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message


class MessageRepository:
    """Репозиторий для работы с сообщениями."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, message: Message) -> Message:
        """Сохраняет сообщение."""
        self._session.add(message)
        await self._session.commit()
        await self._session.refresh(message)
        return message
    
    async def get_by_id(self, message_id: int) -> Optional[Message]:
        """Получает сообщение по ID."""
        stmt = select(Message).where(Message.id == message_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_session_id(self, session_id: int, limit: int = 10) -> List[Message]:
        """Получает сообщения по ID сессии."""
        stmt = (
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(desc(Message.timestamp))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_recent_messages(self, user_id: int, limit: int = 5) -> List[Message]:
        """Получает последние сообщения пользователя."""
        stmt = (
            select(Message)
            .join(Message.session)
            .where(Message.session.has(user_id=user_id))
            .order_by(desc(Message.timestamp))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def count_user_messages(self, user_id: int) -> int:
        """Подсчитывает количество сообщений пользователя."""
        stmt = (
            select(func.count(Message.id))
            .join(Message.session)
            .where(Message.session.has(user_id=user_id))
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0
    
    async def get_messages_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime,
        limit: int = 100
    ) -> List[Message]:
        """Получает сообщения за период."""
        stmt = (
            select(Message)
            .where(
                and_(
                    Message.timestamp >= start_date,
                    Message.timestamp <= end_date
                )
            )
            .order_by(desc(Message.timestamp))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_average_processing_time(self, days: int = 7) -> float:
        """Получает среднее время обработки сообщений за последние дни."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        stmt = (
            select(func.avg(Message.processing_time))
            .where(
                and_(
                    Message.timestamp >= cutoff_date,
                    Message.processing_time.is_not(None)
                )
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar() or 0.0
    
    async def search_messages(self, query: str, limit: int = 50) -> List[Message]:
        """Поиск сообщений по содержимому."""
        stmt = (
            select(Message)
            .where(
                Message.user_message.ilike(f"%{query}%") |
                Message.bot_response.ilike(f"%{query}%")
            )
            .order_by(desc(Message.timestamp))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def delete_old_messages(self, days: int = 365) -> int:
        """Удаляет старые сообщения."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        stmt = select(Message).where(Message.timestamp < cutoff_date)
        result = await self._session.execute(stmt)
        messages_to_delete = result.scalars().all()
        
        count = len(messages_to_delete)
        
        for message in messages_to_delete:
            await self._session.delete(message)
        
        await self._session.commit()
        return count
