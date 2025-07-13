"""Middleware для обработки запросов."""
from aiogram import Dispatcher

from .auth_middleware import AuthMiddleware
from .logging_middleware import LoggingMiddleware
from .rate_limit_middleware import RateLimitMiddleware
from .metrics_middleware import MetricsMiddleware

from app.services.auth_service import AuthService
from app.services.user_service import UserService


def register_middleware(dp: Dispatcher) -> None:
    """Регистрирует все middleware в правильном порядке."""
    
    # Сначала метрики (для учета всех запросов)
    dp.message.middleware(MetricsMiddleware())
    dp.callback_query.middleware(MetricsMiddleware())
    
    # Затем логирование
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    
    # Ограничение скорости
    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())
    
    # Аутентификация (последняя, так как может использовать данные из других middleware)
    user_service = UserService()
    auth_service = AuthService(user_service)
    dp.message.middleware(AuthMiddleware(auth_service))
    dp.callback_query.middleware(AuthMiddleware(auth_service))
