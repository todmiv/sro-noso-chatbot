"""
Основной модуль приложения SRO NOSO Chat-Bot.

Этот модуль отвечает за:
- Инициализацию всех компонентов системы
- Запуск и остановку сервера
- Обработку сигналов graceful shutdown
- Настройку маршрутов API
- Интеграцию с Telegram Bot API

Архитектура:
- FastAPI для HTTP API и health checks
- Aiogram 3 для Telegram бота
- Асинхронная обработка всех операций
- Graceful shutdown с сохранением состояния
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from fastapi import APIRouter, status
from sqlalchemy.ext.asyncio import AsyncSession
from aioredis import Redis

# Добавляем путь к проекту для корректного импорта модулей
sys.path.append(str(Path(__file__).parent.parent))

from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler
from aiohttp import web

from config.settings import config
from app.bot.bot_instance import create_bot, create_dispatcher
from app.bot.handlers import register_handlers
from app.bot.middleware import register_middleware
from app.database.connection import (
    init_database,
    init_redis,
    close_database,
    close_redis,
    get_redis
)
from app.utils.logging_config import setup_logging
from app.monitoring.metrics import setup_metrics, SERVICE_HEALTH

# Health check router
health_router = APIRouter()

@health_router.get("/health")
async def health_check():
    """Endpoint для проверки состояния сервиса."""
    db_status = await check_db_connection()
    redis_status = await check_redis_connection()
    
    # Обновляем метрики
    SERVICE_HEALTH.labels(service="database").set(1 if db_status else 0)
    SERVICE_HEALTH.labels(service="redis").set(1 if redis_status else 0)
    
    return {
        "status": "OK", 
        "services": {
            "database": db_status,
            "redis": redis_status
        }
    }

async def check_db_connection() -> bool:
    """Проверка подключения к базе данных."""
    try:
        async with AsyncSession() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logging.error(f"Database connection error: {e}")
        return False

async def check_redis_connection() -> bool:
    """Проверка подключения к Redis."""
    try:
        redis: Redis = await get_redis()
        return await redis.ping()
    except Exception as e:
        logging.error(f"Redis connection error: {e}")
        return False

logger = logging.getLogger(__name__)

# Глобальные переменные для graceful shutdown
shutdown_event = asyncio.Event()


bot = create_bot()
dispatcher = create_dispatcher()
register_middleware(dispatcher)
register_handlers(dispatcher)

from aiogram import types

@dispatcher.message(Command("test_callback"))
async def cmd_test_callback(message: types.Message):
    """Test command to generate callback test button."""
    kb = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="Test", callback_data="test_callback")]]
    )
    await message.answer("Test callback button:", reply_markup=kb)



def signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown."""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    shutdown_event.set()


async def startup_sequence():
    """Последовательность инициализации приложения."""
    global bot, dispatcher
    
    logger.info("Starting SRO NOSO Chat-Bot...")
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Running in {'production' if config.is_production else 'development'} mode")
    
    # 1. Настройка логирования
    setup_logging()
    logger.debug("Logging configured")
    
    # 2. Инициализация Redis
    logger.debug("Initializing Redis connection...")
    await init_redis()
    logger.info("Redis connection established")
    
    # 3. Инициализация базы данных
    logger.debug("Initializing database connection...")
    await init_database()
    logger.info("Database connection established")
    
    # 4. Создание бота и диспетчера
    # bot и dispatcher уже созданы глобально и роутеры зарегистрированы
    logger.debug(f"Bot token: {config.bot.token[:5]}...")
    logger.debug(f"Registered handlers: {len(dispatcher.sub_routers)}")
    
    # 5. Инициализация AI сервисов
    from app.services.global_services import services
    logger.info("Initializing AI services...")
    _ = services.rag_system  # Инициализация RAG системы
    logger.debug(f"AI services: {services.__dict__.keys()}")
    logger.info("AI services initialized")
    
    # 6. Настройка мониторинга
    setup_metrics()
    logger.debug("Metrics system initialized")
    
    logger.info("Startup sequence completed successfully")


async def shutdown_sequence():
    """Последовательность завершения работы приложения."""
    logger.info("Starting shutdown sequence...")
    
    try:
        # 1. Останавливаем polling (если активен)
        if dispatcher and dispatcher.workflow_data.get("polling_task"):
            polling_task = dispatcher.workflow_data["polling_task"]
            polling_task.cancel()
            try:
                await polling_task
            except asyncio.CancelledError:
                pass
        
        # 2. Закрываем бота
        if bot:
            await bot.session.close()
            logger.info("Bot session closed")
        
        # 3. Закрываем базу данных
        await close_database()
        
        # 4. Закрываем Redis
        await close_redis()
        
        logger.info("Shutdown sequence completed")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


async def start_polling():
    """Запуск бота в режиме polling для разработки."""
    
    try:
        await startup_sequence()
        
        logger.info("Starting bot in polling mode...")
        
        # Удаление webhook если установлен
        await bot.delete_webhook(drop_pending_updates=True)

        
        # Запуск polling в задаче для возможности отмены
        polling_task = asyncio.create_task(
            dispatcher.start_polling(bot, allowed_updates=None)
        )
        
        # Сохраняем задачу для graceful shutdown
        dispatcher.workflow_data["polling_task"] = polling_task
        
        # Ожидаем сигнал завершения или завершение polling
        done, pending = await asyncio.wait(
            [polling_task, asyncio.create_task(shutdown_event.wait())],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Отменяем незавершенные задачи
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
    except Exception as e:
        logger.error("Error in polling mode", exc_info=e)
        raise
    finally:
        await shutdown_sequence()


async def create_app() -> web.Application:
    """Создает и настраивает веб-приложение для продакшена."""
    
    await startup_sequence()
    
    # Создание веб-приложения
    app = web.Application()
    
    # Настройка webhook если в продакшене
    if config.bot.webhook_url:
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dispatcher,
            bot=bot
        )
        webhook_requests_handler.register(app, path="/webhook")
        
        # Установка webhook
        await bot.set_webhook(config.bot.webhook_url + "/webhook")
        logger.info(f"Webhook set to {config.bot.webhook_url}/webhook")
    
    # Добавление роутов для мониторинга
    # setup_health_check(app)                                                   - временно отключено
    
    # Сохранение объектов в контексте приложения
    app['bot'] = bot
    app['dispatcher'] = dispatcher
    
    # Обработчик shutdown для веб-приложения
    async def cleanup_app(app):
        await shutdown_sequence()
    
    app.on_cleanup.append(cleanup_app)
    
    return app


def main():
    """Точка входа в приложение."""
    
    # Настройка обработчика сигналов для graceful shutdown
    if sys.platform != "win32":
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        if config.is_production:
            # В продакшене запускаем веб-сервер
            logger.info("Starting in production mode")
            app = asyncio.run(create_app())
            web.run_app(app, host='0.0.0.0', port=8000)
        else:
            # В разработке запускаем polling
            logger.info("Starting in development mode")
            asyncio.run(start_polling())
    
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
