from typing import Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.error_log import ErrorLog
from app.database.connection import get_async_session


class ErrorRepository:
    """Репозиторий для работы с логами ошибок."""
    
    def __init__(self, session: AsyncSession = None):
        self._session = session
        self._own_session = session is None

    async def _get_session(self) -> AsyncSession:
        if self._session is None or self._session.closed:
            self._session = get_async_session()
            self._own_session = True
        return self._session

    async def create_error_log(
        self,
        error_type: str,
        error_message: str,
        traceback: Optional[str] = None,
        user_id: Optional[int] = None,
        update_id: Optional[int] = None,
        context: Optional[dict] = None
    ) -> ErrorLog:
        """Создает запись об ошибке в базе данных."""
        session = await self._get_session()
        try:
            error_log = ErrorLog(
                error_type=error_type,
                error_message=error_message,
                traceback=traceback,
                user_id=user_id,
                update_id=update_id,
                context=context
            )
            session.add(error_log)
            await session.commit()
            await session.refresh(error_log)
            return error_log
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            if self._own_session:
                await session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._own_session and self._session:
            await self._session.close()

    async def get_error_logs(
        self,
        limit: int = 100,
        error_type: Optional[str] = None,
        user_id: Optional[int] = None
    ) -> list[ErrorLog]:
        """Возвращает список ошибок с возможностью фильтрации."""
        from sqlalchemy import select
        from sqlalchemy.sql import desc
        
        stmt = select(ErrorLog)
        
        if error_type:
            stmt = stmt.where(ErrorLog.error_type == error_type)
        if user_id:
            stmt = stmt.where(ErrorLog.user_id == user_id)
            
        stmt = stmt.order_by(desc(ErrorLog.created_at)).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()
