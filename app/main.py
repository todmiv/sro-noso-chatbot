import asyncio
import logging
import signal
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config.settings import config
from app.bot.bot_instance import create_bot, create_dispatcher
from app.database.connection import (
    init_database, 
    init_redis, 
    close_database, 
    close_redis
)
from app.utils.logging_config import setup_logging
from app.monitoring.health_check import setup_health_check
from app.monitoring.metrics import setup_metrics

logger = logging.getLogger(__name__)

# Глобальные переменные для graceful shutdown
shutdown_event = asyncio.Event()
bot: Bot = None
dispatcher: Dispatcher = None


def signal_handler(signum, frame):
    """Обработчик сигналов для graceful shutdown."""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    shutdown_event.set()


async def startup_sequence():
    """Последовательность инициализации приложения."""
    global bot, dispatcher
    
    logger.info("Starting SRO NOSO Chat-Bot...")
    
    # 1. Настройка логирования
    setup_logging()
    
    # 2. Инициализация Redis
    await init_redis()
    
    # 3. Инициализация базы данных
    await init_database()
    
    # 4. Создание бота и диспетчера
    bot = create_bot()
    dispatcher = create_dispatcher()
    
    # 5. Настройка мониторинга
    setup_metrics()
    
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
        logger.error(f"Error in polling mode: {e}")
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
