import time
from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
import redis

from config.settings import config

# Подключение к Redis для хранения лимитов
redis_client = redis.from_url(config.redis.url)


class RateLimitMiddleware(BaseMiddleware):
    """Middleware для ограничения количества запросов."""
    
    def __init__(self, rate_limit: int = 60, window: int = 60):
        """
        Args:
            rate_limit: Максимальное количество запросов в окне
            window: Размер окна в секундах
        """
        self.rate_limit = rate_limit
        self.window = window
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user_id = None
        
        # Определяем ID пользователя
        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
        
        if user_id is None:
            return await handler(event, data)
        
        # Проверяем лимит
        if await self._is_rate_limited(user_id):
            await self._handle_rate_limit(event)
            return
        
        # Увеличиваем счетчик
        await self._increment_counter(user_id)
        
        return await handler(event, data)
    
    async def _is_rate_limited(self, user_id: int) -> bool:
        """Проверяет, превышен ли лимит для пользователя."""
        try:
            key = f"rate_limit:{user_id}"
            current_time = int(time.time())
            window_start = current_time - self.window
            
            # Удаляем старые записи
            redis_client.zremrangebyscore(key, 0, window_start)
            
            # Считаем текущие запросы
            current_count = redis_client.zcard(key)
            
            return current_count >= self.rate_limit
            
        except Exception:
            # При ошибке Redis пропускаем запрос
            return False
    
    async def _increment_counter(self, user_id: int) -> None:
        """Увеличивает счетчик запросов."""
        try:
            key = f"rate_limit:{user_id}"
            current_time = int(time.time())
            
            # Добавляем текущий запрос
            redis_client.zadd(key, {str(current_time): current_time})
            
            # Устанавливаем TTL для автоматической очистки
            redis_client.expire(key, self.window * 2)
            
        except Exception:
            # При ошибке Redis игнорируем
            pass
    
    async def _handle_rate_limit(self, event: TelegramObject) -> None:
        """Обрабатывает превышение лимита."""
        message = (
            f"🚫 Превышен лимит запросов ({self.rate_limit} запросов в {self.window} секунд).\n"
            f"Пожалуйста, подождите немного перед следующим запросом."
        )
        
        try:
            if isinstance(event, Message):
                await event.answer(message)
            elif isinstance(event, CallbackQuery):
                await event.answer(message, show_alert=True)
        except Exception:
            # Если не удается отправить сообщение, просто игнорируем
            pass
