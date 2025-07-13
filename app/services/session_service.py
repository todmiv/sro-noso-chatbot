from typing import List, Dict, Optional
import json
import redis
from datetime import datetime, timedelta

from config.settings import config
from app.database.connection import get_async_session
from app.database.repositories.message_repository import MessageRepository
from app.database.repositories.session_repository import SessionRepository
from app.models.message import Message
from app.models.session import Session


class SessionService:
    """Сервис для управления сессиями пользователей."""
    
    def __init__(self):
        self.redis_client = redis.from_url(config.redis.url)
        self.session_ttl = 3600  # 1 час
        self.conversation_history_limit = 10
    
    async def get_or_create_session(self, user_id: int) -> Dict:
        """Получает или создает сессию для пользователя."""
        session_key = f"session:{user_id}"
        
        # Проверяем существующую сессию в Redis
        session_data = self.redis_client.get(session_key)
        
        if session_data:
            session = json.loads(session_data)
            # Обновляем время последней активности
            session["last_activity"] = datetime.now().isoformat()
            await self._save_session_to_redis(user_id, session)
            return session
        
        # Создаем новую сессию
        session = {
            "user_id": user_id,
            "session_id": f"session_{user_id}_{int(datetime.now().timestamp())}",
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "context": {},
            "conversation_history": []
        }
        
        # Сохраняем в Redis и базе данных
        await self._save_session_to_redis(user_id, session)
        await self._save_session_to_db(session)
        
        return session
    
    async def _save_session_to_redis(self, user_id: int, session: Dict) -> None:
        """Сохраняет сессию в Redis."""
        session_key = f"session:{user_id}"
        self.redis_client.setex(
            session_key,
            self.session_ttl,
            json.dumps(session, default=str)
        )
    
    async def _save_session_to_db(self, session: Dict) -> None:
        """Сохраняет сессию в базе данных."""
        async with get_async_session() as db_session:
            session_repo = SessionRepository(db_session)
            
            db_session_obj = Session(
                user_id=session["user_id"],
                session_id=session["session_id"],
                created_at=datetime.fromisoformat(session["created_at"]),
                last_activity=datetime.fromisoformat(session["last_activity"]),
                context=session.get("context", {}),
                is_active=True
            )
            
            await session_repo.save(db_session_obj)
    
    async def update_session_context(self, user_id: int, context_key: str, context_value: any) -> None:
        """Обновляет контекст сессии."""
        session = await self.get_or_create_session(user_id)
        session["context"][context_key] = context_value
        session["last_activity"] = datetime.now().isoformat()
        
        await self._save_session_to_redis(user_id, session)
    
    async def get_session_context(self, user_id: int, context_key: str) -> any:
        """Получает значение из контекста сессии."""
        session = await self.get_or_create_session(user_id)
        return session.get("context", {}).get(context_key)
    
    async def save_interaction(
        self,
        user_id: int,
        user_message: str,
        bot_response: str,
        context_used: Optional[str] = None
    ) -> None:
        """Сохраняет взаимодействие пользователя с ботом."""
        # Сохраняем в базе данных
        async with get_async_session() as db_session:
            message_repo = MessageRepository(db_session)
            session_repo = SessionRepository(db_session)
            
            # Получаем или создаем сессию в БД
            db_session_obj = await session_repo.get_active_session(user_id)
            if not db_session_obj:
                session_data = await self.get_or_create_session(user_id)
                db_session_obj = Session(
                    user_id=user_id,
                    session_id=session_data["session_id"],
                    created_at=datetime.fromisoformat(session_data["created_at"]),
                    last_activity=datetime.now(),
                    context=session_data.get("context", {}),
                    is_active=True
                )
                await session_repo.save(db_session_obj)
            
            # Сохраняем сообщение
            message = Message(
                session_id=db_session_obj.id,
                user_message=user_message,
                bot_response=bot_response,
                context_used=context_used,
                timestamp=datetime.now()
            )
            
            await message_repo.save(message)
        
        # Обновляем историю в Redis
        session = await self.get_or_create_session(user_id)
        
        interaction = {
            "user_message": user_message,
            "bot_response": bot_response,
            "timestamp": datetime.now().isoformat(),
            "context_used": context_used
        }
        
        session["conversation_history"].append(interaction)
        
        # Ограничиваем размер истории
        if len(session["conversation_history"]) > self.conversation_history_limit:
            session["conversation_history"] = session["conversation_history"][-self.conversation_history_limit:]
        
        session["last_activity"] = datetime.now().isoformat()
        await self._save_session_to_redis(user_id, session)
    
    async def get_conversation_history(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Получает историю диалога пользователя."""
        session = await self.get_or_create_session(user_id)
        history = session.get("conversation_history", [])
        
        # Возвращаем последние N сообщений
        return history[-limit:] if history else []
    
    async def clear_conversation_history(self, user_id: int) -> None:
        """Очищает историю диалога."""
        session = await self.get_or_create_session(user_id)
        session["conversation_history"] = []
        session["last_activity"] = datetime.now().isoformat()
        
        await self._save_session_to_redis(user_id, session)
    
    async def close_session(self, user_id: int) -> None:
        """Закрывает активную сессию пользователя."""
        # Удаляем из Redis
        session_key = f"session:{user_id}"
        self.redis_client.delete(session_key)
        
        # Обновляем статус в базе данных
        async with get_async_session() as db_session:
            session_repo = SessionRepository(db_session)
            await session_repo.close_active_session(user_id)
    
    async def get_active_sessions_count(self) -> int:
        """Получает количество активных сессий."""
        pattern = "session:*"
        keys = self.redis_client.keys(pattern)
        return len(keys)
    
    async def cleanup_expired_sessions(self) -> int:
        """Очищает истекшие сессии из базы данных."""
        cutoff_time = datetime.now() - timedelta(hours=24)
        
        async with get_async_session() as db_session:
            session_repo = SessionRepository(db_session)
            return await session_repo.cleanup_expired_sessions(cutoff_time)
    
    async def get_user_activity_stats(self, user_id: int) -> Dict:
        """Получает статистику активности пользователя."""
        async with get_async_session() as db_session:
            message_repo = MessageRepository(db_session)
            session_repo = SessionRepository(db_session)
            
            total_messages = await message_repo.count_user_messages(user_id)
            total_sessions = await session_repo.count_user_sessions(user_id)
            last_activity = await session_repo.get_last_activity(user_id)
            
            return {
                "total_messages": total_messages,
                "total_sessions": total_sessions,
                "last_activity": last_activity.isoformat() if last_activity else None
            }
