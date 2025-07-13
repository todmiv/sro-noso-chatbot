from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session


class SessionRepository:
    """Репозиторий для работы с сессиями."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def save(self, session_obj: Session) -> Session:
        """Сохраняет сессию."""
        self._session.add(session_obj)
        await self._session.commit()
        await self._session.refresh(session_obj)
        return session_obj
    
    async def get_by_id(self, session_id: int) -> Optional[Session]:
        """Получает сессию по ID."""
        stmt = select(Session).where(Session.id == session_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_session_id(self, session_id: str) -> Optional[Session]:
        """Получает сессию по session_id."""
        stmt = select(Session).where(Session.session_id == session_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_active_session(self, user_id: int) -> Optional[Session]:
        """Получает активную сессию пользователя."""
        stmt = (
            select(Session)
            .where(
                and_(
                    Session.user_id == user_id,
                    Session.is_active == True
                )
            )
            .order_by(desc(Session.last_activity))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_user_sessions(self, user_id: int, limit: int = 10) -> List[Session]:
        """Получает сессии пользователя."""
        stmt = (
            select(Session)
            .where(Session.user_id == user_id)
            .order_by(desc(Session.created_at))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def close_active_session(self, user_id: int) -> bool:
        """Закрывает активную сессию пользователя."""
        session_obj = await self.get_active_session(user_id)
        if session_obj:
            session_obj.close()
            await self._session.commit()
            return True
        return False
    
    async def close_session_by_id(self, session_id: str) -> bool:
        """Закрывает сессию по session_id."""
        session_obj = await self.get_by_session_id(session_id)
        if session_obj:
            session_obj.close()
            await self._session.commit()
            return True
        return False
    
    async def update_last_activity(self, session_id: str) -> bool:
        """Обновляет время последней активности."""
        session_obj = await self.get_by_session_id(session_id)
        if session_obj:
            session_obj.last_activity = datetime.utcnow()
            await self._session.commit()
            return True
        return False
    
    async def count_active_sessions(self) -> int:
        """Подсчитывает количество активных сессий."""
        stmt = select(func.count(Session.id)).where(Session.is_active == True)
        result = await self._session.execute(stmt)
        return result.scalar() or 0
    
    async def count_user_sessions(self, user_id: int) -> int:
        """Подсчитывает количество сессий пользователя."""
        stmt = select(func.count(Session.id)).where(Session.user_id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar() or 0
    
    async def get_last_activity(self, user_id: int) -> Optional[datetime]:
        """Получает время последней активности пользователя."""
        stmt = (
            select(func.max(Session.last_activity))
            .where(Session.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        return result.scalar()
    
    async def get_sessions_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime,
        limit: int = 100
    ) -> List[Session]:
        """Получает сессии за период."""
        stmt = (
            select(Session)
            .where(
                and_(
                    Session.created_at >= start_date,
                    Session.created_at <= end_date
                )
            )
            .order_by(desc(Session.created_at))
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def cleanup_expired_sessions(self, cutoff_time: datetime) -> int:
        """Очищает истекшие сессии."""
        stmt = (
            select(Session)
            .where(
                and_(
                    Session.is_active == True,
                    Session.last_activity < cutoff_time
                )
            )
        )
        result = await self._session.execute(stmt)
        sessions_to_close = result.scalars().all()
        
        count = 0
        for session_obj in sessions_to_close:
            session_obj.close()
            count += 1
        
        await self._session.commit()
        return count
    
    async def get_average_session_duration(self, days: int = 7) -> float:
        """Получает среднюю продолжительность сессий за последние дни."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        stmt = (
            select(Session)
            .where(
                and_(
                    Session.created_at >= cutoff_date,
                    Session.session_end.is_not(None)
                )
            )
        )
        result = await self._session.execute(stmt)
        sessions = result.scalars().all()
        
        if not sessions:
            return 0.0
        
        total_duration = sum(session.duration or 0 for session in sessions)
        return total_duration / len(sessions)
