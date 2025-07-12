import asyncio
import logging
import sys
from pathlib import Path

# Добавляем путь к проекту
sys.path.append(str(Path(__file__).parent.parent))

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config.settings import config
from app.bot.bot_instance import create_bot, create_dispatcher
from app.database.connection import init_database
from app.utils.logging_config import setup_logging
from app.monitoring.health_check import health_check_handler
from app.monitoring.metrics import setup_metrics

async def create_app() -> web.Application:
    """Создает и настраивает веб-приложение"""
    
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)
    
    # Инициализация базы данных
    await init_database()
    
    # Создание бота и диспетчера
    bot = create_bot()
    dp = create_dispatcher()
    
    # Создание веб-приложения
    app = web.Application()
    
    # Настройка webhook если в продакшене
    if config.is_production and config.bot.webhook_url:
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot
        )
        webhook_requests_handler.register(app, path="/webhook")
        
        # Установка webhook
        await bot.set_webhook(config.bot.webhook_url + "/webhook")
        logger.info(f"Webhook set to {config.bot.webhook_url}/webhook")
    
    # Добавление роутов для мониторинга
    app.router.add_get('/health', health_check_handler)
    
    # Настройка метрик
    setup_metrics(app)
    
    # Сохранение объектов в контексте приложения
    app['bot'] = bot
    app['dp'] = dp
    
    return app

async def start_polling():
    """Запуск бота в режиме polling для разработки"""
    logger = logging.getLogger(__name__)
    
    try:
        # Настройка логирования
        setup_logging()
        
        # Инициализация базы данных
        await init_database()
        
        # Создание бота и диспетчера
        bot = create_bot()
        dp = create_dispatcher()
        
        logger.info("Starting bot in polling mode...")
        
        # Удаление webhook если установлен
        await bot.delete_webhook()
        
        # Запуск polling
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise
    finally:
        await bot.session.close()

def main():
    """Точка входа в приложение"""
    
    if config.is_production:
        # В продакшене запускаем веб-сервер
        app = asyncio.run(create_app())
        web.run_app(app, host='0.0.0.0', port=8000)
    else:
        # В разработке запускаем polling
        asyncio.run(start_polling())

if __name__ == "__main__":
    main()
