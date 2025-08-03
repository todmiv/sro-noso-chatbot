import logging
import traceback
from aiogram import Router
from sqlalchemy.exc import DatabaseError
from requests.exceptions import RequestException
from aiogram.filters import ExceptionTypeFilter
from aiogram.types import ErrorEvent

from app.services.notification_service import NotificationService
from app.monitoring.metrics import REQUEST_COUNT
from app.database.repositories.error_repository import ErrorRepository

router = Router()
logger = logging.getLogger(__name__)


@router.error()
async def error_handler(event: ErrorEvent) -> None:
    """Глобальный обработчик ошибок."""
    # Получаем информацию о пользователе
    user_info = None
    if hasattr(event.update, 'message') and event.update.message:
        user_info = event.update.message.from_user
    elif hasattr(event.update, 'callback_query') and event.update.callback_query:
        user_info = event.update.callback_query.from_user

    error_traceback = ''.join(traceback.format_tb(event.exception.__traceback__))
    logger.error(
        f"Update {event.update.update_id} caused error: {event.exception}\n"
        f"Full traceback:\n{error_traceback}",
        exc_info=True
    )
    
    # Сохраняем ошибку в базу данных
    try:
        error_repo = ErrorRepository()
        await error_repo.create_error_log(
            error_type=event.exception.__class__.__name__,
            error_message=str(event.exception),
            traceback=error_traceback,
            user_id=user_info.id if user_info else None,
            update_id=event.update.update_id,
            context={
                'handler': 'error_handler',
                'update': event.update.to_python() if hasattr(event.update, 'to_python') else str(event.update)
            }
        )
    except Exception as e:
        logger.error(f"Failed to save error to database: {e}")
    
    # Увеличиваем счетчик ошибок
    REQUEST_COUNT.labels(event_type="error", status="error").inc()
    
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
    error_traceback = ''.join(traceback.format_tb(event.exception.__traceback__))
    logger.warning(f"Validation error: {event.exception}\nFull traceback:\n{error_traceback}")
    
    try:
        error_repo = ErrorRepository()
        await error_repo.create_error_log(
            error_type=event.exception.__class__.__name__,
            error_message=str(event.exception),
            traceback=error_traceback,
            user_id=event.update.message.from_user.id if hasattr(event.update, 'message') else None,
            update_id=event.update.update_id,
            context={'handler': 'value_error_handler'}
        )
    except Exception as e:
        logger.error(f"Failed to save validation error to database: {e}")
    REQUEST_COUNT.labels(event_type="validation", status="error").inc()
    
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
    error_traceback = ''.join(traceback.format_tb(event.exception.__traceback__))
    logger.warning(f"Permission error: {event.exception}\nFull traceback:\n{error_traceback}")
    
    try:
        error_repo = ErrorRepository()
        await error_repo.create_error_log(
            error_type=event.exception.__class__.__name__,
            error_message=str(event.exception),
            traceback=error_traceback,
            user_id=event.update.message.from_user.id if hasattr(event.update, 'message') else None,
            update_id=event.update.update_id,
            context={'handler': 'permission_error_handler'}
        )
    except Exception as e:
        logger.error(f"Failed to save permission error to database: {e}")
    REQUEST_COUNT.labels(event_type="permission", status="error").inc()
    
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
    error_traceback = ''.join(traceback.format_tb(event.exception.__traceback__))
    logger.warning(f"Timeout error: {event.exception}\nFull traceback:\n{error_traceback}")
    
    try:
        error_repo = ErrorRepository()
        await error_repo.create_error_log(
            error_type=event.exception.__class__.__name__,
            error_message=str(event.exception),
            traceback=error_traceback,
            user_id=event.update.message.from_user.id if hasattr(event.update, 'message') else None,
            update_id=event.update.update_id,
            context={'handler': 'timeout_error_handler'}
        )
    except Exception as e:
        logger.error(f"Failed to save timeout error to database: {e}")
    REQUEST_COUNT.labels(event_type="timeout", status="error").inc()
    
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


