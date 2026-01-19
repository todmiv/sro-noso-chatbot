"""
Фабричные функции для создания экземпляров Telegram бота и диспетчера.

Этот модуль отвечает за:
- Создание Bot экземпляра с токеном из конфигурации
- Настройку Dispatcher с Redis хранилищем для FSM (Finite State Machine)
- Конфигурацию хранения состояний диалогов пользователей

Архитектура:
- Bot: основной интерфейс для взаимодействия с Telegram API
- Dispatcher: маршрутизатор входящих обновлений
- Redis Storage: персистентное хранение состояний пользователей
"""

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from config.settings import config


def create_bot() -> Bot:
    """
    Создает и настраивает экземпляр Telegram бота.

    Returns:
        Bot: Экземпляр бота с токеном аутентификации

    Примечания:
        - Токен берется из конфигурации config.bot.token
        - Бот использует асинхронный HTTP клиент для API запросов
        - Поддерживает все типы обновлений от Telegram
    """
    return Bot(token=config.bot.token)


def create_dispatcher() -> Dispatcher:
    """
    Создает диспетчер с настроенным Redis хранилищем для состояний.

    Returns:
        Dispatcher: Экземпляр диспетчера с Redis storage

    Примечания:
        - Redis используется для хранения FSM состояний пользователей
        - Поддерживает масштабирование (несколько экземпляров бота)
        - Автоматическая сериализация/десериализация состояний
        - URL подключения берется из config.redis.url
    """
    # Создаем Redis хранилище для FSM состояний
    # Это позволяет сохранять состояния пользователей между перезапусками
    storage = RedisStorage.from_url(config.redis.url)

    # Создаем диспетчер с настроенным хранилищем
    dp = Dispatcher(storage=storage)

    return dp
