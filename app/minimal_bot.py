import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from config.settings import config

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Минимальный запуск бота для тестирования."""
    logger.info("Starting minimal bot...")
    
    # Создание бота и диспетчера
    bot = Bot(token=config.bot.token)
    dp = Dispatcher()
    
    # Простой обработчик
    @dp.message(CommandStart())
    async def cmd_start(message: Message):
        await message.answer("✅ Бот СРО НОСО запущен успешно!")
    
    @dp.message()
    async def echo(message: Message):
        await message.answer(f"Получено сообщение: {message.text}")
    
    # Запуск polling
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
