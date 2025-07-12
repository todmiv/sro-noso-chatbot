"""Factory функции для создания Bot и Dispatcher."""
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from config.settings import config

def create_bot() -> Bot:
    return Bot(token=config.bot.token)

def create_dispatcher() -> Dispatcher:
    storage = RedisStorage.from_url(config.database.redis_url)
    return Dispatcher(storage=storage)
