import time
from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from app.monitoring.metrics import REQUEST_COUNT, RESPONSE_TIME


class MetricsMiddleware(BaseMiddleware):
    """Middleware для сбора метрик."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        start_time = time.time()
        
        # Определяем тип события
        event_type = self._get_event_type(event)
        
        # Увеличиваем счетчик запросов
        REQUEST_COUNT.labels(
            event_type=event_type,
            status="processing"
        ).inc()
        
        try:
            # Выполняем обработчик
            result = await handler(event, data)
            
            # Успешная обработка
            REQUEST_COUNT.labels(
                event_type=event_type,
                status="success"
            ).inc()
            
            return result
            
        except Exception as e:
            # Ошибка при обработке
            REQUEST_COUNT.labels(
                event_type=event_type,
                status="error"
            ).inc()
            
            raise e
            
        finally:
            # Записываем время обработки
            processing_time = time.time() - start_time
            status = "error" if 'e' in locals() else "success"
            RESPONSE_TIME.labels(
                event_type=event_type,
                status=status
            ).observe(processing_time)
    
    def _get_event_type(self, event: TelegramObject) -> str:
        """Определяет тип события."""
        if isinstance(event, Message):
            if event.text and event.text.startswith('/'):
                return "command"
            elif event.text:
                return "message"
            elif event.document:
                return "document"
            elif event.photo:
                return "photo"
            else:
                return "other_message"
        elif isinstance(event, CallbackQuery):
            return "callback_query"
        else:
            return "unknown"