@router.error(ExceptionTypeFilter(ConnectionError))
async def connection_error_handler(event: ErrorEvent) -> None:
    """Обработчик ошибок соединения."""
    error_traceback = ''.join(traceback.format_tb(event.exception.__traceback__))
    logger.error(
        f"Connection error: {event.exception}\n"
        f"Full traceback:\n{error_traceback}",
        exc_info=True
    )
    
    try:
        error_repo = ErrorRepository()
        await error_repo.create_error_log(
            error_type=event.exception.__class__.__name__,
            error_message=str(event.exception),
            traceback=error_traceback,
            user_id=event.update.message.from_user.id if hasattr(event.update, 'message') else None,
            update_id=event.update.update_id,
            context={'handler': 'connection_error_handler'}
        )
    except Exception as e:
        logger.error(f"Failed to save connection error to database: {e}")
    REQUEST_COUNT.labels(event_type="connection", status="error").inc()
    
    try:
        if hasattr(event.update, 'message') and event.update.message:
            await event.update.message.answer(
                "🔌 Ошибка соединения. Пожалуйста, проверьте интернет-соединение.\n"
                "Попробуйте повторить запрос через несколько минут."
            )
        elif hasattr(event.update, 'callback_query') and event.update.callback_query:
            await event.update.callback_query.answer(
                "🔌 Ошибка соединения", show_alert=True
            )
    except Exception as e:
        logger.error(f"Failed to handle connection error: {e}")


@router.error(ExceptionTypeFilter(DatabaseError))
async def database_error_handler(event: ErrorEvent) -> None:
    """Обработчик ошибок базы данных."""
    error_traceback = ''.join(traceback.format_tb(event.exception.__traceback__))
    logger.critical(
        f"Database error: {event.exception}\n"
        f"Full traceback:\n{error_traceback}",
        exc_info=True
    )
    
    try:
        error_repo = ErrorRepository()
        await error_repo.create_error_log(
            error_type=event.exception.__class__.__name__,
            error_message=str(event.exception),
            traceback=error_traceback,
            user_id=event.update.message.from_user.id if hasattr(event.update, 'message') else None,
            update_id=event.update.update_id,
            context={'handler': 'database_error_handler'}
        )
    except Exception as e:
        logger.error(f"Failed to save database error to database: {e}")
    REQUEST_COUNT.labels(event_type="database", status="error").inc()
    
    try:
        if hasattr(event.update, 'message') and event.update.message:
            await event.update.message.answer(
                "🛑 Критическая ошибка базы данных. Мы уже работаем над её устранением.\n"
                "Попробуйте повторить запрос позже."
            )
        elif hasattr(event.update, 'callback_query') and event.update.callback_query:
            await event.update.callback_query.answer(
                "🛑 Ошибка базы данных", show_alert=True
            )
    except Exception as e:
        logger.error(f"Failed to handle database error: {e}")


@router.error(ExceptionTypeFilter(RequestException))
async def request_exception_handler(event: ErrorEvent) -> None:
    """Обработчик ошибок HTTP запросов."""
    error_traceback = ''.join(traceback.format_tb(event.exception.__traceback__))
    logger.error(
        f"HTTP request error: {event.exception}\n"
        f"Full traceback:\n{error_traceback}",
        exc_info=True
    )
    
    try:
        error_repo = ErrorRepository()
        await error_repo.create_error_log(
            error_type=event.exception.__class__.__name__,
            error_message=str(event.exception),
            traceback=error_traceback,
            user_id=event.update.message.from_user.id if hasattr(event.update, 'message') else None,
            update_id=event.update.update_id,
            context={'handler': 'request_exception_handler'}
        )
    except Exception as e:
        logger.error(f"Failed to save HTTP request error to database: {e}")
    REQUEST_COUNT.labels(event_type="http_request", status="error").inc()
    
    try:
        if hasattr(event.update, 'message') and event.update.message:
            await event.update.message.answer(
                "🌐 Ошибка при выполнении запроса. Сервис временно недоступен.\n"
                "Попробуйте повторить запрос через несколько минут."
            )
        elif hasattr(event.update, 'callback_query') and event.update.callback_query:
            await event.update.callback_query.answer(
                "🌐 Ошибка запроса", show_alert=True
            )
    except Exception as e:
        logger.error(f"Failed to handle HTTP request error: {e}")
