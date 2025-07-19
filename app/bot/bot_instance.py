"""Factory функции для создания Bot и Dispatcher."""
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from config.settings import config


def create_bot() -> Bot:
    """Создает экземпляр бота."""
    return Bot(token=config.bot.token)


def create_dispatcher() -> Dispatcher:
    """Создает диспетчер с настроенным хранилищем."""
    storage = RedisStorage.from_url(config.redis.url)
    dp = Dispatcher(storage=storage)
    return dp
