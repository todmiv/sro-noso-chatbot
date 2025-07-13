"""Инициализация Telegram-бота (aiogram 3.x)."""

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from config.settings import config
from app.bot.handlers import register_handlers
from app.bot.middleware import register_middleware


def setup_dispatcher() -> Dispatcher:
    """Создаёт и настраивает Dispatcher."""
    storage = RedisStorage.from_url(config.redis.url)
    dp = Dispatcher(storage=storage)

    # Подключаем обработчики и middleware
    register_handlers(dp)
    register_middleware(dp)

    return dp
