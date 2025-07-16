import logging
from aiogram import Router, types
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent

from app.services.notification_service import NotificationService
from app.monitoring.metrics import REQUEST_COUNT

router = Router()
logger = logging.getLogger(__name__)


@router.error()
async def error_handler(event: ErrorEvent) -> None:
    """Глобальный обработчик ошибок."""
    logger.error(f"Update {event.update.update_id} caused error: {event.exception}")
    
    # Увеличиваем счетчик ошибок
    REQUEST_COUNT.labels("error").inc()
    
    # Получаем информацию о пользователе
    user_info = None
    if hasattr(event.update, 'message') and event.update.message:
        user_info = event.update.message.from_user
    elif hasattr(event.update, 'callback_query') and event.update.callback_query:
        user_info = event.update.callback_query.from_user
    
    # Отправляем уведомление администраторам
    try:
        notification_service = NotificationService()
        await notification_service.notify_admins_about_error(
            error=str(event.exception),
            user_id=user_info.id if user_info else None,
            update_id=event.update.update_id
        )
    except Exception as e:
        logger.error(f"Failed to send error notification: {e}")
    
    # Отправляем сообщение пользователю
    try:
        if hasattr(event.update, 'message') and event.update.message:
            await event.update.message.answer(
                "❌ Произошла техническая ошибка. Мы уже работаем над её устранением.\n"
                "Попробуйте повторить запрос позже или обратитесь в службу поддержки."
            )
        elif hasattr(event.update, 'callback_query') and event.update.callback_query:
            await event.update.callback_query.message.answer(
                "❌ Произошла техническая ошибка. Мы уже работаем над её устранением.\n"
                "Попробуйте повторить запрос позже или обратитесь в службу поддержки."
            )
    except Exception as e:
        logger.error(f"Failed to send error message to user: {e}")


@router.error(ExceptionTypeFilter(ValueError))
async def value_error_handler(event: ErrorEvent) -> None:
    """Обработчик ошибок валидации."""
    logger.warning(f"Validation error: {event.exception}")
    REQUEST_COUNT.labels("validation_error").inc()
    
    try:
        if hasattr(event.update, 'message') and event.update.message:
            await event.update.message.answer(
                "❌ Некорректные данные. Пожалуйста, проверьте введенную информацию."
            )
        elif hasattr(event.update, 'callback_query') and event.update.callback_query:
            await event.update.callback_query.answer(
                "❌ Некорректные данные", show_alert=True
            )
    except Exception as e:
        logger.error(f"Failed to handle validation error: {e}")


@router.error(ExceptionTypeFilter(PermissionError))
async def permission_error_handler(event: ErrorEvent) -> None:
    """Обработчик ошибок доступа."""
    logger.warning(f"Permission error: {event.exception}")
    REQUEST_COUNT.labels("permission_error").inc()
    
    try:
        if hasattr(event.update, 'message') and event.update.message:
            await event.update.message.answer(
                "❌ У вас нет прав для выполнения этого действия.\n"
                "Обратитесь к администратору для получения доступа."
            )
        elif hasattr(event.update, 'callback_query') and event.update.callback_query:
            await event.update.callback_query.answer(
                "❌ Недостаточно прав", show_alert=True
            )
    except Exception as e:
        logger.error(f"Failed to handle permission error: {e}")


@router.error(ExceptionTypeFilter(TimeoutError))
async def timeout_error_handler(event: ErrorEvent) -> None:
    """Обработчик ошибок таймаута."""
    logger.warning(f"Timeout error: {event.exception}")
    REQUEST_COUNT.labels("timeout_error").inc()
    
    try:
        if hasattr(event.update, 'message') and event.update.message:
            await event.update.message.answer(
                "⏱️ Время ожидания истекло. Сервис временно перегружен.\n"
                "Попробуйте повторить запрос через несколько минут."
            )
        elif hasattr(event.update, 'callback_query') and event.update.callback_query:
            await event.update.callback_query.answer(
                "⏱️ Время ожидания истекло", show_alert=True
            )
    except Exception as e:
        logger.error(f"Failed to handle timeout error: {e}")
