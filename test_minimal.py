import asyncio
import logging
from pathlib import Path

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_basic_functionality():
    """Тестирование базовой функциональности."""
    
    try:
        logger.info("Starting basic functionality test...")
        
        # Тест 1: Импорт конфигурации
        logger.info("Testing config import...")
        from config.settings import config
        logger.info("✓ Config imported successfully")
        
        # Тест 2: Создание бота
        logger.info("Testing bot creation...")
        from aiogram import Bot
        bot = Bot(token=config.bot.token)
        logger.info("✓ Bot created successfully")
        
        # Тест 3: Создание диспетчера
        logger.info("Testing dispatcher creation...")
        from aiogram import Dispatcher
        dp = Dispatcher()
        logger.info("✓ Dispatcher created successfully")
        
        # Тест 4: Простой обработчик
        @dp.message()
        async def echo(message):
            await message.answer("Тест прошел успешно!")
        
        logger.info("✓ Handler registered successfully")
        
        # Закрытие
        await bot.session.close()
        logger.info("✓ All tests passed")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
