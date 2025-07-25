import logging
import structlog
from logging.handlers import RotatingFileHandler

def setup_logging() -> None:
    """Configure application logging."""
    try:
        # Настройка формата логов
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
        )
        
        # Хендлер для консоли
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        # Хендлер для файла с ротацией
        file_handler = RotatingFileHandler(
            filename='bot.log',
            maxBytes=10*1024*1024,  # 10 MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        
        # Основная конфигурация
        logging.basicConfig(
            level=logging.DEBUG,  # Более детальный уровень для разработки
            handlers=[console_handler, file_handler]
        )
        
        # Конфигурация structlog
        structlog.configure(
            wrapper_class=structlog.make_filtering_bound_logger(logging.DEBUG)
        )
    except Exception as e:
        logging.error(f"Failed to configure logging: {e}")
        raise
